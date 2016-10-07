# -*- coding: utf-8 -*-
import json
import os.path

from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone

from labAdmin.models import UserProfile


def import_fablabto_users(users_json):
    """
    Call this function from a django shell.
    Takes the path of json users dump
    """
    with open(users_json, 'r') as f:
        users = json.load(f)
        for fabuser in users:
            try:
               bio = fabuser['biografia']
            except KeyError:
               bio = fabuser['description']

            now = timezone.now()

            user, created = User.objects.get_or_create(username=fabuser['id'])
            if not created:
                continue

            up = UserProfile(
                user=user,
                name=fabuser['title'],
                address=fabuser['address'],
                tax_code=fabuser['fiscalCode'],
                vat_id=fabuser['vat'],
                bio=bio,
                endSubscription=now,
            )

            try:
                up.nfcId = int(fabuser['rfid'], 16)
            except:
                print(up.name, up.nfcId, fabuser['rfid'])

            if 'immagine' in fabuser:
                with open(fabuser['immagine'], 'rb') as img:
                    f = File(img)
                    name = os.path.basename(fabuser['immagine'])
                    up.picture.save(name, f)

            try:
                up.save()
            except Exception as e:
                print(up.name, e)
