from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found
from members.views import custom_404
from django.http import JsonResponse


def api_root(request):
    return JsonResponse(
        {
            "message": "Welcome to Task Manager API",
            "endpoints": ["/users/", "/tasks/", "/categories/"],
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # Frontend routes
    path("", include("members.urls")),
]

# Conditionally include API URLs if REST framework is installed
try:
    import rest_framework
    from api.urls import router

    # Add API routes with a separate namespace
    urlpatterns += [
        path("api/", api_root, name="api-root"),
        path("api/", include((router.urls, "api"))),
    ]
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Set up custom error handlers
handler404 = "members.views.custom_404"
