import os

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from datetime import date, datetime
from django.utils.translation import gettext as _
from bookingsystem.Classes.PortalClasses.custom_availability_updater import CustomAvailabilityUpdater
from bookingsystem.Classes.PortalClasses.menu_shower import MenuShower
from bookingsystem.Classes.PortalClasses.menu_updater import MenuUpdater
from bookingsystem.Classes.PortalClasses.reservation_maker import ReservationMaker
from bookingsystem.Classes.PortalClasses.reservation_shower import reservationShower
from bookingsystem.Classes.PortalClasses.restaurant_info_updater import RestaurantInfoUpdater
from bookingsystem.Classes.PortalClasses.restaurant_tables_updater import RestaurantTablesUpdater
from bookingsystem.Classes.PortalClasses.table_management_manager import TableManagementManager
from bookingsystem.Classes.PortalClasses.table_management_shower import TableManagementShower
from bookingsystem.models import Reservations, Errors, Courses, Dishes, UserRestaurantLink, Restaurants, \
    CustomRestaurantAvailability, Tables
from we_book import settings


def restaurant_portal(request):
    if request.user.groups.filter(name='table_management'):
        table_management_shower = TableManagementShower()
        context = table_management_shower.prepare_table_management(request)
        return render(request, 'restaurant_portal.html', context)
    else:
        context = {'action': './show_reservations/show_reservations.html'}
        return render(request, 'restaurant_portal.html', context)



def get_table_bill(request, table_id):
    table_management_shower = TableManagementShower()
    context = table_management_shower.get_table_bill(request, table_id)
    return JsonResponse(context)


def add_dish_to_table(request, dish_id, table_id):
    table_management_manager = TableManagementManager()
    response = table_management_manager.add_dish(request, dish_id, table_id)
    return JsonResponse(response)


def remove_dish_from_table(request, order_id, table_id, current_quantity):
    table_management_manager = TableManagementManager()
    response = table_management_manager.remove_dish(order_id, table_id, current_quantity)
    return JsonResponse(response)


def clear_table(request, table_id):
    table_management_manager = TableManagementManager()
    response = table_management_manager.clear_table(table_id)
    return JsonResponse(response)


def show_reservations(request):
    context = {'action': './show_reservations/show_reservations.html'}
    return render(request, 'restaurant_portal.html', context)


def calculate_reservation_table(request):
    current_user = request.user.id
    reservation_shower = reservationShower()
    context = reservation_shower.prepare_table(current_user)
    return JsonResponse(context)


def rollback_deletion(request):
    reservation_id = request.GET['reservationID']
    Reservations.objects.filter(id=reservation_id).update(cancelled=False, confirmed=True)
    current_user = request.user.id
    reservation_shower = reservationShower()
    context = reservation_shower.prepare_table(current_user)
    context['rolled_back_deletion'] = reservation_id
    return render(request, 'restaurant_portal.html', context)


def make_reservation_in_portal(request):
    try:
        if request.method == 'POST':
            reservation_maker = ReservationMaker()
            reservation_maker.make_reservation(request)
            context = {'action': './show_reservations/show_reservations.html'}
            return render(request, 'restaurant_portal.html', context)
    except Exception as e:
        error_message = _("could_not_make_booking_check_table_nr_date_and_time")
        Errors.objects.create(message=error_message, user_id=request.user.id, created_at=datetime.now())
        context = {'error_message': error_message}
        return render(request, 'error_page.html', context)


def view_menu(request):
    context = MenuShower().prepare_menu(request)
    return render(request, 'restaurant_portal.html', context)


def update_menu(request):
    if request.method == 'POST':
        menu_updater = MenuUpdater()
        restaurant_id = menu_updater.update_menu(request)
        menu_updater.generate_menu_html(restaurant_id)
        # TODO: generate html and send html to correct branch and remote and push (GitPython)
    context = MenuShower().prepare_menu(request)
    return render(request, 'restaurant_portal.html', context)
    # return redirect('bookingsystem:/view_menu')


def delete_course(request, course_id):
    try:
        record = Courses.objects.get(pk=course_id)
        record.delete()
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)
    except Courses.DoesNotExist:
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)


def delete_dish(request, dish_id):
    try:
        record = Dishes.objects.get(pk=dish_id)
        record.delete()
        response_data = {'message': 'Record deleted successfully'}
        return JsonResponse(response_data)
    except Courses.DoesNotExist:
        print('course does not exist')


def add_dish(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    if request.method == 'POST':
        try:
            name = request.POST['name']
            price = request.POST['price'].replace(',', '.')
            dish_order = request.POST['dish_order']
            course_id = request.POST['course_id']
            Dishes.objects.create(name=name, price=price, dish_order=dish_order, course_id=course_id,
                                  restaurant_id=restaurant_id)
        except Exception as e:
            print('could not add course', e)
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)


