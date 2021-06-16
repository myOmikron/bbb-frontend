import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bbb_frontend.settings')

from django.core.asgi import get_asgi_application

http = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from frontend.routing import websocket

application = ProtocolTypeRouter({
    "http": http,
    "websocket": websocket,
})
