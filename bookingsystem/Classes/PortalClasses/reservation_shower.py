import datetime

from django.db.models import Q

from bookingsystem.models import UserRestaurantLink, Reservations, Tables, Restaurants


class reservationShower:
    def prepare_table(self, current_user):
        current_restaurant_id = \
            UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
        try:
            dates = sorted(list(
                Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True, cancelled=False).values_list(
                    "reservation_date", flat=True).distinct()))

            today = datetime.date.today()

            yesterday = today - datetime.timedelta(days=1)
            dates = [date for date in dates if date > yesterday]

            timeslots = self.get_timeslots(current_restaurant_id)

            # Find table numbers of Restaurant (the x-axis of the reservation table)
            tables = Tables.objects.filter(restaurant_id=current_restaurant_id).order_by('table_nr')
            table_nrs = [table.table_nr for table in tables]
            table_nrs.insert(0, 'timeslot')

            all_reservations_dict = {}
            for date in dates:
                # Fill Reservation Matrix
                reservation_matrix = []
                for timeslot in timeslots:
                    availability = {}
                    # availability[1] = str(timeslot)
                    for index, table_nr in enumerate(table_nrs, start=1):
                        # print(index, table_nr)
                        if index == 1:
                            availability[index] = str(timeslot)
                        else:
                            # table_id = Tables.table_nr
                            lower_bound_query = Q(restaurant_id=current_restaurant_id) & Q(
                                table__table_nr=table_nr) & Q(
                                reservation_date=date) & Q(arrival_time__lte=timeslot)
                            upper_bound_query = Q(restaurant_id=current_restaurant_id) & Q(
                                table__table_nr=table_nr) & Q(
                                reservation_date=date) & Q(end_time__gte=timeslot)
                            table_booked = Reservations.objects.filter(lower_bound_query & upper_bound_query & Q(confirmed=True) & Q(cancelled=False))
                            if table_booked:
                                availability[index] = 'booked', table_booked[0].customer.full_name, \
                                                      table_booked[0].customer.email, \
                                                      table_booked[0].customer.telephone_nr, \
                                                      table_booked[0].arrival_time, \
                                                      table_booked[0].reservation_date, \
                                                      table_booked[0].number_of_persons, \
                                                      table_booked[0].table.table_nr, \
                                                      table_booked[0].id
                            else:
                                availability[index] = ''

                    reservation_matrix.append(availability)
                all_reservations_dict[str(date)] = reservation_matrix


            context = {'dates': dates, 'action': './show_reservations/show_reservations.html',
                       'all_reservations_dict': all_reservations_dict,
                       'tables': table_nrs}
        except Exception as e:  # No restaurant found for current user
            print(e)
            context = {'status': 'no_restaurant_known_for_user'}
        return context

    def get_timeslots(self, current_restaurant_id):
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        earliest_opening_time = ''
        lastest_closing_time = ''
        restaurant = Restaurants.objects.get(id=current_restaurant_id)
        for day in days_of_week:
            # Construct the field names for opening and closing times for the current day
            opening_time_field = f'opening_time_{day}'
            closing_time_field = f'closing_time_{day}'
            opening_time = getattr(restaurant, opening_time_field)
            closing_time = getattr(restaurant, closing_time_field)
            if earliest_opening_time != '':
                if opening_time < earliest_opening_time:
                    earliest_opening_time = opening_time
            elif earliest_opening_time == '':
                earliest_opening_time = opening_time

            if lastest_closing_time != '':
                if closing_time > lastest_closing_time:
                    lastest_closing_time = closing_time
            elif lastest_closing_time == '':
                lastest_closing_time = closing_time



        start_time = datetime.datetime.strptime(str(earliest_opening_time), "%H:%M:%S")
        end_time = datetime.datetime.strptime(str(lastest_closing_time), "%H:%M:%S")
        timeslots = []
        for i in range(
                96):  # Generate timestamps for every 15 minutes in a day (24 hours * 60 minutes / 15 minutes)
            while start_time <= end_time:
                timeslots.append(start_time.strftime("%H:%M"))
                start_time += datetime.timedelta(minutes=15)

        return timeslots
