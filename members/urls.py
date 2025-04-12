from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    
    # Auth URLs - Use CustomLoginView
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='members/logout.html',
        next_page='home'
    ), name='logout'),
    
    # Task URLs
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/new/', views.TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:task_id>/comment/', views.add_comment, name='add-comment'),
    
    # Task templates for AJAX loading
    path('tasks/task-template/<int:task_id>/', views.task_template, name='task-template'),
    path('tasks/task-row-template/<int:task_id>/', views.task_row_template, name='task-row-template'),
    path('tasks/detail-template/<int:task_id>/', views.task_detail_partial, name='task-detail-partial'),
    
    # Category templates for AJAX loading
    path('categories/category-template/<int:category_id>/', views.category_template, name='category-template'),
    
    # AJAX comment submission
    path('tasks/<int:task_id>/comment-ajax/', views.comment_form_submit, name='comment-ajax'),
    
    # New Kanban board URLs
    path('kanban/', views.kanban_board, name='kanban-board'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update-task-status'),
    
    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    
    # Profile URL
    path('profile/', views.profile, name='profile'),
    
    # Employee List URL
    path('employees/', views.employee_list, name='employee-list'),
    
    # New partial template endpoints for real-time updates
    path('tasks/<int:task_id>/observers-partial/', views.task_observers_partial, name='task-observers-partial'),
    path('api/notifications/unread-count/', views.get_unread_notification_count, name='notification-unread-count'),
    path('categories/partial/', views.categories_list_partial, name='categories-list-partial'),
]
