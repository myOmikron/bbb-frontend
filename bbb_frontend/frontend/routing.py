from channels.routing import URLRouter
from channels.sessions import SessionMiddlewareStack
from django.urls import re_path

from frontend.consumer import WebsocketConsumer


websocket = SessionMiddlewareStack(
    URLRouter([
        re_path(r"watch/(?P<meeting_id>.+)", WebsocketConsumer.as_asgi()),
    ])
)
