import datetime

from django.db.models import Q

from bookingsystem.models import UserRestaurantLink, Reservations, Tables, Restaurants


class reservationShower:
    # def prepare_table(self, current_user):
    #     try:
    #         # Fetch restaurant and user info in a single query
    #         user_link = UserRestaurantLink.objects.select_related('restaurant').get(user_id=current_user)
    #         current_restaurant = user_link.restaurant
    #         current_restaurant_id = current_restaurant.id
    #
    #         # Fetch all reservations for the restaurant in a single query
    #         reservations = Reservations.objects.filter(
    #             restaurant_id=current_restaurant_id,
    #             confirmed=True,
    #             cancelled=False
    #         ).select_related('customer', 'table')
    #
    #         # Fetch tables for the restaurant in a single query
    #         tables = Tables.objects.filter(restaurant=current_restaurant).order_by('table_nr')
    #
    #         # Generate a set of all existing table numbers
    #         table_nrs_set = {table.table_nr for table in tables}
    #
    #         # Get unique reservation dates
    #         dates = reservations.values_list('reservation_date', flat=True).distinct().order_by('reservation_date')
    #
    #         # Get a list of all available timeslots
    #         timeslots = self.get_timeslots(current_restaurant)
    #
    #         # Create a dictionary to store all reservations
    #         all_reservations_dict = {}
    #
    #         for date in dates:
    #             # Create an empty reservation matrix
    #             reservation_matrix = []
    #
    #             for timeslot in timeslots:
    #                 availability = {}
    #                 availability[1] = str(timeslot)
    #
    #                 for table_nr in table_nrs_set:
    #                     lower_bound_query = Q(
    #                         restaurant_id=current_restaurant_id,
    #                         table__table_nr=table_nr,
    #                         reservation_date=date,
    #                         arrival_time__lte=timeslot
    #                     )
    #                     upper_bound_query = Q(
    #                         restaurant_id=current_restaurant_id,
    #                         table__table_nr=table_nr,
    #                         reservation_date=date,
    #                         end_time__gte=timeslot
    #                     )
    #
    #                     # Filter reservations using both lower and upper bounds
    #                     table_booked = reservations.filter(
    #                         lower_bound_query & upper_bound_query
    #                     )
    #
    #                     if table_booked:
    #                         reservation = table_booked[0]
    #                         availability[table_nr] = (
    #                             'booked',
    #                             reservation.customer.full_name,
    #                             reservation.customer.email,
    #                             reservation.customer.telephone_nr,
    #                             reservation.arrival_time,
    #                             reservation.reservation_date,
    #                             reservation.number_of_persons,
    #                             reservation.table.table_nr,
    #                             reservation.id
    #                         )
    #                     else:
    #                         availability[table_nr] = ''
    #
    #                 reservation_matrix.append(availability)
    #
    #             all_reservations_dict[str(date)] = reservation_matrix
    #
    #         context = {
    #             'dates': dates,
    #             'action': './show_reservations/show_reservations.html',
    #             'all_reservations_dict': all_reservations_dict,
    #             'tables': ['timeslot'] + sorted(table_nrs_set)
    #         }
    #     except UserRestaurantLink.DoesNotExist:
    #         context = {'status': 'no_restaurant_known_for_user'}
    #
    #     return context
    #
    # def get_timeslots(self, current_restaurant):
    #     # start_time = current_restaurant.opening_time
    #     # end_time = current_restaurant.closing_time
    #     start_time = datetime.datetime.strptime(str(current_restaurant.opening_time), "%H:%M:%S")
    #     end_time = datetime.datetime.strptime(str(current_restaurant.closing_time), "%H:%M:%S")
    #     timeslots = []
    #
    #     while start_time <= end_time:
    #         timeslots.append(start_time.strftime("%H:%M"))
    #         start_time += datetime.timedelta(minutes=15)
    #
    #     return timeslots









    def prepare_table(self, current_user):
        current_restaurant_id = \
            UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
        try:
            dates = sorted(list(
                Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True, cancelled=False).values_list(
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
