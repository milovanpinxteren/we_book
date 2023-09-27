import calendar
import datetime
from datetime import date, timedelta

from bookingsystem.models import Restaurants, CustomRestaurantAvailability


class AvailabilityChecker():
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


