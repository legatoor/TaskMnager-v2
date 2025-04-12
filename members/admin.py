from django.contrib import admin
from .models import UserProfile, Category, Task, Comment, Notification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'user__email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'created_by')
    search_fields = ('name',)
    list_filter = ('created_by',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_date'
    filter_horizontal = ('observers',)  # Add this line for better M2M field display

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'task__title', 'message')
