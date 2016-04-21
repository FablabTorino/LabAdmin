from django.contrib import admin
from labAdmin.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(Category_Device)
admin.site.register(Device)
admin.site.register(Payment)
admin.site.register(LogAccess)
admin.site.register(LogDevice)
admin.site.register(LogError)
admin.site.register(TimeSlot)
