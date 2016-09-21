from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import decimal

# Create your models here.

class TimeSlot(models.Model):
    """
    TimeSlots are assigned to Roles
    """
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

class UserProfile(models.Model):
    """
    The User Profile
    """
    user=models.OneToOneField(User)

    name=models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    tax_code = models.CharField(max_length=50, null=True, blank=True)
    vat_id = models.CharField(max_length=50, null=True, blank=True)
    picture = models.ImageField(upload_to="labadmin/users/pictures", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    firstSignup = models.DateField()
    lastSignup = models.DateField()
    endSubscription = models.DateField()
    needSubscription = models.BooleanField(default=True)
    nfcId=models.BigIntegerField(unique=True, null=True)

    # define Many-To-Many fields
    groups=models.ManyToManyField('Group')

    def subscription_end(self):
        return self.endSubscription if self.needSubcription else "Subcription not needed"

    def subscriptionExpired(self):
        return self.needSubcription and self.endSubscription < timezone.now()

    def can_open_door_now(self):
        # Define groups and role
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role__group__user=self,role__role_kind=0,role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception Return False
            return False

    def can_use_device_now(self, device):
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role__group__user=self,role__role_kind=1, role__category_device=device.category_device, role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception Return False
            return False

    def displaygroups(self):
        data = []
        for g in self.groups.all():
            data.append(g.name)
        return ",".join(data)

    def __str__(self):
        return self.name

class Category(models.Model):
    name=models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return "%s"%(self.name)

class Group(models.Model):
    name=models.CharField(max_length=50)
    # define Many-To-Many fields
    roles=models.ManyToManyField('Role')

    def can_open_door_now(self):
        # Define groups and role
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role__group=self,role__role_kind=0,role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception return False
            return False

    def can_use_device_now(self, device):
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role__group=self,role__role_kind=1, role__category_device=device.category_device, role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception return False
            return False

    def __str__(self):
        return "%s" % (self.name)

class Role(models.Model):
    # define role kind choices
    ROLE_KIND_CHOICES = (
        (0, "Door Access"),
        (1, "Use Device"),
    )

    name=models.CharField(max_length=50)

    role_kind=models.IntegerField(choices=ROLE_KIND_CHOICES)
    time_slots=models.ManyToManyField(TimeSlot)
    valid=models.BooleanField(default=True)

    # define Many-To-Many Fieds
    categories=models.ManyToManyField('Category',blank=True)

    def can_open_door_now(self):
        # Define groups and role
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role=self, role__role_kind=0,role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception return False
            return False

    def can_use_device_now(self, device):
        try:
            n = timezone.now()
            return len(TimeSlot.objects.filter(role=self, role__role_kind=1, role__category_device=device.category_device, role__valid=True,hour_start__lte=n.time(),hour_end__gte=n.time(),weekday_start__lte=n.isoweekday(),weekday_end__gte=n.isoweekday())) > 0
        except:
            # Any Exception Return False
            return False

    def __str__(self):
        return "%s - %s" % (self.name, self.ROLE_KIND_CHOICES[self.role_kind][1])

class Device(models.Model):
    name=models.CharField(max_length=100)
    hourlyCost=models.FloatField(default=0.0)
    category=models.ForeignKey('Category')
    mac=models.CharField(max_length=30)

    def __str__(self):
        return "%010d - %s" %(self.id, self.name)

class Payment(models.Model):
    date = models.DateField(default=timezone.now().today)
    value=models.FloatField(default=0.0)
    user=models.ForeignKey(UserProfile)

class LogError(models.Model):
    datetime = models.DateTimeField(default=timezone.now)
    description=models.CharField(max_length=200)
    code=models.CharField(default='',blank=True,max_length=200)

# Relations
class LogAccess(models.Model):
    datetime=models.DateTimeField(default=timezone.now)
    user=models.ForeignKey('UserProfile')
    opened=models.BooleanField(default=False)

    def __str__(self):
        return "%s Enter in Fablab it %s: Enter %sPermitted" %(self.user, self.datetime, "Not " if not self.opened else "")

class LogDevice(models.Model):
    hourlyCost=models.FloatField(default=0.0)
    user=models.ForeignKey('UserProfile')
    device=models.ForeignKey('Device')
    bootDevice=models.DateTimeField()
    startWork=models.DateTimeField()
    finishWork=models.DateTimeField()
    shutdownDevice=models.DateTimeField()
    inWorking=models.BooleanField(default=True)

    def priceWork(self):
        c = (finishWork-startWork)
        duration = 0.01*decimal.Decimal((c.days*24+c.seconds/3600)*100)
        return 'inWorking...' if self.inWorking else self.hourlyCost*duration

    def stop(self):
        n = timezone.now()
        self.finishWork = self.shutdownDevice = n

    def __str__(self):
        return "user: %s\ndevice: %s\nboot: %s\nstart: %s\ninWorking: %s\nHourlyCost: %f" %(self.user, self.device, self.bootDevice, self.startWork, "yes" if self.inWorking else "no\nshutdown: %s\nfinish: %s"%(self.shutdownDevice, self.finishWork), self.hourlyCost)
