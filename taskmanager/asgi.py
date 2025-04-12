"""
ASGI config for taskmanager project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

# Get the ASGI application first
django_asgi_app = get_asgi_application()

# Try to import channels and set up WebSocket routing
try:
    import channels
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.security.websocket import AllowedHostsOriginValidator

    # Try to import websocket_urlpatterns
    try:
        from members.routing import websocket_urlpatterns

        print(f"WebSocket URL patterns: {websocket_urlpatterns}")
        print("URL patterns found. WebSocket routes will be available at:")
        for pattern in websocket_urlpatterns:
            print(f" - {pattern.pattern}")

        application = ProtocolTypeRouter(
            {
                "http": django_asgi_app,
                "websocket": AllowedHostsOriginValidator(
                    AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
                ),
            }
        )
        print("ASGI application configured with Channels WebSocket support")

    except ImportError as e:
        print(f"Error importing websocket_urlpatterns: {e}")
        application = ProtocolTypeRouter(
            {
                "http": django_asgi_app,
            }
        )
        print(
            "ASGI application configured with Channels (but no WebSocket patterns found)"
        )

except ImportError as e:
    print(f"Django Channels not found: {e}")
    print("WARNING: Using standard ASGI application without WebSocket support")
    application = django_asgi_app
