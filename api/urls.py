from django.urls import path, include
from django.http import JsonResponse

# Fallback view when REST framework is not installed
def api_not_available(request):
    return JsonResponse({
        'error': 'API is not available',
        'detail': 'Django REST Framework is not installed. Install it with: pip install djangorestframework'
    }, status=501)

urlpatterns = [
    path('', api_not_available, name='api-root'),
]

# Use REST framework if available
try:
    from rest_framework.routers import DefaultRouter
    from . import views
    
    router = DefaultRouter()
    router.register(r'users', views.UserViewSet)
    router.register(r'categories', views.CategoryViewSet)
    router.register(r'tasks', views.TaskViewSet)
    router.register(r'comments', views.CommentViewSet)
    router.register(r'profiles', views.UserProfileViewSet)
    
    urlpatterns = router.urls + [
        path('auth/', api_not_available, name='api-auth'),
    ]
    
    # Try to include REST auth views if possible
    try:
        from rest_framework.urls import urlpatterns as auth_urlpatterns
        urlpatterns += [path('auth/', include('rest_framework.urls'))]
    except ImportError:
        pass
        
except ImportError:
    pass
