# Generated by Django 4.2.4 on 2023-08-18 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tables',
            old_name='restaurant_id',
            new_name='restaurant',
        ),
    ]
