import httplib, urllib2
import pytz
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import fromstring
from base64 import b64encode


API_VERSION = 'v4'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def get_tz_aware_date(doc, attr):
    """Extracts a datetime from the document and makes it TZ aware (UTC)."""
    timestamp = datetime.strptime(doc.findtext(attr), DATE_FORMAT)
    return pytz.timezone('utc').localize(timestamp)


class Client:
    def __init__(self, token, site_name):
        self.auth = b64encode('%s:x' % token)
        self.base_host = 'spreedly.com'
        self.base_path = '/api/%s/%s' % (API_VERSION, site_name)
        self.base_url = 'https://%s%s' % (self.base_host, self.base_path)
        self.url = None
    
    def get_response(self):
        return self.response
    
    def get_url(self):
        return self.url
    
    def set_url(self, url):
        self.url = '%s/%s' % (self.base_url, url)
    
    def query(self, data=None):
        req = urllib2.Request(url=self.get_url())
        req.add_header('User-agent', 'python-spreedly 1.0')
        req.add_header('Authorization', 'Basic %s' % self.auth)
        
        # Convert to POST if we got some data
        if data:
            req.add_header('Content-Type', 'application/xml')
            req.add_data(data)
        
        f = urllib2.urlopen(req)
        self.response = f.read()
    
    def get_plans(self):
        self.set_url('subscription_plans.xml')
        self.query()
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscription-plan'):
            data = {
                'name': plan.findtext('name'),
                'description': plan.findtext('description'),
                'terms': plan.findtext('terms'),
                'plan_type': plan.findtext('plan-type'),
                'price': Decimal(plan.findtext('price')),
                'enabled': True if plan.findtext('enabled') == 'true' else False,
                'force_recurring': \
                    True if plan.findtext('force-recurring') == 'true' else False,
                'force_renew': \
                    True if plan.findtext('needs-to-be-renewed') == 'true' else False,
                'duration': int(plan.findtext('duration-quantity')),
                'duration_units': plan.findtext('duration-units'),
                'feature_level': plan.findtext('feature-level'),
                'return_url': plan.findtext('return-url'),
                'version': int(plan.findtext('version')) \
                    if plan.findtext('version') else 0,
                'speedly_id': int(plan.findtext('id')),
                'speedly_site_id': int(plan.findtext('site-id')) \
                    if plan.findtext('site-id') else 0,
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
            }
            result.append(data)
        return result
    
    def create_subscriber(self, customer_id, screen_name):
        '''
        Creates a subscription
        '''
        data = '''
        <subscriber>
            <customer-id>%d</customer-id>
            <screen-name>%s</screen-name>
        </subscriber>
        ''' % (customer_id, screen_name)
        
        self.set_url('subscribers.xml')
        self.query(data)
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }
            
            result.append(data)
        return result[0]
    
    def delete_subscriber(self, id):
        if 'test' in self.base_path:
            headers = {'Authorization': 'Basic %s' % self.auth}
            conn = httplib.HTTPSConnection(self.base_host)
            conn.request(
                'DELETE', '%s/subscribers/%d.xml' % (self.base_path, id),
                '',
                headers
            )
            response = conn.getresponse()
            return response.status
        return
    
    def subscribe(self, subscriber_id, plan_id, trial=False):
        '''
        Subscribe a user to some plan
        '''
        data = '<subscription_plan><id>%d</id></subscription_plan>' % plan_id
        
        if trial:
            self.set_url('subscribers/%d/subscribe_to_free_trial.xml' % subscriber_id)
        
        self.query(data)
        
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }
            result.append(data)
        return result[0]
        
    def allow_free_trial(self, subscriber_id):
        '''
        Allows a Subscriber another Free Trial.
        https://spreedly.com/manual/integration-reference/programatically-allowing-another-free-trial
        '''
        data = '<subscriber><customer-id>%d</customer-id></subscriber>' % subscriber_id
        self.set_url('subscribers/%d/allow_free_trial.xml' % subscriber_id)
        self.query(data)

    def complimentary_subscription(self, subscriber_id, duration_quantity, duration_units, feature_level):
        '''
        Creates a complimentary subscription for the specified feature level
        '''
        data = '''
        <complimentary_subscription>
            <duration_quantity>%s</duration_quantity>
            <duration_units>%s</duration_units>
            <feature_level>%s</feature_level>
        </complimentary_subscription>
        ''' % (duration_quantity, duration_units, feature_level)
    
        self.set_url('subscribers/%d/complimentary_subscriptions.xml' % subscriber_id)
        self.query(data)

        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }

            result.append(data)
        return result[0]
        
    def lifetime_complimentary_subscription(self, subscriber_id, feature_level):
        '''
        Creates a lifetime complimentary subscription for the specified feature level
        '''
        data = '''
        <lifetime_complimentary_subscription>
          <feature_level>%s</feature_level>
        </lifetime_complimentary_subscription>
        ''' % feature_level

        self.set_url('subscribers/%d/lifetime_complimentary_subscriptions.xml' % subscriber_id)
        self.query(data)

        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }

            result.append(data)
        return result[0]

    def complimentary_time_extension(self, subscriber_id, duration_quantity, duration_units):
        '''
        Creates a complimentary time extension
        '''
        data = '''
        <complimentary_time_extension>
            <duration_quantity>%s</duration_quantity>
            <duration_units>%s</duration_units>
        </complimentary_time_extension>
        ''' % (duration_quantity, duration_units)
        
        self.set_url('subscribers/%d/complimentary_time_extensions.xml' % subscriber_id)
        self.query(data)

        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }

            result.append(data)
        return result[0]


    def add_store_credit(self, subscriber_id, amount):
        '''
        Adds store credit to a users subscription account
        '''
        data = '''
        <credit>
          <amount>%f</amount>
        </credit>
        ''' % amount

        self.set_url('subscribers/%d/credits.xml' % subscriber_id)
        self.query(data)

        return self.get_response()  
        
        
    def cleanup(self):
        '''
        Removes ALL subscribers. NEVER USE IN PRODUCTION!
        '''
        if 'test' in self.base_path:
            headers = {'Authorization': 'Basic %s' % self.auth}
            conn = httplib.HTTPSConnection(self.base_host)
            conn.request(
                'DELETE', '%s/subscribers.xml' % self.base_path,
                '',
                headers
            )
            response = conn.getresponse()
            return response.status
        return
    
    def get_info(self, subscriber_id):
        self.set_url('subscribers/%d.xml' % subscriber_id)
        self.query('')
    
        # Parse
        result = []
        tree = fromstring(self.get_response())
        for plan in tree.getiterator('subscriber'):
            data = {
                'customer_id': int(plan.findtext('customer-id')),
                'first_name': plan.findtext('billing-first-name'),
                'last_name': plan.findtext('billing-last-name'),
                'active': True if plan.findtext('active') == 'true' else False,
                'trial_active': \
                    True if plan.findtext('on-trial') == 'true' else False,
                'trial_elegible': \
                    True if plan.findtext('eligible-for-free-trial') == 'true' \
                    else False,
                'lifetime': \
                    True if plan.findtext('lifetime-subscription') == 'true' \
                    else False,
                'recurring': \
                    True if plan.findtext('recurring') == 'true' \
                    else False,
                'card_expires_before_next_auto_renew': \
                    True if plan.findtext('card-expires-before-next-auto-renew') == 'true' \
                    else False,
                'token': plan.findtext('token'),
                'name': plan.findtext('subscription-plan-name'),
                'feature_level': plan.findtext('feature-level'),
                'store_credit': Decimal(plan.findtext('store-credit')),
                'created_at': get_tz_aware_date(plan, 'created-at'),
                'date_changed': get_tz_aware_date(plan, 'updated-at'),
                'active_until': get_tz_aware_date(plan, 'active_until') if plan.findtext('active-until') else None,
            }
            result.append(data)
        return result[0]
        
    def stop_auto_renew(self, subscriber_id):
        self.set_url('subscribers/%d/stop_auto_renew.xml' % subscriber_id)
        
        data = '''
        <subscriber>
            <customer-id>%d</customer-id>
        </subscriber>
        ''' % (subscriber_id)
        self.query(data)
        
        return self.get_response()
    
    def get_or_create_subscriber(self, subscriber_id, screen_name):
        try:
            return self.get_info(subscriber_id)
        except urllib2.HTTPError, e:
            if e.code == 404:
                return self.create_subscriber(subscriber_id, screen_name)
