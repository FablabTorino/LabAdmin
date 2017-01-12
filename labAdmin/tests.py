import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone, dateparse

from .models import (
    Card, Group, LogAccess, Role, TimeSlot, UserProfile, TimeSlot,
    LogCredits, Category, Device, LogDevice
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

        card = Card.objects.create(nfc_id=123456)
        user = User.objects.create(username="alessandro.monaco")
        u = UserProfile.objects.create(
            user=user,
            card=card,
            name="Alessandro Monaco",
            needSubscription=False,
            endSubscription=timezone.now()
        )
        u.groups.add(guest_group)

        category = Category.objects.create(
            name="category"
        )

        device = Device.objects.create(
            name="device",
            hourlyCost=1.0,
            category=category,
            mac="00:00:00:00:00:00"
        )

        cls.card = card
        cls.userprofile = u
        cls.device = device

    def test_login_by_nfc(self):
        client = Client()
        url = reverse('nfc-users')
        data = {
            'nfc_id': self.card.nfc_id
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(len(response_data), 1)
        user_profile = response_data[0]
        self.assertEqual(user_profile['id'], self.userprofile.pk)
        self.assertEqual(user_profile['name'], self.userprofile.name)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_open_door_by_nfc(self):

        self.assertFalse(LogAccess.objects.all().exists())

        client = Client()
        url = reverse('open-door-nfc')
        data = {
            'nfc_id': self.card.nfc_id
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertIn('users', response_data)
        self.assertEqual(len(response_data['users']), 1)
        user_profile = response_data['users'][0]
        self.assertEqual(user_profile['id'], self.userprofile.pk)
        self.assertEqual(user_profile['name'], self.userprofile.name)
        self.assertEqual(response_data['type'], 'other')
        self.assertIn('datetime', response_data)
        self.assertEqual(response_data['open'], self.userprofile.can_open_door_now())

        users = UserProfile.objects.all()
        logaccess = LogAccess.objects.filter(users=users, card=self.card)
        self.assertTrue(logaccess.exists())

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_timeslot_manager_now(self):
        now = timezone.now()
        now_time = now.time()
        now_weekday = now.isoweekday()

        # enough for the tests to work :)
        end = now + datetime.timedelta(minutes=1)
        end_time = end.time()
        end_weekday = now.isoweekday()

        self.assertFalse(TimeSlot.objects.can_now().exists())

        open_ts = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=end_time,
            weekday_start=now_weekday,
            weekday_end=end_weekday
        )

        closed_ts_weekday = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=end_time,
            weekday_start=end_weekday+1,
            weekday_end=end_weekday+1
        )

        closed_ts_hour = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=now_time,
            weekday_start=now_weekday,
            weekday_end=end_weekday
        )

        ts_now = TimeSlot.objects.can_now()
        self.assertTrue(ts_now.exists())
        self.assertEqual(ts_now.count(), 1)
        self.assertEqual(ts_now.first().pk, open_ts.pk)

    def test_get_card_credits(self):

        client = Client()
        url = reverse('card-credits')
        card = Card.objects.create(
            nfc_id=1,
            credits=1
        )
        data = {
            'nfc_id': card.nfc_id
        }

        auth = 'Token {}'.format(self.device.token)
        response = client.get(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_data, {
            'nfc_id': card.nfc_id,
            'credits': 1
        })

        data = {
            'nfc_id': 0
        }
        response = client.get(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # no auth token
        response = client.get(url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_card_credits(self):
        client = Client()
        auth = 'Token {}'.format(self.device.token)
        url = reverse('card-credits')
        card = Card.objects.create(
            nfc_id=1,
            credits=10
        )

        self.assertEqual(LogCredits.objects.count(), 0)

        # not enough credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': -20
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 403)

        # can't add credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': 10
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # consume credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': -10
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_data, {
            'nfc_id': 1,
            'credits': 0
        })

        self.assertEqual(LogCredits.objects.count(), 1)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        data = {
            'nfc_id': 1,
            'amount': 'amount'
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # no auth
        data = {
            'nfc_id': 0
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_device_token_creation(self):
        category = Category.objects.create(
            name="category"
        )

        device = Device.objects.create(
            name="device",
            hourlyCost=1.0,
            category=category,
            mac="00:00:00:00:00:00"
        )
        self.assertTrue(device.token)

        # token is created once
        old_token = device.token
        device.save()
        device = Device.objects.get(pk=device.pk)
        self.assertEqual(old_token, device.token)

    def test_device_stop(self):
        now = timezone.now()
        logdevice = LogDevice.objects.create(
            device=self.device,
            user=self.userprofile,
            bootDevice=now,
            startWork=now,
            shutdownDevice=now,
            finishWork=now,
            hourlyCost=self.device.hourlyCost,
        )
        logdevice.stop()
        self.assertEqual(logdevice.startWork, logdevice.bootDevice)
        self.assertTrue(logdevice.startWork < logdevice.finishWork)
        self.assertEqual(logdevice.finishWork, logdevice.shutdownDevice)
