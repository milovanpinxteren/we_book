import os
from datetime import date, datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from bookingsystem.Classes.PortalClasses.reservation_shower import reservationShower
from bookingsystem.Classes.availability_checker import AvailabilityChecker
from bookingsystem.Classes.booking_confirmer import BookingConfirmer
from bookingsystem.Classes.booking_maker import BookingMaker
from bookingsystem.Classes.email_sender import EmailSender
from bookingsystem.Classes.id_handler import IDHandler
from bookingsystem.forms import ReservationForm, ConfirmBookingForm
from bookingsystem.models import Restaurants, Reservations

def index(request):
    try:
        id_code = request.GET['restaurantID']
        restaurantID = IDHandler().decode(id_code)
        # restaurantID = request.GET['restaurantID']
        request.session['restaurantID'] = restaurantID
    except Exception as e:
        try:
            restaurantID = request.session['restaurantID']
        except Exception as e:
            restaurantID = 1

    restaurant = Restaurants.objects.get(id=restaurantID)
    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year
    disabled_dates = AvailabilityChecker.get_disabled_dates(request, restaurant, current_month, current_year)
    timestamps = AvailabilityChecker.make_timestamps(request)
    request.session['timestamps'] = timestamps
    try:
        status = request.session['status']
        print(status)
    except Exception as e:
        print(e)
        status = ''
    context = {'restaurant': restaurant, 'disabled_dates': disabled_dates, 'status': status}
    return render(request, 'index.html', context)


def check_available_dates(request):
    restaurant_id = int(request.POST['restaurantID'])
    restaurant = Restaurants.objects.get(pk=restaurant_id)
    disabled_dates = AvailabilityChecker.get_disabled_dates(request, restaurant, int(request.POST['month']),
                                                            int(request.POST['year']))
    response_data = {'disabled_dates': disabled_dates}
    return JsonResponse(response_data)


def check_availability(request):
    restaurant_id = int(request.POST['restaurantID'])
    timestamps = request.session['timestamps']
    restaurant = Restaurants.objects.get(pk=restaurant_id)
    if request.POST['number_of_persons'] != '':
        availability = AvailabilityChecker.query_availability(request, restaurant, request.POST['reservation_date'],
                                                              request.POST['number_of_persons'], timestamps)
    else:
        print('number of persons not filled in')
    return JsonResponse(availability)


def make_reservation(request):
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST, request.FILES)
        if reservation_form.is_valid():
            # Form is valid, check if you can find a possible table
            restaurant_id = request.GET['restaurantID']
            restaurant = Restaurants.objects.get(pk=restaurant_id)
            number_of_persons = reservation_form['number_of_persons'].value()
            reservation_date = reservation_form['reservation_date'].value()
            reservation_time = reservation_form['reservation_time'].value()
            bookingmaker = BookingMaker()
            context = bookingmaker.make_booking(restaurant_id, number_of_persons, reservation_date, reservation_time)
            request.session['status'] = context['status']
            request.session['reservation_date'] = reservation_date
            request.session['start_time'] = reservation_time
            request.session['number_of_persons'] = number_of_persons
            request.session['restaurant_name'] = restaurant.name
            request.session['restaurant_email'] = restaurant.email
            request.session['restaurant_website'] = restaurant.website

            if context['status'] == 'possible_reservation_found':
                request.session['held_reservation_id'] = context['held_reservation_id']
                request.session['table_id'] = context['table_id']
                confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
                context['confirmation_form'] = confirmation_form
                context['restaurant_name'] = restaurant.name
                context['restaurant_email'] = restaurant.email
                context['restaurant_website'] = restaurant.website
                return render(request, 'booking_confirmation.html', context)
            else:  # form valid, but no possible reservation found
                message = _("booking_failed")
                request.session['status'] = message
                context = {'message': message, 'restaurant_name': restaurant.name,
                           'reservation_date': request.session['reservation_date'],
                           'start_time': request.session['start_time'],
                           'number_of_persons': request.session['number_of_persons'],
                           'restaurant_phone_nr': restaurant.telephone_nr}
                return render(request, 'booking_confirmation.html', context)
        else:  # form invalid
            print('invalid form')
            message = _("booking_failed")
            request.session['status'] = message
            return redirect('bookingsystem:index')
    return redirect('bookingsystem:index')  # request methods is not post


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
            context['restaurant_name'] = request.session['restaurant_name']
            context['restaurant_email'] = request.session['restaurant_email']
            context['restaurant_website'] = request.session['restaurant_website']
        else:
            print(confirmation_form.errors)
            request.session['status'] = 'booking_failed'
            context = {'status': request.session['status'],
                       'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                       'start_time': request.session['start_time'],
                       'number_of_persons': request.session['number_of_persons'],
                       'held_reservation_id': False,
                       'confirmation_form': confirmation_form, 'restaurant_name': request.session['restaurant_name']
                , 'restaurant_email': request.session['restaurant_email'],
                       'restaurant_website': request.session['restaurant_website']}
            render(request, 'booking_confirmation.html', context)

    else:
        confirmation_form = ConfirmBookingForm()
        request.session['status'] = 'booking_failed'
        context = {'status': request.session['status'],
                   'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'],
                   'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id'],
                   'confirmation_form': confirmation_form, 'restaurant_name': request.session['restaurant_name']
            , 'restaurant_email': request.session['restaurant_email'],
                   'restaurant_website': request.session['restaurant_website']}
        render(request, 'booking_confirmation.html', context)
    return render(request, 'booking_confirmed.html', context)


