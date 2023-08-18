from django.utils.translation import gettext as _

class BookingMaker():
    def make_booking(self, restaurant, number_of_persons, reservation_date, reservation_time):
        context =  {'message': _("booking_succes")}
        return context