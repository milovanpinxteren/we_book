from django.core.exceptions import ObjectDoesNotExist

from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import Courses, UserRestaurantLink, Dishes


class MenuUpdater():


    def update_menu(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True).first()

        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                parts = response.split('-')
                column_name = parts[0]
                column_value = request.POST[response]
                part_id = parts[1]
                if 'dish' in part_id:
                    row_id = part_id[7:]
                    DatabaseUpdater().update_model_instance(Dishes, restaurant_id, row_id, column_name, column_value)
                elif 'course' in part_id:
                    row_id = part_id[9:]
                    DatabaseUpdater().update_model_instance(Courses, restaurant_id, row_id, column_name, column_value)
        return