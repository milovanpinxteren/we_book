from django.contrib import admin

# Register your models here.
from bookingsystem.models import Restaurants, Tables, Customers, Reservations


@admin.register(Restaurants)
class RestaurantsAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'email', 'telephone_nr']

    def restaurant(self, obj):
        return obj.restaurant.name

@admin.register(Tables)
class TablesAdmin(admin.ModelAdmin):
    list_display = ['table_nr', 'min_pers', 'max_pers', 'duration_hours', 'min_time', 'max_time']

@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'telephone_nr', 'created_at']

@admin.register(Reservations)
class ReservationsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'restaurant',  'table', 'reservation_date', 'arrival_time', 'comments']