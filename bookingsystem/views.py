import datetime
from django.shortcuts import render

from bookingsystem.booking_maker import BookingMaker
from bookingsystem.forms import ReservationForm
from bookingsystem.models import Restaurants
from datetime import date, datetime
from django.utils.translation import gettext as _

def index(request):
    try:
        restaurantID = request.GET['restaurantID']
        request.session['restaurantID'] = restaurantID
    except Exception as e:
        restaurantID = request.session['restaurantID']

    restaurant = Restaurants.objects.get(id=restaurantID)
    reservationform = ReservationForm(initial={'restaurant': restaurant, 'number_of_persons': 2,
                                       'reservation_date': date.today(),
                                    'reservation_time': datetime.now().strftime("%H:%M:%S")})

    context = {'restaurant': restaurant, 'reservationform': reservationform}
    return render(request, 'index.html', context)


def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = request.GET['restaurantID']
            number_of_persons = form['number_of_persons'].value()
            reservation_date = form['reservation_date'].value()
            reservation_time = form['reservation_time'].value()
            bookingmaker = BookingMaker()
            context = bookingmaker.make_booking(restaurant, number_of_persons, reservation_date, reservation_time)
        else:
            message = _("booking_failed")
            print(form.errors)
            context = {'message': message}
    return render(request, 'booking_confirmation.html', context)