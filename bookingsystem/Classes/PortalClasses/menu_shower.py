from bookingsystem.models import UserRestaurantLink, Courses


class MenuShower():
        # course_dish_set = Courses.objects.select_related('restaurant').prefetch_related(
        #     'restaurant__userrestaurantlink_set').filter(
        #     restaurant__userrestaurantlink__user_id=current_user).prefetch_related(
        #     'restaurant__courses_set__dishes_set').values_list('name', 'dishes__name').order_by('course_order', 'dishes__dish_order')

    def prepare_menu(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True)[
            0]
        courses = Courses.objects.filter(restaurant_id=restaurant_id).order_by('course_order')
        course_dishes = {}
        for course in courses:
            ordered_dishes = course.dishes_set.order_by('dish_order')
            course_dishes[course] = ordered_dishes
        context = {'action': './view_menu/view_menu.html', 'course_dishes': course_dishes}
        return context