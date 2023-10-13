# Generated by Django 4.2.4 on 2023-08-24 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0009_remove_tables_duration_hours_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customrestaurantavailability',
            name='meal_duration',
        ),
        migrations.AddField(
            model_name='restaurants',
            name='meal_duration',
            field=models.IntegerField(default=0),
        ),
    ]