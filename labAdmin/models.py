from django.db import models
from django.utils import timezone

# Create your models here.

class TimeSlot(models.Model):
    WEEKDAY_CHOICES = (
        (1,'Monday'),
        (2,'Tuesday'),
        (3,'Wednesday'),
        (4,'Thursday'),
        (5,'Friday'),
        (6,'Saturday'),
        (7,'Sunday')
    )
    name=models.CharField(max_length=50)
    weekday_start=models.SmallIntegerField(default=0, choices=WEEKDAY_CHOICES)
    weekday_end=models.SmallIntegerField(default=0, choices=WEEKDAY_CHOICES)
    hour_start=models.TimeField()
    hour_end=models.TimeField()

    def have_permission_now(self):
        n = timezone.now()
        return self.weekday_start <= n.weekday <= self.weekday_end and self.hour_start <= n.time <= self.hour_end

    def __str__(self):
        return "%s: %s - %s, %s - %s"%(self.name, self.WEEKDAY_CHOICES[self.weekday_start-1][1],self.WEEKDAY_CHOICES[self.weekday_end-1][1],self.hour_start,self.hour_end)

class User(models.Model):
    name=models.CharField(max_length=200)
    firstSignup = models.DateField()
    lastSignup = models.DateField()
    endSubcription = models.DateField()
    needSubcription = models.BooleanField(default=True)
    nfcId=models.BigIntegerField(unique=True, null=True)

    # define Many-To-Many fields
    groups=models.ManyToManyField('Group')

    def subscription_end(self):
        return self.endSubcription if self.needSubcription else "Subcription not needed"

    def subscriptionExpired(self):
        return self.needSubcription and self.endSubcription < timezone.now()

    def can_open_door_now(self):
        # Define groups and role
        n = timezone.now()
        return len(TimeSlot.objects.filter(role__group__user=self,roles__role_kind=0,roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def can_use_device_now(self, device):
        n = timezone.now()
        return len(TimeSlot.objects.filter(role__group__user=self,roles__role_kind=1, role__category_device=device.category_device, roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def __str__(self):
        return self.name

class Category_Device(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return "%s"%(self.name)

class Group(models.Model):
    name=models.CharField(max_length=50)
    # define Many-To-Many fields
    roles=models.ManyToManyField('Role')


    def can_open_door_now(self):
        # Define groups and role
        n = timezone.now()
        return len(TimeSlot.objects.filter(role__group=self,roles__role_kind=0,roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def can_use_device_now(self, device):
        n = timezone.now()
        return len(TimeSlot.objects.filter(role__group=self,roles__role_kind=1, role__category_device=device.category_device, roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def __str__(self):
        return "%s" % (self.name)

class Role(models.Model):
    # define role kind choices
    ROLE_KIND_CHOICES = (
        (0, "Door Access"),
        (1, "Use Device"),
    )

    name=models.CharField(max_length=50)

    # weekday=models.Week
    role_kind=models.IntegerField(choices=ROLE_KIND_CHOICES)
    time_slots=models.ManyToManyField(TimeSlot)
    valid=models.BooleanField(default=True)

    # define Many-To-Many Fieds
    category_devices=models.ManyToManyField('Category_Device',blank=True)

    def can_open_door_now(self):
        # Define groups and role
        n = timezone.now()
        return len(TimeSlot.objects.filter(role=self, roles__role_kind=0,roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def can_use_device_now(self, device):
        n = timezone.now()
        return len(TimeSlot.objects.filter(role=self, roles__role_kind=1, role__category_device=device.category_device, roles__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.weekday(),weekday_end__gte=n.weekday())) > 0

    def __str__(self):
        return "%s - %s" % (self.name, self.ROLE_KIND_CHOICES[self.role_kind][1])

class Device(models.Model):
    name=models.CharField(max_length=100)
    hourlyCost=models.FloatField(default=0.0)
    category_device=models.ForeignKey('Category_Device')

    def __str__(self):
        return "%010d - %s" %(self.id, self.name)

class Payment(models.Model):
    date = models.DateField(default=timezone.now().today)
    value=models.FloatField(default=0.0)
    user=models.ForeignKey(User)


class LogError(models.Model):
    description=models.CharField(max_length=200)
    nfc=models.IntegerField(default='',blank=True)

# Relations
class LogAccess(models.Model):
    datetime=models.DateTimeField(default=timezone.now)
    user=models.ForeignKey('User')
    opened=models.BooleanField(default=False)

    def __str__(self):
        return "%s Enter in Fablab it %s: Enter %sPermitted" %(self.user, self.datetime, "Not " if not self.opened else "")

class LogDevice(models.Model):
    hourlyCost=models.FloatField(default=0.0)
    user=models.ForeignKey('User')
    device=models.ForeignKey('Device')
    bootDevice=models.DateTimeField()
    startWork=models.DateTimeField()
    finishWork=models.DateTimeField()
    shutdownDevice=models.DateTimeField()
    inWorking=models.BooleanField(default=True)

    def __str__(self):
        return "user: %s\ndevice: %s\nboot: %s\nstart: %s\ninWorking: %s\nHourlyCost: %f" %(self.user, self.device, self.bootDevice, self.startWork, "yes" if self.inWorking else "no\nshutdown: %s\nfinish: %s"%(self.shutdownDevice, self.finishWork), self.hourlyCost)
