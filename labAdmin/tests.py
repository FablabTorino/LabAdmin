from django.test import TestCase
from django.contrib.auth.models import User
from labAdmin.models import *
from django.utils import timezone, dateparse
# Create your tests here.

UserProfile.objects.all().delete()
Group.objects.all().delete()
Role.objects.all().delete()



r1 = Role(name="Fablab Access", hour_start=dateparse.parse_time("8:0:0"), hour_end=dateparse.parse_time("23:0:0"), thursday=True, role_kind=0)
r1.save()
r2 = Role(name="Guest Access", hour_start=dateparse.parse_time("14:0:0"), hour_end=dateparse.parse_time("20:0:0"), thursday=True, role_kind=0)
r2.save()
r3 = Role(name="Fresatori", hour_start=dateparse.parse_time("14:0:0"), hour_end=dateparse.parse_time("20:0:0"), thursday=True, role_kind=0)
r3.save()

g1 = Group(name="Fablab Guest")
g1.save()
g1.roles.add(r1,r2)
g2 = Group(name="Guest")
g2.save()
g2.roles.add(r2)
g3 = Group(name="Arduino")

user = User.objects.create(username="alessandro.monaco")
u = UserProfile(user=user, name="Alessandro Monaco",firstSignup=timezone.now(),lastSignup=timezone.now(),needSubcription=False,endSubcription=timezone.now())
u.save()
u.groups.add(g2)
u.listRoles()
