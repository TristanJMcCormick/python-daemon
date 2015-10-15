from django.shortcuts import render
from django.http import HttpResponse
from models import Task, Text

# @csrf_exempt
# def task(request):
#     print request.POST
#     return HttpResponse('HELLO TASK')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def task(request):
    incoming_text = Text.objects.create(
    body = request.POST.get('Body'),
    message_sid = request.POST.get('MessageSid'),
    from_number = request.POST.get('From'),
    to_number = request.POST.get('To'),
    )
    twiml = '<Response><Message>Got the text "' + incoming_text.body + '" from ' + incoming_text.from_number + '</Message></Response>'
    return HttpResponse(twiml, content_type='text/xml')
