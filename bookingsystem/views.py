import os
from datetime import date, datetime

from django.contrib.auth.views import LoginView as DefaultLoginView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
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
from bookingsystem.Classes.availability_checker import AvailabilityChecker
from bookingsystem.Classes.booking_confirmer import BookingConfirmer
from bookingsystem.Classes.booking_maker import BookingMaker
from bookingsystem.Classes.email_sender import EmailSender
from bookingsystem.Classes.id_handler import IDHandler
from bookingsystem.forms import ReservationForm, ConfirmBookingForm
from bookingsystem.models import Restaurants, UserRestaurantLink, Reservations, Courses, Dishes, Errors, Tables, \
    CustomRestaurantAvailability, Orders
from we_book import settings


class LogoutView():
    def logout(self, request):
        request.session.flush()
        return render(request, 'login.html')


class CustomLoginView(DefaultLoginView):
    def form_valid(self, form):

        if form.is_valid():
            print('valid')
            response = super().form_valid(form)
            current_user = form.get_user().id
            restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id',
                                                                                                flat=True).first()
            self.request.session['restaurant_name'] = Restaurants.objects.get(pk=restaurant_id).name
            self.request.session['restaurant_url'] = Restaurants.objects.get(pk=restaurant_id).website
        user_language = self.request.LANGUAGE_CODE  # Use the name of the language selector field in your form
        redirect_url = reverse('bookingsystem:restaurant_portal')
        # Append the language code as a prefix to the URL path
        if user_language:
            redirect_url = f'/{user_language}{redirect_url}'
        return redirect(redirect_url)


def index(request):
    try:
        id_code = request.GET['restaurantID']
        restaurantID = IDHandler().decode(id_code)
        # restaurantID = request.GET['restaurantID']
        request.session['restaurantID'] = restaurantID
    except Exception as e:
        try:
            restaurantID = request.session['restaurantID']
        except Exception as e:
            restaurantID = 1

    restaurant = Restaurants.objects.get(id=restaurantID)
    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year
    disabled_dates = AvailabilityChecker.get_disabled_dates(request, restaurant, current_month, current_year)
    timestamps = AvailabilityChecker.make_timestamps(request)
    request.session['timestamps'] = timestamps
    try:
        status = request.session['status']
        print(status)
    except Exception as e:
        print(e)
        status = ''
    context = {'restaurant': restaurant, 'disabled_dates': disabled_dates, 'status': status}
    return render(request, 'index.html', context)


def check_available_dates(request):
    restaurant_id = int(request.POST['restaurantID'])
    restaurant = Restaurants.objects.get(pk=restaurant_id)
    disabled_dates = AvailabilityChecker.get_disabled_dates(request, restaurant, int(request.POST['month']),
                                                            int(request.POST['year']))
    response_data = {'disabled_dates': disabled_dates}
    return JsonResponse(response_data)


def check_availability(request):
    restaurant_id = int(request.POST['restaurantID'])
    timestamps = request.session['timestamps']
    restaurant = Restaurants.objects.get(pk=restaurant_id)
    if request.POST['number_of_persons'] != '':
        availability = AvailabilityChecker.query_availability(request, restaurant, request.POST['reservation_date'],
                                                              request.POST['number_of_persons'], timestamps)
    else:
        print('number of persons not filled in')
    return JsonResponse(availability)


def make_reservation(request):
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST, request.FILES)
        if reservation_form.is_valid():
            # Form is valid, check if you can find a possible table
            restaurant_id = request.GET['restaurantID']
            restaurant = Restaurants.objects.get(pk=restaurant_id)
            number_of_persons = reservation_form['number_of_persons'].value()
            reservation_date = reservation_form['reservation_date'].value()
            reservation_time = reservation_form['reservation_time'].value()
            bookingmaker = BookingMaker()
            context = bookingmaker.make_booking(restaurant_id, number_of_persons, reservation_date, reservation_time)
            request.session['status'] = context['status']
            request.session['reservation_date'] = reservation_date
            request.session['start_time'] = reservation_time
            request.session['number_of_persons'] = number_of_persons
            request.session['restaurant_name'] = restaurant.name
            request.session['restaurant_email'] = restaurant.email
            request.session['restaurant_website'] = restaurant.website

            if context['status'] == 'possible_reservation_found':
                request.session['held_reservation_id'] = context['held_reservation_id']
                request.session['table_id'] = context['table_id']
                confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
                context['confirmation_form'] = confirmation_form
                context['restaurant_name'] = restaurant.name
                context['restaurant_email'] = restaurant.email
                context['restaurant_website'] = restaurant.website
                return render(request, 'booking_confirmation.html', context)
            else:  # form valid, but no possible reservation found
                message = _("booking_failed")
                request.session['status'] = message
                context = {'message': message, 'restaurant_name': restaurant.name,
                           'reservation_date': request.session['reservation_date'],
                           'start_time': request.session['start_time'],
                           'number_of_persons': request.session['number_of_persons'],
                           'restaurant_phone_nr': restaurant.telephone_nr}
                return render(request, 'booking_confirmation.html', context)
        else:  # form invalid
            print('invalid form')
            message = _("booking_failed")
            request.session['status'] = message
            return redirect('bookingsystem:index')
    return redirect('bookingsystem:index')  # request methods is not post


