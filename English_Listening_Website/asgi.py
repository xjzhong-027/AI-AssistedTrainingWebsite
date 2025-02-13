"""
ASGI config for English_Listening_Website project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""


import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import announce.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from .scheduler import start_scheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'English_Listening_Website.settings')
django.setup()

application = AuthMiddlewareStack(
    get_asgi_application()
)

# 将 announce 应用的 WebSocket 路由添加到 ASGI 应用中
application = ProtocolTypeRouter({
    'http': application,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            announce.routing.websocket_urlpatterns
        )
    ),
})

start_scheduler()

