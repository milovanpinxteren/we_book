from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import UserRestaurantLink, Tables
from datetime import datetime

class RestaurantTablesUpdater():
    def update_tables(self, request):
        global table_id
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                            flat=True).first()
        database_updater = DatabaseUpdater()
        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                parts = response.split('-')
                column_name = parts[0]
                column_value = request.POST[response]
                table_id = parts[1][8:]
                database_updater.update_model_instance(Tables, restaurant_id, table_id, column_name,
                                                       column_value)
        database_updater.update_model_instance(Tables, restaurant_id, table_id, 'updated_at',
                                               datetime.now())