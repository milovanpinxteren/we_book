from datetime import date, datetime, timedelta

from bookingsystem.Classes.PortalClasses.reservation_shower import reservationShower
from bookingsystem.models import UserRestaurantLink, Tables, Restaurants, Reservations, Customers


class ReservationMaker():
    def make_reservation(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[
            0]
        table_id = Tables.objects.filter(restaurant_id=restaurant_id, table_nr=request.POST['table_nr'])[0].id
        reservation_duration = Restaurants.objects.filter(id=restaurant_id).values_list('meal_duration', flat=True)[0]
        input_time = datetime.strptime(request.POST['reservation_time'], '%H:%M')
        result_time = input_time + timedelta(hours=reservation_duration)
        end_time = result_time.strftime('%H:%M')
        customer = Customers.objects.create(full_name=request.POST['customer_name'], email=request.POST['customer_email'],
                                 telephone_nr=request.POST['customer_telephone_nr'], created_at=datetime.now(),
                                    updated_at=datetime.now())
        Reservations.objects.create(reservation_date=request.POST['reservation_date'],
                                    arrival_time=request.POST['reservation_time'],
                                    end_time=end_time, comments='', created_at=datetime.now(),
                                    updated_at=datetime.now(),
                                    customer=customer, restaurant_id=restaurant_id, table_id=table_id, confirmed=True,
                                    number_of_persons=request.POST['number_of_persons'], cancelled=False,
                                    created_by_restaurant=True)


        self.show_reservations(current_user)


    def show_reservations(self, current_user):
        reservation_shower = reservationShower()
        context = reservation_shower.prepare_table(current_user)
        return context
