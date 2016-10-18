from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from labAdmin.serializers import *
from labAdmin.models import *
from labAdmin import functions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from oauth2_provider.models import AccessToken

from labAdmin import functions

from .permissions import DeviceTokenPermission


class LoginByNFC(APIView):
    """
    API For Login (return user informations)
    In order to use this API send a POST with a value named 'nfc_id'
    The return value is a json array with users associated to the card

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an error message to client (HTTP_400_BAD_REQUEST)
    """

    def post(self, request, format=None):
        nfc = request.data.get('nfc_id')
        users = UserProfile.objects.filter(card__nfc_id=nfc)
        if not users.exists():
            LogError(description="Api: Login By NFC - NFC not Valid", code=nfc).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        return Response(UserProfileSerializer(users, many=True).data, status=status.HTTP_200_OK)

class OpenDoorByNFC(APIView):
    """
    API For Opening the Door with Nfc (return log information)
    In order to use this API send a POST with a value named 'nfc_id'
    The return value is a json array with:
        'users': an object with 'id' and 'name' of users
        'utype': 'fablab' if there's a user in the 'Fablab'group or 'other'
        'datetime': datetime objects of the current time
        'open': return if the user can open the door or not

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an alert message to client (HTTP_400_BAD_REQUEST)
    """
    def post(self, request, format=None):
        nfc = request.data.get('nfc_id')
        users = UserProfile.objects.filter(card__nfc_id=nfc)
        if not users.exists():
            LogError(description="Api: Open Door By NFC - NFC not Valid", code=nfc).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        can_open = False
        for u in users:
           if u.can_open_door_now():
               can_open = True
               break
        card = users.first().card
        log_access = LogAccess.objects.log(users=users, card=card, opened=can_open)
        users_pks = users.values_list('pk', flat=True)
        if Group.objects.filter(userprofile__in=users_pks, name__icontains='Fablab').exists():
            utype = "fablab"
        else:
            utype = "other"

        data = {
            "users": UserProfileSerializer(users, many=True).data,
            "type": utype,
            "datetime": log_access.datetime,
            "open": log_access.opened
        }
        return Response(data, status=status.HTTP_201_CREATED)

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

class CardCredits(APIView):
    """
    API for getting card credits
    In order to use this API send a GET with:
    - 'nfc_id', to identifiy the card

    The return value is a json array with the nfc_id and the credits amount for the card.

    If the nfc code isn't valid a 'LogError' instance is saved and returns 400 status code
    """

    permission_classes = (DeviceTokenPermission,)

    def get(self, request, format=None):
        nfc = request.query_params.get('nfc_id')
        try:
            card = Card.objects.get(nfc_id=nfc)
        except Card.DoesNotExist:
            LogError(description="Api: Update Card Credits - NFC not Valid", code=nfc or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        return Response(CardSerializer(card).data, status=status.HTTP_200_OK)

    """
    API for updating card credits
    In order to use this API send a POST with:
    - 'nfc_id', to identifiy the card
    - 'amount', integer to add to credit amount

    The return value is a json array with the nfc_id and new credits amount for the card.

    The amount must be negative and if there's not enough credits it'll returns 403 status code
    If the amount or the nfc code isn't valid a 'LogError' instance is saved and status code 400 returned
    """
    def post(self, request, format=None):
        serializer = CardUpdateSerializer(data=request.data)
        nfc = serializer.initial_data.get('nfc_id')
        if not serializer.is_valid():
            LogError(description="Api: Update Card Credits - Invalid data", code=nfc or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        try:
            # avoid race conditions updating the card model
            with transaction.atomic():
                try:
                    card = Card.objects.get(nfc_id=nfc)
                except Card.DoesNotExist:
                    LogError(description="Api: Update Card Credits - NFC not Valid", code=nfc).save()
                    return Response("", status=status.HTTP_400_BAD_REQUEST)

                amount = serializer.data['amount']
                if amount >= 0:
                    msg = "Api: Update Card Credits - amount can only be negative: {}".format(
                        amount
                    )
                    LogError(description=msg, code=nfc).save()
                    return Response("", status=status.HTTP_400_BAD_REQUEST)

                new_amount = card.credits + amount
                if new_amount < 0:
                    msg = "Api: Update Card Credits - Not enough credits: requested {} of {} available".format(
                        amount, card.credits
                    )
                    LogError(description=msg, code=nfc).save()
                    return Response("", status=status.HTTP_403_FORBIDDEN)

                # update the card with the new credits amount
                card.credits = new_amount
                card.save(update_fields=['credits'])
                user = request.user if request.user.is_authenticated() else None
                card.log_credits_update(amount=amount, user=user)

        except IntegrityError:
            LogError(description="Api: Update Card Credits - IntegrityError", code=nfc).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        return Response(CardSerializer(card).data, status=status.HTTP_200_OK)
