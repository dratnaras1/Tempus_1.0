from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from calender.authhelper import get_signin_url, get_token_from_code
from calender.outlookservice import get_me
from calender.outlookservice import create_appointment
from calender.authhelper import get_signin_url, get_token_from_code, get_access_token
from calender.outlookservice import get_my_events
from django.shortcuts import render_to_response
from django.template import Context


from .forms import ClientAppointmentForm

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

def events(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('calender:gettoken')))
    user_email = request.session['user_email']
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

def clientBooking(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('calender:gettoken')))
    user_email = request.session['user_email']

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
            if not access_token:
                return HttpResponseRedirect(reverse('calender:home'))
            else:
                response = create_appointment(access_token, user_email, date, time, email, name)
                c =  Context({'status_code' : response})
                return HttpResponse(c)
                # return (request, 'calender/createEvents.html', c)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClientAppointmentForm()

    return render(request, 'calender/client_booking.html', {'form': form})