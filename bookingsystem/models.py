from django.db import models


################################################Restaurants#############################################################

class Restaurants(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    website = models.URLField()
    email = models.CharField(max_length=250, default='', blank=True)
    telephone_nr = models.CharField(max_length=250, default='', blank=True)
    user_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tables(models.Model):
    table_nr = models.IntegerField(default=0)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='', blank=True)
    min_pers = models.IntegerField(default=0)
    max_pers = models.IntegerField(default=0)
    duration_hours = models.IntegerField(default=0)
    min_time = models.TimeField() #Cannot reserve table on day before this time
    max_time = models.TimeField() #Cannot reserve table on day after this time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

################################################Customers###############################################################

class Customers(models.Model):
    full_name = models.CharField(max_length=250, default='', blank=True)
    email = models.CharField(max_length=250, default='', blank=True)
    telephone_nr = models.CharField(max_length=250, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

################################################Reservations############################################################

class Reservations(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, default='', blank=True)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='', blank=True)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, default='', blank=True)
    reservation_date = models.DateTimeField()
    arrival_time = models.TimeField()
    end_time = models.TimeField()
    comments = models.CharField(max_length=2500, default='', blank=True)
    paid = models.BooleanField()
    paid_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)