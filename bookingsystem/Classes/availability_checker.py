import datetime
import calendar

from django.db.models import Q

from bookingsystem.models import Restaurants, CustomRestaurantAvailability, Tables, Reservations


class AvailabilityChecker():
    def get_availability(self, restaurant_id):
        availability_dict = {}
        availability_list, closed_list = self.get_availability_of_day(restaurant_id)
        opening_time = Restaurants.objects.filter(id=restaurant_id).values_list("opening_time", flat=True)[0]
        closing_time = Restaurants.objects.filter(id=restaurant_id).values_list("closing_time", flat=True)[0]
        for day in availability_list:
            day_dict = self.get_available_timeslots(restaurant_id, day, opening_time, closing_time)
            availability_dict[str(day)] = day_dict
        return availability_dict, closed_list

    def get_availability_of_day(self, restaurant_id): # get available days for the next year
    #For normal restaurant availability
        restaurant = Restaurants.objects.filter(id=restaurant_id)
        today = datetime.date.today()
        availability_list = []
        closed_list = []
        for _ in range(366):  # Include today, so range goes from 0 to 365
            today += datetime.timedelta(days=1)
            day_name = calendar.day_name[today.weekday()].lower()
            column_name = 'open_' + day_name
            restaurant_open = restaurant.values_list(column_name, flat=True)[0]
            if restaurant_open:
                availability_list.append(today)
            else:
                closed_list.append(str(today))

    #For custom availability
        custom_availabilities = CustomRestaurantAvailability.objects.filter(restaurant_id=restaurant_id)
        for custom_availability in custom_availabilities:
            try:
                if custom_availability.open:
                    availability_list.append(custom_availability.date)
                    closed_list.remove(str(custom_availability.date))
                elif not custom_availability.open:
                    availability_list.remove(custom_availability.date)
                    closed_list.append(str(custom_availability.date))
            except Exception as e:
                continue

        availability_list = sorted(availability_list)
        return availability_list, closed_list

    def get_available_timeslots(self, restaurant_id, day, opening_time, closing_time):
        day_dict = {}
        times_dict = {}
        timestamps = []
        start_time = datetime.datetime.strptime("00:00", "%H:%M")
        for i in range(96):  # Generate timestamps for every 15 minutes in a day (24 hours * 60 minutes / 15 minutes)
            timestamps.append(start_time.strftime("%H:%M"))
            start_time += datetime.timedelta(minutes=15)
            if opening_time <= start_time.time() <= closing_time:
                times_dict[str(start_time.time())[:5]] = 'enabled'
            else:
                times_dict[str(start_time.time())[:5]] = 'disabled'

        # day_dict[day] = times_dict
        return times_dict