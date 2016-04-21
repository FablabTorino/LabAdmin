from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
    name=models.CharField(max_length=200)
    firstSignup = models.DateField()
    lastSignup = models.DateField()
    endSubcription = models.DateField()
    needSubcription = models.BooleanField(default=True)
    nfcId=models.IntegerField(unique=True, null=True)

    # define Many-To-Many fields
    groups=models.ManyToManyField('Group')

    def subscription_end(self):
        return self.endSubcription if self.needSubcription else "Subcription not needed"

    def subscriptionExpired(self):
        return self.needSubcription and self.endSubcription < timezone.now()

    # def listRoles(self):
    #     rr = Role.objects.filter(group__user=self,role_kind=0,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
    #     if rr == True:
    #         print(len(rr))
    #     else:
    #         print("VUOTO")
    #     print(len(rr))
    #
    #     print("\nEND\n")


    def can_open_door_now(self):
        # Define groups and role
        rr = Role.objects.filter(group__user=self,role_kind=0,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
        for r in rr:
            if r.can_open_door_now():
                return True
        return False

    def can_use_device_now(self, device):
        rr = Role.objects.filter(role_kind=1, category_device=device.category_device,group__user=self,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
        for r in rr:
            if r.can_use_device_now():
                return True
        return False

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


    # def listRoles(self):
    #     rr = Role.objects.filter(group=self,role_kind=0,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
    #     if rr == True:
    #         print(len(rr))
    #     else:
    #         print("VUOTO")
    #
    #     print("\nEND\n")

    def can_open_door_now(self):
        rr = Role.objects.filter(group=self,role_kind=0,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
        for r in rr:
            if r.can_open_door_now():
                return True
        return False

    def can_use_device_now(self, device):
        rr = Role.objects.filter(role_kind=1, category_device=device.category_device,group__user=self,valid=True,hour_start__lte=timezone.now(),hour_end__gte=timezone.now())
        for r in rr:
            if r.can_open_door_now():
                return True
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
    hour_start=models.TimeField()
    hour_end=models.TimeField()
    monday=models.BooleanField(default=False)
    tuesday=models.BooleanField(default=False)
    wednesday=models.BooleanField(default=False)
    thursday=models.BooleanField(default=False)
    friday=models.BooleanField(default=False)
    saturday=models.BooleanField(default=False)
    sunday=models.BooleanField(default=False)
    # weekday=models.Week
    role_kind=models.IntegerField(choices=ROLE_KIND_CHOICES)
    valid=models.BooleanField(default=True)

    # define Many-To-Many Fieds
    category_devices=models.ManyToManyField('Category_Device',blank=True)

    def can_open_door_now(self):
        if self.role_kind == 0:
            now=timezone.now()
            day=now.weekday()
            hour=now.time()

            if day == 1:
                daypermission=self.monday
            elif day==2:
                daypermission=self.tuesday
            elif day==3:
                daypermission=self.wednesday
            elif day==4:
                daypermission=self.thursday
            elif day==5:
                daypermission=self.friday
            elif day==6:
                daypermission=self.saturday
            elif day==7:
                daypermission=self.sunday
            else:
                daypermission=False

            return daypermission and self.hour_start <= hour <= self.hour_end and self.valid
        else:
            return False

    def can_use_device_now(self, device):
        """

        """
        if self.role_kind == 1:
            try:
                p = self.category_devices.objects.get(pk=device.category_device)
            except Category_Device.DoesNotExist:
                return False

            now=timezone.now()
            day=now.weekday()
            hour=now.time()

            if day == 1:
                daypermission=self.monday
            elif day==2:
                daypermission=self.tuesday
            elif day==3:
                daypermission=self.wednesday
            elif day==4:
                daypermission=self.thursday
            elif day==5:
                daypermission=self.friday
            elif day==6:
                daypermission=self.saturday
            elif day==7:
                daypermission=self.sunday
            else:
                daypermission=False

            return daypermission and self.hourStart <= hour <= self.hourEnd and self.valid
        else:
            return False

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
        return "user: %s\ndevice: %s\nboot: %s\nstart: %s\ninWorking: %s\nHourlyCost: %f" %(self.user, self.delete, self.bootDevice, self.startWork, "yes" if self.inWorking else "no\nshutdown: %s\nfinish: %s"%(self.shutdownDevice, self.finishWork), self.hourlyCost)
