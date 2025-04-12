import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class UserStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for tracking user online/offline status
    """
    
    async def connect(self):
        try:
            # Accept the WebSocket connection
            await self.accept()
            logger.info(f"WebSocket connection accepted: {self.channel_name}")
            
            # Add to user group for broadcasts
            await self.channel_layer.group_add(
                "user_status",
                self.channel_name
            )
            logger.info(f"Added {self.channel_name} to user_status group")
            
            # Update user as online if authenticated
            if self.scope["user"].is_authenticated:
                logger.info(f"User authenticated: {self.scope['user'].username}")
                await self.set_user_online(self.scope["user"])
                
                # Broadcast to others that this user is online
                await self.channel_layer.group_send(
                    "user_status",
                    {
                        "type": "user_status_change",
                        "user_id": self.scope["user"].id,
                        "status": "online"
                    }
                )
            else:
                logger.warning("User not authenticated")
            
            # Send current online users to the newly connected client
            online_users = await self.get_online_users()
            logger.info(f"Sending online users: {len(online_users)} users")
            await self.send(text_data=json.dumps({
                'type': 'user_list',
                'users': online_users
            }))
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            logger.error(traceback.format_exc())
            # Still accept connection to avoid connection errors
            if not hasattr(self, 'accepted') or not self.accepted:
                await self.accept()
            # Send error message
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def disconnect(self, close_code):
        # Remove from group
        await self.channel_layer.group_discard(
            "user_status",
            self.channel_name
        )
        
        # Mark user as offline if authenticated
        if self.scope["user"].is_authenticated:
            await self.set_user_offline(self.scope["user"])
            
            # Broadcast to others that this user is offline
            await self.channel_layer.group_send(
                "user_status",
                {
                    "type": "user_status_change",
                    "user_id": self.scope["user"].id,
                    "status": "offline"
                }
            )

    async def receive(self, text_data):
        # Handle messages from client (not required for this feature)
        pass

    # Handle broadcast messages about user status changes
    async def user_status_change(self, event):
        # Send status change notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status_change',
            'user_id': event['user_id'],
            'status': event['status']
        }))

    @database_sync_to_async
    def set_user_online(self, user):
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

    @database_sync_to_async
    def set_user_offline(self, user):
        # We keep the last_login time but will use it with a threshold check
        pass

    @database_sync_to_async
    def get_online_users(self):
        # Consider users with activity in last 15 minutes as online
        online_threshold = timezone.now() - datetime.timedelta(minutes=15)
        users = User.objects.all().values('id', 'username')
        
        # Add status to each user based on last_login
        user_list = list(users)
        for user in user_list:
            # Check if user has logged in recently and mark as online/offline
            user_obj = User.objects.get(id=user['id'])
            if user_obj.last_login and user_obj.last_login >= online_threshold:
                user['status'] = 'online'
            else:
                user['status'] = 'offline'
        
        return user_list


class EchoConsumer(AsyncWebsocketConsumer):
    """
    Simple echo consumer for testing WebSockets
    """
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Hello from the server!'
        }))
    
    async def receive(self, text_data):
        await self.send(text_data=f"Echo: {text_data}")
    
    async def disconnect(self, close_code):
        pass


class TaskManagerConsumer(AsyncWebsocketConsumer):
    """
    General WebSocket consumer for all real-time updates in the Task Manager
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Add to the task_updates group
        await self.channel_layer.group_add(
            "task_updates",
            self.channel_name
        )
        
        # Add to specific user group if authenticated
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
            
            # Add to user_updates group
            await self.channel_layer.group_add(
                "user_updates",
                self.channel_name
            )
        
        await self.accept()
        
        # Send connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': 'connected',
            'message': 'Successfully connected to TaskManager WebSocket'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove from the task_updates group
        await self.channel_layer.group_discard(
            "task_updates",
            self.channel_name
        )
        
        # Remove from user-specific group if authenticated
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
            
            # Remove from user_updates group
            await self.channel_layer.group_discard(
                "user_updates",
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            # Handle different message types
            if message_type == 'task_status_change':
                # Handle task status change requests
                if self.scope["user"].is_authenticated:
                    task_id = data.get('task_id')
                    new_status = data.get('status')
                    
                    # Update the task status in the database
                    success = await self.update_task_status(task_id, new_status, self.scope["user"])
                    
                    if success:
                        # The broadcast will happen through signals
                        await self.send(text_data=json.dumps({
                            'type': 'status_update_response',
                            'success': True,
                            'task_id': task_id
                        }))
                    else:
                        await self.send(text_data=json.dumps({
                            'type': 'status_update_response',
                            'success': False,
                            'message': 'Не удалось обновить статус задачи.'
                        }))
            
            elif message_type == 'new_comment':
                # Handle new comment submission
                if self.scope["user"].is_authenticated:
                    await self.process_new_comment(data, self.scope["user"])
            
            elif message_type == 'mark_notification_read':
                # Handle marking notification as read
                if self.scope["user"].is_authenticated:
                    notification_id = data.get('notification_id')
                    await self.mark_notification_read(notification_id, self.scope["user"])
            
            elif message_type == 'mark_all_notifications_read':
                # Handle marking all notifications as read
                if self.scope["user"].is_authenticated:
                    await self.mark_all_notifications_read(self.scope["user"])
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Получены некорректные данные.'
            }))
        except Exception as e:
            logger.error(f"Error in TaskManagerConsumer.receive: {str(e)}")
            logger.error(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Произошла ошибка: {str(e)}'
            }))

    # Event handlers for broadcasts from channels layer

    async def task_update(self, event):
        """Handle task update broadcasts"""
        # Forward the update to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'task_id': event['task_id'],
            'action': event['action'],  # 'created', 'updated', or 'deleted'
            'task_data': event.get('task_data', {}),
            'updated_by': event.get('updated_by', {})
        }))

    async def task_comment(self, event):
        """Handle new comment broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'task_comment',
            'task_id': event['task_id'],
            'comment_id': event['comment_id'],
            'comment_data': event['comment_data']
        }))
    
    async def task_comment_deleted(self, event):
        """Handle comment deletion broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'task_comment_deleted',
            'task_id': event['task_id'],
            'comment_id': event['comment_id']
        }))
    
    async def task_observers_update(self, event):
        """Handle task observers update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'task_observers_update',
            'task_id': event['task_id'],
            'action': event['action'],
            'task_data': event.get('task_data', {})
        }))

    async def notification(self, event):
        """Handle notification broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_id': event['notification_id'],
            'message': event['message'],
            'task_id': event.get('task_id')
        }))
    
    async def notification_update(self, event):
        """Handle notification status update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'notification_id': event['notification_id'],
            'action': event['action'],
            'user_id': event['user_id'],
            'notification_data': event.get('notification_data', {})
        }))

    async def category_update(self, event):
        """Handle category update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'category_update',
            'category_id': event['category_id'],
            'action': event['action'],
            'category_data': event.get('category_data', {})
        }))
    
    async def user_update(self, event):
        """Handle user update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'user_update',
            'user_id': event['user_id'],
            'action': event['action'],
            'user_data': event.get('user_data', {})
        }))
    
    async def user_profile_update(self, event):
        """Handle user profile update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'user_profile_update',
            'user_id': event['user_id'],
            'action': event['action'],
            'user_data': event.get('user_data', {})
        }))

    # Database operations

    @database_sync_to_async
    def update_task_status(self, task_id, new_status, user):
        """Update task status in the database"""
        from members.models import Task
        try:
            task = Task.objects.get(id=task_id)
            
            # Check if user has permission to update this task
            if user == task.assigned_to or user == task.created_by or user.is_superuser:
                task.status = new_status
                task.save()
                return True
            return False
        except Task.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")
            return False

    @database_sync_to_async
    def process_new_comment(self, data, user):
        """Create a new comment in the database"""
        from members.models import Task, Comment
        try:
            task_id = data.get('task_id')
            text = data.get('text')
            
            if not text or text.strip() == '':
                return False
                
            task = Task.objects.get(id=task_id)
            comment = Comment.objects.create(
                task=task,
                user=user,
                text=text
            )
            
            # Note: The broadcast will be handled by signals
            return True
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id, user):
        """Mark a notification as read"""
        from members.models import Notification
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            if not notification.is_read:
                notification.is_read = True
                notification.save()
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self, user):
        """Mark all notifications as read for a user"""
        from members.models import Notification
        try:
            Notification.objects.filter(user=user, is_read=False).update(is_read=True)
            return True
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return False
