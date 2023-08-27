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
    path("show_reservations", views.show_reservations, name="show_reservations"),
    path("show_dashboard", views.show_dashboard, name="show_dashboard"),

]
