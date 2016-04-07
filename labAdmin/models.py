from django.db import models
from django.utils import timezone
from django import forms

from django.db import models

# Create your models here.

class User(models.Model):
    username=models.CharField(max_length=200)
    utype=models.ForeignKey('Usertype')
    signup=models.DateTimeField()
    subscriptionEnd=models.DateTimeField()
    needSubcription=models.BooleanField(default=True)
    nfcId=models.IntegerField(default=0)

    def subscription_end(self):
        return self.subscriptionEnd if self.needSubcription else "Don\'t need subcription"

    def have_permission_now(self):
        wdperm_bin = self.utype.weekdays_permission_binary()
        n = timezone.now()
        day_bin = 1 << n.weekday()
        return day_bin & wdperm_bin == day_bin and self.utype.hourStart <= n.time() <= self.utype.hourEnd

    # def openDoor(self):
    #     if self.have_permission_now():
    #         opened = True
    #         # Function For Open The Door
    #     else:
    #         opened = False
    #
    #     l = Logdoor(user=self,doorOpened=opened)
    #     l.save()
    #
    #     return opened

    #
    # Methods For Using Devices
    #
    #
    # def have_permission_for_device(self, dev):
    #     devtype = dev.dtype
    #     try:
    #         pp = Permission.objects.get(user=self, devicetype=devtype)
    #         print(pp)
    #         return pp.level
    #     except Permission.DoesNotExist:
    #         print("Does Not Exist Any Permission Object")
    #         return 0
    #
    # def useDevice(self, dev):
    #     if self.have_permission_now:
    #         if self.haveself.have_permission_for_device(dev):
    #             boot = dev.boot()
    #             workstart = dev.start()
    #             workfinish = dev.end()
    #             shutdown = dev.shutdown()
    #             hcost = dev.hourlyCost
    #
    #             Logdevice(user=user,device=dev, hourlyCost=hcost, bootDevice=boot, shutdownDevice=shutdown, startWork=workstart,finishWork=workfinish).save()
    #
    #             return True
    #         else:
    #             print("You haven\'t the permission for use this kind of devices")
    #             return False
    #     else:
    #         print("You haven\'t the permission for use this kind of devices in this moment")
    #         return False


    def __str__(self):
        return self.username

class Usertype(models.Model):
    name=models.CharField(max_length=200)
    monday=models.BooleanField(default=False)
    tuesday=models.BooleanField(default=False)
    wednesday=models.BooleanField(default=False)
    thursday=models.BooleanField(default=False)
    friday=models.BooleanField(default=False)
    saturday=models.BooleanField(default=False)
    sunday=models.BooleanField(default=False)
    hourStart = models.TimeField()
    hourEnd = models.TimeField()
    isAdmin=models.BooleanField(default=False)

    def weekdays(self):
        ss = ""
        if self.monday:
            ss+="Mon;"
        if self.tuesday:
            ss+="Tue;"
        if self.wednesday:
            ss+="Wed;"
        if self.thursday:
            ss+="Thu;"
        if self.friday:
            ss+="Fri;"
        if self.saturday:
            ss+="Sat;"
        if self.sunday:
            ss+="Sun;"

        return ss if len(ss) > 0 else ""

    def weekdays_permission_binary(self):
        p = 0
        p += 1<<0 if self.monday else 0
        p += 1<<1 if self.tuesday else 0
        p += 1<<2 if self.wednesday else 0
        p += 1<<3 if self.thursday else 0
        p += 1<<4 if self.friday else 0
        p += 1<<5 if self.saturday else 0
        p += 1<<6 if self.sunday else 0

        return p

    def weekdays_permission_binary_str(self):
        return "{0:07b}".format(self.weekdays_permission_binary())

    def __str__(self):
        return self.name

class Device(models.Model):
    name=models.CharField(max_length=200)
    dtype=models.ForeignKey('Devicetype')
    hourlyCost=models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Devicetype(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Permission(models.Model):
    level=models.IntegerField(default=0)
    user=models.ForeignKey('User', null=False)
    devicetype=models.ForeignKey('Devicetype', null=False)

    def __str__(self):
        return "{0} - {1} - Permission Level: {2}".format(self.user,self.devicetype,self.level)

    def changePermissionLevel(self, level):
        self.level = level


class Logdoor(models.Model):
    hour=models.DateTimeField(default=timezone.now)
    doorOpened=models.BooleanField(default=False)
    user=models.ForeignKey('User')

    def wasOpen(self):
        return self.doorOpened

    def openDoor(self):
        self.doorOpened = True

    def closeDoor(self):
        self.doorOpened = False

    def __str__(self):
        return "{0} Enters in Fablab at {1} : {2}".format(self.user, self.hour.strftime("%Y-%m-%d %H:%M:%S"),"Permitted" if self.doorOpened else "Not Permitted")

class Logdevice(models.Model):
    bootDevice=models.DateTimeField()
    shutdownDevice=models.DateTimeField()
    startWork=models.DateTimeField()
    finishWork=models.DateTimeField()
    hourlyCost=models.FloatField(default=0.0)
    user=models.ForeignKey('User')
    device=models.ForeignKey('Device')
