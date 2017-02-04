# from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
# from django.contrib.auth.models import User
# rom django.conf import settings
# from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User
#
# def create_unsubscribe_link(self):
#     User, token = self.make_token().split(":", 1)
#     return reverse('calender.views.unsubscribe',
#                    kwargs={'username': User, 'token': token,})
#
# def make_token(self):
#     return TimestampSigner().sign(self.user.username)
#
# def check_token(self, token):
#     try:
#         key = '%s:%s' % (self.user.username, token)
#         TimestampSigner().unsign(key, max_age=60 * 60 * 48) # Valid for 2 days
#     except (BadSignature, SignatureExpired):
#         return False
#     return True
#
# def _make_token_with_timestamp(self, user, timestamp):
#     # timestamp is number of days since 2001-1-1.  Converted to
#     # base 36, this gives us a 3 digit string until about 2121
#     ts_b36 = int_to_base36(timestamp)
#
#     hash = salted_hmac(
#         self.key_salt,
#         self._make_hash_value(user, timestamp),
#     ).hexdigest()[::2]
#     return "%s-%s" %

from calender.models import OutlookAuth, BookingToken
from calender.models import OutlookAuth
from django.http import Http404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from calender.helper import getUser, getUser_by_username
from django.core.signing import Signer
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

def create_token(request):
    # create a random url that is linked to analyst
    user= getUser(request)
    # make each url unique
    signer = Signer(salt=time.time())
    username_token = signer.sign(request.user)
    username, token = username_token.split(":", 1)
    token_obect = BookingToken(analyst=user, token=token, used=False)
    token_obect.save()
    some_data_to_dump = {
        'token': token
    }
    data = json.dumps(some_data_to_dump)

    return HttpResponse(data, content_type='application/json')
