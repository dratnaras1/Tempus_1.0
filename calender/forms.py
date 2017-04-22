from django import forms
from django.core.validators import validate_email
from django.forms.models import fields_for_model
# from models import Pattern
# from calender.token import
class ClientAppointmentForm (forms.Form):
    # name = forms.CharField(label = 'Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name ...','name' : 'f1-first-name', 'class' : 'f1-first-name form-control', 'id' : 'f1-first-name'}))
    # email = forms.EmailField(label = 'Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email ...','name' : 'f1-email', 'class' : 'f1-email form-control', 'id' : 'f1-email'}))
    date = forms.CharField(label = 'Date', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Date ...','name' : 'f1-Date', 'class' : 'f1-Date form-control', 'id' : 'f1-Date'}))
    time = forms.CharField(label = 'Time', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Time ...','name' : 'f1-time', 'class' : 'f1-time form-control', 'id' : 'f1-Time'}))
    address = forms.CharField(label = 'Address', widget=forms.Textarea(attrs={'placeholder': 'Address ...','name' : 'f1-about-yourself', 'class' : 'f1-about-yourself form-control', 'id' : 'f1-about-yourself'}))

    # forms.attrs.update({})
    # forms.attrs.update({'placeholder' : 'First name...'})
    # forms.attrs.update({'class' : 'f1-first-name form-control'})
    # forms.attrs.update({'id' : 'f1-first-name'})
    # q = forms.CharField(label='search',
    #                     )


    # <!--<input type="text" name="f1-first-name" placeholder="" class="f1-first-name form-control" id="f1-first-name">-->
class AppointmentFormAnalystDashboard(forms.Form):
    name = forms.CharField(label = 'Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name ...','name' : 'f1-first-name', 'class' : 'f1-first-name form-control', 'id' : 'f1-first-name'}))
    email = forms.EmailField(label = 'Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email ...','name' : 'f1-email', 'class' : 'f1-email form-control', 'id' : 'f1-email'}))
    date = forms.CharField(label = 'Date', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Date ...','name' : 'f1-Date', 'class' : 'f1-Date form-control', 'id' : 'f1-Date'}))
    time = forms.CharField(label = 'Time', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Time ...','name' : 'f1-time', 'class' : 'f1-time form-control', 'id' : 'f1-Time'}))
    address = forms.CharField(label = 'Address', widget=forms.Textarea(attrs={'placeholder': 'Address ...','name' : 'f1-about-yourself', 'class' : 'f1-about-yourself form-control', 'id' : 'f1-about-yourself'}))

class BookingUrlEmailForm(forms.Form):
    initial_subject= "ITRS Site Visit"

    client_name = forms.CharField(label = 'Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'ng-model':'name' }))
    to_Recipients = forms.EmailField(label = 'Email', max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'type':'email'}))
    # carbon_copy = forms.EmailField(label = 'CC', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    subject = forms.CharField(label = 'Subject', max_length=100, initial=initial_subject, widget=forms.TextInput(attrs={'class':'form-control'}))
    body = forms.CharField( widget=forms.Textarea(attrs={'class':'form-control'}))

class BookingLinkGeneratorForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=100)
    email = forms.CharField(label = 'Email', max_length=100)

class BookingUrlEmailForm1(forms.Form):
    initial_subject= "ITRS Site Visit"
    to_Recipients = forms.EmailField(label = 'To', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    # carbon_copy = forms.EmailField(label = 'CC', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    subject = forms.CharField(label = 'Subject', max_length=100, initial=initial_subject, widget=forms.TextInput(attrs={'class':'form-control'}))

class BookingUrlEmailForm2(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