def drop_reservation(request):
    reservation_id_1 = int(request.GET.get('reservation_id'))
    reservation_id_2 = request.session['held_reservation_id']
    if reservation_id_1 == reservation_id_2:
        if Reservations.objects.filter(id=reservation_id_1).values_list('confirmed', flat=True)[0] == False:
            Reservations.objects.filter(id=reservation_id_1).update(cancelled=True, confirmed=False)
            print('deleted reservation')
    return HttpResponse("Session expired, no reservation made")


def delete_reservation(request):
    email_sender = EmailSender()
    reservation_id = request.GET['reservationID']
    path = request.GET['path']
    Reservations.objects.filter(id=reservation_id).update(cancelled=True, confirmed=False)
    # TODO: send email
    reservation = Reservations.objects.get(id=reservation_id)
    restaurant_name = reservation.restaurant.name

    booker_subject = 'Cancellazione Prenotazione al ' + restaurant_name
    booker_message_text = 'Gentile Cliente,\n\n La tua prenotazione presso ' + restaurant_name + ' per ' + str(
        reservation.reservation_date) + ' alle ore ' + str(reservation.arrival_time)[
                                                       :5] + " viene cancellato. \n\n Puoi effettuare un'altra prenotazione sul sito web " + reservation.restaurant.website + " oppure contatta il ristorante tramite " + reservation.restaurant.telephone_nr + "\n\nCordiali saluti,\n" + restaurant_name
    english_translation = 'Dear Customer,\n\nYour reservation at ' + restaurant_name + ' for ' + str(
        reservation.reservation_date) + ' at ' + str(reservation.arrival_time)[
                                                 :5] + " has been canceled. \n\nYou can make another reservation on the website " + reservation.restaurant.website + " or contact the restaurant at " + reservation.restaurant.telephone_nr + "\n\nBest regards,\n" + restaurant_name + '\n\n'

    restaurant_subject = 'Cancellazione Prenotazione'
    restaurant_message_text = 'Gentile Cliente,\n\n Una prenotazione presso per ' + str(
        reservation.reservation_date) + ' alle ore ' + str(reservation.arrival_time)[
                                                       :5] + ' viene cancellato. \n\n Nome di cliente: ' + reservation.customer.full_name + '\n Email: ' + reservation.customer.email + '\n numerò di telephono: ' + str(
        reservation.customer.telephone_nr) + '\n numerò di tavolo: ' + str(reservation.table.table_nr) + '\n\n'

    email_sender.send_booker_email(reservation.customer.email, booker_subject, booker_message_text, english_translation)
    email_sender.send_restaurant_email(reservation.restaurant.email, restaurant_subject, restaurant_message_text)
    email_sender.send_restaurant_email('info@ristaiuto.it', restaurant_subject, restaurant_message_text)  # for checking
    request.session['status'] = 'reservation_cancelled'
    if path == 'confirmed_booking':
        context = {'status': request.session['status'],
                   'table_id': request.session['table_id'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'],
                   'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id']}
        return render(request, 'booking_confirmed.html', context)
    elif path == 'show_reservations':
        current_user = request.user.id
        reservation_shower = reservationShower()
        context = reservation_shower.prepare_table(current_user)
        context['deleted_reservation'] = reservation_id
        return render(request, 'restaurant_portal.html', context)



