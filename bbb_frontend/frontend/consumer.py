import hashlib
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.exceptions import InvalidChannelLayerError
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings

from frontend.counter import viewers
from frontend.models import Channel

channel_layer = get_channel_layer()


class WebsocketConsumer(AsyncWebsocketConsumer):

    meeting_id: str

    @database_sync_to_async
    def load_session(self):
        "Please don't be lazy" in self.scope["session"]

    async def websocket_connect(self, message):
        # Check for valid session data
        await self.load_session()
        if "checksum" not in self.scope["session"]:
            await self.close(1008)
            return
        if "user_name" not in self.scope["session"]:
            await self.close(1008)
            return

        # Store relevant data
        user_name = self.scope["session"]["user_name"]
        meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]

        # Check checksum
        tmp_checksum = hashlib.sha512(
            f"{user_name}{meeting_id}{settings.SHARED_SECRET}".encode("utf-8")
        ).hexdigest()
        if self.scope["session"]["checksum"] != tmp_checksum:
            await self.close(1008)
            return

        # Setup channel group
        self.groups.append(meeting_id)
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError(
                "BACKEND is unconfigured or doesn't support groups"
            )

        # Accept connection
        await self.accept()

        # Increment the viewer count by 1
        await viewers[meeting_id].increment()

        # Save meeting and user
        # => When these aren't set, this method didn't terminate correctly and the counter wasn't incremented
        self.meeting_id = meeting_id

    def __del__(self):
        # Check if consumer has finished connecting
        if hasattr(self, "meeting_id"):
            # Decrement the viewer count by 1
            viewers[self.meeting_id].decrement()

    async def page_reload(self, message):
        await self.send(text_data=json.dumps(message))

    async def page_redirect(self, message):
        await self.send(text_data=json.dumps(message))

    @staticmethod
    def reload(meeting_id):
        async_to_sync(channel_layer.group_send)(meeting_id, {
            "type": "page.reload",
        })

    @staticmethod
    def redirect(meeting_id):
        async_to_sync(channel_layer.group_send)(meeting_id, {
            "type": "page.redirect",
            "url": Channel.objects.get(meeting_id=meeting_id).redirect_url,
        })
