from django.shortcuts import render
from django.http import HttpResponse
from models import Task, Text
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

#custom pips
import foursquare

@csrf_exempt
def task(request):
    incoming_text = Text.objects.create(
    body = request.POST.get('Body'),
    message_sid = request.POST.get('MessageSid'),
    from_number = request.POST.get('From'),
    to_number = request.POST.get('To'),
    )
    twiml_response = 'nothing set. Something\'s wrong!'
    if incoming_text.body and 'foursquare' in incoming_text.body:
        #Initialize client
        client = foursquare.Foursquare(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET, version=settings.FOURSQUARE_VERSION)
        #Grab the query to dish it to 4sqr.
        foursquare_query = incoming_text.body.split("foursquare",1)[1].strip()
        #Optional near param?
        venue_query_response = client.venues.search(params={'query': foursquare_query,'near':settings.LOCATION})
        #Api's up
        if venue_query_response.get('venues') and venue_query_response.get('venues')[0]:
            contact = venue_query_response.get('venues')[0].get('contact')
            location = venue_query_response.get('venues')[0].get('location')
            if location.get('formattedAddress'):
                twiml_response = '<Response><Message>Bingo. ' + " ".join(location.get('formattedAddress')) + ', ' + contact.get('phone') + '</Message></Response>'
            else:
                twiml_response = '<Response><Message>Bingo. ' + location.get('address','No Address!') + ', at ' + location.get('crossStreet','No crossStreet') + ', ' + contact.get('phone') + '</Message></Response>'
    else:
        twiml_response = '<Response><Message>Got the text "' + incoming_text.body + '." Not sure what it means.</Message></Response>'
    return HttpResponse(twiml_response, content_type='text/xml')
