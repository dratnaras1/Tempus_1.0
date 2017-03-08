from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from calender.authhelper import get_signin_url, get_token_from_code, get_temp_access_token
from calender.outlookservice import get_me, get_events_by_range
from calender.outlookservice import create_appointment
from calender.authhelper import get_signin_url, get_token_from_code, get_access_token, get_token_from_refresh_token
from calender.outlookservice import  get_events_by_range, get_my_events,send_email
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import Context
from django.template import Template
from calender.mailHelper import *
from .forms import ClientAppointmentForm, AppointmentFormAnalystDashboard, BookingUrlEmailForm
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
# from datetime import datetime
from pytz import timezone
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from calender.models import OutlookAuth, BookingToken
from calender.helper import getUser, getUser_by_username
from django.core.signing import Signer
from calender.token import *
import time
import json
import re
import dateutil.parser
import datetime


from django.utils import six
# Create your views here.
# def home(request):
#     redirect_uri = request.build_absolute_uri(reverse('gettoken'))
#     print(redirect_uri)
#     sign_in_url = get_signin_url(redirect_uri)
#     print("signinurl:" +  sign_in_url)
#     return HttpResponse('<a href="' + sign_in_url +'">Click here to sign in and view your mail</a>')

@login_required
def home(request):
    # Check if user has connected app with their outlook, if not direct to connection page
    try:
        outh = OutlookAuth.objects.get(user_email=request.user.email)
        return dashboard(request)
    except ObjectDoesNotExist:
        redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
        sign_in_url = get_signin_url(redirect_uri)
        c = Context({'sign_in_url': sign_in_url})
        # return render(request, 'calender/index.html' , c)
        return render(request, 'calender/dashboard_outlookSync.html' , c)
