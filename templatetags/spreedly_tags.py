from django.conf import settings
from django import template

from spreedly.functions import subscription_url, return_url

register = template.Library()

@register.simple_tag
def existing_plan_url(user, return_url):
    return 'https://spreedly.com/%(site_name)s/subscriber_accounts/%(user_token)s/?return_url=%(return_url)s' % {
        'site_name': settings.SPREEDLY_SITE_NAME,
        'user_token': user.subscription.token,
        'return_url': return_url
    }

@register.simple_tag
def new_plan_url(plan, user, return_url):
    return subscription_url(plan, user, return_url)