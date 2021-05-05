import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from frontend.routing import websocket


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bbb_frontend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": websocket,
})
