from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import UserRestaurantLink, Restaurants


class RestaurantInfoUpdater():
    def update_restaurant_info(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                            flat=True).first()
        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                column_name = response
                column_value = request.POST[response]
                DatabaseUpdater().update_model_instance(Restaurants, restaurant_id, restaurant_id, column_name, column_value)
