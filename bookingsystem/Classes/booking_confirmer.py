from datetime import datetime

from bookingsystem.Classes.email_sender import EmailSender
from bookingsystem.models import Reservations, Customers, Restaurants


class BookingConfirmer():
    def confirm_booking(self, reservationID, name, email, telephone_nr):
        print('confirming booking')
        email_sender = EmailSender()
        customer = Customers.objects.create(full_name=name, email=email, telephone_nr=telephone_nr, updated_at=datetime.now())
        reservation = Reservations.objects.filter(id=reservationID)
        reservation.update(confirmed=True, customer=customer)
        restaurantID = reservation.values_list('restaurant', flat=True)[0]
        restaurant_name = Restaurants.objects.filter(id=restaurantID).values_list('name', flat=True)[0]
        restaurant_email = Restaurants.objects.filter(id=restaurantID).values_list('email', flat=True)[0]

        booker_subject = 'Conferma Prenotazione al ' + restaurant_name
        booker_message_text = 'Gentile Cliente,\n\n La tua prenotazione presso ' + restaurant_name + ' per ' + str(reservation.values_list('reservation_date', flat=True)[0]) + ' alle ore ' + str(reservation.values_list('arrival_time', flat=True)[0])[:5] + ' è stata confermata con successo. \n\n Attendiamo con impazienza la Sua visita!\n\nCordiali saluti,\n' + restaurant_name
        booker_english_translation = 'Dear Customer,\n\nYour reservation at ' + restaurant_name + ' for ' + str(reservation.values_list('reservation_date', flat=True)[0]) + ' at ' + str(reservation.values_list('arrival_time', flat=True)[0])[:5] + ' has been successfully confirmed. We look forward to your visit!\n\nBest regards,\n' + restaurant_name + '\n\n'

        restaurant_subject = 'È stata effettuata una prenotazione'
        restaurant_message_text = 'Gentile Cliente,\n\n Una prenotazione presso per ' + str(reservation.values_list('reservation_date', flat=True)[0]) + ' alle ore ' + str(reservation.values_list('arrival_time', flat=True)[0])[:5] + ' è stata confermata con successo. \n\n Nome di cliente: ' + customer.full_name + '\n Email: ' + customer.email + '\n numerò di telephono: ' + str(customer.telephone_nr) + '\n numerò di tavolo: ' + str(reservation.values_list('table__table_nr', flat=True)[0]) + '\n\n Puoi gestire la prenotazione nel sistema\n'

        email_sender.send_booker_email(customer.email, booker_subject, booker_message_text, booker_english_translation)
        email_sender.send_restaurant_email(restaurant_email, restaurant_subject, restaurant_message_text)
        email_sender.send_restaurant_email('info@ristaiuto.it', restaurant_subject, restaurant_message_text) #confirmation for developer
        context = {'confirmed_reservation': True, 'status': 'booking_confirmed',
                   'reservation_date': reservation.values_list('reservation_date', flat=True)[0],
                   'start_time': reservation.values_list('arrival_time', flat=True)[0],
                   'number_of_persons': reservation.values_list('number_of_persons', flat=True)[0],
                   'name': customer.full_name, 'email_adress': customer.email, 'telephone_number': customer.telephone_nr,
                   'restaurant': restaurant_name, 'restaurantID': restaurantID, 'reservationID': reservationID
                   }
        return context