from django.contrib import admin

from spreedly.models import Plan, Subscription

class PlanAdmin(admin.ModelAdmin):
    pass

admin.site.register(Plan, PlanAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Subscription, SubscriptionAdmin)