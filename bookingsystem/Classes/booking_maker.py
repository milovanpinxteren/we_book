import time

from django.db.models import Q
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from bookingsystem.models import Tables, Reservations, Restaurants, CustomRestaurantAvailability
import calendar
from django.utils.translation import get_language


class BookingMaker():
    def make_booking(self, restaurant_id, number_of_persons, reservation_date, reservation_time):
        reservation_date, reservation_time = self.format_reservation_date_time(reservation_date, reservation_time)
        context = self.check_availability(restaurant_id, number_of_persons, reservation_date, reservation_time)
        return context

    def check_availability(self, restaurant_id, number_of_persons, reservation_date, reservation_time):
        #check if restaurant is open on date
        valid_reservation = self.get_restaurant_availability(restaurant_id, reservation_date, reservation_time)
        if not valid_reservation:
            context = {'status': "restaurant_closed",
                       'table_id': '', 'start_time': reservation_time,
                       'number_of_persons': number_of_persons}
            return context
        #get possible tables
        table_query = Q(restaurant_id=restaurant_id) & Q(min_pers__lte=number_of_persons) & Q(max_pers__gte=number_of_persons)
        possible_tables = Tables.objects.filter(table_query)
        date_condition = Q(reservation_date=reservation_date)

        for possible_table in possible_tables:
            duration = Restaurants.objects.filter(id=restaurant_id).values_list('meal_duration', flat=True)[0]
            start_time = reservation_time
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
                                            table_id=possible_table.id, confirmed=False, number_of_persons=number_of_persons)
                context = {'status': "possible_reservation_found",
                           'table_id': possible_table.id, 'reservation_date': reservation_date,
                           'start_time': reservation_time, 'number_of_persons': number_of_persons,
                           'held_reservation_id': held_reservation.id}
                return context
        context = {'status': "no_possible_reservation_found",
                   'table_id': '', 'start_time': reservation_time,
                   'number_of_persons': number_of_persons}
        return context

    def get_restaurant_availability(self, restaurant_id, reservation_date, reservation_time):
        valid_reservation = False
        restaurant = Restaurants.objects.filter(id=restaurant_id)

        changed_availability = CustomRestaurantAvailability.objects.filter(date=reservation_date)

        if not changed_availability:
            day_name = calendar.day_name[reservation_date.weekday()].lower()
            column_name = 'open_' + day_name
            restaurant_open = restaurant.values_list(column_name, flat=True)[0]
            if restaurant_open: #check if reservation date is within opening hours

                restaurant_opening_time = restaurant.values_list('opening_time', flat=True)[0]
                restaurant_closing_time = restaurant.values_list('closing_time', flat=True)[0]
                meal_duration = restaurant.values_list('meal_duration', flat=True)[0]

                fixed_date = datetime(1900, 1, 1)
                restaurant_opening_time = fixed_date.replace(hour=restaurant_opening_time.hour, minute=restaurant_opening_time.minute)
                restaurant_closing_time = fixed_date.replace(hour=restaurant_closing_time.hour, minute=restaurant_closing_time.minute)
                last_reservation_time = restaurant_closing_time - timedelta(hours=meal_duration)
                reservation_time = fixed_date.replace(hour=reservation_time.hour, minute=reservation_time.minute)

                valid_reservation = restaurant_opening_time <= reservation_time <= last_reservation_time
                if valid_reservation:
                    valid_reservation = True
                else:
                    valid_reservation = False
            return valid_reservation
        elif changed_availability:
            restaurant_open = changed_availability.values_list('open', flat=True)[0]
            if restaurant_open:  # check if reservation date is within opening hours
                restaurant_opening_time = restaurant.values_list('opening_time', flat=True)[0]
                restaurant_closing_time = restaurant.values_list('closing_time', flat=True)[0]
                meal_duration = restaurant.values_list('meal_duration', flat=True)[0]
                last_reservation_time = restaurant_closing_time - timedelta(hours=meal_duration)
                valid_reservation = restaurant_opening_time <= reservation_time <= last_reservation_time
                if valid_reservation:
                    valid_reservation = True
                else:
                    valid_reservation = False

        return valid_reservation

    def format_reservation_date_time(self, reservation_date, reservation_time):
        current_language = get_language()
        reservation_time = datetime.strptime(reservation_time, "%H:%M")
        try:
            if current_language == 'de':
                reservation_date = datetime.strptime(reservation_date, '%d.%M.%Y')
            elif current_language == 'fr' or current_language == 'it':
                reservation_date = datetime.strptime(reservation_date, '%d/%M/%Y')
            elif current_language == 'en':
                reservation_date = datetime.strptime(reservation_date, '%Y-%M-%d')
            elif current_language == 'nl':
                reservation_date = datetime.strptime(reservation_date, '%Y-%M-%d')
        except Exception as e:
            reservation_date = datetime.strptime(reservation_date, '%Y-%M-%d')
        return reservation_date, reservation_time




