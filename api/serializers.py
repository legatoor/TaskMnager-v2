from django.contrib.auth.models import User
from members.models import Task, Category, UserProfile, Comment

# Try to use REST framework if available
try:
    from rest_framework import serializers

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'first_name', 'last_name']

    class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = '__all__'

    class TaskSerializer(serializers.ModelSerializer):
        class Meta:
            model = Task
            fields = '__all__'
            
    class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = '__all__'

    class UserProfileSerializer(serializers.ModelSerializer):
        user = UserSerializer(read_only=True)
        
        class Meta:
            model = UserProfile
            fields = '__all__'
            
except ImportError:
    # Create empty classes as placeholders
    class EmptySerializer:
        pass
        
    UserSerializer = CategorySerializer = TaskSerializer = CommentSerializer = UserProfileSerializer = EmptySerializer
