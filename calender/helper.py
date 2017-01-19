from calender.models import OutlookAuth
from django.http import Http404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

def getUser(request):
    try:
        # user = OutlookAuth.objects.get(user_email=request.user.email)
        user = OutlookAuth.objects.get(user_email=request.user.email)
        return user
    except OutlookAuth.DoesNotExist:
        raise Http404("error, Registered user email and outlook email do not match contact admin ")

def getUser_by_username(username):
    try:
        user = User.objects.get(username = username)
        oauth_user = OutlookAuth.objects.get(user_email = user.email)
        return oauth_user
    except OutlookAuth.DoesNotExist:
        raise Http404("error, Registered user email and outlook email do not match contact admin ")
