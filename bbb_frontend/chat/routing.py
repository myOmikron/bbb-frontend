from channels.routing import URLRouter, ChannelNameRouter
from channels.sessions import SessionMiddlewareStack
from django.urls import re_path

from chat.consumer import ChatConsumer, ChatCallbackConsumer

websocket = SessionMiddlewareStack(
    URLRouter([
        re_path(r"watch/(?P<meeting_id>.+)", ChatConsumer.as_asgi()),
    ])
)

channel = ChannelNameRouter({
    "chatCallback": ChatCallbackConsumer.as_asgi(),
})
