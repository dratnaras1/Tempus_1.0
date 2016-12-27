from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from calender.authhelper import get_signin_url, get_token_from_code, get_temp_access_token
from calender.outlookservice import get_me, get_events_by_range
from calender.outlookservice import create_appointment
from calender.authhelper import get_signin_url, get_token_from_code, get_access_token, get_token_from_refresh_token
from calender.outlookservice import  get_events_by_range
from django.shortcuts import render_to_response
from django.template import Context
from django.template import Template
from calender.mailHelper import *
from .forms import ClientAppointmentForm, AppointmentFormAnalystDashboard
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from datetime import datetime
from pytz import timezone
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from calender.models import OutlookAuth
import time
import json
import re
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

    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']

    # create outlook object
    oauth= OutlookAuth.objects.get(pk=1)
    oauth.user_email= user['EmailAddress']
    oauth.refresh_token = refresh_token
    if(oauth.auth_code != auth_code):
        oauth.auth_code = auth_code
        oauth.save()



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
        # events = get_my_events(access_token, user_email)
        events = get_events_by_range(access_token, user_email)
        # context = { 'events': events['value'] }
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

def dashboard_appointments(request):
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

            oauth = OutlookAuth.objects.get(pk=1)
            auth_code = oauth.auth_code
            user_email = oauth.user_email
            rt = oauth.refresh_token
            redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))


            json = get_token_from_refresh_token(rt, redirect_uri)
            token = json["access_token"]

            # user_email = "dratnaras@itrsgroup.onmicrosoft.com"
            response = create_appointment(token, user_email, date, time, email, name)

            # send email to analyst
            # send_mail(
            #     'New Site Visit Booking',
            #     name + ' has booked a new appointment with you on ' + date +' at ' +time,
            #     'tempus@itrsgroup.onmicrosoft.com',
            #     ['dratnaras@itrsgroup.com'],
            #     fail_silently=False,
            #     )
            #
            c =  Context({'status_code' : response })
            #
            # return HttpResponse('<h1>site visit booked, analyst will be in touch</h1>')
            #
            #
            return HttpResponse(c)



    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClientAppointmentForm()



    return render(request, 'calender/dashboard_appointments.html', {'form': form})


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

            oauth = OutlookAuth.objects.get(pk=1)
            auth_code = oauth.auth_code
            user_email = oauth.user_email
            rt = oauth.refresh_token
            redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))


            json = get_token_from_refresh_token(rt, redirect_uri)
            token = json["access_token"]

            # user_email = "dratnaras@itrsgroup.onmicrosoft.com"
            response = create_appointment(token, user_email, date, time, email, name)

            # send email to analyst
            # send_mail(
            #     'New Site Visit Booking',
            #     name + ' has booked a new appointment with you on ' + date +' at ' +time,
            #     'tempus@itrsgroup.onmicrosoft.com',
            #     ['dratnaras@itrsgroup.com'],
            #     fail_silently=False,
            #  )

            c =  Context({'status_code' : response })

            # return HttpResponse('<h1>site visit booked, analyst will be in touch</h1>')


            return HttpResponse(c)



    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClientAppointmentForm()

    # time = [[13,0],[14,0]]

    return render(request, 'calender/client_booking_bs', {'form': form})
    # return render(request, 'calender/client_booking_bs', {'form': form, 'time': time})

def getTimes(request):


    selectedDate = request.GET['selectedDate']
    startTime = 'T09:00:00.0000000'
    endTime = 'T17:30:00.0000000'
    convertStartDate = selectedDate+startTime
    convertEndDate = selectedDate+endTime

    oauth = OutlookAuth.objects.get(pk=1)
    auth_code = oauth.auth_code
    user_email = oauth.user_email
    rt = oauth.refresh_token
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    json_token = get_token_from_refresh_token(rt, redirect_uri)
    token = json_token["access_token"]

    events =get_events_by_range(token, redirect_uri, convertStartDate, convertEndDate)
    # print(events.keys())
    eventsVal = events['value']
    # # print(len(eventsVal))
    # eventsDate = eventsVal[1]
    # print(len(eventsDate))
    # eventsDateStarts = eventsDate['Start']
    # print(eventsDateStarts)
    # json.loads(eventsVal)

    time = []

    for val in eventsVal:
        eventStart = val['Start']
        eventStartDateTime = eventStart['DateTime']
        eventEnd = val['End']
        eventEndDateTime = eventEnd['DateTime']

        m = re.search('T\d\d.\d\d', eventStartDateTime)
        if m:
            found = m.group(0)
            hourMinute = found[1:]
            temp = hourMinute.split(":")
            time.append(temp)


        # print(time)
        # print(eventEndDateTime)


    # print(eventsVal)
    # print(events)
    # print(events['Start'])
    # eventsArr= json.loads(events)
    #
    # for x in eventsArr['Start']:
    #     print (x['DateTime'])

    # print(events['start'])

    # time = [['13','00'],['14','00']]

    print(time)
    some_data_to_dump = {
        'time': time
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')
