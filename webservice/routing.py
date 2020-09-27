from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chatbot_webservice.routing

application = ProtocolTypeRouter({
    'websocket':
        URLRouter(
            chatbot_webservice.routing.websocket_urlpatterns
        )
})
