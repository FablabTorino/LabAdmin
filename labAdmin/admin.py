from django.contrib import admin
from labAdmin.models import *

from .arp import get_neighbours


class CardAdmin(admin.ModelAdmin):
    list_display = ('nfc_id', 'credits')

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.log_credits_update(amount=obj.credits, user=request.user, from_admin=True)

admin.site.register(Card, CardAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'card', 'displaygroups','firstSignup', 'lastSignup', 'subscription')
    ordering = ('name','-needSubscription','-endSubscription') # The negative sign indicate descendent order

    def subscription(self, obj):
        return obj.endSubscription if obj.needSubscription else "lifetime membership"

admin.site.register(UserProfile, UserProfileAdmin)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_kind','valid',)
    ordering = ('name',)

admin.site.register(Role, RoleAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


admin.site.register(Group, GroupAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)

admin.site.register(Category, CategoryAdmin)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'hourlyCost', 'category', 'mac',)
    ordering = ('name',)
    change_form_template = 'labadmin/admin/device_change_form.html'
    add_form_template = 'labadmin/admin/device_change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['labadmin_available_devices'] = get_neighbours()
        return super(DeviceAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['labadmin_available_devices'] = get_neighbours()
        return super(DeviceAdmin, self).add_view(
            request, form_url, extra_context=extra_context
        )

admin.site.register(Device, DeviceAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('date', 'value', 'user',)
    ordering = ('-date','user',)

admin.site.register(Payment, PaymentAdmin)


class LogAccessAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'card', 'opened',)
    ordering = ('-datetime', 'card',)

admin.site.register(LogAccess,LogAccessAdmin)


class LogDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'bootDevice', 'shutdownDevice', 'startWork', 'finishWork', 'inWorking', 'priceWork',)
    ordering = ('-bootDevice','-startWork',)

admin.site.register(LogDevice, LogDeviceAdmin)

class LogErrorAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'description', 'code',)
    ordering = ('-datetime',)

admin.site.register(LogError, LogErrorAdmin)

class LogCreditsAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'card', 'amount', 'user', 'from_admin')
    list_filter = ('user',)

admin.site.register(LogCredits, LogCreditsAdmin)


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'weekday_start', 'weekday_end', 'hour_start', 'hour_end',)
    ordering = ('name',)

admin.site.register(TimeSlot, TimeSlotAdmin)