#
# @login_required
# def index(request):
#     # Check if user has connected app with their outlook, if not direct to connection page
#     try:
#         outh = OutlookAuth.objects.get(user_email=request.user.email)
#         return dashboard(request)
#     except ObjectDoesNotExist:
#         redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
#         sign_in_url = get_signin_url(redirect_uri)
#         c = Context({'sign_in_url': sign_in_url})
#         return render(request, 'calender/index.html' , c)

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
    # oauth= OutlookAuth.objects.get(pk=1)
    # oauth.user_email= user['EmailAddress']
    # oauth.refresh_token = refresh_token
    # if(oauth.auth_code != auth_code):
    #     oauth.auth_code = auth_code
    #     oauth.save()

    ouath = OutlookAuth.objects.create(user_email = user['EmailAddress'], refresh_token = refresh_token, auth_code = auth_code, user = request.user)

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


    return dashboard(request)
    # return HttpResponse('User Email: {0}, Access token: {1}'.format(user['EmailAddress'], access_token))

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
        # events = get_events_by_range(access_token, user_email)
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

        form = AppointmentFormAnalystDashboard(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            oauth = getUser(request)
            # oauth = OutlookAuth.objects.get(pk=1)
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
        form = AppointmentFormAnalystDashboard()



    return render(request, 'calender/dashboard_appointments.html', {'form': form})

def dashboard_bookingUrl(request):
    # s = SessionStore()
    # if request.session.get('booking_url_token', False):
    if request.session.get('booking_url_token', None) == None:
        request.session['booking_url_token'] = create_token_str_not_saved_in_db(request)

    body = "Hello {{name}},\n\n" \
          "{{user}} is available for a technical site visit.\n\n" \
          "If you would like to take us up on this offer please click on the link below and select a time that works best for you.\n\n" \
          "https://{{ host }}/calender/booking/"+request.session.get('booking_url_token', None)+"\n\n" \
          "Regards,\n\n" \
          "{{user}} "
    form = BookingUrlEmailForm(initial={'body':body})

    # request.session['booking_url_token'] \
    # print("initial "+ request.session['booking_url_token'])
    # "https://{{ host }}/calender/booking/"+request.session['booking_url_token']+"\n\n" \

    # print("dosplay"+ booking_url_token)
    # +"https://{{ host }}/calender/booking/"+create_token_str(request)+"\n\n" + \





    # print("initial" + booking_url_token)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:


        form = BookingUrlEmailForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            to_recipients = form.cleaned_data['to_Recipients']
            client_name = form.cleaned_data['client_name']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            oauth = getUser(request)
            # oauth = OutlookAuth.objects.get(pk=1)
            auth_code = oauth.auth_code
            user_email = oauth.user_email
            rt = oauth.refresh_token
            redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
            json = get_token_from_refresh_token(rt, redirect_uri)
            token = json["access_token"]
            add_token_to_db(request.user, request.session['booking_url_token'], client_name, to_recipients)

            # print("save"  + booking_url_token)

            # user_email = "dratnaras@itrsgroup.onmicrosoft.com"
            response = send_email(token, user_email, to_recipients,body, subject)
            request.session['booking_url_token'] = None


            c =  Context({'status_code' : response })

            return HttpResponse(c)
    # if a GET (or any other method) we'll create a blank form
    else:
        # form = BookingUrlEmailForm(initial={'interest_rate': 3.5, 'number_of_years':5})
        # body = "Hello {{name}},\n\n" \
        #        "{{user}} is available for a technical site visit.\n\n" \
        #        "If you would like to take us up on this offer please click on the link below and select a time that works best for you.\n\n" \
        #        "https://{{ host }}/calender/booking/"+request.session.get('booking_url_token')+"\n\n"\
        #        "Regards,\n\n" \
        #        "{{user}} "
        # # print("dosplay"+ booking_url_token)
        #        # +"https://{{ host }}/calender/booking/"+create_token_str(request)+"\n\n" + \
        #
        # form = BookingUrlEmailForm(initial={'body':body})

        return render(request, 'calender/dashboard_bookingUrl.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'calender/dashboard_home.html')


@login_required
def dashboard_routePlanner(request):
    # context = {'user':request.user}
    return render(request, 'calender/dashboard_routePlanner.html')

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

def clientBooking_for_user(request,username):
    # print(username)
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

            # oauth = OutlookAuth.objects.get(pk=1)
            oauth = getUser_by_username(username)
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

def clientBooking_for_token(request,token):
    if check_token_valid(token):
        name_token = get_clientName_from_token(token)
        email_token = get_clientEmail_from_token(token)

        # print(email)

        if (request.method == 'POST'):
            # create a form instance and populate it with data from the request:

            form = ClientAppointmentForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                # name = name_token
                # email = email_token
                date = form.cleaned_data['date']
                time = form.cleaned_data['time']


                oauth = get_user_from_token(token)
                auth_code = oauth.auth_code
                user_email = oauth.user_email
                rt = oauth.refresh_token
                redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))

                token = BookingToken.objects.get(token=token)
                token.used = True
                token.save()


                json = get_token_from_refresh_token(rt, redirect_uri)
                token = json["access_token"]

                # user_email = "dratnaras@itrsgroup.onmicrosoft.com"
                response = create_appointment(token, user_email, date, time, email_token, name_token)
                # statusCode = response.status

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


                return render(request, 'calender/client_booking_bs_response.html', c)



        # if a GET (or any other method) we'll create a blank form
        else:
            form = ClientAppointmentForm()


        return render(request, 'calender/client_booking_bs', {'form': form, 'name':name_token})
    else:
        return HttpResponse('<h1>Token expired</h1>')

