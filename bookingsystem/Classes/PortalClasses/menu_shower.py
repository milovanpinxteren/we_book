from bookingsystem.models import UserRestaurantLink, Courses


class MenuShower():
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