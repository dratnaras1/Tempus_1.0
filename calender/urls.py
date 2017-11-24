####################################################################################################################
# Created by Daniel Ratnaras ITRS Group Ltd
####################################################################################################################

from django.conf.urls import url
from calender import views, token
from django.contrib import admin
from django.contrib.auth import views as auth_views
urlpatterns = [
    # The home view ('/calender/')
    url(r'^$', views.home, name='home'),
    # Redirect to get token ('/calender/gettoken/')
    url(r'^gettoken/$', views.gettoken, name='gettoken'),
    # url(r'^maps/$', views.maps, name='maps'),
    # dashboard view ('/caldender/dashboard')
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # dashboard_appointment view (calender/dashboard/appointment)
    url(r'^dashboard/appointments/$', views.dashboard_appointments, name='dashboardAppointments'),
    # route planner view
    url(r'^dashboard/routeplanner/$', views.dashboard_routePlanner, name='routePlanner'),
    # get booking url
    url(r'^dashboard/bookingurl/$', views.dashboard_bookingUrl, name='dashboardBookingUrl'),
    # change password
    url(r'^dashboard/change_password/$', views.change_password, name='change_password'),
    # generate booking URL
    url(r'^dashboard/generatebookingurl/(?P<name>[\w ]+)/(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$', token.create_token, name='GenerateBookingUrl'),
    # booking by token
    url(r'^booking/(?P<token>[\w.:\-_=]+)$', views.clientBooking_for_token, name='clientBookingToken'),
    #Get avilable Times for appointment booking
    url(r'^getTimes/$', views.getTimes, name='getTimes'),
    # get times for user
    url(r'^getTimes/(?P<token>[\w.:\-_=]+)$', views.getTimes_for_user, name='getTimes_for_user'),
    # get events for dashboard view
    url(r'^getEventsDashboard/$', views.getEventsDashboard, name='getEventsDashboard'),
    # get events for today
    url(r'^getEventsForToday/$', views.get_events_for_today, name='getEventsForToday'),
    # url(r'^login/$', auth_views.login, name='login'),
    url(r'^login/$', auth_views.login, {'template_name':'calender/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),

]


