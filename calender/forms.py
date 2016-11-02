from django import forms

class ClientAppointmentForm (forms.Form):
    name = forms.CharField(label = 'name', max_length=100)
    email = forms.CharField(label = 'email', max_length=100)
    date = forms.CharField(label = 'date', max_length=100)
    time = forms.CharField(label = 'time', max_length=100)


