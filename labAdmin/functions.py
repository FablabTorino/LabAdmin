from labAdmin.models import *

def get_user_by_nfc_or_None(nfc):
    """
    Function that return the User that has the nfc code passed as parameter else returns None
    """
    try:
        u = User.objects.get(nfcId=nfc)
        return u
    except User.DoesNotExist:
        return None

def get_user_or_None(id):
    """
    Function that return the User that has the id passed as parameter else returns None
    """
    try:
        u = User.objects.get(id=id)
        return u
    except User.DoesNotExist:
        return None

def get_device_by_mac_or_None(mac):
    """
    Function that return the Device that has the mac passed as parameter else returns None
    """
    try:
        d = Device.objects.get(mac=mac)
        return d
    except Device.DoesNotExist:
        return None

def get_device_or_None(id):
    """
    Function that return the Device that has the id passed as parameter else returns None
    """
    try:
        d = Device.objects.get(id=id)
        return d
    except Device.DoesNotExist:
        return None
