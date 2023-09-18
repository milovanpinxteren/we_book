from django import forms
# from phonenumber_field.formfields import PhoneNumberField as PhoneNumberField

class ReservationForm(forms.Form):
    number_of_persons = forms.IntegerField()
    reservation_date = forms.DateField(input_formats=['%d/%M/%Y'])
    reservation_time = forms.TimeField()

class ConfirmBookingForm(forms.Form):
    # reservationID = forms.IntegerField()
    name = forms.CharField()
    email = forms.EmailField()
    telephone_nr = forms.CharField()