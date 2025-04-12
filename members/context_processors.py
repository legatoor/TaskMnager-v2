def notifications(request):
    """Add notification count to the context of all templates."""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}

def online_users(request):
    """Add online users count to context"""
    if request.user.is_authenticated:
        from django.contrib.auth.models import User
        from django.utils import timezone
        import datetime
        
        online_threshold = timezone.now() - datetime.timedelta(minutes=15)
        online_count = User.objects.filter(last_login__gte=online_threshold).count()
        
        return {
            'online_users_count': online_count
        }
    return {'online_users_count': 0}
