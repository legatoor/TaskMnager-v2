# Database Migration Guide

This guide will help you set up the database for your Task Manager application.

## Steps to Create and Apply Migrations

1. **Make sure Django is installed**:
   ```
   pip install django
   ```

2. **Create migrations for your models**:
   ```
   python manage.py makemigrations members
   ```
   This will create migration files based on your model changes.

3. **Apply the migrations to create the database tables**:
   ```
   python manage.py migrate
   ```
   This will create all the necessary tables in your database.

4. **Create a superuser to access the admin interface**:
   ```
   python manage.py createsuperuser
   ```
   Follow the prompts to create a username, email, and password.

## Common Issues and Solutions

### Issue: "no such table" error
If you see an error like "no such table: members_userprofile", it means you haven't applied migrations. Run:
```
python manage.py migrate
```

### Issue: Migration files not being created
Make sure your app is in INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ...
    'members.apps.MembersConfig',
    # ...
]
```

### Issue: "Inconsistent migration history" error
You might need to reset your migrations:
1. Delete all files in the migrations folder except `__init__.py`
2. Delete your database (db.sqlite3 file)
3. Run `python manage.py makemigrations`
4. Run `python manage.py migrate`

## Using the Helper Scripts

1. Run the database setup script:
   ```
   python setup_database.py
   ```
   This will create and apply migrations, and offer to create a superuser.

2. If you're having issues, run the migration check script:
   ```
   python check_migrations.py
   ```
   This will check if migrations exist and suggest what to do.

## Once Migrations Are Complete

After successfully applying migrations, you can run the development server:
```
python manage.py runserver
```

Then visit http://127.0.0.1:8000/ in your browser to use the Task Manager application.
