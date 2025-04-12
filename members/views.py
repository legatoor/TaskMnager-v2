from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Task, Category, Comment, UserProfile, Notification
from .forms import TaskForm, CommentForm, UserRegisterForm, UserProfileForm, CategoryForm
from django.http import Http404, JsonResponse
from django.contrib.auth.views import LoginView
from django.db import models
import logging
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'members/home.html')

@login_required
def dashboard(request):
    user_tasks = Task.objects.filter(assigned_to=request.user).order_by('status', '-priority', 'due_date')
    created_tasks = Task.objects.filter(created_by=request.user).order_by('-created_date')
    return render(request, 'members/dashboard.html', {
        'user_tasks': user_tasks,
        'created_tasks': created_tasks
    })

def register(request):
    if request.method == 'POST':
        logger.debug("Обработка POST-запроса для регистрации")
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            logger.debug("Форма валидна, создание пользователя")
            user = form.save()
            # UserProfile is created via signals
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для пользователя {username}! Теперь вы можете войти.')
            logger.debug(f"Пользователь {username} успешно создан, перенаправление на вход")
            return redirect('login')
        else:
            logger.debug(f"Ошибка валидации формы: {form.errors}")
    else:
        logger.debug("Отображение пустой формы регистрации")
        form = UserRegisterForm()
    return render(request, 'members/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view for displaying and updating user profile information."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль был обновлен!')
            return redirect('profile')
    else:
        # Create form instance with current profile data
        form = UserProfileForm(instance=request.user.profile)
    
    context = {'form': form}
    
    # If this is a partial request, return only the profile content
    if request.GET.get('partial') == 'true':
        return render(request, 'members/partials/profile_content.html', context)
    
    return render(request, 'members/profile.html', context)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'members/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        assigned_to = self.request.GET.get('assigned_to')
        created_by = self.request.GET.get('created_by')
        
        queryset = Task.objects.all()
        
        if category:
            queryset = queryset.filter(category__id=category)
        if status:
            queryset = queryset.filter(status=status)
        if assigned_to:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if created_by:
            queryset = queryset.filter(created_by__id=created_by)
            
        # Get tasks by status for template context
        self.todo_tasks = queryset.filter(status='TODO').order_by('-priority', 'due_date')
        self.in_progress_tasks = queryset.filter(status='IN_PROGRESS').order_by('-priority', 'due_date')
        self.review_tasks = queryset.filter(status='REVIEW').order_by('-priority', 'due_date')
        self.done_tasks = queryset.filter(status='DONE').order_by('-priority', 'due_date')
        
        return queryset.order_by('status', '-priority', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['users'] = User.objects.all()
        context['status_choices'] = Task.STATUS_CHOICES
        
        # Add task lists to context
        context['todo_tasks'] = getattr(self, 'todo_tasks', Task.objects.none())
        context['in_progress_tasks'] = getattr(self, 'in_progress_tasks', Task.objects.none())
        context['review_tasks'] = getattr(self, 'review_tasks', Task.objects.none())
        context['done_tasks'] = getattr(self, 'done_tasks', Task.objects.none())
        
        # Add counters
        context['todo_count'] = context['todo_tasks'].count()
        context['in_progress_count'] = context['in_progress_tasks'].count()
        context['review_count'] = context['review_tasks'].count()
        context['done_count'] = context['done_tasks'].count()
        
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'members/task_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'members/task_form.html'
    success_url = reverse_lazy('task-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Pass request to form
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Задача успешно создана!')
        
        # Note: We don't need to manually broadcast here as it's handled by signals
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_websocket_enabled'] = True  # Flag to enable WebSocket in template
        return context

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'members/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Pass request to form
        return kwargs
    
    def get_queryset(self):
        """ 
        Filter queryset to only allow:
        - Admin users to edit any task
        - Users to edit tasks they created
        - Users to edit tasks assigned to them
        """
        base_queryset = Task.objects.all()
        user = self.request.user
        
        if user.is_superuser:
            return base_queryset
        
        # Allow both the creator and the assigned user to edit
        return base_queryset.filter(
            models.Q(created_by=user) | models.Q(assigned_to=user)
        )
    
    def get_success_url(self):
        return reverse_lazy('task-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Задача успешно обновлена!')
        return response
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет разрешения на редактирование этой задачи.")
        return redirect('task-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_websocket_enabled'] = True  # Flag to enable WebSocket in template
        return context

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'members/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')
    
    def get_queryset(self):
        """
        Filter queryset to only allow:
        - Admin users to delete any task
        - Users to delete tasks they created
        """
        base_queryset = Task.objects.all()
        user = self.request.user
        
        if user.is_superuser:
            return base_queryset
        
        # Only allow the creator to delete
        return base_queryset.filter(created_by=user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Задача успешно удалена!')
        return super().delete(request, *args, **kwargs)
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет разрешения на удаление этой задачи.")
        return redirect('task-list')

@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен!')
            return redirect('task-detail', pk=task_id)
    
    return redirect('task-detail', pk=task_id)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'members/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        Get all categories and assign current user as creator for categories without a creator.
        This is a temporary fix after adding the created_by field.
        """
        queryset = Category.objects.all()
        
        # Count categories without a creator
        unclaimed_count = queryset.filter(created_by__isnull=True).count()
        
        # If there are unclaimed categories and the user is either a superuser or staff,
        # assign them to the current user
        if unclaimed_count > 0 and (self.request.user.is_superuser or self.request.user.is_staff):
            # Get the categories without a creator
            unclaimed_categories = queryset.filter(created_by__isnull=True)
            
            # Assign the current user as the creator
            for category in unclaimed_categories:
                category.created_by = self.request.user
                category.save()
        
        return queryset

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'members/category_form.html'
    success_url = reverse_lazy('category-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Категория успешно создана!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'members/category_form.html'
    success_url = reverse_lazy('category-list')
    
    def get_queryset(self):
        """Limit editing to admin or the user who created the category"""
        if self.request.user.is_superuser:
            return Category.objects.all()
        return Category.objects.filter(created_by=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Категория успешно обновлена!')
        return super().form_valid(form)
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет разрешения на редактирование этой категории.")
        return redirect('category-list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'members/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    
    def get_object(self, queryset=None):
        """
        Get the object with better error handling.
        """
        try:
            # Get the category ID from the URL
            pk = self.kwargs.get('pk')
            
            # Try to get the category
            obj = get_object_or_404(Category, pk=pk)
            
            # Check if user has permission to delete
            if not (self.request.user.is_superuser or obj.created_by == self.request.user or obj.created_by is None):
                messages.error(self.request, "У вас нет разрешения на удаление этой категории.")
                raise Http404("У вас нет разрешения на удаление этой категории.")
            
            return obj
        except Http404:
            # Log the error
            print(f"Категория с ID {self.kwargs.get('pk')} не найдена или доступ запрещен.")
            raise
    
    def get_queryset(self):
        """Limit deletion to admin or the user who created the category"""
        if self.request.user.is_superuser:
            return Category.objects.all()
        return Category.objects.filter(created_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            category = self.get_object()
            category_name = category.name
            result = super().delete(request, *args, **kwargs)
            messages.success(self.request, f'Категория "{category_name}" успешно удалена!')
            return result
        except Http404:
            messages.error(self.request, "Категория не найдена или у вас нет разрешения на её удаление.")
            return redirect('category-list')
        except Exception as e:
            messages.error(request, f"Ошибка при удалении категории: {str(e)}")
            return redirect('category-list')
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет разрешения на удаление этой категории.")
        return redirect('category-list')

@login_required
def kanban_board(request):
    """View for the Kanban board that displays tasks by status"""
    # Get filter parameters
    category_id = request.GET.get('category')
    assigned_to_id = request.GET.get('assigned_to')
    
    # Start with all tasks
    tasks = Task.objects.all()
    
    # Apply filters if specified
    if category_id:
        tasks = tasks.filter(category_id=category_id)
    if assigned_to_id:
        tasks = tasks.filter(assigned_to_id=assigned_to_id)
    
    # Group tasks by status
    todo_tasks = tasks.filter(status='TODO').order_by('-priority', 'due_date')
    in_progress_tasks = tasks.filter(status='IN_PROGRESS').order_by('-priority', 'due_date')
    review_tasks = tasks.filter(status='REVIEW').order_by('-priority', 'due_date')
    done_tasks = tasks.filter(status='DONE').order_by('-priority', 'due_date')
    
    context = {
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'done_tasks': done_tasks,
        'categories': Category.objects.all(),
        'users': User.objects.all(),
    }
    
    return render(request, 'members/kanban_board.html', context)

@login_required
@require_POST
def update_task_status(request, task_id):
    """AJAX endpoint to update a task's status when dragged on the kanban board"""
    try:
        # Get the task
        task = get_object_or_404(Task, id=task_id)
        
        # Check permissions (only assigned user or creator can update)
        if not (request.user == task.assigned_to or request.user == task.created_by or request.user.is_superuser):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get the new status from request body
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validate the status
        valid_statuses = [status for status, _ in Task.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Update the task
        task.status = new_status
        task.save()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'status': task.status,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def task_template(request, task_id):
    """Return a task card HTML for AJAX loading"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'members/partials/task_card.html', {'task': task})

@login_required
def task_row_template(request, task_id):
    """Return a task row HTML for AJAX loading in list view"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'members/partials/task_row.html', {'task': task})

@login_required
def category_template(request, category_id):
    """Return a category row HTML for AJAX loading"""
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'members/partials/category_row.html', {'category': category})

def custom_404(request, exception=None):
    """Custom 404 error handler"""
    message = str(exception) if exception else "Страница, которую вы ищете, не существует."
    return render(request, 'members/404.html', {'message': message}, status=404)

def logout_confirm(request):
    """Show logout confirmation page."""
    return render(request, 'members/logout_confirm.html')

class CustomLoginView(LoginView):
    template_name = 'members/login.html'
    
    def get_success_url(self):
        # Redirect to home by default
        return reverse_lazy('dashboard')
    
    def get_redirect_url(self):
        # If there's a specific next parameter, use Django's logic
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        if redirect_to:
            return redirect_to
        # Otherwise go to home
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, "Неверное имя пользователя или пароль.")
        return super().form_invalid(form)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'members/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect back to notifications page
    return redirect('notifications')

@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    # Redirect back to notifications page
    return redirect('notifications')

@login_required
def employee_list(request):
    """View for displaying a list of all employees with online/offline status."""
    # Consider users active if they've logged in within the last 15 minutes
    online_threshold = timezone.now() - datetime.timedelta(minutes=15)
    users = User.objects.all().order_by('username')
    
    # Add an is_online attribute to each user
    for user in users:
        user.is_online = user.last_login is not None and user.last_login >= online_threshold
    
    return render(request, 'members/employee_list.html', {'users': users})

@login_required
def task_detail_partial(request, task_id):
    """Return task detail HTML partial for AJAX loading"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'members/partials/task_detail_partial.html', {
        'task': task,
        'comment_form': CommentForm()
    })

@login_required
def comment_form_submit(request, task_id):
    """Handle comment form submission via AJAX/WebSocket"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(
                task=task,
                user=request.user,
                text=text
            )
            # Signal will handle WebSocket broadcast
            return JsonResponse({
                'success': True,
                'comment_id': comment.id
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Неверные данные для комментария'
    })

@login_required
def task_observers_partial(request, task_id):
    """Return task observers list HTML partial for AJAX loading"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'members/partials/task_observers_partial.html', {
        'task': task
    })

@login_required
def get_unread_notification_count(request):
    """Return the number of unread notifications for the current user"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def categories_list_partial(request):
    """Return categories list HTML partial for AJAX loading"""
    categories = Category.objects.all()
    return render(request, 'members/partials/categories_list_partial.html', {
        'categories': categories
    })