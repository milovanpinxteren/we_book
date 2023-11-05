
from datetime import date, timedelta, datetime

from django.db.models import Q

from bookingsystem.models import Restaurants, CustomRestaurantAvailability, Tables, Reservations


class AvailabilityChecker():
    def make_timestamps(self):
        timestamps = []
        start_time = datetime.strptime("00:00", "%H:%M")
        for i in range(
                96):  # Generate timestamps for every 15 minutes in a day (24 hours * 60 minutes / 15 minutes)
            timestamps.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=15)
        return timestamps

    def get_disabled_dates(self, restaurant, current_month, current_year):
        first_day = date(current_year, current_month, 1)
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year
        last_day = date(next_year, next_month, 1) - timedelta(days=1)
        closed_dates = []

        current_date = first_day
        while current_date <= last_day:
            field_name = f'open_{current_date.strftime("%A").lower()}'
            if getattr(restaurant, field_name) is False:
                closed_dates.append(str(current_date))
            current_date += timedelta(days=1)

        custom_closed_dates_query = CustomRestaurantAvailability.objects.filter(
            restaurant=restaurant,
            date__range=(first_day, last_day),
            open=False)
        custom_open_dates_query = CustomRestaurantAvailability.objects.filter(
            restaurant=restaurant,
            date__range=(first_day, last_day),
            open=True)

        for custom_closed_date in custom_closed_dates_query:
            if str(custom_closed_date.date) not in closed_dates:
                closed_dates.append(str(custom_closed_date.date))

        for custom_open_date in custom_open_dates_query:
            if str(custom_open_date.date) in closed_dates:
                closed_dates.remove(str(custom_open_date.date))



        return closed_dates


    def query_availability(self, restaurant, reservation_date, number_of_persons, timestamps):
        date = datetime.strptime(reservation_date, '%m/%d/%Y')
        query_date = date.strftime('%Y-%m-%d')
        day = date.strftime('%A').lower()
        custom_availability = CustomRestaurantAvailability.objects.filter(restaurant=restaurant, date=date)
        if custom_availability:
            opening_time = custom_availability.values_list('start_time', flat=True)[0]
            closing_time = custom_availability.values_list('end_time', flat=True)[0]
        else:
            opening_time_1_field_name = f'opening_time_{day}_1'
            opening_time_1 = getattr(restaurant, opening_time_1_field_name)
            closing_time_1_field_name = f'closing_time_{day}_1'
            closing_time_1 = getattr(restaurant, closing_time_1_field_name)
            opening_time_2_field_name = f'opening_time_{day}_2'
            opening_time_2 = getattr(restaurant, opening_time_2_field_name)
            closing_time_2_field_name = f'closing_time_{day}_2'
            closing_time_2 = getattr(restaurant, closing_time_2_field_name)

        opening_time_1 = datetime.strptime(str(opening_time_1), "%H:%M:%S")
        closing_time_1 = datetime.strptime(str(closing_time_1), "%H:%M:%S")
        opening_time_2 = datetime.strptime(str(opening_time_2), "%H:%M:%S")
        closing_time_2 = datetime.strptime(str(closing_time_2), "%H:%M:%S")
        table_query = Q(restaurant_id=restaurant.id) & Q(min_pers__lte=number_of_persons) & Q(max_pers__gte=number_of_persons)
        possible_tables = Tables.objects.filter(table_query)
        time_availability_dict = {}
        for timestamp in timestamps:
            time_availability_dict[timestamp] = 'disabled'
            timestamp_datetime = datetime.strptime(timestamp, "%H:%M")
            if opening_time_1 <= timestamp_datetime <= closing_time_1:
                reservation_end_time = timestamp_datetime + timedelta(hours=restaurant.meal_duration)
                for possible_table in possible_tables:
                    reservations = Reservations.objects.filter(
                        Q(restaurant_id=restaurant.id) & Q(table_id=possible_table.id) & Q(reservation_date=query_date) & Q(confirmed=True))

                    before_timeslot_query = Q(arrival_time__lt=reservation_end_time) | Q(end_time__gt=timestamp)
                    after_timeslot_query = Q(arrival_time__gt=reservation_end_time)
                    within_reserved_timeslot = reservations.filter(before_timeslot_query)
                    below_lower_bound = reservations.filter(after_timeslot_query)
                    if within_reserved_timeslot and not below_lower_bound:
                        print('table reserved, check new table')
                    else:
                        time_availability_dict[timestamp] = 'enabled'
            if opening_time_2 <= timestamp_datetime <= closing_time_2:
                reservation_end_time = timestamp_datetime + timedelta(hours=restaurant.meal_duration)
                for possible_table in possible_tables:
                    reservations = Reservations.objects.filter(
                        Q(restaurant_id=restaurant.id) & Q(table_id=possible_table.id) & Q(
                            reservation_date=query_date) & Q(confirmed=True))

                    before_timeslot_query = Q(arrival_time__lt=reservation_end_time) | Q(end_time__gt=timestamp)
                    after_timeslot_query = Q(arrival_time__gt=reservation_end_time)
                    within_reserved_timeslot = reservations.filter(before_timeslot_query)
                    below_lower_bound = reservations.filter(after_timeslot_query)
                    if within_reserved_timeslot and not below_lower_bound:
                        print('table reserved, check new table')
                    else:
                        time_availability_dict[timestamp] = 'enabled'
        return time_availability_dict



