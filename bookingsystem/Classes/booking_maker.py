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
                Q(restaurant_id=restaurant_id) & Q(table_id=possible_table.id) & date_condition & Q(confirmed=True))

            before_timeslot_query = Q(arrival_time__lt=end_time) | Q(end_time__gt=start_time)
            overlapping_reservations = reservations.filter(before_timeslot_query)
            if overlapping_reservations:
                print('table reserved, check new table')
            else:
                print('found table')
                held_reservation = Reservations.objects.create(reservation_date=reservation_date, arrival_time=reservation_time,
                                            end_time=end_time, created_at=datetime.now(),
                                            updated_at=datetime.now(), restaurant_id=restaurant_id, customer_id=0,
                                            table_id=possible_table.id, confirmed=False, number_of_persons=number_of_persons)
                context = {'status': "possible_reservation_found",
                           'table_id': possible_table.id, 'reservation_date': reservation_date,
                           'start_time': reservation_time, 'number_of_persons': number_of_persons,
                           'held_reservation_id': held_reservation.id}
                return context
        context = {'status': "no_possible_reservation_found",
                   'table_id': '', 'start_time': reservation_time, 'reservation_date': reservation_date,
                   'number_of_persons': number_of_persons,
                   'restaurant_phone_nr': Restaurants.objects.filter(id=restaurant_id).values_list('telephone_nr', flat=True)[0]}
        return context

    def get_restaurant_availability(self, restaurant_id, reservation_date, reservation_time):
        valid_reservation = False
        restaurant = Restaurants.objects.get(id=restaurant_id)

        changed_availability = CustomRestaurantAvailability.objects.filter(date=reservation_date)

        if not changed_availability:
            day_name = calendar.day_name[reservation_date.weekday()].lower()
            column_name = 'open_' + day_name
            restaurant_open = getattr(restaurant, column_name)
            if restaurant_open: #check if reservation date is within opening hours
                opening_time_1_field_name = f'opening_time_{day_name}_1'
                opening_time_1 = getattr(restaurant, opening_time_1_field_name)
                closing_time_1_field_name = f'closing_time_{day_name}_1'
                closing_time_1 = getattr(restaurant, closing_time_1_field_name)
                opening_time_2_field_name = f'opening_time_{day_name}_2'
                opening_time_2 = getattr(restaurant, opening_time_2_field_name)
                closing_time_2_field_name = f'closing_time_{day_name}_2'
                closing_time_2 = getattr(restaurant, closing_time_2_field_name)
                # meal_duration = getattr(restaurant, 'meal_duration')
                reservation_time = reservation_time.time()

                valid_reservation = (opening_time_1 <= reservation_time <= closing_time_1) or (opening_time_2 <= reservation_time <= closing_time_2)
                if valid_reservation:
                    valid_reservation = True
                else:
                    valid_reservation = False
            return valid_reservation
        elif changed_availability:
            restaurant_open = changed_availability.values_list('open', flat=True)[0]
            if restaurant_open:  # check if reservation date is within opening hours
                restaurant_opening_time = changed_availability.values_list('start_time', flat=True)[0]
                restaurant_closing_time = changed_availability.values_list('end_time', flat=True)[0]
                fixed_date = datetime(1900, 1, 1)
                restaurant_opening_time = fixed_date.replace(hour=restaurant_opening_time.hour, minute=restaurant_opening_time.minute)
                restaurant_closing_time = fixed_date.replace(hour=restaurant_closing_time.hour, minute=restaurant_closing_time.minute)
                meal_duration = restaurant.values_list('meal_duration', flat=True)[0]
                last_reservation_time = restaurant_closing_time - timedelta(hours=meal_duration)
                valid_reservation = restaurant_opening_time <= reservation_time <= last_reservation_time
                if valid_reservation:
                    valid_reservation = True
                else:
                    valid_reservation = False

        return valid_reservation

    def format_reservation_date_time(self, reservation_date, reservation_time):
        reservation_date = datetime.strptime(reservation_date, '%m/%d/%Y')
        reservation_time = datetime.strptime(reservation_time, "%H:%M")
        return reservation_date, reservation_time




