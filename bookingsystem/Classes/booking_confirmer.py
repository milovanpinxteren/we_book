from datetime import datetime

from bookingsystem.models import Reservations, Customers, Restaurants


class BookingConfirmer():
    def confirm_booking(self, reservationID, name, email, telephone_nr):
        print('confirming booking')
        customer = Customers.objects.create(full_name=name, email=email, telephone_nr=telephone_nr, updated_at=datetime.now())
        reservation = Reservations.objects.filter(id=reservationID)
        reservation.update(confirmed=True, customer=customer)
        restaurantID = reservation.values_list('restaurant', flat=True)[0]
        restaurant = Restaurants.objects.filter(id=restaurantID).values_list('name', flat=True)[0]
        #TODO: send email
        context = {'confirmed_reservation': True, 'status': 'booking_confirmed',
                   'reservation_date': reservation.values_list('reservation_date', flat=True)[0],
                   'start_time': reservation.values_list('arrival_time', flat=True)[0],
                   'number_of_persons': reservation.values_list('number_of_persons', flat=True)[0],
                   'name': customer.full_name, 'email_adress': customer.email, 'telephone_number': customer.telephone_nr,
                   'restaurant': restaurant, 'restaurantID': restaurantID, 'reservationID': reservationID
                   }
        return context