def getTimes(request):


    selectedDate = request.GET['selectedDate']
    startTime = 'T09:00:00.0000000'
    endTime = 'T17:30:00.0000000'
    convertStartDate = selectedDate+startTime
    convertEndDate = selectedDate+endTime

    # oauth = OutlookAuth.objects.get(pk=1)
    oauth = (request)
    auth_code = oauth.auth_code
    user_email = oauth.user_email
    rt = oauth.refresh_token
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    json_token = get_token_from_refresh_token(rt, redirect_uri)
    token = json_token["access_token"]

    events =get_events_by_range(token, redirect_uri, convertStartDate, convertEndDate)
    # print(events.keys())
    eventsVal = events['value']

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

    # time = [['13','00'],['14','00']]

    # print(time)
    some_data_to_dump = {
        'time': time
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')

def getTimes_for_user(request, token):


    selectedDate = request.GET['selectedDate']
    startTime = 'T09:00:00.0000000'
    endTime = 'T17:30:00.0000000'
    convertStartDate = selectedDate+startTime
    convertEndDate = selectedDate+endTime

    # oauth = OutlookAuth.objects.get(pk=1)
    # oauth = getUser(request)
    oauth = get_user_from_token(token)
    auth_code = oauth.auth_code
    user_email = oauth.user_email
    rt = oauth.refresh_token
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    json_token = get_token_from_refresh_token(rt, redirect_uri)
    token = json_token["access_token"]

    events =get_events_by_range(token, redirect_uri, convertStartDate, convertEndDate)
    # print(events.keys())
    eventsVal = events['value']


    time = []

    for val in eventsVal:
        eventStart = val['Start']
        eventStartDateTime = dateutil.parser.parse(str(eventStart['DateTime']))
        eventEnd = val['End']
        eventEndDateTime = dateutil.parser.parse(str(eventEnd['DateTime']))
        print(str(eventStartDateTime) + "   " + str(eventEndDateTime))
        # print(eventStartDateTime.isoformat())
        while eventStartDateTime <= eventEndDateTime:
            simplifiedTime = eventStartDateTime.strftime("%H:%M")
            # time.append()
            # print(eventStartDateTime.strftime("%H:%M"))
            temp = simplifiedTime.split(":")
            time.append(temp)
            eventStartDateTime+=datetime.timedelta(minutes=30)


    print(time)
    some_data_to_dump = {
        'time': time
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')

def get_events_for_today(request):
    oauth = getUser(request)

    user_email = oauth.user_email
    rt = oauth.refresh_token
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    json_token = get_token_from_refresh_token(rt, redirect_uri)
    token = json_token["access_token"]

    todaysDate = time.strftime("%Y-%m-%d")
    startTime = 'T09:00:00.0000000'
    endTime = 'T17:30:00.0000000'
    convertStartDate = todaysDate+startTime
    convertEndDate = todaysDate+endTime

    events=get_events_by_range(token, redirect_uri, convertStartDate, convertEndDate)

    eventsArr = []
    eventsVal = events['value']
    for val in eventsVal:
        subject = val['Subject']
        eventStart = val['Start']
        eventStartDateTime = eventStart['DateTime']
        eventEnd = val['End']
        eventEndDateTime = eventEnd['DateTime']
        eventStartDateTime = eventStartDateTime.replace("T", " ")
        eventEndDateTime = eventEndDateTime.replace("T", " ")
        individualEvent = []
        individualEvent.append(eventStartDateTime)
        individualEvent.append(eventEndDateTime)
        individualEvent.append(subject)
        eventsArr.append(individualEvent)
        # print(eventStartDateTime + eventEndDateTime )

    # print(eventsArr)
    some_data_to_dump = {
        'events': eventsArr
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')

def getEventsDashboard(request):
    oauth = getUser(request)
    # auth_code = oauth.auth_code
    user_email = oauth.user_email
    rt = oauth.refresh_token
    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    json_token = get_token_from_refresh_token(rt, redirect_uri)
    token = json_token["access_token"]
    events = get_my_events(token, user_email)
    # context = { 'events': events['value'] }
    # some_data_to_dump = {
    #     'events': events['value']
    # }
    # print(userEvents)

    eventsArr = []
    eventsVal = events['value']
    for val in eventsVal:
        subject = val['Subject']
        eventStart = val['Start']
        eventStartDateTime = eventStart['DateTime']
        eventEnd = val['End']
        eventEndDateTime = eventEnd['DateTime']
        eventStartDateTime = eventStartDateTime.replace("T", " ")
        eventEndDateTime = eventEndDateTime.replace("T", " ")
        individualEvent = []
        individualEvent.append(eventStartDateTime)
        individualEvent.append(eventEndDateTime)
        individualEvent.append(subject)
        eventsArr.append(individualEvent)
        # print(eventStartDateTime + eventEndDateTime )

    # print(eventsArr)
    some_data_to_dump = {
        'events': eventsArr
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')
    # return HttpResponse(context)


