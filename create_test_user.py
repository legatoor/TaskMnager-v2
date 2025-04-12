#!/usr/bin/env python
"""
Creates a test user for debugging login issues
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

def create_test_user(username='testuser', password='testpass123', email='test@example.com'):
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"User '{username}' created successfully!")
        print(f"Login with: {username} / {password}")
        return user
    except IntegrityError:
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Password reset to: {password}")
        return user

if __name__ == "__main__":
    create_test_user()
