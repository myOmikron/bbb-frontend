from django.db import models
from django.db.models import CharField


class Channel(models.Model):
    meeting_id = CharField(default="", max_length=255)
    streaming_key = CharField(default="", max_length=255)
