from calender.models import OutlookAuth, BookingToken
from calender.models import OutlookAuth
from django.http import Http404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from calender.helper import getUser, getUser_by_username
from calender.forms import BookingLinkGeneratorForm
from django.core.signing import Signer
from django.core import signing
import time
from django.http import HttpResponse, HttpResponseRedirect
import json

def check_token_valid(token):
    try:
        token_used = BookingToken.objects.get(token=token)
        if token_used.used:
            return False
        else:
            return True
    except ObjectDoesNotExist:
        raise Http404("bad url")

def get_user_from_token(token):
    try:
        token_used = BookingToken.objects.get(token=token)
        user = OutlookAuth()
        user= token_used.analyst
        return user
    except ObjectDoesNotExist:
        raise Http404("error")

# def create_token(request):
#     # create a random url that is linked to analyst
#     user= getUser(request)
#     # make each url unique
#     signer = Signer(salt=time.time())
#     username_token = signer.sign(request.user)
#     username, token = username_token.split(":", 1)
#     token_obect = BookingToken(analyst=user, token=token, used=False)
#     token_obect.save()
#     some_data_to_dump = {
#         'token': token
#     }
#     data = json.dumps(some_data_to_dump)
#
#     return HttpResponse(data, content_type='application/json')

def create_token(request, name, email):
    # create a random url that is linked to analyst
    user= getUser(request)
    # dump = str(request.user)+"^"+name+"^"+email
    # print(dump)
    # make each url unique
    signer = Signer(salt=time.time())
    key_token = signer.sign(request.user)
    key, token = key_token.split(":", 1)
    # print(token)
    token_obect = BookingToken(clientName = name, clientEmail = email, analyst=user, token=token, used=False)
    token_obect.save()
    some_data_to_dump = {
        'token': token
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')



def create_token_str_not_saved_in_db(request):

    # make each url unique
    signer = Signer(salt=time.time())
    username_token = signer.sign(request.user)
    username, token = username_token.split(":", 1)
    return token

def add_token_to_db(user, token, name, email):
    user = getUser_by_username(user)
    token_obect = BookingToken(clientName = name, clientEmail = email, analyst=user, token=token, used=False)
    token_obect.save()

def get_clientName_from_token(token):
    token_object = BookingToken.objects.get(token=token)
    return token_object.clientName

def get_clientEmail_from_token(token):
    token_object = BookingToken.objects.get(token=token)
    return token_object.clientEmail