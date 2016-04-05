from django.db import models
from django.utils import timezone
from django import forms



class User(models.Model):
    username=models.CharField(max_length=200)
    type=models.ForeignKey('Usertype')
    signup=models.DateTimeField()
    subscriptionEnd=models.DateTimeField()
    needSubcription=models.BooleanField(default=True)
    nfcId=models.IntegerField(default=0)

    def subscription_end(self):
        return self.subscriptionEnd if self.needSubcription else "Don\'t need subcription"

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

    def havePermission(self):
        wdperm_bin = self.weekdays_permission_binary()
        n = timezone.now()
        day_bin = 1 << n.weekday()
        return True if day_bin & wdperm_bin == day_bin and self.hourStart <= n.time() <= self.hourEnd else False

    def __str__(self):
        return self.name

class Device(models.Model):
    name=models.CharField(max_length=200)
    type=models.ForeignKey('Devicetype')

class Devicetype(models.Model):
        name=models.CharField(max_length=200)

class Permission(models.Model):
        level=models.IntegerField(default=0),
        user=models.ForeignKey('User'),
        devicetype=models.ForeignKey('Devicetype')

class Logdoor(models.Model):
    hour=models.DateTimeField()
    doorOpened=models.BooleanField(default=False)
    user=models.ForeignKey('User')

class Logdevice(models.Model):
    bootDevice=models.DateTimeField()
    shutdownDevice=models.DateTimeField()
    startWork=models.DateTimeField()
    finishWork=models.DateTimeField()
    hourlyCost=models.FloatField(default=0.0)
    user=models.ForeignKey('User')
    device=models.ForeignKey('Device')
