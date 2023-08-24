from datetime import datetime

from bookingsystem.models import Reservations, Customers


class BookingConfirmer():
    def confirm_booking(self, reservationID, name, email, telephone_nr):
        print('confirming booking')
        customer = Customers.objects.create(full_name=name, email=email, telephone_nr=telephone_nr, updated_at=datetime.now())
        reservation = Reservations.objects.filter(id=reservationID).update(confirmed=True, customer=customer)

        #TODO: send email
        context = {'confirmed_reservation': True, 'reservation': reservationID,
                   'customer': customer.id}
        return context