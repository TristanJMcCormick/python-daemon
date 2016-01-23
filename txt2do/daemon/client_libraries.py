import foursquare
from twilio.rest import TwilioRestClient
from django.conf import settings

#Docs https://github.com/mLewisLogic/foursquare
class FoursquareClient(object):
    DEFAULT_NUM_OF_LOCATIONS = 1

    def __init__(self, query_with_options=None, num_of_locations = DEFAULT_NUM_OF_LOCATIONS):
        self.client = foursquare.Foursquare(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            version=settings.FOURSQUARE_VERSION
        )
        if query_with_options:
            venues = self._query_foursquare_venues(query_with_options)
            self.venues = venues[0:num_of_locations]
        else:
            self.venues = []

    def query_foursquare_venues(self, query_with_options, num_of_locations = DEFAULT_NUM_OF_LOCATIONS):
        return self._query_foursquare_venues(query_with_options, num_of_locations)

    def _query_foursquare_venues(self, query_with_options, num_of_locations):
        venue_details_response = self.client.venues.search(params=query_with_options)
        if venue_details_response.get('venues'):
            self.venues = venue_details_response.get('venues')[0:num_of_locations]
            return self.venues
        else:
            return false

class TwilioClient(object):
    def __init__(self):
        self.client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    def send_sms(self, sender, recipient, sms_body):
        self.client.messages.create(
            body = sms_body,
            to = recipient,
            from_ = sender,
        )
