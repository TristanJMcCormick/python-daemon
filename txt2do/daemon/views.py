#!/usr/bin/env python
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from models import Text
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime

#Non-Django imports
from client_libraries import TwilioClient
from twilio.rest.exceptions import TwilioRestException
import foursquare_wrapper
from templates import SMS_TEMPLATES

'''
This is the only endpoint right now. It handles posts from twilio to accomplish
certain predetermined tasks. For now, that just means foursquare business detail
queries.
'''


@csrf_exempt
@require_http_methods(["POST"])
def task(request):
    incoming_text = Text.objects.create(
        body = request.POST.get('Body', 'No message body').lower(),
        message_sid = request.POST.get('MessageSid'),
        from_number = request.POST.get('From'),
        to_number = request.POST.get('To'),
    )
    twilio_client = TwilioClient()
    # Split out the pre-flag text, this will indicate the task to accomplish and any required keywords
    parsed_task = _parse_task_parts(incoming_text)
    #Handle foursquare task
    if parsed_task['task_type'] == 'foursquare':
        return foursquare_wrapper.handle_foursquare_task(parsed_task, incoming_text.from_number)
    if parsed_task['task_type'] == 'budget':
        return HttpResponse('Bloop!')
    else:
        twilio_client.send_sms(settings.TWILIO_NUMBER, incoming_text.from_number, SMS_TEMPLATES['WRONG_TASK_TYPE'])
        return HttpResponseBadRequest()
    return HttpResponse('All branches should be handled, we shouldn\'t get here.')

'''
    Takes the new incoming text and produces a dictionary with three keys:
        'task_type' : Which of the configured daemon behaviors this text is calling on
            e.g. As of 1.9 that was only foursquare but budgeting is coming soon and
            the options are endless
        'query' : The text of the query for whatever service, task is being called
            e.g. Brooklyn Bagel
        'flag_list' : The list of task flags to pass to arg_parse
            e.g. '-n brooklyn -d 3' --> ['-n','brooklyn','-d','3']
        'errors' : A string representing any errors with the incoming text to be
            returned to the texter
    Note that this method depends on the text being formatted as
    "<keyword> <query> <-flag param -flag param...>" and will throw an error if
    it doesn't
'''
def _parse_task_parts(incoming_text):
    errors = ''
    sms_body = incoming_text.body.lower()
    #Check for and grab the first word in the text.
    if sms_body.find(' ') is not -1:
        task_type = sms_body[:sms_body.find(' ')]
    else:
        errors += 'No task type specified'
    #Grab the text from the first word to the first flag.
    #Note that if flags are absent, the slice-ending index is -1, which
    #(apparently) resolves to the end of the string. Which is fine in this case.
    task_query = sms_body[sms_body.find(' '):sms_body.find('-')].strip()
    #Check for and grab any flags
    flags_list = []
    if sms_body.find('-') is not -1:
        flags_list = sms_body[sms_body.find('-'):].split(' ')#NOTE:ASSUMES NO SPACES WITHOUT FLAG
    parsed_sms = {'task_type':task_type, 'query':task_query, 'flags':flags_list, 'errors':errors}
    return parsed_sms
