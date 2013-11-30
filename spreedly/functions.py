from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from spreedly.models import Plan, Subscription
from spreedly.client import Client

def subscriber_url(subscriber_id):
    return "https://subs.pinpayments.com/%s/subscribers/%s" % (settings.SPREEDLY_SITE_NAME, subscriber_id)

def sync_plans():
    '''
    Sync subscription plans with Spreedly API
    '''
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)

    for plan in client.get_plans():
        p, created = Plan.objects.get_or_create(speedly_id=plan['speedly_id'])

        changed = False
        for k, v in plan.items():
            if hasattr(p, k) and not getattr(p, k) == v:
                setattr(p, k, v)
                changed = True
        if changed:
            p.save()

def get_subscription(user):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    data = client.get_info(user.id)

    subscription, created = Subscription.objects.get_or_create(
        user=user
    )
    for k, v in data.items():
        if hasattr(subscription, k):
            setattr(subscription, k, v)
    subscription.save()
    return subscription

def create_subscription(user):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.get_or_create_subscriber(user.id, user.username)
    return get_subscription(user)

def get_or_create_subscription(user):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    data = client.get_or_create_subscriber(user.id, user.username)

    subscription, created = Subscription.objects.get_or_create(
        user=user
    )
    for k, v in data.items():
        if hasattr(subscription, k):
            setattr(subscription, k, v)
    subscription.save()
    return subscription

def check_trial_eligibility(plan, user):
    if plan.plan_type != 'free_trial':
        return False
    try:
        # make sure the user is trial eligable (they don't have a subscription yet, or they are trial_elegible)
        not_allowed = Subscription.objects.get(user=user, trial_elegible=False)
        return False
    except Subscription.DoesNotExist:
        return True

def start_free_trial(plan, user):
    if check_trial_eligibility(plan, user):
        client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
        client.get_or_create_subscriber(user.id, user.username)
        client.subscribe(user.id, plan.pk, trial=True)
        get_subscription(user)
        return True
    else:
        return False

def allow_free_trial(user):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.allow_free_trial(user.id)

def complimentary_time_extension(user, duration_quantity, duration_units):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.complimentary_time_extension(user.id, duration_quantity, duration_units)
    return get_subscription(user)

def complimentary_subscription(user, duration_quantity, duration_units, feature_level):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.complimentary_subscription(user.id, duration_quantity, duration_units, feature_level)
    return get_subscription(user)

def lifetime_complimentary_subscription(user, feature_level):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.lifetime_complimentary_subscription(user.id, feature_level)
    return get_subscription(user)

def add_store_credit(user, amount):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.add_store_credit(user.id, amount)
    return get_subscription(user)

def stop_auto_renew(user):
    client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
    client.stop_auto_renew(user.id)
    return get_subscription(user)

def return_url(plan, user, trial=False):
    url = 'http://%s%s' % (Site.objects.get(id=settings.SITE_ID), reverse('spreedly_return', args=[user.id, plan.pk]))
    if trial:
        url = url + '?trial=true'
    return url

def subscription_url(plan, user, return_url):
    return 'https://subs.pinpayments.com/%(site_name)s/subscribers/%(user_id)s/subscribe/%(plan_id)s/%(user_username)s?email=%(user_email)s&return_url=%(return_url)s&first_name=%(first_name)s&last_name=%(last_name)s' % {
        'site_name': settings.SPREEDLY_SITE_NAME,
        'plan_id': plan.pk,
        'user_id': user.id,
        'user_username': user.username,
        'user_email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'return_url': return_url
    }
