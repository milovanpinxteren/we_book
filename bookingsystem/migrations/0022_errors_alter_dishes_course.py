# Generated by Django 4.2.4 on 2023-09-23 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookingsystem', '0021_alter_dishes_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='Errors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, default='', max_length=1250)),
                ('user_id', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='dishes',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookingsystem.courses'),
        ),
    ]
