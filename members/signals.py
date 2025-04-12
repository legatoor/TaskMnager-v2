import json
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import UserProfile, Task, Comment, Category, Notification

channel_layer = get_channel_layer()

def get_task_data(task):
    """Serialize task data for broadcast"""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'assigned_to': {
            'id': task.assigned_to.id,
            'username': task.assigned_to.username
        } if task.assigned_to else None,
        'category': {
            'id': task.category.id,
            'name': task.category.name,
            'color': task.category.color
        } if task.category else None,
        'created_date': task.created_date.isoformat()
    }

def get_user_data(user):
    """Serialize user data for broadcast"""
    return {
        'id': user.id,
        'username': user.username
    } if user else None

def get_category_data(category):
    """Serialize category data for broadcast"""
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_by': get_user_data(category.created_by) if category.created_by else None
    }

def get_comment_data(comment):
    """Serialize comment data for broadcast"""
    return {
        'id': comment.id,
        'text': comment.text,
        'created_at': comment.created_at.isoformat(),
        'user': get_user_data(comment.user)
    }
    
def get_notification_data(notification):
    """Serialize notification data for broadcast"""
    return {
        'id': notification.id,
        'message': notification.message,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat(),
        'task': get_task_data(notification.task) if notification.task else None,
        'user': get_user_data(notification.user)
    }

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for each new User."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
    
    # Broadcast user update to all clients
    try:
        async_to_sync(channel_layer.group_send)(
            "user_updates",
            {
                "type": "user_update",
                "user_id": instance.id,
                "action": "updated",
                "user_data": get_user_data(instance)
            }
        )
    except Exception as e:
        print(f"Error broadcasting user update: {str(e)}")

@receiver(post_save, sender=Task)
def notify_task_updated(sender, instance, created, **kwargs):
    """Notify observers when a task is updated."""
    # Only process updates, not creations
    if not created:
        # Logic to notify observers about the update
        # This would typically involve sending emails or in-app notifications
        # For now, we'll just print to the console
        observer_usernames = ", ".join([user.username for user in instance.observers.all()])
        if observer_usernames:
            print(f"Task '{instance.title}' updated. Notifying observers: {observer_usernames}")

@receiver(post_save, sender=Task)
def create_task_notifications(sender, instance, created, **kwargs):
    """Create notifications for observers when a task is updated."""
    from .models import Notification  # Import here to avoid circular import
    
    # If this is a new task, no need to notify about updates
    if created:
        return
    
    # Create notifications for all observers
    for observer in instance.observers.all():
        # Skip creating notification for the user who made the change (would need to be passed)
        # if observer == updated_by:
        #     continue
        
        Notification.objects.create(
            user=observer,
            task=instance,
            message=f"Задача '{instance.title}' была обновлена."
        )

@receiver(m2m_changed, sender=Task.observers.through)
def handle_observers_changed(sender, instance, action, **kwargs):
    """Handle when observers are added or removed from a task."""
    if action in ["post_add", "post_remove", "post_clear"]:
        print(f"Observers for task '{instance.title}' have been updated.")
        # Broadcast observer changes
        try:
            async_to_sync(channel_layer.group_send)(
                "task_updates",
                {
                    "type": "task_observers_update",
                    "task_id": instance.id,
                    "action": action,
                    "task_data": get_task_data(instance)
                }
            )
        except Exception as e:
            print(f"Error broadcasting observer changes: {str(e)}")

