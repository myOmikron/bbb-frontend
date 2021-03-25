from django.db import models
from channels.db import database_sync_to_async

from frontend.models import Channel


class CachedManager(models.Manager):

    def __init__(self, field_name):
        super().__init__()
        self.field = field_name
        self.cache = {}

    async def aget(self, value, **kwargs):
        if value is None:
            return await database_sync_to_async(super().get)(**kwargs)
        elif value not in self.cache:
            self.cache[value] = await database_sync_to_async(super().get)((self.field, value))
            return self.cache[value]
        else:
            if self.cache[value].id is None:
                del self.cache[value]
                raise self.model.DoesNotExist
            else:
                return self.cache[value]

    def get(self, value=None, **kwargs):
        if value is None:
            return super().get(**kwargs)
        elif value not in self.cache:
            self.cache[value] = super().get((self.field, value))
            return self.cache[value]
        else:
            if self.cache[value].id is None:
                del self.cache[value]
                raise self.model.DoesNotExist
            else:
                return self.cache[value]


class Chat(models.Model):

    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)
    callback_uri = models.CharField(max_length=255, default="")
    callback_secret = models.CharField(max_length=255, default="")
    callback_id = models.CharField(max_length=255, default="")

    objects = CachedManager("channel__meeting_id")

    def __str__(self):
        return self.channel.meeting_id
