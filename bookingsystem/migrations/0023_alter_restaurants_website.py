# Generated by Django 4.2.4 on 2023-09-23 14:11

import bookingsystem.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0022_errors_alter_dishes_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurants',
            name='website',
            field=models.URLField(validators=[bookingsystem.models.https_url_validator]),
        ),
    ]