def add_course(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    if request.method == 'POST':
        try:
            name = request.POST['name']
            course_order = request.POST['course_order']
            Courses.objects.create(name=name, course_order=course_order, restaurant_id=restaurant_id)
        except Exception as e:
            print('could not add course', e)
        context = MenuShower().prepare_menu(request)
        return render(request, 'restaurant_portal.html', context)


def view_restaurant_settings(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    restaurant_info = Restaurants.objects.get(pk=restaurant_id)
    context = {'action': './restaurant_settings/restaurant_settings.html', 'restaurant_info': restaurant_info}
    return render(request, 'restaurant_portal.html', context)


def update_restaurant_info(request):
    RestaurantInfoUpdater().update_restaurant_info(request)
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    restaurant_info = Restaurants.objects.get(pk=restaurant_id)
    context = {'action': './restaurant_settings/restaurant_settings.html', 'restaurant_info': restaurant_info}
    return render(request, 'restaurant_portal.html', context)


def custom_restaurant_availability(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    custom_restaurant_availability = CustomRestaurantAvailability.objects.filter(restaurant_id=restaurant_id).order_by(
        'date')
    context = {'action': './custom_restaurant_availability/custom_restaurant_availability.html',
               'custom_restaurant_availability': custom_restaurant_availability}
    return render(request, 'restaurant_portal.html', context)


def add_custom_restaurant_availability(request):
    CustomAvailabilityUpdater().add_availability(request)
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    custom_restaurant_availability = CustomRestaurantAvailability.objects.filter(restaurant_id=restaurant_id).order_by(
        'date')
    context = {'action': './custom_restaurant_availability/custom_restaurant_availability.html',
               'custom_restaurant_availability': custom_restaurant_availability}
    return render(request, 'restaurant_portal.html', context)


def update_custom_availability(request):
    CustomAvailabilityUpdater().update_availability(request)
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    custom_restaurant_availability = CustomRestaurantAvailability.objects.filter(restaurant_id=restaurant_id).order_by(
        'date')
    context = {'action': './custom_restaurant_availability/custom_restaurant_availability.html',
               'custom_restaurant_availability': custom_restaurant_availability}
    return render(request, 'restaurant_portal.html', context)


def delete_availability(request, availability_id):
    try:
        record = CustomRestaurantAvailability.objects.get(pk=availability_id)
        record.delete()
        response_data = {'message': 'Record deleted successfully'}
        return JsonResponse(response_data)
    except CustomRestaurantAvailability.DoesNotExist:
        print('table does not exist')
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    custom_restaurant_availability = CustomRestaurantAvailability.objects.filter(restaurant_id=restaurant_id)
    context = {'action': './custom_restaurant_availability/custom_restaurant_availability.html',
               'custom_restaurant_availability': custom_restaurant_availability}
    return render(request, 'restaurant_portal.html', context)


def view_restaurant_tables(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    tables = Tables.objects.filter(restaurant_id=restaurant_id).order_by('table_nr')
    context = {'action': './restaurant_tables/restaurant_tables.html', 'tables': tables}
    return render(request, 'restaurant_portal.html', context)


def update_tables(request):
    RestaurantTablesUpdater().update_tables(request)
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    tables = Tables.objects.filter(restaurant_id=restaurant_id).order_by('table_nr')
    context = {'action': './restaurant_tables/restaurant_tables.html', 'tables': tables}
    return render(request, 'restaurant_portal.html', context)


def delete_table(request, table_id):
    try:
        record = Tables.objects.get(pk=table_id)
        record.delete()
        response_data = {'message': 'Record deleted successfully'}
        return JsonResponse(response_data)
    except Tables.DoesNotExist:
        print('table does not exist')


def add_table(request):
    current_user = request.user.id
    restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                        flat=True).first()
    if request.method == 'POST':
        try:
            table_nr = request.POST['table_nr']
            min_pers = request.POST['min_pers']
            max_pers = request.POST['max_pers']
            Tables.objects.create(table_nr=table_nr, min_pers=min_pers, max_pers=max_pers, restaurant_id=restaurant_id,
                                  created_at=datetime.now(), updated_at=datetime.now())
        except Exception as e:
            print('could not add table', e)
    tables = Tables.objects.filter(restaurant_id=restaurant_id).order_by('table_nr')
    context = {'action': './restaurant_tables/restaurant_tables.html', 'tables': tables}
    return render(request, 'restaurant_portal.html', context)


def serve_generated_menu(request, template_name):
    file_path = os.path.join(settings.BASE_DIR, 'bookingsystem/static/menus', template_name)
    try:
        with open(file_path, 'r') as file:
            html_content = file.read()
        return HttpResponse(html_content)
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
