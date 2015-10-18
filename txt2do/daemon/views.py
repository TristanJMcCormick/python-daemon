from django.shortcuts import render
from django.http import HttpResponse
from models import Task, Text
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

#Non-Django imports
import foursquare
from twilio.rest import TwilioRestClient
from xml.sax.saxutils import escape
from twilio.rest import TwilioRestClient


@csrf_exempt
def task(request):
    incoming_text = Text.objects.create(
    body = request.POST.get('Body', 'No message body').lower(),
    message_sid = request.POST.get('MessageSid'),
    from_number = request.POST.get('From'),
    to_number = request.POST.get('To'),
    )
    twiml_response = 'No reponse. Something is wrong!'
    if incoming_text.body and 'foursquare' in incoming_text.body:
        #Initialize client
        client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, version=settings.FOURSQUARE_VERSION)
        #Grab the query to dish it to 4sqr.
        foursquare_query = incoming_text.body.split("foursquare",1)[1].strip()
        #Parse arguments
        #Why not both? <3 Love Toph
        #handle flags function, treat in generalized way, make easy to add new flags with new behavior
        # flags = .split('-') ???????
        near_param = ""
        if '-n' in incoming_text.body:
            start_index = incoming_text.find('-n') + 2
            end_index = incoming_text[start_index:].find('-') + start_index
            near_param = incoming_text[start_index:end_index].strip()
        elif '-h' in incoming_text.body:
            hours_requested = True
            #ADD CALL TO GET HOURS
        venue_details_response = client.venues.search(params={'query': foursquare_query,'near':settings.LOCATION if not near_param else near_param})
        # Api's up
        if venue_details_response.get('venues') and venue_details_response.get('venues')[0]:
            contact = venue_details_response.get('venues')[0].get('contact')
            location = venue_details_response.get('venues')[0].get('location')

            client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

            if location.get('formattedAddress'):
                message = client.messages.create(
                    body = 'Bingo. ' + " ".join(location.get('formattedAddress')) + ', ' + contact.get('phone'),
                    to = incoming_text.from_number,
                    from_ = settings.TWILIO_NUMBER,
                )
            else:
                message = client.messages.create(
                    body = 'Bingo. ' + location.get('address','No Address!') + ', at ' + location.get('crossStreet','No crossStreet') + ', ' + contact.get('phone'),
                    to = incoming_text.from_number,
                    from_ = settings.TWILIO_NUMBER
                )

    return HttpResponse("Received")
