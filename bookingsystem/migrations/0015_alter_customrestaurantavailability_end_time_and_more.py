# Generated by Django 4.2.4 on 2023-09-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0014_reservations_cancelled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customrestaurantavailability',
            name='end_time',
            field=models.TimeField(default='23:59', null=True),
        ),
        migrations.AlterField(
            model_name='customrestaurantavailability',
            name='start_time',
            field=models.TimeField(default='10:00', null=True),
        ),
    ]
