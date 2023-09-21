from django.test import TestCase, Client
from django.urls import reverse

from django.contrib.auth.models import User
from bookingsystem.models import UserRestaurantLink, Restaurants, Tables, Reservations, PaymentFrequencies
from datetime import datetime, timedelta

class TestViews(TestCase):
    def setUp(self):
        # Create an existing user with id=3
        self.existing_user = User.objects.create_user(
            id=3,  # Set the user's ID explicitly to 3
            username='existinguser',
            password='existingpassword'
        )

        self.payment_frequencies = PaymentFrequencies.objects.create(
            id=0,
            name='Free Trial',
            amount_of_months=3
        )
        # Create a test restaurant
        self.restaurant = Restaurants.objects.create(
            name='Test Restaurant',
            meal_duration=2,  # Replace with the desired meal duration in hours,
        )

        # Create a test table for the restaurant
        self.table = Tables.objects.create(
            restaurant=self.restaurant,
            table_nr='101'
        )

        # Create a test user-restaurant link
        self.user_restaurant_link = UserRestaurantLink.objects.create(
            user_id=3,
            restaurant=self.restaurant
        )


    def test_make_reservation_in_portal(self):
        client = Client()
        client.login(username='existinguser', password='existingpassword')

        data = {
            'number_of_persons': 3,
            'reservation_date': '2023-09-30',
            'reservation_time': '17:11',
            'customer_name': 'Milo van Pinxteren',
            'table_nr': '111',
            'customer_email': 'test@gmail.com',
            'customer_telephone_nr': '06123456789',
            # Include any form data that the view expects
        }


        response = client.post(reverse('bookingsystem:make_reservation_in_portal'), data)
        self.assertEqual(response.status_code, 200)  # Adjust the status code as needed
