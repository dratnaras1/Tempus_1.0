from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from calender.authhelper import get_signin_url, get_token_from_code, get_temp_access_token
from calender.outlookservice import get_me
from calender.outlookservice import create_appointment
from calender.authhelper import get_signin_url, get_token_from_code, get_access_token, get_access_token_from_auth
from calender.outlookservice import get_my_events
from django.shortcuts import render_to_response
from django.template import Context
from django.template import Template
from calender.mailHelper import *
from .forms import ClientAppointmentForm
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from datetime import datetime
from pytz import timezone
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from calender.models import OutlookAuth

import time

# Create your views here.
# def home(request):
#     redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
#     sign_in_url = get_signin_url(redirect_uri)
#     return HttpResponse('<a href="' + sign_in_url +'">Click here to sign in and view your mail</a>')


def home(request):
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    sign_in_url = get_signin_url(redirect_uri)
    c = Context({'sign_in_url': sign_in_url})
    return render(request, 'calender/index.html' , c)

def gettoken(request):
    auth_code = request.GET['code']
    # print("auth_code" + auth_code)
    # create outlook object
    oauth= OutlookAuth.objects.get(pk=1)
    # oauth.user_email= user['EmailAddress']
    if(oauth.auth_code != auth_code):
        oauth.auth_code = auth_code
        oauth.save()

    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']


    # expires_in is in seconds
    # Get current timestamp (seconds since Unix Epoch) and
    # add expires_in to get expiration time
    # Subtract 5 minutes to allow for clock differences
    expiration = int(time.time()) + expires_in - 300

    # Save the token in the session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    request.session['token_expires'] = expiration
    request.session['user_email'] = user['EmailAddress']



    return HttpResponse('User Email: {0}, Access token: {1}'.format(user['EmailAddress'], access_token))

def gettempttoken(request):
    auth_code = request.GET['code']
    redirect_uri = request.build_absolute_uri(reverse('calender:gettemptoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)
    expires_in = token['expires_in']

    # expires_in is in seconds
    # Get current timestamp (seconds since Unix Epoch) and
    # add expires_in to get expiration time
    # Subtract 5 minutes to allow for clock differences
    expiration = int(time.time()) + expires_in - 30

    # Save the token in the session
    request.session['access_token'] = access_token
    request.session['token_expires'] = expiration
    request.session['user_email'] = user['EmailAddress']
    return HttpResponse('User Email: {0}, Access token: {1}'.format(user['EmailAddress'], access_token))

def events(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('calender:gettoken')))
    user_email = request.session['user_email']
    # print(user_email)
    # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('calender:home'))
    else:
        events = get_my_events(access_token, user_email)
        context = { 'events': events['value'] }
        return render(request, 'calender/events.html', context)

def create_event_view(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('calender:gettoken')))
    user_email = request.session['user_email']

    if not access_token:
        return HttpResponseRedirect(reverse('calender:home'))
    else:
        create_event_view = create_event(access_token, user_email)
        c =  Context({'status_code' : create_event_view})
        return render(request, 'calender/createEvents.html', c)

def schedule(request):
    return render(request, 'calender/calender.html')


# def dashboard(request):
#     return render(request, 'calender/dashboardTest.html')

def dashboard(request):
    return render(request, 'calender/dashboard_base.html')

# def clientBooking(request):
#     return render(request, 'calender/client_booking.html')

# def clientBooking(request):
#
#     access_token = get_access_token(request, request.build_absolute_uri(reverse('calender:gettoken')))
#     user_email = request.session['user_email']
#
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = ClientAppointmentForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             # ...
#             # redirect to a new URL:
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             date = form.cleaned_data['date']
#             time = form.cleaned_data['time']
#             if not access_token:
#                 return HttpResponseRedirect(reverse('calender:home'))
#             else:
#
#              response = create_appointment(access_token, user_email, date, time, email, name)
#              send_mail(
#                  'Subject here',
#                  'Here is the message.',
#                  'dratnaras@itrsgroup.onmicrosoft.com',
#                  ['dratnaras@itrsgroup.com'],
#                  fail_silently=False,
#              )
#              c =  Context({'status_code' : response })
#
#
#
#              return HttpResponse(c)
#
#
#                 # Test
#                 # dateTime = date+"T"+time+":00"
#                 # context = Context({"dateTime_test": dateTime})
#                 # return HttpResponse(context)
#
#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = ClientAppointmentForm()
#
#     return render(request, 'calender/client_booking.html', {'form': form})
#

