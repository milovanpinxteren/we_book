import datetime
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
        restaurantID = request.session['restaurantID']

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
            restaurant_id = request.GET['restaurantID']
            number_of_persons = reservation_form['number_of_persons'].value()
            reservation_date = reservation_form['reservation_date'].value()
            reservation_time = reservation_form['reservation_time'].value()
            bookingmaker = BookingMaker()
            context = bookingmaker.make_booking(restaurant_id, number_of_persons, reservation_date, reservation_time)
            confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
            context['confirmation_form'] = confirmation_form
        else:
            message = _("booking_failed")
            print(reservation_form.errors)
            context = {'message': message}
    return render(request, 'booking_confirmation.html', context)


def confirm_booking(request):
    #TODO: change confirmed to true and add Customer and Id
    if request.method == 'POST':
        confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
        if confirmation_form.is_valid():
            reservationID = request.GET['reservationID']
            name = confirmation_form['name'].value()
            email = confirmation_form['email'].value()
            telephone_nr = confirmation_form['telephone_nr'].value()
            bookingconfirmer = BookingConfirmer()
            context = bookingconfirmer.confirm_booking(reservationID, name, email, telephone_nr)
        else:
            message = _("booking_failed")
            print(confirmation_form.errors)
            context = {'message': message}
    return render(request, 'booking_confirmation.html', context)

def see_reservations(request):
    current_user = request.user.id
    current_restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
    reservations = Reservations.objects.filter(restaurant_id=current_restaurant_id)
    context = {'reservations': reservations}
    return render(request, 'see_reservations.html', context)