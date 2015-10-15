from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract=True

class Task(BaseModel):
    query = models.CharField(max_length=100)
    response = models.TextField(null=True)

#Map one-to-one to twilio POSTed object
class Text(BaseModel):
    body = models.TextField()#max_length = 1600 characters
    message_sid = models.CharField(max_length=34)#34 character limit from Twilio
    from_number = models.CharField(max_length=12)
    to_number = models.CharField(max_length=12)
