from labAdmin.models import Logdoor

from rest_framework import serializers


class LogdoorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logdoor
        fields = ('id', 'hour', 'user','doorOpened')
