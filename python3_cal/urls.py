"""python3_cal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from calender import views

urlpatterns = [
    # Invoke the home view in the tutorial app by default
    url(r'^$', views.home, name='home'),
    # Defer any URLS to the /tutorial directory to the tutorial app
    url(r'^calendar/', include('calender.urls', namespace='calender')),
    url(r'^admin/', admin.site.urls),
]
