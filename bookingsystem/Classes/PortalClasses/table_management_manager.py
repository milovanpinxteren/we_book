from bookingsystem.models import UserRestaurantLink, Dishes, Orders, Tables


class TableManagementManager():
    def add_dish(self, request, dish_id, table_id):
        restaurant_id = \
        UserRestaurantLink.objects.filter(user_id=request.user.id).values_list('restaurant_id', flat=True)[0]
        print(request)
        dish = Dishes.objects.get(pk=dish_id)
        course = dish.course
        table = Tables.objects.get(pk=table_id)
        try:
            order = Orders.objects.get(course=course, dish_id=dish_id, restaurant_id=restaurant_id, table=table)
            original_quantity = order.quantity
            original_amount = order.amount
            new_quantity = original_quantity + 1
            new_amount = original_amount + dish.price
            order.delete()
            Orders.objects.create(course=course, dish_id=dish_id, restaurant_id=restaurant_id, table=table,
                                  quantity=new_quantity, amount=new_amount)
        except Orders.DoesNotExist:
            Orders.objects.create(course=course, dish_id=dish_id, restaurant_id=restaurant_id, table=table,
                                  quantity=1, amount=dish.price)

        # Orders.objects.create(course=course, dish_id=dish_id, restaurant_id=restaurant_id)

        return {'table_nr': table.table_nr}
