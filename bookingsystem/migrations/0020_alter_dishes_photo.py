# Generated by Django 4.2.4 on 2023-09-22 10:29

import bookingsystem.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0019_remove_reservations_paid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dishes',
            name='photo',
            field=models.ImageField(null=True, upload_to=bookingsystem.models.dish_photo_upload_path),
        ),
    ]