from django.db.models import Q
import datetime
from bookingsystem.models import UserRestaurantLink, Reservations, Tables, Restaurants


class reservationShower:
    def prepare_table(self, current_user):
        current_restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]
        try:
            dates = sorted(list(
                Reservations.objects.filter(restaurant_id=current_restaurant_id, confirmed=True).values_list(
                    "reservation_date", flat=True).distinct()))
            restaurant_opening_time = Restaurants.objects.filter(id=current_restaurant_id).values_list('opening_time', flat=True)[0]
            restaurant_closing_time = Restaurants.objects.filter(id=current_restaurant_id).values_list('closing_time', flat=True)[0]


            timeslots = []
            start_time = datetime.datetime.strptime(str(restaurant_opening_time), "%H:%M:%S")
            end_time = datetime.datetime.strptime(str(restaurant_closing_time), "%H:%M:%S")
            for i in range(96):  # Generate timestamps for every 15 minutes in a day (24 hours * 60 minutes / 15 minutes)
                while start_time <= end_time:
                    timeslots.append(start_time.strftime("%H:%M"))
                    start_time += datetime.timedelta(minutes=15)


            tables = Tables.objects.filter(restaurant_id=current_restaurant_id).order_by('table_nr')

            all_reservations_dict = {}
            for date in dates:
                date_dict = {}
                for table in tables:
                    reservation_dict = {}

                    #Find reservations for date and table, add to dict
                    query = Q(restaurant_id=current_restaurant_id) & Q(reservation_date=date) & Q(table=table)
                    table_reservations = Reservations.objects.filter(query)
                    for table_reservation in table_reservations:
                        reservation_dict['name'] = table_reservation.customer.full_name
                        reservation_dict['no_persons'] = table_reservation.number_of_persons
                        reservation_dict['telephone_nr'] = table_reservation.customer.telephone_nr
                        reservation_dict['arrival_time'] = str(table_reservation.arrival_time)
                        reservation_dict['end_time'] = str(table_reservation.end_time)

                    date_dict[table.table_nr] = reservation_dict
                all_reservations_dict[str(date)] = date_dict



            # reservations_dict = {'date1': {'table1': {'reservation1': {'name': 'name', 'no_persons': 'no_persons', 'phone_nr': 'phone_nr', 'begin_time': 'begin_time', 'end_time': 'end_time'}}}}
            context = {'dates': dates, 'action': './show_reservations/show_reservations.html',
                       'all_reservations_dict': all_reservations_dict, 'timeslots': timeslots}
        except Exception as e:  # No restaurant found for current user
            context = {'status': 'no_restaurant_known_for_user'}
        return context