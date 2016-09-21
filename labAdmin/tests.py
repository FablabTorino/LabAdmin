from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone, dateparse

from .models import (
    Group, Role, TimeSlot, UserProfile
)


class TestLabAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        daily_timeslot = TimeSlot.objects.create(
            name="thursday full day",
            weekday_start=4,
            weekday_end=4,
            hour_start=dateparse.parse_time("8:0:0"),
            hour_end=dateparse.parse_time("23:0:0"),
        )
        reduced_timeslot = TimeSlot.objects.create(
            name="thursday reduced",
            weekday_start=4,
            weekday_end=4,
            hour_start=dateparse.parse_time("14:0:0"),
            hour_end=dateparse.parse_time("20:0:0"),
        )

        fablab_role = Role.objects.create(
            name="Fablab Access",
            role_kind=0
        )
        fablab_role.time_slots.add(daily_timeslot)

        guest_role = Role.objects.create(
            name="Guest Access",
            role_kind=0
        )
        guest_role.time_slots.add(reduced_timeslot)

        fab_guest_group = Group.objects.create(name="Fablab Guest")
        fab_guest_group.roles.add(fablab_role, guest_role)
        guest_group = Group.objects.create(name="Guest")
        guest_group.roles.add(guest_role)

        user = User.objects.create(username="alessandro.monaco")
        u = UserProfile.objects.create(
            user=user,
            name="Alessandro Monaco",
            firstSignup=timezone.now(),
            lastSignup=timezone.now(),
            needSubscription=False,
            endSubscription=timezone.now()
        )
        u.groups.add(guest_group)
