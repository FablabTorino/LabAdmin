from django.contrib import admin
from labAdmin.models import *

class MyModelAdmin(admin.ModelAdmin):
    pass
from .models import User


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['username']}),
        ('User Type', {'fields': ['utype']}),
        ('Tag NFC ID', {'fields': ['nfcId']}),
        ('Sign Up Date', {'fields': ['signup']}),
        ('Subcription End Date', {'fields': ['subscriptionEnd']}),
        ('Need Subcription', {'fields': ['needSubcription']}),
    ]
    list_display = ('username','id','utype','signup','subscription_end','nfcId', 'subscriptionExpired')

class UsertypeAdmin(admin.ModelAdmin):
    list_display = ('name','id','isAdmin','weekdays','hourStart', 'hourEnd')

admin.site.register(User, UserAdmin)
admin.site.register(Usertype,UsertypeAdmin)
admin.site.register(Device)
admin.site.register(Devicetype)
admin.site.register(Permission)
admin.site.register(Logdoor)
admin.site.register(Logdevice)
