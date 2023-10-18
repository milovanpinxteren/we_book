# your_app/management/commands/my_custom_command.py
from django.core.management.base import BaseCommand
from bookingsystem.Classes.PortalClasses.menu_updater import MenuUpdater
from bookingsystem.models import Restaurants
from django.conf import settings





class GenerateMenus(BaseCommand):

    help = 'Generate menus post-deployment task for each restaurant'

    def handle(self, *args, **options):
        settings.configure()
        restaurants = Restaurants.objects.all()  # Query all restaurants
        for restaurant in restaurants:
            # Your task logic here for each restaurant
            self.stdout.write(f'Processing restaurant: {restaurant.name}')
            # Perform your actions here for each restaurant
            menu_updater = MenuUpdater()
            menu_updater.generate_menu_html(restaurant.id)


