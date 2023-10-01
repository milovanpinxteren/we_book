import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings



class EmailSender():
    def send_booker_email(self, receiver_email, subject, message_text, english_translation):

        sender_email = 'info@ristaiuto.it'

        footer = """
        <small><i>questa mail è inviata da Ristaiuto - Il tuo partner digitale per il successo del tuo ristorante -- Siti web, disponibilità online e sistemi di prenotazioni. <br>
                 Per ulteriori informazioni, visita il nostro sito web: <a href="http://www.ristaiuto.it">http://www.ristaiuto.it</a></i></small>
                 """


        # Create a MIMEText object for the email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        between_languages_text = "<br><br><i><small>For English, see below:</small></i><br>_______________________________________________________________________________________________________________<br><br>"
        # Attach the email content (text)
        message.attach(MIMEText(message_text, 'plain'))
        message.attach(MIMEText(between_languages_text, 'html'))
        message.attach(MIMEText(english_translation, 'plain'))
        message.attach(MIMEText(footer, 'html'))

        # SMTP server configuration (for Gmail)
        smtp_server = 'smtp.hostinger.com'
        smtp_port = 587  # Port for TLS
        smtp_username = 'info@ristaiuto.it'
        smtp_password = settings.EMAIL_PASSWORD

        # Create an SMTP server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

        # Close the SMTP server
        server.quit()

        print('Email sent successfully')

    def send_restaurant_email(self, restaurant_email, subject, message_text):
        sender_email = 'info@ristaiuto.it'

        footer = """
        <small><i>questa mail è inviata da Ristaiuto - Il tuo partner digitale per il successo del tuo ristorante -- Siti web, disponibilità online e sistemi di prenotazioni. <br>
                 Per ulteriori informazioni, visita il nostro sito web: <a href="http://www.ristaiuto.it">http://www.ristaiuto.it</a></i></small>
                 """

        # Create a MIMEText object for the email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = restaurant_email
        message['Subject'] = subject

        # Attach the email content (text)
        message.attach(MIMEText(message_text, 'plain'))
        message.attach(MIMEText(footer, 'html'))

        # SMTP server configuration (for Gmail)
        smtp_server = 'smtp.hostinger.com'
        smtp_port = 587  # Port for TLS
        smtp_username = 'info@ristaiuto.it'
        smtp_password = settings.EMAIL_PASSWORD

        # Create an SMTP server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, restaurant_email, message.as_string())

        # Close the SMTP server
        server.quit()

        print('Email sent successfully')
