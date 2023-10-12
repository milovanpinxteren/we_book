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
            dishes = ordered_dishes.values_list('id', 'name', 'price', 'dish_order', 'course_id')
            result_as_dict = [
                {
                    'id': item[0],
                    'name': item[1],
                    'price': float(item[2]),
                    'dish_order': item[3],
                    'course_id': item[4]
                }
                for item in dishes
            ]
            course_dishes[course] = result_as_dict


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
        ).order_by('course__course_order', 'dish__dish_order')
        total_amount = orders.aggregate(total_amount=Sum('amount'))['total_amount']

        orders_list = list(orders)
        context = {'orders': orders_list, 'total_amount': total_amount}
        return context


