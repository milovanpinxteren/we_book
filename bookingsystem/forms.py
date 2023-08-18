from django import forms

class ReservationForm(forms.Form):
    number_of_persons = forms.IntegerField()
    reservation_date = forms.DateField()
    reservation_time = forms.TimeField()