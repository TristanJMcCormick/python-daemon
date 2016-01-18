import foursquare
from twilio.rest import TwilioRestClient
from django.conf import settings


TWILIO_CLIENT = {}
FOURSQUARE_CLIENT = {}

class FoursquareClient(object):
    def __init__(self):
        self.client = foursquare.Foursquare(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            version=settings.FOURSQUARE_VERSION
        )
    def query_foursquare_venues(self, query_with_options):
        venues = self.client.venues.search(params=query_with_options)
        return venues

class TwilioClient(object):
    def __init__(self):
        self.client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    #Takes a query string and dictionary of optional flags, e.g. -n for near and TODO
    # -d for depth
    def send_sms(self, sender, recipient, sms_body):
        self.client.messages.create(
            body = sms_body,
            to = recipient,
            from_ = sender,
        )
