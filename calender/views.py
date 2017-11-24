####################################################################################################################
# Created by Daniel Ratnaras ITRS Group Ltd
####################################################################################################################

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from calender.outlookservice import get_me
from calender.outlookservice import create_appointment
from calender.authhelper import get_signin_url, get_token_from_code,get_token_from_refresh_token
from calender.outlookservice import  get_events_by_range, get_my_events,send_email
from django.contrib.auth.decorators import login_required
from django.template import Context
from .forms import ClientAppointmentForm, AppointmentFormAnalystDashboard, BookingUrlEmailForm
from django.core.exceptions import ObjectDoesNotExist
from calender.token import *
import time
import json
import re
import dateutil.parser
import datetime
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect


from django.utils import six

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


def gettoken(request):
    auth_code = request.GET['code']
    # print("auth_code" + auth_code)

    redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']

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

@login_required
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
            address = form.cleaned_data['address']

            oauth = getUser(request)
            # oauth = OutlookAuth.objects.get(pk=1)
            auth_code = oauth.auth_code
            user_email = oauth.user_email
            rt = oauth.refresh_token
            redirect_uri = request.build_absolute_uri(reverse('calender:gettoken'))


            json = get_token_from_refresh_token(rt, redirect_uri)
            token = json["access_token"]



            # user_email = "dratnaras@itrsgroup.onmicrosoft.com"
            response = create_appointment(token, user_email, date, time, email, name, address)

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
            messages.success(request, 'Appointment Created!')
            return redirect('calender:dashboardAppointments')
        else:
            messages.error(request, 'Unable to create appointment')



    # if a GET (or any other method) we'll create a blank form
    else:
        form = AppointmentFormAnalystDashboard()



    return render(request, 'calender/dashboard_appointments.html', {'form': form})

@login_required
def dashboard_bookingUrl(request):
    # s = SessionStore()
    # if request.session.get('booking_url_token', False):
    if request.session.get('booking_url_token', None) == None:
        request.session['booking_url_token'] = create_token_str_not_saved_in_db(request)

    body = "Hello {{name}},\n\n" \
          "{{user}} is available for a technical site visit.\n\n" \
          "If you would like to take us up on this offer please click on the link below and select a time that works best for you.\n\n" \
          "https://{{ host }}/calendar/booking/"+request.session.get('booking_url_token', None)+"\n\n" \
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


            c =  Context({'status_code' : response,
                          'form': form})

            # return HttpResponse("<script>alert('message sent')</script>")
            messages.success(request, 'Email Sent!')
            return redirect('calender:dashboardBookingUrl')
        else:
            messages.error(request, 'Unable to send email')
            # return render(request, 'calender/dashboard_bookingUrl.html', c)
            # return HttpResponse(status=204)
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


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('calender:change_password')
        else:
            messages.error(request, 'Please correct the error')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'calender/dashboard_change_password.html', {
        'form': form
    })



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
                address = form.cleaned_data['address']


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
                response = create_appointment(token, user_email, date, time, email_token, name_token, address)
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
                # print(c.str)

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
        if val['ShowAs'] != 'Free':
            eventStart = val['Start']
            eventStartDateTime = dateutil.parser.parse(str(eventStart['DateTime']))
            eventEnd = val['End']
            eventEndDateTime = dateutil.parser.parse(str(eventEnd['DateTime']))
            # print(eventStartDateTime.isoformat())
            while eventStartDateTime <= eventEndDateTime:
                simplifiedTime = eventStartDateTime.strftime("%H:%M")
                # time.append()
                # print(eventStartDateTime.strftime("%H:%M"))
                temp = simplifiedTime.split(":")
                if temp not in time:
                    time.append(temp)
                eventStartDateTime+=datetime.timedelta(minutes=30)


    workingHours = [['9','00'],['9','30'], ['10', '00'], ['10', '30'],['11','00'],['11','30'],['12','00'],['12','30'],['13','00'],['13','30'],['14','00'],['14','30'],['15','00'],['15','30'],['16','00']]

    #logic for only displaying times where clinet has time to get to and from the site vitist
    for slot in workingHours:
        timeObj = timedelta(hours = int(slot[0]), minutes = int(slot[1]))
        time_minus_30 = timeObj - timedelta(minutes=30)
        time_add_30 = timeObj + timedelta(minutes=30)
        time_add_60 = timeObj + timedelta(minutes=60)
        time_add_90 = timeObj + timedelta(minutes=90)

        timesArr =[timeObj + timedelta(minutes=30), timeObj + timedelta(minutes=60), + timeObj+ timedelta(minutes=90)]

        time_minus_30_Str = ':'.join(str(time_minus_30).split(':')[:2])
        time_minus_30_arr = [time_minus_30_Str.split(':')[0],time_minus_30_Str.split(':')[1]]

        time_add_30_Str = ':'.join(str(time_add_30).split(':')[:2])
        time_add_30_arr = [time_add_30_Str.split(':')[0],time_add_30_Str.split(':')[1]]

        time_add_60_Str = ':'.join(str(time_add_60).split(':')[:2])
        time_add_60_arr = [time_add_60_Str.split(':')[0],time_add_60_Str.split(':')[1]]

        time_add_90_Str = ':'.join(str(time_add_90).split(':')[:2])
        time_add_90_arr = [time_add_90_Str.split(':')[0],time_add_90_Str.split(':')[1]]

        if(time_add_30_arr in time or time_add_60_arr in time):
            time.append(slot)
            if(time_minus_30_arr in time or time_add_90_arr in time):
                time.append(slot)
        else:
            continue


    #
    # time = [['9','00'],['9','30']]
    #
    # print(time)
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


