from rest_framework.permissions import BasePermission
from rest_framework.authentication import get_authorization_header

from .models import Device


class DeviceTokenPermission(BasePermission):
    def has_permission(self, request, view):
        auth = get_authorization_header(request).split()

        if len(auth) != 2:
            return False

        try:
            token = auth[1].decode()
        except UnicodeError:
            return False

        try:
            Device.objects.get(token=token)
        except Device.DoesNotExist:
            return False

        return True
