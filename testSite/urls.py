"""testSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin

from labAdmin import views

urlpatterns = [
    # url(r'^labAdmin/', include('labAdmin.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^labAdmin/opendoorbynfc/$', views.OpenDoorByNFC.as_view()),
    url(r'^labAdmin/updateUsers/$', views.tempUpdateUser.as_view()),
    # url(r'^nfc/(?P<nfc>.+)/$', views.NfcLogin.as_view()),
    # url(r'^nfc/', views.NfcLogin.as_view()),
    # url(r'^getpermission/', views.GetPermission.as_view()),
    # url(r'^usedevice/', views.LogdeviceUse.as_view()),
    # url(r'^usedevicelist/', views.LogdeviceUseList.as_view()),
    # url(r'^getToken/', views.GetTokenExample.as_view()),
    # url(r'^users/', views.UserList.as_view()),
    # url(r'^repeat/', views.Repeat.as_view()),
]
