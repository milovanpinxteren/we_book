# import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from bookingsystem.Classes.PortalClasses.menu_shower import MenuShower
from bookingsystem.Classes.PortalClasses.menu_updater import MenuUpdater
from bookingsystem.Classes.PortalClasses.reservation_maker import ReservationMaker
from bookingsystem.Classes.PortalClasses.reservation_shower import reservationShower
from bookingsystem.Classes.availability_checker import AvailabilityChecker
from bookingsystem.Classes.booking_confirmer import BookingConfirmer
from bookingsystem.Classes.booking_maker import BookingMaker
from bookingsystem.forms import ReservationForm, ConfirmBookingForm
from bookingsystem.models import Restaurants, UserRestaurantLink, Reservations, Tables, Courses, Dishes
from datetime import date, datetime, timedelta
from django.utils.translation import gettext as _


def index(request):
    try:
        restaurantID = request.GET['restaurantID']
        request.session['restaurantID'] = restaurantID
    except Exception as e:
        try:
            restaurantID = request.session['restaurantID']
        except Exception as e:
            restaurantID = 1

    restaurant = Restaurants.objects.get(id=restaurantID)
    #TODO: only select timeslots based on availability
    availability_checker = AvailabilityChecker()
    availability, closed_list = availability_checker.get_availability(restaurantID)
    reservationform = ReservationForm(initial={'restaurant': restaurant, 'number_of_persons': 2,
                                       'reservation_date': date.today(),
                                    'reservation_time': datetime.now().strftime("%H:%M:%S")})

    json_availabilitydata = str(availability).replace("'", '"')
    json_disable_datesdata = str(closed_list).replace("'", '"')
    context = {'restaurant': restaurant, 'reservationform': reservationform, 'availability': json_availabilitydata,
               'json_disable_datesdata': json_disable_datesdata}
    return render(request, 'index.html', context)


def make_reservation(request):
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST, request.FILES)
        if reservation_form.is_valid():
            #Form is valid, check if you can find a possible table
            restaurant_id = request.GET['restaurantID']
            number_of_persons = reservation_form['number_of_persons'].value()
            reservation_date = reservation_form['reservation_date'].value()
            reservation_time = reservation_form['reservation_time'].value()
            bookingmaker = BookingMaker()
            context = bookingmaker.make_booking(restaurant_id, number_of_persons, reservation_date, reservation_time)

            if context['status'] == 'possible_reservation_found':
                request.session['status'] = context['status']
                request.session['table_id'] = context['table_id']
                request.session['reservation_date'] = str(context['reservation_date'])
                request.session['start_time'] = str(context['start_time'])
                request.session['number_of_persons'] = context['number_of_persons']
                request.session['held_reservation_id'] = context['held_reservation_id']
                request.session['held_reservation_id'] = context['held_reservation_id']
            confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
            context['confirmation_form'] = confirmation_form
        else:
            message = _("booking_failed")
            print(reservation_form.errors)
            context = {'message': message}
    else:
        context = {}
        context['status'] = request.session['status']
        context['table_id'] = request.session['table_id']
        context['reservation_date'] = request.session['reservation_date']
        context['start_time'] = request.session['start_time']
        context['number_of_persons'] = request.session['number_of_persons']
        context['held_reservation_id'] = request.session['held_reservation_id']
        context['held_reservation_id'] = request.session['held_reservation_id']
    return render(request, 'booking_confirmation.html', context)


def confirm_booking(request):
    if request.method == 'POST':
        confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
        if confirmation_form.is_valid():
            reservationID = request.GET['reservationID']
            name = confirmation_form['name'].value()
            email = confirmation_form['email'].value()
            telephone_nr = confirmation_form['telephone_nr'].value()
            bookingconfirmer = BookingConfirmer()
            context = bookingconfirmer.confirm_booking(reservationID, name, email, telephone_nr)
            request.session['status'] = context['status']
        else:
            print(confirmation_form.errors)
            request.session['status'] = 'booking_failed'
            context = {'status': request.session['status'],
                       'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                       'start_time': request.session['start_time'],
                       'number_of_persons': request.session['number_of_persons'],
                       'held_reservation_id': False,
                       'confirmation_form': confirmation_form}
            render(request, 'booking_confirmation.html', context)

    else:
        confirmation_form = ConfirmBookingForm()
        request.session['status'] = 'booking_failed'
        context = {'status': request.session['status'],
                   'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'], 'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id'], 'confirmation_form': confirmation_form}
        render(request, 'booking_confirmation.html', context)
    return render(request, 'booking_confirmed.html', context)


def drop_reservation(request):
    reservation_id_1 = int(request.GET.get('reservation_id'))
    reservation_id_2 = request.session['held_reservation_id']
    if reservation_id_1 == reservation_id_2:
        if Reservations.objects.filter(id=reservation_id_1).values_list('confirmed', flat=True)[0] == False:
            Reservations.objects.filter(id=reservation_id_1).update(cancelled=True, confirmed=False)
            print('deleted reservation')
    # return index(request)
    return HttpResponse("Session expired")

def delete_reservation(request):
    reservation_id = request.GET['reservationID']
    path = request.GET['path']
    Reservations.objects.filter(id=reservation_id).update(cancelled=True, confirmed=False)
    #TODO: send email
    request.session['status'] = 'reservation_cancelled'
    if path == 'confirmed_booking':
        context = {'status': request.session['status'],
                   'table_id': request.session['table_id'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'], 'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id']}
        return render(request, 'booking_confirmed.html', context)
    elif path == 'show_reservations':
        current_user = request.user.id
        reservation_shower = reservationShower()
        context = reservation_shower.prepare_table(current_user)
        context['deleted_reservation'] = reservation_id
        return render(request, 'restaurant_portal.html', context)


###########################################FOR RESTAURANTS##############################################################

def restaurant_portal(request):
    return render(request, 'restaurant_portal.html')


def show_reservations(request):
    current_user = request.user.id
    reservation_shower = reservationShower()
    context = reservation_shower.prepare_table(current_user)
    # add_reservation_form = AddReservationForm()
    # context['add_reservation_form'] = add_reservation_form

    return render(request, 'restaurant_portal.html', context)





def rollback_deletion(request):
    reservation_id = request.GET['reservationID']
    Reservations.objects.filter(id=reservation_id).update(cancelled=False, confirmed=True)
    current_user = request.user.id
    reservation_shower = reservationShower()
    context = reservation_shower.prepare_table(current_user)
    context['rolled_back_deletion'] = reservation_id
    return render(request, 'restaurant_portal.html', context)


def make_reservation_in_portal(request):
    if request.method == 'POST':
        reservation_maker = ReservationMaker()
        context = reservation_maker.make_reservation(request)
    return render(request, 'restaurant_portal.html', context)


def view_menu(request):
    context = MenuShower().prepare_menu(request)
    return render(request, 'restaurant_portal.html', context)

def update_menu(request):
    if request.method == 'POST':
        menu_updater = MenuUpdater()
        context = menu_updater.update_menu(request)
        return render(request, 'restaurant_portal.html', context)


def delete_course(request, course_id):
    try:
        record = Courses.objects.get(pk=course_id)
        record.delete()
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)
    except Courses.DoesNotExist:
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)


def delete_dish(request, dish_id):
    try:
        record = Dishes.objects.get(pk=dish_id)
        record.delete()
        # context = MenuShower().prepare_menu(request)
        response_data = {'message': 'Record deleted successfully'}
        return JsonResponse(response_data)
    except Courses.DoesNotExist:
        # context = MenuShower().prepare_menu(request)
        # return render(request, 'restaurant_portal.html', context)
        print('asdfads')