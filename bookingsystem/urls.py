from django.urls import path

from . import views

app_name = 'bookingsystem'

urlpatterns = [
    path("", views.index, name="index"),
    path("make_reservation", views.make_reservation),
    path("confirm_booking", views.confirm_booking),
    path("see_reservations", views.see_reservations)
]
