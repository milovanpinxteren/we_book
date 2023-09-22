from django.core.exceptions import ObjectDoesNotExist

from bookingsystem.models import Courses, UserRestaurantLink, Dishes


class MenuUpdater():
    def update_model_instance(self, model_class, restaurant_id, instance_id, column_name, column_value):
        try:
            instance = model_class.objects.get(restaurant_id=restaurant_id, id=instance_id)
            if hasattr(instance, column_name):
                if column_name == 'price':
                    column_value = float(column_value.replace(',', '.'))
                setattr(instance, column_name, column_value)
                instance.save()
            else:
                print(f'Invalid column_name {column_name} for model {model_class.__name__}')
        except ObjectDoesNotExist:
            print(f'{model_class.__name__} with id {instance_id} does not exist')

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
                    self.update_model_instance(Dishes, restaurant_id, row_id, column_name, column_value)
                elif 'course' in part_id:
                    row_id = part_id[9:]
                    self.update_model_instance(Courses, restaurant_id, row_id, column_name, column_value)


        #
        # courses = Courses.objects.filter(restaurant_id=restaurant_id).order_by('course_order')
        # course_dishes = {}
        # for course in courses:
        #     ordered_dishes = course.dishes_set.order_by('dish_order')
        #     course_dishes[course] = ordered_dishes
        # context = {'action': './view_menu/view_menu.html', 'course_dishes': course_dishes}
        # return context

        return