def clientBooking(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:

        form = ClientAppointmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            # auth_code = 'OAQABAAAAAADRNYRQ3dhRSrm-4K-adpCJz1zjklby0bfXPoYDzVT0_TLiLV_ENiReaK9gZ3h3z5_J2-y6HRq-_aBV34_SiLMWT-lV64i4bBt8GM5dYzitZlhmetiPN5HXGEyUiPU8kaZghskfupLg8RltPgL-25Jq0B_bWUIKVBcwYQoWeFLyWSh24_1vdAf9nYcZ-FmZeL997GN5EQiKN43CoN0yGYCqbA20a0X0gpV9rX3PZSj90IGUed0F097VC31QrEEMULK-GFbqqEtV9XcFcNT1qfaupju1c7YcwfwCsa6iUk6XWEzorESAaA57fuTqoqhadXUALdCpSDArytqgTdjO-3NYHWtCB9RHWQCcCCa_IdJxU4wRSQHtRUUBcmzhgYOx-Q4BY-KLqLa1n_oEuiq7ggsAA0VydH_1n7vb52a3P_Y6PqJ6Pj4XeurULFHxuI11q9p6htaLP9hePlM5f7J6JavNYDKUN0Vk12vJJvh4sRA_5Iu44Z9rJJNkhyRTJo6Id3ITUX1NX60CAGWHPPgzQkdhyQbvBWzQUl9-nq4g5YVKJh4aSaim8cXcnY8ULVv13qUdBCoQD5B3Woi1K3vxrEfcf3IZpcCOBItVJfZb8hBg4rkkqiKmkvyDTfVBvhjqfVc1fFjoa8ihL1tT7EjlXQPY_EKoNvUTYjWWu8fGRMmMpWw8l1EtbazOfwW_HjfMwrn9rSsgeBYCejxhEIcShE6KzEirYbu3mdoVKO9NNDLZGAa0B6fSeK8ZFthBhzPPmWkmSukGUbdE-htvnrL2kKwXlOaM3qQzzMdt-8qr5Rs2i_HNBBQikPPsaJGszefnK0EewnulG4prUaKvkbIDzpjkIAA'
            oauth = OutlookAuth.objects.get(pk=1)
            auth_code = oauth.auth_code
            # print("au" + auth_code)
            # print("au_db" + oauth.auth_code)
            # auth_code = OutlookAuth.objects.ge

            redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
            # token = get_token_from_code(auth_code, redirect_uri)
            # access_token = token['access_token']
            # print("token p" )

            token = get_access_token_from_auth(auth_code, redirect_uri)

            user_email = "dratnaras@itrsgroup.onmicrosoft.com"
            response = create_appointment(token, user_email, date, time, email, name)

            # send email to analyst
            # send_mail(
            #     'New Site Visit Booking',
            #     name + ' has booked a new appointment with you on ' + date +' at ' +time,
            #     'dratnaras@itrsgroup.onmicrosoft.com',
            #     ['dratnaras@itrsgroup.com'],
            #     fail_silently=False,
            #  )

            c =  Context({'status_code' : response })

            # return HttpResponse('<h1>site visit booked, analyst will be in touch</h1>')


            return HttpResponse(c)


                # Test
                # dateTime = date+"T"+time+":00"
                # context = Context({"dateTime_test": dateTime})
                # return HttpResponse(context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClientAppointmentForm()

    return render(request, 'calender/client_booking.html', {'form': form})
