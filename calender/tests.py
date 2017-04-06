from django.test import TestCase
from calender.models import OutlookAuth
from django.contrib.auth.models import AnonymousUser, User


# Create your tests here.

class OutlookAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        OutlookAuth.objects.create(user=self.user, user_email='jacob@…', auth_code='sdfg234567899876fkm', refresh_token='dfghjkldfghjkldfghjk24568efg')

    # def test_outlookauth(self):
