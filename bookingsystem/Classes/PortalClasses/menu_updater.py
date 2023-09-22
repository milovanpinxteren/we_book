from bookingsystem.models import Courses, UserRestaurantLink, Dishes


class MenuUpdater():
    def update_menu(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[0]

        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                parts = response.split('-')
                column_name = parts[0]
                column_value = request.POST[response]
                if column_name == 'price':
                    column_value = float(column_value.replace(',', '.'))
                part_id = parts[1]
                id = part_id[-1]
                if 'dish' in part_id:
                    query_result = Dishes.objects.filter(restaurant_id=restaurant_id, id=id,**{column_name: column_value})
                    if not query_result.exists():
                        dish = Dishes.objects.get(restaurant_id=restaurant_id, id=id)
                        if hasattr(dish, column_name): # Update the attribute and save the dish object
                            setattr(dish, column_name, column_value)
                            dish.save()
                        else:  # Handle the case where column_name is not a valid attribute
                            print('Invalid column_name:', column_name)
                elif 'course' in part_id:
                    query_result = Courses.objects.filter(restaurant_id=restaurant_id, id=id, **{column_name: column_value})
                    if not query_result.exists():
                        course = Courses.objects.get(restaurant_id=restaurant_id, id=id)
                        if hasattr(course, column_name): # Update the attribute and save the dish object
                            setattr(course, column_name, column_value)
                            course.save()
                        else:  # Handle the case where column_name is not a valid attribute
                            print('Invalid column_name:', column_name)


        courses = Courses.objects.filter(restaurant_id=restaurant_id).order_by('course_order')
        course_dishes = {}
        for course in courses:
            ordered_dishes = course.dishes_set.order_by('dish_order')
            course_dishes[course] = ordered_dishes
        context = {'action': './view_menu/view_menu.html', 'course_dishes': course_dishes}
        return context