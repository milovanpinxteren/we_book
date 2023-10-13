# Generated by Django 4.2.4 on 2023-08-24 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0010_remove_customrestaurantavailability_meal_duration_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRestaurantLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0)),
                ('restaurant', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.restaurants')),
            ],
        ),
    ]
