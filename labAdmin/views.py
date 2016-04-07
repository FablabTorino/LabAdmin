from django.http import HttpResponse

from labAdmin.serializers import LogdoorSerializer
from labAdmin.models import Logdoor
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

class LogdoorList(APIView):
    """
    List all FabLab Access, or create
    """
    def get(self, request, format=None):
        logdoors = Logdoor.objects.all()
        serializer = LogdoorSerializer(logdoors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = LogdoorSerializer(data=request.data)
        if serializer.is_valid():
            logdoor = serializer.save()
            if logdoor.user.have_permission_now():
                logdoor.openDoor()

            logdoor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
