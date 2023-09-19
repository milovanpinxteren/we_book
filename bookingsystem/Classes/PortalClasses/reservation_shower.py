import datetime

from django.db.models import Q

from bookingsystem.models import UserRestaurantLink, Reservations, Tables, Restaurants


class reservationShower:
    def prepare_table(self, current_user):
        current_restaurant_id = \
            UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
        try:
            dates = sorted(list(
                Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True).values_list(
                    "reservation_date", flat=True).distinct()))
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
                            table_booked = Reservations.objects.filter(lower_bound_query & upper_bound_query)
                            if table_booked:
                                availability[index] = 'booked', table_booked[0].customer.full_name, \
                                                      table_booked[0].customer.email, \
                                                      table_booked[0].customer.telephone_nr, \
                                                      table_booked[0].arrival_time, \
                                                      table_booked[0].reservation_date, \
                                                      table_booked[0].number_of_persons, \
                                                      table_booked[0].table.table_nr
                            else:
                                availability[index] = ''

                    reservation_matrix.append(availability)
                all_reservations_dict[str(date)] = reservation_matrix

            # reservation_matrix = [
            #     # [101, 102, 103, 104, 105],
            #     {1: '12:00', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '12:15', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '12:30', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '12:45', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '13:00', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '13:15', 2: 'reservation1', 3: 'none', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '13:30', 2: 'none', 3: 'reservation2', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '13:45', 2: 'none', 3: 'reservation2', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '14:00', 2: 'none', 3: 'reservation2', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '14:15', 2: 'none', 3: 'reservation2', 4: 'none', 5: 'none', 6: 'none'},
            #     {1: '14:30', 2: 'none', 3: 'reservation2', 4: 'none', 5: 'none', 6: 'none'},
            # ]

            context = {'dates': dates, 'action': './show_reservations/show_reservations.html',
                       'all_reservations_dict': all_reservations_dict,
                       'tables': table_nrs}
        except Exception as e:  # No restaurant found for current user
            context = {'status': 'no_restaurant_known_for_user'}
        return context

    def get_timeslots(self, current_restaurant_id):
        restaurant_opening_time = \
            Restaurants.objects.filter(id=current_restaurant_id).values_list('opening_time', flat=True)[0]
        restaurant_closing_time = \
            Restaurants.objects.filter(id=current_restaurant_id).values_list('closing_time', flat=True)[0]

        # Generate time slots based on restaurant opening hours (the y-axis of reservation table)
        timeslots = []
        start_time = datetime.datetime.strptime(str(restaurant_opening_time), "%H:%M:%S")
        end_time = datetime.datetime.strptime(str(restaurant_closing_time), "%H:%M:%S")
        for i in range(
                96):  # Generate timestamps for every 15 minutes in a day (24 hours * 60 minutes / 15 minutes)
            while start_time <= end_time:
                timeslots.append(start_time.strftime("%H:%M"))
                start_time += datetime.timedelta(minutes=15)

        return timeslots
