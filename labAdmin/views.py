from django.http import HttpResponse, Http404

from labAdmin.serializers import *
from labAdmin.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def myPrint(string):
    print("\n\n\n\n")
    print(string)
    print("\n\n\n\n")

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

# class LogdoorList(APIView):
#     """
#     List all FabLab Access, or create
#     """
#     def get(self, request, format=None):
#         logdoors = Logdoor.objects.all()
#         serializer = LogdoorSerializer(logdoors, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = LogdoorSerializer(data=request.data)
#         send = {}
#
#         if serializer.is_valid():
#             logdoor = serializer.save()
#             puoAprire = False
#             if logdoor.user.have_permission_now():
#                 logdoor.openDoor()
#                 puoAprire = True
#
#             logdoor.save()
#             return Response({'username': logdoor.user.username,'type':logdoor.user.utype.__str__(), 'hour':logdoor.hour, 'open': puoAprire}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NfcLogin(APIView):
    """
    API For Login with Nfc (return user information)
    """

    def get_object(self, nfc):
        try:
            u = User.objects.get(nfcId=nfc)
            return u
        except User.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        nfc = NfcSerializer(data=request.data)
        if nfc.is_valid():
            u = self.get_object(nfc=nfc.data.get('nfcId'))
            return Response(UserSerializer(u).data, status=status.HTTP_200_OK)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

class LogdoorEnter(APIView):

    def get_user(self, nfc):
        try:
            user = User.objects.get(nfcId=nfc)
            return user
        except User.DoesNotExist:
            return None

    def post(self, request, format=None):
        user = self.get_user(nfc=request.data.get("nfcId"))
        if user is None:
            print("\n\n\n\n\n")
            print("ERRORE NFC")
            print(request.POST.get("nfcId"))
            print("\n\n\n\n\n")
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        canOpen = True if user.have_permission_now() else False
        logdoor=Logdoor(user=user,doorOpened=canOpen)
        logdoor.save()
        return Response({'username': user.username,'hour':logdoor.hour, 'open': canOpen}, status=status.HTTP_201_CREATED)

class GetPermission(APIView):

    def get_device(self, device):
        try:
            return Device.objects.get(pk=device)
        except Device.DoesNotExist:
            return None

    def get_permission(self, devtype, user):
        try:
            return Permission.objects.get(devicetype=devtype, user=user)
        except Permission.DoesNotExist:
            return None

    def post(self, request, format=None):
        device = request.data.get("device")
        user = request.data.get("user")

        device = self.get_device(device=device)

        if device is None:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        perm = self.get_permission(devtype=device.dtype,user=user)

        if perm is None:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        if not perm.user.have_permission_now():
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(PermissionSerializer(perm).data,status=status.HTTP_200_OK)

class LogdeviceUse(APIView):

    def get_device(self, device):
        try:
            return Device.objects.get(pk=device)
        except Device.DoesNotExist:
            return None

    def get_permission(self, devtype, user):
        try:
            return Permission.objects.get(devicetype=devtype, user=user)
        except Permission.DoesNotExist:
            return None

    def post(self, request, format=None):
        device = request.data.get("device")
        user = request.data.get("user")
        bootDevice = request.data.get("bootDevice")
        startWork = request.data.get("startWork")
        finishWork = request.data.get("finishWork")
        shutdownDevice = request.data.get("shutdownDevice")

        device = self.get_device(device)

        if device is None:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


        perm = self.get_permission(devtype=device.dtype,user=user)

        if perm is None or perm.level == 0:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        # if not perm.user.have_permission_now():
        #     return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        logdevice = Logdevice(
            user=perm.user,
            device=device,
            bootDevice=bootDevice,
            startWork=startWork,
            finishWork=finishWork,
            shutdownDevice=shutdownDevice,
            hourlyCost=device.hourlyCost
        )
        logdevice.save()
        return Response({'user':logdevice.user.id,'device':logdevice.device.id,'bootDevice':bootDevice,'startWork':startWork,'finishWork':finishWork,'shutdownDevice':shutdownDevice,'hourlyCost':logdevice.hourlyCost,'username':logdevice.user.username },status=status.HTTP_201_CREATED)


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class LogdeviceUseList(APIView):

    def get(self, request, format=None):
        users = Logdevice.objects.get(pk=1)
        serializer = LogdeviceSerializer(users)
        return Response(serializer.data)

class GetTokenExample(APIView):

    def get(self, request, format=None):
        return Response({"Token":"tokenSTRING"})

class Repeat(APIView):

    def post(self, request, format=None):
        print(request.data);
        return Response(request.data,status=status.HTTP_200_OK);
