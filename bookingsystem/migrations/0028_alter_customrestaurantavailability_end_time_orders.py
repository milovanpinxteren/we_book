# Generated by Django 4.2.4 on 2023-10-12 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0027_alter_restaurants_front_page_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customrestaurantavailability',
            name='end_time',
            field=models.TimeField(default='23:00', null=True),
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('course', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.courses')),
                ('dish', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.dishes')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.restaurants')),
                ('table', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.tables')),
            ],
        ),
    ]
