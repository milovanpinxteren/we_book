from django.db.models import Sum

from bookingsystem.models import UserRestaurantLink, Tables, Courses, Orders


class TableManagementShower():
    def prepare_table_management(self, request):
        current_user = request.user.id
        restaurant = UserRestaurantLink.objects.get(user_id=current_user).restaurant
        tables = Tables.objects.filter(restaurant=restaurant).order_by('table_nr')

        courses = Courses.objects.filter(restaurant=restaurant).order_by('course_order')
        course_dishes = {}
        for course in courses:
            ordered_dishes = course.dishes_set.order_by('dish_order')
            course_dishes[course] = ordered_dishes


        context = {'action': './table_management.html', 'tables': tables, 'course_dishes': course_dishes}
        return context

    def get_table_bill(self, request, table_id):
        current_user = request.user.id
        restaurant = UserRestaurantLink.objects.get(user_id=current_user).restaurant
        orders = Orders.objects.filter(table_id=table_id, restaurant=restaurant).select_related('dish').values(
            'table__table_nr',
            'course__name',
            'dish__name',
            'quantity',
            'amount'
        )
        total_amount = orders.aggregate(total_amount=Sum('amount'))['total_amount']

        orders_list = list(orders)
        context = {'orders': orders_list, 'total_amount': total_amount}
        return context
