from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from labAdmin.serializers import *
from labAdmin.models import *
from labAdmin import functions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from oauth2_provider.models import AccessToken

from labAdmin import functions
# Create your views here.

class LoginByNFC(APIView):
    """
    API For Login (return user informations)
    In order to use this API send a POST with a value named 'nfcId'
    The return value is a json array with user informations

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an error message to client (HTTP_400_BAD_REQUEST)
    """

    def post(self, request, format=None):
        nfc = request.data.get('nfcId')
        u = functions.get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api: Login By NFC - NFC not Valid",code=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        return Response(UserProfileSerializer(u).data, status=status.HTTP_200_OK)

class OpenDoorByNFC(APIView):
    """
    API For Opening the Door with Nfc (return log information)
    In order to use this API send a POST with a value named 'nfcId'
    The return value is a json array with:
        'id': id of user
        'name': name of user
        'utype': type of user ('fablab' or 'other')
        'datetime': datetime objects of the current time
        'open': return if the user can open the door or not

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an alert message to client (HTTP_400_BAD_REQUEST)
    """
    def post(self,request,format=None):
        nfc = request.data.get('nfcId')
        u = functions.get_user_by_nfc_or_None(nfc=nfc)
        if u is None:
            LogError(description="Api: Open Door By NFC - NFC not Valid",code=nfc).save()
            return Response("",status=status.HTTP_400_BAD_REQUEST)
        l=LogAccess(user=u,opened=u.can_open_door_now())
        l.save()
        utype="fablab" if len(Group.objects.filter(user=u,name__icontains='Fablab')) > 0 else "other"

        return Response({"name":u.name,"type":utype,"datetime":l.datetime,"open":l.opened},status=status.HTTP_201_CREATED)

class GetDeviceByMac(APIView):
    """
    API for getting informations about a Device that use a NIC
    In order to use this API send a POST with a value named 'mac'
    The return value is a json array with:
        'id': id of device
        'name': name of device
    These values must be saved on client cache

    If the MAC isn't correct or vaild, the API save in 'LogError' a new error that contains the error then return an alert message to client
    (HTTP_400_BAD_REQUEST)
    """
    def post(self, request, format=None):
        mac = request.data.get("mac")
        d = functions.get_device_by_mac_or_None(mac=mac)

        if d is None:
            LogError(description="Api: Get Device By Mac - Mac not valid",code=mac)
            return Response("",status=status.HTTP_400_BAD_REQUEST)

        return Response({"id":d.id,"name":d.name},status=status.HTTP_200_OK)

class UseDevice(APIView):
    """
    API for insert a new 'LogDevice' object if the user can use the device, else return an alert to client
    In order to use this API send a POST with the following values:
        'deviceId': the id of device
        'userId': the id of user
    """
    def post(self,request,format=None):
        u = functions.get_user_or_None(id=request.data.get('userId'))

        if u is None:
            LogError(description="Api: Use Device - user ID not valid",nfc=request.data.get('userId'))
            return Response("",status=status.HTTP_400_BAD_REQUEST)

        d = functions.get_device_or_None(id=request.data.get('deviceId'))

        if d is None:
            LogError(description="Api: Use Device - device ID not valid",code=request.data.get('deviceId'))
            return Response("",status=status.HTTP_400_BAD_REQUEST)

        if u.can_use_device_now(d):
            # New Object
            try:
                log = LogDevice.objects.filter(device=d,inWorking=True)
                if len(log) > 0:
                    for ll in log:
                        ll.stop()
                        ll.save()

                n = timezone.now()
                newLog = LogDevice(device=d,user=u, startWork=n,bootDevice=n,shutdownDevice=n - timezone.timedelta("-10 seconds"),finishWork=n - timezone.timedelta("-10 seconds"),hourlyCost=d.hourlyCost)
                newLog.save()
                return Response({"logId":n.id,"cost":n.hourlyCost,"canUse":True},status=status.HTTP_201_CREATED)
            except:
                return Response("Error during processing", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            LogError(description="Api: Use Device - the user %d can't use the device %d" % (u.id, d.id))
            return Response("",status=status.HTTP_400_BAD_REQUEST)

class tempUpdateUser(APIView):
    def post(self, request, format=None):
        users = request.data.get('users')

        unk = Group.objects.get(name="Unknown")
        ard = Group.objects.get(name="Arduino")
        fh = Group.objects.get(name="Fablab Host")
        fe = Group.objects.get(name="Fablab Executive")
        fu = Group.objects.get(name="Fablab User")
        e = 0
        ee = 0

        for uu in users:
            n = uu['name']
            nfc = uu['nfc']
            t = uu['type'].title()

            u = UserProfile.objects.get(name=n, nfcId=nfc)
            u.groups.remove(unk)
            if t == 'Arduino':
                u.groups.add(ard)
                u.needSubcription = False
            elif t == 'Ordinario':
                u.groups.add(fu)
                u.needSubcription = True
            elif t == 'Host' or t == 'Full':
                u.groups.add(fh)
                u.needSubcription = True
            elif t == 'Direttivo':
                u.groups.add(fe)
                u.needSubcription = True
            else:
                ee += 1
            u.save()



        return Response("Updated except %d, %d" % (e,ee))

class UserIdentity(APIView):
    def get(self, request, format=None):
        token_string = request.GET.get('access_token')
        now = timezone.now()
        token = get_object_or_404(AccessToken, token=token_string, expires__gt=now, user__isnull=False)
        user = token.user
        if not user.is_active:
            raise Http404

        try:
            up = user.userprofile
        except UserProfile.DoesNotExist:
            up = None

        content = {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
        }

        if up:
            meta = request.META
            if meta['SERVER_PORT'] and meta['SERVER_PORT'] not in ('443', '80'):
                port = ':{}'.format(meta['SERVER_PORT'])
            else:
                port = ''
            base_url = '{}://{}{}'.format(request.scheme, meta['SERVER_NAME'], port)
            groups = up.groups.values_list('name', flat=True)
            content.update({
                'name': up.name,
                'avatar_url': '{}{}'.format(base_url, up.picture.url) if up.picture else '',
                'bio': up.bio or '',
                'groups': groups,
            })
        return Response(content)
