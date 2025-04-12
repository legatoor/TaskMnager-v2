from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task, Category, UserProfile, Comment

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category')
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            status='TODO',
            priority=2,
            assigned_to=self.user,
            created_by=self.user,
            category=self.category
        )
    
    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.status, 'TODO')
        self.assertEqual(self.task.assigned_to, self.user)

class TaskViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
    
    def test_task_list_view(self):
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/task_list.html')
