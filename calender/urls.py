from django.conf.urls import url
from calender import views

urlpatterns = [
    # The home view ('/calender/')
    url(r'^$', views.home, name='home'),
    # Explicit home ('/calender/home/')
    url(r'^home/$', views.home, name='home'),
    # Redirect to get token ('/calender/gettoken/')
    url(r'^gettoken/$', views.gettoken, name='gettoken'),
    # Redirect to get temporary token ('/calender/gettoken/')
    url(r'^gettemptoken/$', views.gettempttoken, name='gettemptoken'),
    # Events view ('/calender/events/')
    url(r'^events/$', views.events, name='events'),
    # url(r'^maps/$', views.maps, name='maps'),
    # Create Event ('/calender/CreateEvent/')
    url(r'^CreateEvent/$', views.create_event_view, name='createEvent'),
    #  schedule view ('/calender/schedule/')
    url(r'^schedule/$', views.schedule, name='schedule'),
    # dashboard view ('/caldender/dashboard')
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # client booking view ('/caldender/booking')
    # url(r'^booking/$', views.clientBooking, name='clientBooking')
    url(r'^booking/$', views.clientBooking, name='clientBooking')
]

