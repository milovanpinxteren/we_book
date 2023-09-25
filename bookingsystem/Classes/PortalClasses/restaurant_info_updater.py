from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import UserRestaurantLink, Restaurants


class RestaurantInfoUpdater():
    def update_restaurant_info(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                            flat=True).first()
        day_array = ['open_monday', 'open_tuesday', 'open_wednesday', 'open_thursday', 'open_friday', 'open_saturday',
                     'open_sunday']
        database_updater = DatabaseUpdater()
        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                column_name = response
                column_value = request.POST[response]
                database_updater.update_model_instance(Restaurants, restaurant_id, restaurant_id, column_name,
                                                       column_value)
                # If value does not appear in request.POST, the value is not checked -> restaurant closed
                if column_name in day_array: day_array.remove(column_name)

        for closed_day in day_array:
            database_updater.update_model_instance(Restaurants, restaurant_id, restaurant_id, closed_day, False)
