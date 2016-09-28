from django.conf.urls import url
from calender import views

urlpatterns = [
    # The home view ('/calender/')
    url(r'^$', views.home, name='home'),
    # Explicit home ('/calender/home/')
    url(r'^home/$', views.home, name='home'),
    # Redirect to get token ('/calender/gettoken/')
    url(r'^gettoken/$', views.gettoken, name='gettoken'),
    # Events view ('/tutorial/events/')
    url(r'^events/$', views.events, name='events'),
    # url(r'^maps/$', views.maps, name='maps'),

]