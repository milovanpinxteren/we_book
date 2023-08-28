import datetime

from django.http import HttpResponse
from django.shortcuts import render
from bookingsystem.Classes.booking_confirmer import BookingConfirmer
from bookingsystem.Classes.booking_maker import BookingMaker
from bookingsystem.forms import ReservationForm, ConfirmBookingForm
from bookingsystem.models import Restaurants, UserRestaurantLink, Reservations
from datetime import date, datetime
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
    reservationform = ReservationForm(initial={'restaurant': restaurant, 'number_of_persons': 2,
                                       'reservation_date': date.today(),
                                    'reservation_time': datetime.now().strftime("%H:%M:%S")})

    context = {'restaurant': restaurant, 'reservationform': reservationform}
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
            Reservations.objects.filter(id=reservation_id_1).delete()
            print('deleted reservation')
    # return index(request)
    return HttpResponse("Session expired")

def delete_reservation(request):
    reservation_id = request.GET['reservationID']
    path = request.GET['path']
    Reservations.objects.filter(id=reservation_id).delete()
    #TODO: send email
    request.session['status'] = 'reservation_cancelled'
    if path == 'confirmed_booking':
        context = {'status': request.session['status'],
                   'table_id': request.session['table_id'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'], 'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id']}
        return render(request, 'booking_confirmed.html', context)
    elif path == 'show_reservations':
        current_restaurant_id = UserRestaurantLink.objects.filter(user_id=request.user.id).values_list('restaurant_id', flat=True)[0]
        reservations = Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True).order_by('reservation_date', 'arrival_time')
        dates = sorted(list(reservations.values_list("reservation_date", flat=True).distinct()))
        context = {'reservations': reservations, 'dates': dates, 'action': './show_reservations/show_reservations.html'}
        return render(request, 'restaurant_portal.html', context)

###########################################FOR RESTAURANTS##############################################################

def restaurant_portal(request):
    return render(request, 'restaurant_portal.html')


def show_reservations(request):
    current_user = request.user.id
    try:
        current_restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
        reservations = Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True).order_by('reservation_date', 'arrival_time')
        dates = sorted(list(reservations.values_list("reservation_date", flat=True).distinct()))
        context = {'reservations': reservations, 'dates': dates, 'action': './show_reservations/show_reservations.html'}
    except Exception as e: #No restaurant found for current user
        context = {'status': 'no_restaurant_known_for_user'}
        return render(request, 'restaurant_portal.html', context)
    return render(request, 'restaurant_portal.html', context)


def show_dashboard(request):
    context = {'action': './show_dashboard/show_dashboard.html'}
    return render(request, 'restaurant_portal.html', context)