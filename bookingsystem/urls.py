from django.urls import path

from . import views

app_name = 'bookingsystem'

urlpatterns = [
    path("", views.index, name="index"),
    path("make_reservation", views.make_reservation, name="make_reservation"),
    path("confirm_booking", views.confirm_booking, name="confirm_booking"),
    path("restaurant_portal", views.restaurant_portal, name="restaurant_portal"),
    path("drop_reservation", views.drop_reservation, name="drop_reservation"),
    path("delete_reservation", views.delete_reservation, name="delete_reservation"),
    path("rollback_deletion", views.rollback_deletion, name="rollback_deletion"),
    path("show_reservations", views.show_reservations, name="show_reservations"),
    path("show_dashboard", views.show_dashboard, name="show_dashboard"),
    path("make_reservation_in_portal", views.make_reservation_in_portal, name="make_reservation_in_portal"),

]
