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
        nfc = request.data.get('nfcId')
        u = get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api:  Open Door By NFC - NFC not Valid",nfc=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        l=LogAccess(user=u,opened=u.can_open_door_now())
        l.save()
        utype="fablab" if len(Group.objects.filter(group__user=u,name__icontains='Fablab')) > 0 else "other"

        return Response("{\"name\":\"%s\", \"type\": \"%s\", \"datetime\":%s, \"open\": %s}"%(u.name, utype, l.datetime, l.opened),status=status.HTTP_201_CREATED)


class UserAddScript(APIView):

    def post(self, request, format=None):
        users = request.data.get("users")
        t = timezone.now()
        g = Group.objects.get(pk=4)
        i = 0
        k = 0
        for u in users:
            k += 1
            try:
                tmp = User.objects.get(name=u["name"].title(),nfcId=u["nfcId"])
            except User.DoesNotExist:
                i +=  1
                tmp = User(name=u["name"].title(),nfcId=u["nfcId"], lastSignup=t,firstSignup=t,endSubcription="2016-12-31")
                tmp.save()
                tmp.groups.add(g)
                tmp.save()



        return HttpResponse("%d su %d" %(i,k))
