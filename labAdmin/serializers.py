from labAdmin.models import *

from rest_framework import serializers


# class LogdoorSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Logdoor
#         fields = ('id', 'hour', 'user','doorOpened')
#
# class NfcSerializer(serializers.ModelSerializer):
#
#     def get_object(self):
#         try:
#             u = User.objects.get(nfcId=self.nfcId)
#             return u
#         except User.DoesNotExist:
#             return None
#
#     class Meta:
#         model = User
#         fields = ('id','nfcId')
#
# class UserSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = User
#         fields = ('id', 'username','utype', 'signup', 'subscriptionEnd', 'needSubcription', 'nfcId')

class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ("id","user","devicetype","level")


class LogdeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logdevice
        fields = (
            'id'
            ,'user'
            ,'device'
            ,'bootDevice'
            ,'shutdownDevice'
            ,'startWork'
            ,'finishWork'
            ,'hourlyCost'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username','signup')
