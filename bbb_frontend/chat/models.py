from django.db import models

from frontend.models import Channel


class Chat(models.Model):

    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)
    callback_uri = models.CharField(max_length=255, default="")
    callback_secret = models.CharField(max_length=255, default="")
    callback_id = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.channel.meeting_id
