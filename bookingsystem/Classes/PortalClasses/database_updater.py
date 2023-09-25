from django.core.exceptions import ObjectDoesNotExist

from bookingsystem.models import Restaurants


class DatabaseUpdater():
    def update_model_instance(self, model_class, restaurant_id, instance_id, column_name, column_value):
        try:
            if model_class != Restaurants:
                instance = model_class.objects.get(restaurant_id=restaurant_id, id=instance_id)
            elif model_class == Restaurants:
                instance = model_class.objects.get(id=restaurant_id)
            if hasattr(instance, column_name):
                if column_name == 'price':
                    column_value = float(column_value.replace(',', '.'))
                setattr(instance, column_name, column_value)
                instance.save()
            else:
                print(f'Invalid column_name {column_name} for model {model_class.__name__}')
        except ObjectDoesNotExist:
            print(f'{model_class.__name__} with id {instance_id} does not exist')