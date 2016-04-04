from django.db import models
from django.utils import timezone
from django import forms


class User(models.Model):
    username=models.CharField(max_length=200)
    type=models.ForeignKey('Usertype')
    signup=models.DateTimeField("Sign Up Date")
    subscriptionEnd=models.DateTimeField("Subscription End Data")
    needSubcription=models.BooleanField(default=True)
    nfcId=models.IntegerField(null=True)

class Usertype(models.Model):
    name=models.CharField(max_length=200)
    monday=models.BooleanField(default=False)
    tuesday=models.BooleanField(default=False)
    wednesday=models.BooleanField(default=False)
    thursday=models.BooleanField(default=False)
    friday=models.BooleanField(default=False)
    saturday=models.BooleanField(default=False)
    sunday=models.BooleanField(default=False)

    HOUR_CHOICES = (
        (0,0),
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5),
        (6,6),
        (7,7),
        (8,8),
        (9,9),
        (10,10),
        (11,11),
        (12,12),
        (13,13),
        (14,14),
        (15,15),
        (16,16),
        (17,17),
        (18,18),
        (19,19),
        (20,20),
        (21,21),
        (22,22),
        (23,23),
        (24,24)
    )

    hourStart = models.IntegerField(choices=HOUR_CHOICES)
    hourEnd = models.IntegerField(choices=HOUR_CHOICES)
    isAdmin=models.BooleanField(default=False)

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
    hour=models.DateTimeField("Hour of entering in FabLab")
    doorOpened=models.BooleanField(default=False)
    user=models.ForeignKey('User')

class Logdevice(models.Model):
    bootDevice=models.DateTimeField("Boot Device")
    shutdownDevice=models.DateTimeField("Start work")
    startWork=models.DateTimeField("Finish work")
    finishWork=models.DateTimeField("Power Off Device")
    hourlyCost=models.FloatField(null=True)
    user=models.ForeignKey('User')
    device=models.ForeignKey('Device')
