import hashlib
import json
import logging
import os
from time import time

from channels.consumer import SyncConsumer
from channels.exceptions import InvalidChannelLayerError
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from rc_protocol import get_checksum
import requests
import httpx

from chat.models import Chat


class ChatConsumer(AsyncWebsocketConsumer):

    meeting_id: str
    user_name: str

    logger = logging.getLogger(f"{__name__}.ChatConsumer")

    @database_sync_to_async
    def load_session(self):
        "Please don't be lazy" in self.scope["session"]._wrapped

    @database_sync_to_async
    def get_chat(self):
        try:
            return Chat.objects.get(self.meeting_id)
        except Chat.DoesNotExist:
            return None

    async def websocket_connect(self, message):
        # Store relevant data
        self.user_name = self.scope["session"]["user_name"]
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]

        # Check for valid session data
        await self.load_session()
        if "checksum" not in self.scope["session"]:
            await self.close(1008)
            return
        if "user_name" not in self.scope["session"]:
            await self.close(1008)
            return

        # Check checksum
        tmp_checksum = hashlib.sha512(
            f"{self.user_name}{self.meeting_id}{settings.SHARED_SECRET}".encode("utf-8")
        ).hexdigest()
        if self.scope["session"]["checksum"] != tmp_checksum:
            await self.close(1008)
            return

        # Setup channel group
        self.groups.append(self.meeting_id)
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError(
                "BACKEND is unconfigured or doesn't support groups"
            )

        # Accept connection
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

        if data["type"] == "chat.message":
            data["user_name"] = self.user_name
            # await self.channel_layer.send("chatCallback", {"chat_id": self.meeting_id, **data})
            await self.channel_layer.group_send(self.meeting_id, data)

            chat = await self.get_chat()
            if chat:
                params = {
                    "chat_id": self.meeting_id,
                    "user_name": self.user_name,
                    "message": data["message"]
                }
                params["checksum"] = get_checksum(params, chat.callback_secret, "sendMessage")

                before = time()
                async with httpx.AsyncClient() as client:
                    await client.post(chat.callback_uri.rstrip("/") + "sendMessage", json=params)
                self.logger.debug(f"Took {time() - before:.3f}ms to send request")
        else:
            raise ValueError(f"Incoming WebSocket json object is of unknown type: '{data['type']}'")

    async def chat_message(self, message):
        await self.send(text_data=json.dumps(message))


class ChatCallbackConsumer(SyncConsumer):

    logger = logging.getLogger(f"{__name__}.callback")

    def chat_message(self, message):
        self.logger.debug(f"Received chat message: {message}")

        try:
            chat = Chat.objects.get(message["chat_id"])
        except Chat.DoesNotExist:
            self.logger.debug("Skipping because the channel doesn't have a running chat bridge")
            return

        if not chat.callback_uri:
            self.logger.debug("Skipping because the chat bridge has no registered callback")
            return

        params = {
            "chat_id": chat.callback_id,
            "user_name": message["user_name"],
            "message": message["message"],
        }
        params["checksum"] = get_checksum(params, chat.callback_secret, "sendMessage")

        requests.post(os.path.join(chat.callback_uri, "sendMessage"), json=params)
