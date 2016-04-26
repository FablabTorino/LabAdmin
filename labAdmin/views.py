from django.http import HttpResponse, Http404

from labAdmin.serializers import *
from labAdmin.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

def get_user_by_nfc_or_None(nfc):
    """
    Function that return the User that has the nfc code passed as parameter else returns None
    """
    try:
        u = User.objects.get(nfcId=nfc)
        return u
    except User.DoesNotExist:
        return None

class LoginByNFC(APIView):
    """
    API For Login (return user informations)
    In order to use this API send a POST with a value named 'nfcId'
    The return value is a json array with user informations

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an error message to client (HTTP_400_BAD_REQUEST)
    """

    def post(self, request, format=None):
        nfc = request.data.get('nfcId')
        u = get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api: Login By NFC - NFC not Valid",nfc=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(u).data, status=status.HTTP_200_OK)

class OpenDoorByNFC(APIView):
    """
    API For Opening the Door with Nfc (return log information)
    In order to use this API send a POST with a value named 'nfcId'
    The return value is a json array with:
        'name': name of user
        'utype': type of user ('fablab' or 'other')
        'datetime': datetime objects of the current time
        'open': return if the user can open the door or not

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an error message to client (HTTP_400_BAD_REQUEST)
    """
    def post(self,request,format=None):
        nfc = request.data.get('nfcId')
        u = get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api:  Open Door By NFC - NFC not Valid",nfc=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        l=LogAccess(user=u,opened=u.can_open_door_now())
        l.save()
        utype="fablab" if len(Group.objects.filter(user=u,name__icontains='Fablab')) > 0 else "other"

        # return Response("{\"name\":\"%s\", \"type\": \"%s\", \"datetime\":\"%s\", \"open\": %s}"%(u.name, utype, l.datetime.strftime("%Y-%m-%dT%H:%M:%S"), "true" if l.opened else "false"),status=status.HTTP_201_CREATED)
        return Response("{\"open\": \"%s\"}"%("true" if l.opened else "false"),status=status.HTTP_201_CREATED)
