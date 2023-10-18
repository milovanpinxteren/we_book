from django.core.management.base import BaseCommand
from bookingsystem.Classes.PortalClasses.menu_updater import MenuUpdater


class GenerateMenus(BaseCommand):
    help = 'Generate menus post-deployment task for each restaurant'

    def handle(self, *args, **options):
        from bookingsystem.models import Restaurants

        restaurants = Restaurants.objects.all()  # Query all restaurants
        for restaurant in restaurants:
            # Your task logic here for each restaurant
            self.stdout.write(f'Processing restaurant: {restaurant.name}')
            # Perform your actions here for each restaurant
            menu_updater = MenuUpdater()
            menu_updater.generate_menu_html(restaurant.id)
