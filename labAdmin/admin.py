from django.contrib import admin
from labAdmin.models import *

class MyModelAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','type','signup','subscription_end')

class UsertypeAdmin(admin.ModelAdmin):
    list_display = ('id','name','isAdmin','weekdays','hourStart', 'hourEnd','weekdays_permission_binary_str', 'havePermission')

admin.site.register(User, UserAdmin)
admin.site.register(Usertype,UsertypeAdmin)
admin.site.register(Device)
admin.site.register(Devicetype)
admin.site.register(Permission)
admin.site.register(Logdoor)
admin.site.register(Logdevice)
