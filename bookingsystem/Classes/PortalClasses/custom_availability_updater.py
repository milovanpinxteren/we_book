from django.utils.datastructures import MultiValueDictKeyError

from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import UserRestaurantLink, CustomRestaurantAvailability


class CustomAvailabilityUpdater():
    def add_availability(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                            flat=True).first()
        if request.method == 'POST':
            try:
                date = request.POST['date']
                try:
                    open = request.POST['open']
                except MultiValueDictKeyError:  # 'open' checkbox unchecked -> restaurant is closed
                    open = False
                if request.POST['start_time'] == "":
                    start_time = "00:00"
                else:
                    start_time = request.POST['start_time']
                if request.POST['end_time'] == "":
                    end_time = "23:59"
                else:
                    end_time = request.POST['end_time']
                CustomRestaurantAvailability.objects.create(date=date, open=open, start_time=start_time,
                                                            restaurant_id=restaurant_id,
                                                            end_time=end_time)
            except Exception as e:
                print('could not add availability', e)

    def update_availability(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                            flat=True).first()

        database_updater = DatabaseUpdater()
        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                parts = response.split('-')
                column_name = parts[0]
                column_value = request.POST[response]
                availability_id = parts[1][-1]
                database_updater.update_model_instance(CustomRestaurantAvailability, restaurant_id, availability_id,
                                                       column_name,
                                                       column_value)
