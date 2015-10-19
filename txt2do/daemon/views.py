from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
from models import Text
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

#Non-Django imports
import foursquare
from foursquare import InvalidAuth, EndpointError
from twilio.rest import TwilioRestClient
from xml.sax.saxutils import escape
from twilio.rest import TwilioRestClient
from twilio.rest.exceptions import TwilioRestException
from datetime import datetime


'''
This is the only endpoint right now. It handles incoming tasks 
'''

@csrf_exempt
def task(request):
    incoming_text = Text.objects.create(
    body = request.POST.get('Body', 'No message body').lower(),
    message_sid = request.POST.get('MessageSid'),
    from_number = request.POST.get('From'),
    to_number = request.POST.get('To'),
    )
    twiml_response = 'No response. Something is wrong!'

    try:
        twilio_client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        if incoming_text.body:
            query_parts = incoming_text.body.lower().split('-')
            # Split out the pre-flag text, this will indicate the task to accomplish and any required keywords
            task_type = query_parts[0].split(' ',1)[0]
            task_query = query_parts[0].split(' ',1)[1]
            flags = query_parts[1:]
            #Handle foursquare task
            if task_type == 'foursquare':
                if not task_query:
                    user_error_message = twilio_client.messages.create(
                        body = 'Something was wrong with the query. Does it have the form: foursquare <queryterm> [-n <cityname>]',
                        to = incoming_text.from_number,
                        from_ = settings.TWILIO_NUMBER,
                    )
                    return HttpResponseBadRequest("Query malformed")
                near_param = ''
                if flags and 'n ' in flags[0]:
                    near_param = flags[0][1:].strip()
                try:
                    foursquare_client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, version=settings.FOURSQUARE_VERSION)
                    venue_details_response = foursquare_client.venues.search(params={'query': task_query,'near':settings.LOCATION if not near_param else near_param})
                    if venue_details_response.get('venues') and venue_details_response.get('venues')[0]:
                        contact = venue_details_response.get('venues')[0].get('contact')
                        location = venue_details_response.get('venues')[0].get('location')
                        if location.get('formattedAddress'):
                            user_message = twilio_client.messages.create(
                                body = 'Bingo. ' + ' '.join(location.get('formattedAddress')) + ', ' + contact.get('phone','No phone'),
                                to = incoming_text.from_number,
                                from_ = settings.TWILIO_NUMBER,
                            )
                            return HttpResponse("Success")
                        else:
                            user_message = twilio_client.messages.create(
                                body = 'Bingo. ' + location.get('address','No Address') + ', at ' + location.get('crossStreet','No cross street') + ', ' + contact.get('phone','No phone'),
                                to = incoming_text.from_number,
                                from_ = settings.TWILIO_NUMBER
                            )
                            return HttpResponse("Success")
                    else:
                        user_message = twilio_client.messages.create(
                            body = 'Sorry. Nothing came back for that query.',
                            to = incoming_text.from_number,
                            from_ = settings.TWILIO_NUMBER,
                        )
                        admin_message = twilio_client.messages.create(
                            body = 'Yo this text returned nothin. Is that right? "' + incoming_text.body + '"',
                            to = settings.ADMIN_NUMBER,
                            from_ = settings.TWILIO_NUMBER,
                        )
                        return HttpResponse("Nothing returned for that query")

                except EndpointError as ex:
                    admin_error_message = twilio_client.messages.create(
                        body = 'API down or query is malformed. Check logs once you keep them',
                        to = settings.ADMIN_NUMBER,
                        from_ = settings.TWILIO_NUMBER,
                    )
                    user_error_message = twilio_client.messages.create(
                        body = 'Something went wrong with foursquare integration. Tristan is checking into it!',
                        to = incoming_text.from_number,
                        from_ = settings.TWILIO_NUMBER,
                    )
                    return HttpResponseBadRequest('Foursquare api is down or something is wrong with the query')
                except InvalidAuth as ex:
                    admin_error_message = twilio_client.messages.create(
                        body = 'Foursquare api is down or something. Check credentials and API status at ' + str(datetime.now()),
                        to = settings.ADMIN_NUMBER,
                        from_ = settings.TWILIO_NUMBER,
                    )
                    user_error_message = twilio_client.messages.create(
                        body = 'Something went wrong with foursquare integration. Tristan is checking into it!',
                        to = incoming_text.from_number,
                        from_ = settings.TWILIO_NUMBER,
                    )
                    return HttpResponseForbidden('Foursquare authorization failed')
            else:
                user_error_message = twilio_client.messages.create(
                    body = 'That task isn\'t supported. Just foursquare for now.',
                    to = incoming_text.from_number,
                    from_ = settings.TWILIO_NUMBER,
                )
                return HttpResponseNotFound("That task isn't supported yet. Just foursquare for now!")
        else:
            HttpResponse('You gotta send something!')
    except TwilioRestException as ex:
        return HttpResponse('There was a problem with the Twilio client library. Check credentials.')
    return HttpResponse('All branches should be handled, we shouldn\'t get here.')
