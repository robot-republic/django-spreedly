from django.http import Http404, HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import mail_admins
from spreedly.client import Client
from spreedly.functions import subscriber_url
from spreedly.models import Subscription


# TODO: Should we `sync_plans()` first?


def spreedly_listener(request):
    if request.method == 'POST':
        # Try to extract customers' IDs
        if request.POST.has_key('subscriber_ids'):
            subscriber_ids = request.POST['subscriber_ids'].split(',')
            failed_ids = []
            if len(subscriber_ids):
                client = Client(settings.SPREEDLY_AUTH_TOKEN_SECRET, settings.SPREEDLY_SITE_NAME)
                for id in subscriber_ids:
                    # Now let's query Spreedly API for the actual changes
                    data = client.get_info(int(id))
                    
                    try:
                        user = User.objects.get(pk=id)                    
                        subscription, created = Subscription.objects.get_or_create(user=user)
                        for k, v in data.items():
                            if hasattr(subscription, k):
                                setattr(subscription, k, v)
                        subscription.save()
                    except User.DoesNotExist, e:
                        failed_ids.append(id)
                        
                if failed_ids:
                    links = "\n".join([subscriber_url(id) for id in failed_ids])
                    
                    mail_admins(
                        subject="Could not update Spreedly Subscriptions",
                        message="The following subscribers changed on Spreedly, but there's no corresponding User:\n%s" % links
                    )
                    
                return HttpResponse("OK")
    raise Http404