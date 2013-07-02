from django.db import models
from django.utils import timezone
from django.db.models import Q

class PlanManager(models.Manager):
    def enabled(self):
        return self.model.objects.filter(enabled=True, force_recurring=True)


class Plan(models.Model):
    '''
    Subscription plan
    '''
    name = models.CharField(max_length=64, null=True)
    description = models.TextField(blank=True)
    terms = models.CharField(max_length=100, blank=True)
    
    plan_type = models.CharField(max_length=10, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default='0',
        help_text=u'USD', null=True)
    
    enabled = models.BooleanField(default=False)
    force_recurring = models.BooleanField(default=False)
    force_renew = models.BooleanField(default=False)
    
    duration = models.IntegerField(blank=True, default=0)
    duration_units = models.CharField(max_length=10, blank=True)
    
    feature_level = models.CharField(max_length=100, blank=True)
    
    return_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(editable=False, null=True)
    date_changed = models.DateTimeField(editable=False, null=True)
    
    version = models.IntegerField(blank=True, default=1)
    
    speedly_id = models.IntegerField(db_index=True, primary_key=True)
    speedly_site_id = models.IntegerField(db_index=True, null=True)
    
    order = models.PositiveIntegerField(null=True)
    
    objects = PlanManager()
    
    class Meta:
        ordering = ['order', 'price']
    
    def __unicode__(self):
        return '%s: $%s/%s' % (self.name, self.price, self.terms)
    
    def save(self, *args, **kwargs):
        # order the items logically
        if self.plan_type == 'free_trial':
            self.order = 1
        if self.plan_type == 'regular':
            self.order = 2
        if self.plan_type == 'gift':
            self.order = 3
        super(Plan, self).save(*args, **kwargs)
    
    @property
    def plan_type_display(self):
        return self.plan_type.replace('_',' ').title()
    
    @property
    def is_gift_plan(self):
        return self.plan_type == "gift"

    @property
    def is_free_trial_plan(self):
        return self.plan_type == "free_trial"

class SubscriptionManager(models.Manager):
    def has_active(self, user):
        '''
        Determine if given user has active subscription
        '''
        return self.model.objects.filter(user=user, active=True).filter(Q(active_until__gt=timezone.now())|Q(active_until__isnull=True)).count()

class Subscription(models.Model):
    name = models.CharField(max_length=100, blank=True)

    user = models.OneToOneField('auth.User', primary_key=True)
    first_name = models.CharField(blank=True, max_length=100)
    last_name = models.CharField(blank=True, max_length=100)
    feature_level = models.CharField(max_length=100, blank=True)
    active_until = models.DateTimeField(blank=True, null=True)
    token = models.CharField(max_length=100, blank=True)
    
    trial_elegible = models.BooleanField(default=False)
    lifetime = models.BooleanField(default=False)
    recurring = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    
    card_expires_before_next_auto_renew = models.BooleanField(default=False)
    
    store_credit = models.DecimalField(max_digits=6, decimal_places=2, default='0',
        help_text=u'USD', null=True)
    
    objects = SubscriptionManager()
    
    def __unicode__(self):
        return u'Subscription for %s' % self.user
    
    def save(self, *args, **kwargs):
        if self.active and not self.user.is_active:
            self.user.is_active = True
            self.user.save()
        super(Subscription, self).save(*args, **kwargs)
    
    @property
    def subscription_status(self):
        '''gets the status based on current active status and active_until'''
        if self.active:
            if self.active_until:
                if self.active_until > timezone.now():
                    return True
                elif self.lifetime:
                    return True
            elif self.lifetime:
                return True        
        return False
