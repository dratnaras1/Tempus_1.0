from django.test import TestCase
from calender.models import OutlookAuth
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
import requests
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from calender.views import dashboard
from django.test import Client

# Create your tests here.
class BookingTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='daniel_itrs@oulook.com', email='daniel_itrs@oulook.com', password='top_secret')

    def test_getTimes(self):
        client = Client()
        a = OutlookAuth.objects.create(user=self.user, user_email='daniel_itrs@oulook.com', auth_code='Mf7c7db8b-ed77-2f42-9aa3-c48495c9c4d0', refresh_token='MCfIFDcS6ON58PQ7GKI0cJPIBZ*wATpbvGbxCbEWTXVGAVPNq73xeOHkxW2njNs3hbodjbhghVxQzzPpu4HpAzwLnMJxMNRPZ6e*axNlS9txSLVNx8QChQKBBKcNbv1BBc32uXg!erGqeE11INpPvYaXcdtBFDNaPl!RomEz*RcWacBL!kAvWoEBfIPQNxUox05680XSH6PDyJ7PkMPpGXhknPWtIdH0xrPpmSzaep5nAD1vxZTQ!VE4URHCTWedxqfyTp7PUxQpBrPmwn*KsUXQfjiM0nk318X9eDFkZVYsXddIa7tl0LVjV6WV5dIaCcc1MTFpFumYsyKeTBE1zjpJdj62EliC1t7fBe74kI4wyexoW4m8*rNlgqSKxBF!ex0ZZUXs9A8*LgUG*UKzGDquKehU9sbbB1RrVWq14nqJ!vKJZMsV5*pYTeDKfEXvdArjWNk!smV6AxLV7rdF56P*STbsetjwlICo0968ajSKgla0M7twtNZ9ytH43yGhAjw$$')
        a.save()

        response1 = client.get('/calendar/login/')
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, 'csrfmiddlewaretoken')

        loggedin = self.client.login(username='daniel_itrs@oulook.com', password='top_secret' )

        response = self.client.get('/calendar/dashboard/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/calendar/getTimes/', {'selectedDate':'02-03-2016',
                                                           'auth_code':'Mf7c7db8b-ed77-2f42-9aa3-c48495c9c4d0'})
        self.assertEqual(response.status_code, 200)

        response = client.post('/calendar/login/', {'username': 'daniel_itrs@oulook.com', 'password': 'top_secret'}, follow=True)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.context['user'].is_active)
        response = self.client.get('/calendar/dashboard/')
        self.assertEqual(response.status_code, 200)

        # print(response.status_code)
        # print(response.content)


        # # get csrf token
        # body1 = response1.content.decode('utf-8')
        # token = int(body1.split('csrfmiddlewaretokem',body1)[1].split('\'')[2])
        # query = { 'csrfmiddlewaretoken' : token,
        #           'username' : 'daniel_itrs@oulook.com',
        #           'password' : 'top_secret',
        #
        # }
        # response2 = client.post('/calendar/login/',query)
        # self.assertEqual(response2.status_code, 200)

        # response = self.client.get('/calendar/getTimes/', {'selectedDate':'02-03-2016'})
        # print('hello')
        # print(response.context)
        # self.assertEqual(response.context, ['time'])

class AuthenticationTestCase(TestCase):
    def test_login_required(self):
        # test dashboard
        response = self.client.get('/calendar/dashboard/')
        self.assertEqual(response.status_code, 302)
        # booking url
        response = self.client.get('/calendar/dashboard/bookingurl/')
        self.assertEqual(response.status_code, 302)
        # route planner
        response = self.client.get('/calendar/dashboard/routeplanner/')
        self.assertEqual(response.status_code, 302)
        # appointments
        response = self.client.get('/calendar/dashboard/appointments/')
        self.assertEqual(response.status_code, 302)
        # password change
        response = self.client.get('/calendar/dashboard/change_password/')
        self.assertEqual(response.status_code, 302)


