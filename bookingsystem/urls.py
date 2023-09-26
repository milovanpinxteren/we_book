from django.urls import path

from . import views

app_name = 'bookingsystem'

urlpatterns = [
    path("", views.index, name="index"),
    path("make_reservation", views.make_reservation, name="make_reservation"),
    path("confirm_booking", views.confirm_booking, name="confirm_booking"),

    path("restaurant_portal", views.restaurant_portal, name="restaurant_portal"),
    path("make_reservation_in_portal", views.make_reservation_in_portal, name="make_reservation_in_portal"),
    path("drop_reservation", views.drop_reservation, name="drop_reservation"),
    path("delete_reservation", views.delete_reservation, name="delete_reservation"),
    path("rollback_deletion", views.rollback_deletion, name="rollback_deletion"),
    path("show_reservations", views.show_reservations, name="show_reservations"),
    path("calculate_reservation_table", views.calculate_reservation_table, name="calculate_reservation_table"),

    path("view_menu", views.view_menu, name="view_menu"),
    path("update_menu", views.update_menu, name="update_menu"),
    path("add_dish", views.add_dish, name="add_dish"),
    path("add_course", views.add_course, name="add_course"),
    path("delete_course/<int:course_id>/", views.delete_course, name="delete_course"),
    path("delete_dish/<int:dish_id>/", views.delete_dish, name="delete_dish"),

    path("view_restaurant_settings", views.view_restaurant_settings, name="view_restaurant_settings"),
    path("update_restaurant_info", views.update_restaurant_info, name="update_restaurant_info"),

    path("custom_restaurant_availability", views.custom_restaurant_availability, name="custom_restaurant_availability"),
    path("add_custom_restaurant_availability", views.add_custom_restaurant_availability, name="add_custom_restaurant_availability"),
    path("delete_availability/<int:availability_id>/", views.delete_availability, name="delete_availability"),
    path("update_custom_availability", views.update_custom_availability, name="update_custom_availability"),



    path("view_restaurant_tables", views.view_restaurant_tables, name="view_restaurant_tables"),
    path("add_table", views.add_table, name="add_table"),
    path("update_tables", views.update_tables, name="update_tables"),
    path("delete_table/<int:table_id>/", views.delete_table, name="delete_table"),

]
