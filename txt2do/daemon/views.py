from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
from models import Text
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime

#Non-Django imports
from foursquare import InvalidAuth, EndpointError
from twilio.rest.exceptions import TwilioRestException
from txt2do.client_libraries import FoursquareClient, TwilioClient



'''
This is the only endpoint right now. It handles posts from twilio to accomplish
certain predetermined tasks. For now, that just means foursquare business detail
queries.
'''

TASKS = [
    'FOURSQUARE',
]

SMS_TEMPLATES = {
    'WRONG_TASK_TYPE':'Something was wrong with the query. We can only handle ' + ' ,'.join(TASKS),
    'MALFORMED_QUERY':{
        'foursquare':'Something was wrong with the query. Does it have the form: foursquare <queryterm> [-n <cityname>]',
        },
    'NO_RESPONSE':{
        'foursquare':'No results for that venue'
    },
    'QUERY_RESPONSE':{
        'foursquare':'Found somewhere. {0}'
    },
    'ADMIN_NOTIFIED':'Something went wrong with foursquare integration. Tristan is checking into it!',
    'NOTIFY_ADMIN':'Foursquare api is down or something. Check credentials and API status',
}



@csrf_exempt
@require_http_methods(["POST"])
def task(request):
    incoming_text = Text.objects.create(
        body = request.POST.get('Body', 'No message body').lower(),
        message_sid = request.POST.get('MessageSid'),
        from_number = request.POST.get('From'),
        to_number = request.POST.get('To'),
    )
    foursquare_client = FoursquareClient()
    twilio_client = TwilioClient()
    # Split out the pre-flag text, this will indicate the task to accomplish and any required keywords
    parsed_task = _parse_task_parts(incoming_text)
    #Handle foursquare task
    if parsed_task['task_type'] == 'foursquare':
        if not parsed_task['task_query']:
            twilio_client.send_sms(settigns.TWILIO_NUMBER, incoming_text.from_number, SMS_TEMPLATES['MALFORMED_QUERY']['foursquare'])
            return HttpResponseBadRequest("Query malformed")
        near_param = ''
        #Right now only handle a "near" parameter that specifies a neighborhood.
        if flags and 'n ' in parsed_task['flags']:
            near_param = parsed_task['flags']['-n']
        query_with_options = {'query':parsed_task['task_query'], 'near':settings.LOCATION if not near_param else near_param}
        venue_details_response = foursquare_client.query_foursquare_venues(query_with_options)
        if venue_details_response.get('venues') and venue_details_response.get('venues')[0]:
            contact = venue_details_response.get('venues')[0].get('contact')
            location = venue_details_response.get('venues')[0].get('location')
            if location.get('formattedAddress'):
                sms_body = SMS_TEMPLATES['QUERY_RESPONSE']['foursquare'].format(' '.join(location.get('formattedAddress', 'No Address')) + ', ' + contact.get('phone','No phone'))
                twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.from_number, sms_body)
                return HttpResponse("Success")
            else:
                sms_body = SMS_TEMPLATES['QUERY_RESPONSE']['foursquare'].format(location.get('address','No Address') + ', at ' + location.get('crossStreet','No cross street') + ', ' + contact.get('phone','No phone'))
                twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.from_number, sms_body)
                return HttpResponse("Success")
        else:
            if incoming_text.from_number is not settings.ADMIN_NUMBER:
                twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.from_number, SMS_TEMPLATES['NO_RESPONSE']['foursquare'])
            twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.ADMIN_NUMBER, SMS_TEMPLATES['NO_RESPONSE']['foursquare'])
            return HttpResponse("Nothing returned for that query")
    else:
        twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.from_number, SMS_TEMPLATES['WRONG_TASK_TYPE'])
        return HttpResponseNotFound("That task isn't supported yet. Just foursquare for now!")
    return HttpResponse('All branches should be handled, we shouldn\'t get here.')

'''
    Takes the new incoming text and produces a dictionary with three keys:
        'task_type' : Which of the configured daemon behaviors this text is calling on
            e.g. As of 1.9 that was only foursquare but budgeting is coming soon and
            the options are endless
        'query' : The text of the query for whatever service, task is being called
            e.g. Brooklyn Bagel
        'flags' : A dictionary of flags
            e.g. -n Brooklyn or -d 3 for "near brooklyn" and "depth of 3"
    Note that this method depends on the text being formatted as
    "<keyword> <query> <-flag param -flag param...>" and will throw an error if
    it doesn't
'''
def _parse_task_parts(incoming_text):
    print('in parsed task parts')
    sms_body = incoming_text.body.lower()
    task_type = sms_body[:sms_body.find(' ')]
    task_query = sms_body[sms_body.find(' '):sms_body.find('-')].strip()
    flags_string = sms_body[sms_body.find('-'):]
    flags_dict = []
    print repr(flags_string)
    return
    # print('flags', flags)
    parsed_sms = {'task_type' : task_type, 'query' : task_query, 'flags' : flags}
    return parsed_sms
