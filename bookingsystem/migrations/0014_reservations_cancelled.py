# Generated by Django 4.2.4 on 2023-08-29 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0013_restaurants_payment_per_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservations',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
    ]