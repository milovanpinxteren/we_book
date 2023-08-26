from django.urls import path

from . import views

app_name = 'bookingsystem'

urlpatterns = [
    path("", views.index, name="index"),
    path("make_reservation", views.make_reservation),
    path("confirm_booking", views.confirm_booking),
    path("see_reservations", views.see_reservations),
    path("drop_reservation", views.drop_reservation, name="drop_reservation"),
    path("delete_reservation", views.delete_reservation, name="delete_reservation")
]
