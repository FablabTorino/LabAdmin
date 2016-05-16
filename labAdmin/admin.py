from django.contrib import admin
from labAdmin.models import *

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'nfcId','firstSignup', 'lastSignup', 'subscription',)
    ordering = ('name',) # The negative sign indicate descendent order

    def subscription(self, obj):
        return obj.endSubcription if obj.needSubcription else "lifetime membership"





admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(Category_Device)
admin.site.register(Device)
admin.site.register(Payment)
admin.site.register(LogAccess)
admin.site.register(LogDevice)
admin.site.register(LogError)
admin.site.register(TimeSlot)
