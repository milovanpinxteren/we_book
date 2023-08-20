import time

from django.db.models import Q
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from bookingsystem.models import Tables, Reservations, Restaurants, CustomRestaurantAvailability
import calendar

class BookingMaker():
    def make_booking(self, restaurant_id, number_of_persons, reservation_date, reservation_time):
        context = self.check_availability(restaurant_id, number_of_persons, reservation_date, reservation_time)
        return context

    def check_availability(self, restaurant_id, number_of_persons, reservation_date, reservation_time):
        #check if restaurant is open on date
        restaurant_open = self.get_restaurant_availability(restaurant_id, reservation_date, reservation_time)
        if not restaurant_open:
            context = {'message': _("restaurant_closed"),
                       'table_id': '', 'start_time': reservation_time,
                       'number_of_persons': number_of_persons}
            return context
        #get possible tables
        table_query = Q(restaurant_id=restaurant_id) & Q(min_pers__lte=number_of_persons) & Q(max_pers__gte=number_of_persons)
        possible_tables = Tables.objects.filter(table_query)
        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d")
        date_condition = Q(reservation_date=reservation_date)
        for possible_table in possible_tables:
            duration = possible_table.duration_hours
            start_time = datetime.strptime(reservation_time, "%H:%M:%S")
            end_time = (start_time + timedelta(hours=duration)).strftime("%H:%M:%S")

            reservations = Reservations.objects.filter(
                Q(restaurant_id=restaurant_id) & Q(table_id=possible_table.id) & date_condition)

            before_timeslot_query = Q(arrival_time__lt=end_time) | Q(end_time__gt=start_time)
            overlapping_reservations = reservations.filter(before_timeslot_query)
            if overlapping_reservations:
                print('table reserved, check new table')
            else:
                print('found table')
                held_reservation = Reservations.objects.create(reservation_date=reservation_date, arrival_time=reservation_time,
                                            end_time=end_time, paid=False, paid_amount=0, created_at=datetime.now(),
                                            updated_at=datetime.now(), restaurant_id=restaurant_id, customer_id=0,
                                            table_id=possible_table.id, confirmed=False)
                context = {'message': _("possible_reservation_found"),
                           'table_id': possible_table.id, 'reservation_date': reservation_date,
                           'start_time': reservation_time, 'number_of_persons': number_of_persons,
                           'held_reservation_id': held_reservation.id}
                return context
        context = {'message': _("no_possible_reservation_found"),
                   'table_id': '', 'start_time': reservation_time,
                   'number_of_persons': number_of_persons}
        return context

    def get_restaurant_availability(self, restaurant_id, reservation_date, reservation_time):
        restaurant_open = False
        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d")
        changed_availability = CustomRestaurantAvailability.objects.filter(date=reservation_date)
        if not changed_availability:
            day_name = calendar.day_name[reservation_date.weekday()].lower()
            column_name = 'open_' + day_name
            restaurant = Restaurants.objects.filter(id=restaurant_id)
            restaurant_open = restaurant.values_list(column_name, flat=True)[0]
        elif changed_availability:
            restaurant_open = changed_availability.values_list('open', flat=True)[0]
        # if restaurant_open:
        #     opening_time = restaurant.values_list()

        return restaurant_open

