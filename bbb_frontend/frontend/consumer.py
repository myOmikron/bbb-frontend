import hashlib

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from frontend.counter import viewers


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