def confirm_booking(request):
    if request.method == 'POST':
        confirmation_form = ConfirmBookingForm(request.POST, request.FILES)
        if confirmation_form.is_valid():
            reservationID = request.GET['reservationID']
            name = confirmation_form['name'].value()
            email = confirmation_form['email'].value()
            telephone_nr = confirmation_form['telephone_nr'].value()
            bookingconfirmer = BookingConfirmer()
            context = bookingconfirmer.confirm_booking(reservationID, name, email, telephone_nr)
            request.session['status'] = context['status']
            context['restaurant_name'] = request.session['restaurant_name']
            context['restaurant_email'] = request.session['restaurant_email']
            context['restaurant_website'] = request.session['restaurant_website']
        else:
            print(confirmation_form.errors)
            request.session['status'] = 'booking_failed'
            context = {'status': request.session['status'],
                       'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                       'start_time': request.session['start_time'],
                       'number_of_persons': request.session['number_of_persons'],
                       'held_reservation_id': False,
                       'confirmation_form': confirmation_form, 'restaurant_name': request.session['restaurant_name']
                , 'restaurant_email': request.session['restaurant_email'],
                       'restaurant_website': request.session['restaurant_website']}
            render(request, 'booking_confirmation.html', context)

    else:
        confirmation_form = ConfirmBookingForm()
        request.session['status'] = 'booking_failed'
        context = {'status': request.session['status'],
                   'table_id': request.session['status'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'],
                   'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id'],
                   'confirmation_form': confirmation_form, 'restaurant_name': request.session['restaurant_name']
            , 'restaurant_email': request.session['restaurant_email'],
                   'restaurant_website': request.session['restaurant_website']}
        render(request, 'booking_confirmation.html', context)
    return render(request, 'booking_confirmed.html', context)


def drop_reservation(request):
    reservation_id_1 = int(request.GET.get('reservation_id'))
    reservation_id_2 = request.session['held_reservation_id']
    if reservation_id_1 == reservation_id_2:
        if Reservations.objects.filter(id=reservation_id_1).values_list('confirmed', flat=True)[0] == False:
            Reservations.objects.filter(id=reservation_id_1).update(cancelled=True, confirmed=False)
            print('deleted reservation')
    return HttpResponse("Session expired, no reservation made")


def delete_reservation(request):
    email_sender = EmailSender()
    reservation_id = request.GET['reservationID']
    path = request.GET['path']
    Reservations.objects.filter(id=reservation_id).update(cancelled=True, confirmed=False)
    # TODO: send email
    reservation = Reservations.objects.get(id=reservation_id)
    restaurant_name = reservation.restaurant.name

    booker_subject = 'Cancellazione Prenotazione al ' + restaurant_name
    booker_message_text = 'Gentile Cliente,\n\n La tua prenotazione presso ' + restaurant_name + ' per ' + str(
        reservation.reservation_date) + ' alle ore ' + str(reservation.arrival_time)[
                                                       :5] + " viene cancellato. \n\n Puoi effettuare un'altra prenotazione sul sito web " + reservation.restaurant.website + " oppure contatta il ristorante tramite " + reservation.restaurant.telephone_nr + "\n\nCordiali saluti,\n" + restaurant_name
    english_translation = 'Dear Customer,\n\nYour reservation at ' + restaurant_name + ' for ' + str(
        reservation.reservation_date) + ' at ' + str(reservation.arrival_time)[
                                                 :5] + " has been canceled. \n\nYou can make another reservation on the website " + reservation.restaurant.website + " or contact the restaurant at " + reservation.restaurant.telephone_nr + "\n\nBest regards,\n" + restaurant_name + '\n\n'

    restaurant_subject = 'Cancellazione Prenotazione'
    restaurant_message_text = 'Gentile Cliente,\n\n Una prenotazione presso per ' + str(
        reservation.reservation_date) + ' alle ore ' + str(reservation.arrival_time)[
                                                       :5] + ' viene cancellato. \n\n Nome di cliente: ' + reservation.customer.full_name + '\n Email: ' + reservation.customer.email + '\n numerò di telephono: ' + str(
        reservation.customer.telephone_nr) + '\n numerò di tavolo: ' + str(reservation.table.table_nr) + '\n\n'

    email_sender.send_booker_email(reservation.customer.email, booker_subject, booker_message_text, english_translation)
    email_sender.send_restaurant_email(reservation.restaurant.email, restaurant_subject, restaurant_message_text)
    email_sender.send_restaurant_email('info@ristaiuto.it', restaurant_subject, restaurant_message_text)  # for checking
    request.session['status'] = 'reservation_cancelled'
    if path == 'confirmed_booking':
        context = {'status': request.session['status'],
                   'table_id': request.session['table_id'], 'reservation_date': request.session['reservation_date'],
                   'start_time': request.session['start_time'],
                   'number_of_persons': request.session['number_of_persons'],
                   'held_reservation_id': request.session['held_reservation_id']}
        return render(request, 'booking_confirmed.html', context)
    elif path == 'show_reservations':
        current_user = request.user.id
        reservation_shower = reservationShower()
        context = reservation_shower.prepare_table(current_user)
        context['deleted_reservation'] = reservation_id
        return render(request, 'restaurant_portal.html', context)


###########################################FOR RESTAURANTS##############################################################

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
