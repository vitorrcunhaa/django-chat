import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

import chat.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
	'http': asgi_application,
	'websocket':
	AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter(chat.routing.websocket_urlpatterns)
		),
	)
})
