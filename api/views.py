from django.http import JsonResponse
from django.contrib.auth.models import User
from members.models import Task, Category, UserProfile, Comment

# Define fallback views when REST framework is not installed
def get_api_info(request):
    return JsonResponse({
        'message': 'API is not fully available',
        'detail': 'Django REST Framework is not installed. Install it with: pip install djangorestframework'
    })

# Try to use REST framework if available
try:
    from rest_framework import viewsets
    from rest_framework.permissions import IsAuthenticated
    from .serializers import (
        UserSerializer, CategorySerializer, 
        TaskSerializer, CommentSerializer, UserProfileSerializer
    )

    class UserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        permission_classes = [IsAuthenticated]

    class CategoryViewSet(viewsets.ModelViewSet):
        queryset = Category.objects.all()
        serializer_class = CategorySerializer
        permission_classes = [IsAuthenticated]

    class TaskViewSet(viewsets.ModelViewSet):
        queryset = Task.objects.all()
        serializer_class = TaskSerializer
        permission_classes = [IsAuthenticated]
        
        def get_queryset(self):
            queryset = Task.objects.all()
            user = self.request.query_params.get('user')
            status = self.request.query_params.get('status')
            
            if user:
                queryset = queryset.filter(assigned_to__id=user)
            if status:
                queryset = queryset.filter(status=status)
                
            return queryset

    class CommentViewSet(viewsets.ModelViewSet):
        queryset = Comment.objects.all()
        serializer_class = CommentSerializer
        permission_classes = [IsAuthenticated]
        
        def get_queryset(self):
            queryset = Comment.objects.all()
            task = self.request.query_params.get('task')
            
            if task:
                queryset = queryset.filter(task__id=task)
                
            return queryset

    class UserProfileViewSet(viewsets.ModelViewSet):
        queryset = UserProfile.objects.all()
        serializer_class = UserProfileSerializer
        permission_classes = [IsAuthenticated]
        
except ImportError:
    # Define placeholders for missing ViewSets
    UserViewSet = CategoryViewSet = TaskViewSet = CommentViewSet = UserProfileViewSet = None
