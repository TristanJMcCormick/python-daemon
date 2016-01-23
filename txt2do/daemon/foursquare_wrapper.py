from django.conf import settings
import argparse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound


from client_libraries import FoursquareClient, TwilioClient
from twilio.rest.exceptions import TwilioRestException
from templates import SMS_TEMPLATES



def handle_foursquare_task(foursquare_task_object, sender):
    foursquare_client = FoursquareClient()
    twilio_client = TwilioClient()

    if not foursquare_task_object['query']:
        twilio_client.send_sms(settigns.TWILIO_NUMBER, sender, SMS_TEMPLATES['MALFORMED_QUERY']['foursquare'])
        return HttpResponseBadRequest("Query malformed")

    task_namespace = _get_task_namespace_object(foursquare_task_object['flags'])

    query_with_options = {'query':foursquare_task_object['query'], 'near':task_namespace.near[0]}
    venues = foursquare_client.query_foursquare_venues(query_with_options, task_namespace.depth[0])
    if venues:
        print len(venues)
        return HttpResponse('dfas')
        for venue in venues:
            contact = venue.get('contact')
            location = venue.get('location')
            if location.get('formattedAddress'):
                sms_body = SMS_TEMPLATES['QUERY_RESPONSE']['foursquare'].format(' '.join(location.get('formattedAddress', 'No Address')) + ', ' + contact.get('phone','No phone'))
                twilio_client.send_sms(settings.TWILIO_NUMBER, sender, sms_body)
                return HttpResponse("Success")
            else:
                sms_body = SMS_TEMPLATES['QUERY_RESPONSE']['foursquare'].format(location.get('address','No Address') + ', at ' + location.get('crossStreet','No cross street') + ', ' + contact.get('phone','No phone'))
                twilio_client.send_sms(settings.TWILIO_NUMBER, sender, sms_body)
                return HttpResponse("Success")
    else:
        twilio_client.send_sms(settings.TWILIO_NUMBER, sender, SMS_TEMPLATES['NO_RESPONSE']['foursquare'])
        return HttpResponseNotFound("Nothing returned for that query")

def _get_task_namespace_object(foursquare_flags_list):
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        '-n',
        dest='near',
        action='store',
        nargs=1,
        default=settings.FOURSQUARE_DEFAULT_LOCATION,
    )
    argument_parser.add_argument(
        '-d',
        dest="depth",
        action='store',
        nargs=1,
        default=1,
        type=int,
    )
    return argument_parser.parse_args(foursquare_flags_list)

def _parse_foursquare_response(response):
    pass
