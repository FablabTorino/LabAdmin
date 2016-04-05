from django.contrib import admin
from labAdmin.models import *

class MyModelAdmin(admin.ModelAdmin):
    pass
admin.site.register(User)
admin.site.register(Usertype)
admin.site.register(Device)
admin.site.register(Devicetype)
admin.site.register(Permission)
admin.site.register(Logdoor)
admin.site.register(Logdevice)
