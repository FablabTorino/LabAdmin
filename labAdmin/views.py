from django.http import HttpResponse, Http404

from labAdmin.serializers import *
from labAdmin.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

def get_user_by_nfc_or_None(nfc):
    try:
        u = User.objects.get(nfcId=nfc)
        return u
    except User.DoesNotExist:
        return None

class LoginByNFC(APIView):
    """
    API For Login with Nfc (return user information)
    """

    def post(self, request, format=None):
        nfc = request.data.get('nfcId', 'Login')
        u = get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api: Login By NFC - NFC not Valid",nfc=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(u).data, status=status.HTTP_200_OK)

class OpenDoorByNFC(APIView):
    """
    API For Opend Door with Nfc (return log information)
    """
    def post(self,request,format=None):
        print("POST REQUEST")
        nfc = request.data.get('nfcId','OpenDoorByNFC')
        u = get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api:  Open Door By NFC - NFC not Valid",nfc=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        l=LogAccess(user=u,opened=u.can_open_door_now())
        l.save()
        utype="other"
        for g in u.groups.all():
            if g.name.lower().find('fablab'):
                utype = 'fablab'
                break
        print("{\"name\":\"%s\", \"type\": \"%s\", \"datetime\":%s, \"open\": %s}"%(u.name, utype, l.datetime, l.opened))
        return Response("{\"name\":\"%s\", \"type\": \"%s\", \"datetime\":%s, \"open\": %s}"%(u.name, utype, l.datetime, l.opened),status=status.HTTP_201_CREATED)
