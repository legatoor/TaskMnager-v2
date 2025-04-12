from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    
    # Check if Pillow is installed before using ImageField
    try:
        from PIL import Image
        profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    except ImportError:
        # Use FileField as a fallback if Pillow is not available
        profile_picture = models.FileField(upload_to='profile_pics', blank=True, null=True)
        # Or if you prefer to avoid the dependency completely:
        # profile_picture = models.CharField(max_length=255, blank=True, null=True, help_text="Path to profile picture (Pillow not installed)")
    
    @property
    def is_online(self):
        """Check if user is currently online (active in last 15 minutes)"""
        if self.user.last_login:
            return timezone.now() - datetime.timedelta(minutes=15) < self.user.last_login
        return False
    
    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Категории"

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'К выполнению'),
        ('IN_PROGRESS', 'В процессе'),
        ('REVIEW', 'На проверке'),
        ('DONE', 'Выполнено'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
        (4, 'Срочно'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Add observers field - users who want to be notified about changes
    observers = models.ManyToManyField(User, related_name='observed_tasks', blank=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий от {self.user.username} к задаче {self.task.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username} about {self.task.title}"
