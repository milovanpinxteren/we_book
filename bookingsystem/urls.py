from django.urls import path

from .views import main_views, portal_views

app_name = 'bookingsystem'

urlpatterns = [
    path("", main_views.index, name="index"),
    path("check_available_dates", main_views.check_available_dates, name="check_available_dates"),
    path("check_availability", main_views.check_availability, name="check_availability"),

    path("make_reservation", main_views.make_reservation, name="make_reservation"),
    path("confirm_booking", main_views.confirm_booking, name="confirm_booking"),

    path("drop_reservation", main_views.drop_reservation, name="drop_reservation"),
    path("delete_reservation", main_views.delete_reservation, name="delete_reservation"),

    path("restaurant_portal", portal_views.restaurant_portal, name="restaurant_portal"),
    path("make_reservation_in_portal", portal_views.make_reservation_in_portal, name="make_reservation_in_portal"),

    path("rollback_deletion", portal_views.rollback_deletion, name="rollback_deletion"),
    path("show_reservations", portal_views.show_reservations, name="show_reservations"),
    path("calculate_reservation_table", portal_views.calculate_reservation_table, name="calculate_reservation_table"),

    path("view_menu", portal_views.view_menu, name="view_menu"),
    path("update_menu", portal_views.update_menu, name="update_menu"),
    path("add_dish", portal_views.add_dish, name="add_dish"),
    path("add_course", portal_views.add_course, name="add_course"),
    path("delete_course/<int:course_id>/", portal_views.delete_course, name="delete_course"),
    path("delete_dish/<int:dish_id>/", portal_views.delete_dish, name="delete_dish"),

    path("view_restaurant_settings", portal_views.view_restaurant_settings, name="view_restaurant_settings"),
    path("update_restaurant_info", portal_views.update_restaurant_info, name="update_restaurant_info"),

    path("custom_restaurant_availability", portal_views.custom_restaurant_availability, name="custom_restaurant_availability"),
    path("add_custom_restaurant_availability", portal_views.add_custom_restaurant_availability,
         name="add_custom_restaurant_availability"),
    path("delete_availability/<int:availability_id>/", portal_views.delete_availability, name="delete_availability"),
    path("update_custom_availability", portal_views.update_custom_availability, name="update_custom_availability"),

    path("view_restaurant_tables", portal_views.view_restaurant_tables, name="view_restaurant_tables"),
    path("add_table", portal_views.add_table, name="add_table"),
    path("update_tables", portal_views.update_tables, name="update_tables"),
    path("delete_table/<int:table_id>/", portal_views.delete_table, name="delete_table"),

    path("get_table_bill/<int:table_id>/", portal_views.get_table_bill, name="get_table_bill"),
    path("add_dish_to_table/<int:dish_id>/<int:table_id>/", portal_views.add_dish_to_table, name="add_dish_to_table"),
    path("remove_dish_from_table/<int:order_id>/<int:table_id>/<int:current_quantity>", portal_views.remove_dish_from_table, name="remove_dish_from_table"),
    path("clear_table/<int:table_id>", portal_views.clear_table, name="clear_table"),

    path('generated_menu/<str:template_name>', portal_views.serve_generated_menu, name='serve_generated_menu'),

]
