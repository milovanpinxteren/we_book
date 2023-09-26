from django.core.exceptions import ValidationError
from django.db import models
import os

def dish_photo_upload_path(instance, filename):
    restaurant_name = instance.restaurant.name
    course_name = instance.course.name
    # Sanitize the restaurant and course names to create valid directory names
    restaurant_name = restaurant_name.replace(" ", "_")
    course_name = course_name.replace(" ", "_")
    # Combine the names to create the upload path
    upload_path = os.path.join('dishphotos', restaurant_name, course_name)
    # Combine the upload path and filename
    return os.path.join(upload_path, filename)

################################################Back-end#############################################################

class PaymentFrequencies(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    amount_of_months = models.IntegerField(default=0)

class Subscriptions(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

class Errors(models.Model):
    message = models.CharField(max_length=1250, default='', blank=True)
    user_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


################################################Restaurants#############################################################
def https_url_validator(value):
    if not value.startswith('https://'):
        raise ValidationError('URL must start with https://')

class Restaurants(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    website = models.URLField(validators=[https_url_validator])
    email = models.CharField(max_length=250, default='')
    telephone_nr = models.CharField(max_length=250, default='', blank=True)
    address = models.CharField(max_length=250, default='')
    postal_code = models.CharField(max_length=25, default='')
    place = models.CharField(max_length=250, default='')
    country = models.CharField(max_length=250, default='')
    front_page_text = models.CharField(max_length=2500, default='')
    meal_duration = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    payment_per_booking = models.DecimalField(default=0.0, decimal_places=2, max_digits=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    open_monday = models.BooleanField(default=True)
    opening_time_monday = models.TimeField(default='12:00:00')
    closing_time_monday = models.TimeField(default='22:00:00')
    open_tuesday = models.BooleanField(default=True)
    opening_time_tuesday = models.TimeField(default='12:00:00')
    closing_time_tuesday = models.TimeField(default='22:00:00')
    open_wednesday = models.BooleanField(default=True)
    opening_time_wednesday = models.TimeField(default='12:00:00')
    closing_time_wednesday = models.TimeField(default='22:00:00')
    open_thursday = models.BooleanField(default=True)
    opening_time_thursday = models.TimeField(default='12:00:00')
    closing_time_thursday = models.TimeField(default='22:00:00')
    open_friday = models.BooleanField(default=True)
    opening_time_friday = models.TimeField(default='12:00:00')
    closing_time_friday = models.TimeField(default='22:00:00')
    open_saturday = models.BooleanField(default=True)
    opening_time_saturday = models.TimeField(default='12:00:00')
    closing_time_saturday = models.TimeField(default='22:00:00')
    open_sunday = models.BooleanField(default=True)
    opening_time_sunday = models.TimeField(default='12:00:00')
    closing_time_sunday = models.TimeField(default='22:00:00')
    payment_frequency = models.ForeignKey(PaymentFrequencies, on_delete=models.CASCADE, default=0)
    discount = models.FloatField(default=0, null=True)

class CustomRestaurantAvailability(models.Model): #overrides regular availability
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField(default='10:00', null=True)
    end_time = models.TimeField(default='23:00', null=True)
    open = models.BooleanField(default=True)


class Tables(models.Model):
    table_nr = models.IntegerField(default=0)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='', blank=True)
    min_pers = models.IntegerField(default=0)
    max_pers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Courses(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, default='', blank=True)
    course_order = models.IntegerField(default=0) #1=top of page, 2= below, etc

class Dishes(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, default='', blank=True)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    photo = models.ImageField(upload_to=dish_photo_upload_path, null=True)
    dish_order = models.IntegerField(default=0) #1=top of page, 2= below, etc

class RestaurantSubscriptionLink(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='')
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, default='')


class UserRestaurantLink(models.Model):
    user_id = models.IntegerField(default=0)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='')
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
    number_of_persons = models.IntegerField(default=0)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, default='', blank=True)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, default='', blank=True)
    reservation_date = models.DateField()
    arrival_time = models.TimeField()
    end_time = models.TimeField()
    comments = models.CharField(max_length=2500, default='', blank=True)
    confirmed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    created_by_restaurant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


################################################Finance############################################################

class Bills(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(default=0, max_digits=6, decimal_places=2)
