from django import forms
from django.forms.models import fields_for_model
# from models import Pattern

class ClientAppointmentForm (forms.Form):
    name = forms.CharField(label = 'Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name ...','name' : 'f1-first-name', 'class' : 'f1-first-name form-control', 'id' : 'f1-first-name'}))
    email = forms.CharField(label = 'Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email ...','name' : 'f1-email', 'class' : 'f1-email form-control', 'id' : 'f1-email'}))
    date = forms.CharField(label = 'Date', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Date ...','name' : 'f1-Date', 'class' : 'f1-Date form-control', 'id' : 'f1-Date'}))
    time = forms.CharField(label = 'Time', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Time ...','name' : 'f1-time', 'class' : 'f1-time form-control', 'id' : 'f1-Time'}))

    # forms.attrs.update({})
    # forms.attrs.update({'placeholder' : 'First name...'})
    # forms.attrs.update({'class' : 'f1-first-name form-control'})
    # forms.attrs.update({'id' : 'f1-first-name'})
    # q = forms.CharField(label='search',
    #                     )


    # <!--<input type="text" name="f1-first-name" placeholder="" class="f1-first-name form-control" id="f1-first-name">-->
class AppointmentFormAnalystDashboard(forms.Form):
    name = forms.CharField(label = 'Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name ...'}))
    email = forms.CharField(label = 'Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email ...'}))
    date = forms.CharField(label = 'Date', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Date ...'}))
    time = forms.CharField(label = 'Time', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Time ...'}))