@receiver(post_save, sender=Task)
def task_saved_handler(sender, instance, created, **kwargs):
    """Broadcast task updates to connected clients"""
    action = 'created' if created else 'updated'
    task_data = get_task_data(instance)
    
    print(f"Broadcasting task {action}: {instance.title}")
    
    # Broadcast to all clients
    try:
        async_to_sync(channel_layer.group_send)(
            "task_updates",
            {
                "type": "task_update",
                "task_id": instance.id,
                "action": action,
                "task_data": task_data,
                "updated_by": get_user_data(instance.created_by)
            }
        )
        print(f"Successfully broadcast task {action}")
    except Exception as e:
        print(f"Error broadcasting task update: {str(e)}")
    
    # Send to specific users that need to be notified
    if not created:
        # Notify observers when task is updated
        for observer in instance.observers.all():
            try:
                async_to_sync(channel_layer.group_send)(
                    f"user_{observer.id}",
                    {
                        "type": "notification",
                        "notification_id": None,
                        "message": f"Задача \"{instance.title}\" была обновлена",
                        "task_id": instance.id
                    }
                )
            except Exception as e:
                print(f"Error sending notification: {str(e)}")
    else:
        # For new tasks, notify assigned user
        if instance.assigned_to and instance.assigned_to != instance.created_by:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"user_{instance.assigned_to.id}",
                    {
                        "type": "notification",
                        "notification_id": None,
                        "message": f"Вам назначена новая задача: \"{instance.title}\"",
                        "task_id": instance.id
                    }
                )
            except Exception as e:
                print(f"Error sending notification to assigned user: {str(e)}")

@receiver(post_delete, sender=Task)
def task_deleted_handler(sender, instance, **kwargs):
    """Broadcast task deletion to connected clients"""
    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "task_update",
            "task_id": instance.id,
            "action": "deleted",
            "task_data": {"id": instance.id}
        }
    )

@receiver(post_save, sender=Comment)
def comment_saved_handler(sender, instance, created, **kwargs):
    """Broadcast comment creation to connected clients"""
    if created:
        # Only broadcast new comments
        comment_data = get_comment_data(instance)
        
        async_to_sync(channel_layer.group_send)(
            "task_updates",
            {
                "type": "task_comment",
                "task_id": instance.task.id,
                "comment_id": instance.id,
                "comment_data": comment_data
            }
        )

@receiver(post_delete, sender=Comment)
def comment_deleted_handler(sender, instance, **kwargs):
    """Broadcast comment deletion to connected clients"""
    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "task_comment_deleted",
            "task_id": instance.task.id,
            "comment_id": instance.id
        }
    )

@receiver(post_save, sender=Notification)
def notification_saved_handler(sender, instance, created, **kwargs):
    """Send notifications to specific users"""
    if created:
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                "type": "notification",
                "notification_id": instance.id,
                "message": instance.message,
                "task_id": instance.task.id if instance.task else None
            }
        )
        
        # Also broadcast to task_updates group for real-time updates of notification counters
        async_to_sync(channel_layer.group_send)(
            "task_updates",
            {
                "type": "notification_update",
                "notification_id": instance.id,
                "action": "created",
                "user_id": instance.user.id,
                "notification_data": get_notification_data(instance)
            }
        )

@receiver(post_save, sender=Notification)
def notification_updated_handler(sender, instance, created, **kwargs):
    """Broadcast notification updates (like mark as read)"""
    if not created:
        async_to_sync(channel_layer.group_send)(
            "task_updates",
            {
                "type": "notification_update",
                "notification_id": instance.id,
                "action": "updated",
                "user_id": instance.user.id,
                "notification_data": get_notification_data(instance)
            }
        )

@receiver(post_save, sender=Category)
def category_saved_handler(sender, instance, created, **kwargs):
    """Broadcast category updates"""
    action = 'created' if created else 'updated'
    category_data = get_category_data(instance)
    
    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "category_update",
            "category_id": instance.id,
            "action": action,
            "category_data": category_data
        }
    )

@receiver(post_delete, sender=Category)
def category_deleted_handler(sender, instance, **kwargs):
    """Broadcast category deletion"""
    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "category_update",
            "category_id": instance.id,
            "action": "deleted",
            "category_data": {"id": instance.id}
        }
    )

@receiver(post_save, sender=UserProfile)
def profile_saved_handler(sender, instance, created, **kwargs):
    """Broadcast profile updates"""
    try:
        user_data = get_user_data(instance.user)
        # Add profile data
        user_data['profile'] = {
            'bio': instance.bio,
            'profile_picture': instance.profile_picture.url if instance.profile_picture else None
        }
        
        async_to_sync(channel_layer.group_send)(
            "user_updates",
            {
                "type": "user_profile_update",
                "user_id": instance.user.id,
                "action": "updated",
                "user_data": user_data
            }
        )
    except Exception as e:
        print(f"Error broadcasting profile update: {str(e)}")