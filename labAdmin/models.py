from django.db import models
from django.utils import timezone
from django import forms

from django.db import models

# Create your models here.

# User Model
class User(models.Model):
    username=models.CharField(max_length=200)
    utype=models.ForeignKey('Usertype')
    signup=models.DateTimeField() # DataTime value: It means when the user sign up the first time
    subscriptionEnd=models.DateTimeField()
    needSubcription=models.BooleanField(default=True) # Booelan value: TRUE --> user need a subcription, FALSE --> user have unlimited subcription
    nfcId=models.IntegerField(default=0) # Integer value. It contains the NFC Code that must be unique
    # It is possible add fields such as 'Email' and 'Phone Number'


    # Function that returns a string that contains when the current subcription end or "Don't need subscription"
    def subscription_end(self):
        return self.subscriptionEnd if self.needSubcription else "Don\'t need subcription"

    # Function that returns a boolean that means if the current subscription is expired (for unlimited subcription returns always FALSE)
    def subscriptionExpired(self):
        return self.subscriptionEnd < timezone.now() and self.needSubcription

    # Function that returns a boolean that means if a user have the permission to enter into Fablab/to use devices (not check if the subcriptions is expired)
    def have_permission_now(self):
        wdperm_bin = self.utype.weekdays_permission_binary()
        n = timezone.now()
        day_bin = 1 << n.weekday()
        return day_bin & wdperm_bin == day_bin and self.utype.hourStart <= n.time() <= self.utype.hourEnd

    # Convert the user objects to string --> Format: username
    def __str__(self):
        return self.username

# User type model
class Usertype(models.Model):
    name=models.CharField(max_length=200)
    # Booleans that mean if these users have the permission to enter in fablab for any day of week
    monday=models.BooleanField(default=False)
    tuesday=models.BooleanField(default=False)
    wednesday=models.BooleanField(default=False)
    thursday=models.BooleanField(default=False)
    friday=models.BooleanField(default=False)
    saturday=models.BooleanField(default=False)
    sunday=models.BooleanField(default=False)
    # Times that mean when these users can enter in fablab
    hourStart = models.TimeField()
    hourEnd = models.TimeField()
    # Boolean that means if users are administrators or not
    isAdmin=models.BooleanField(default=False)

    # Convert day booleans to string
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

    # Function that convert day booleans to 7 bits number (used for check permissions)
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

    # Convert the previous function to binary string
    def weekdays_permission_binary_str(self):
        return "{0:07b}".format(self.weekdays_permission_binary())

    # Convert the user type objects to string --> Format: name
    def __str__(self):
        return self.name

# Device model
class Device(models.Model):
    name=models.CharField(max_length=200)
    dtype=models.ForeignKey('Devicetype')
    # Float number that means how much costs use the device hourly
    hourlyCost=models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Devicetype(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Permission model
class Permission(models.Model):
    # Integer Value that means the level of permission for a user for a device type
    # 0 --> No Permission
    # 1 --> Have Permission
    level=models.IntegerField(default=0)
    user=models.ForeignKey('User', null=False)
    devicetype=models.ForeignKey('Devicetype', null=False)

    def __str__(self):
        return "{0} - {1} - Permission Level: {2}".format(self.user,self.devicetype,self.level)

    # Function that change a permission for a user
    def changePermissionLevel(self, level):
        self.level = level
        self.save()

# Logdoor model
class Logdoor(models.Model):
    # DateTime Value that means when the user try entering in fablab
    hour=models.DateTimeField(default=timezone.now)
    # Boolean that means if a user entered in fablab or not
    doorOpened=models.BooleanField(default=False)
    user=models.ForeignKey('User')

    # Function that return a boolean that mean if a user entered or not
    def wasOpen(self):
        return self.doorOpened

    # Functions for change status of the log
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
