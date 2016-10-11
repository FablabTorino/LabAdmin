from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^opendoorbynfc/$', views.OpenDoorByNFC.as_view(), name="open-door-nfc"),
    url(r'^updateUsers/$', views.tempUpdateUser.as_view()),
    url(r'^user/identity/$', views.UserIdentity.as_view()),
    url(r'^nfc/users/$', views.LoginByNFC.as_view(), name='nfc-users'),
    # url(r'^nfc/(?P<nfc>.+)/$', views.NfcLogin.as_view()),
    # url(r'^nfc/', views.NfcLogin.as_view()),
    # url(r'^getpermission/', views.GetPermission.as_view()),
    # url(r'^usedevice/', views.LogdeviceUse.as_view()),
    # url(r'^usedevicelist/', views.LogdeviceUseList.as_view()),
    # url(r'^getToken/', views.GetTokenExample.as_view()),
    # url(r'^users/', views.UserList.as_view()),
    # url(r'^repeat/', views.Repeat.as_view()),
 ]
