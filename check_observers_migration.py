import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from django.db import connection
from django.apps import apps
from members.models import Task

def check_observer_field():
    """Check if the observers field exists in the Task model"""
    print("Checking observer field in Task model...")
    
    # Get all ManyToMany fields for the Task model
    many_to_many_fields = [f for f in Task._meta.get_fields() if f.many_to_many]
    
    # Check if observers is among them
    observers_field = next((f for f in many_to_many_fields if f.name == 'observers'), None)
    
    if observers_field:
        print("✅ Observer field found in Task model")
        print(f"Field name: {observers_field.name}")
        print(f"Relation: {observers_field.related_model.__name__}")
        return True
    else:
        print("❌ Observer field NOT found in Task model")
        print("You need to run migrations:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        return False

def check_observer_database_table():
    """Check if the database table for Task-User observers exists"""
    print("\nChecking database table for observers...")
    
    # Get the through model table name
    through_model = Task.observers.through
    table_name = through_model._meta.db_table
    
    # Check if the table exists in the database
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names()
        
        if table_name in tables:
            print(f"✅ Observer table found: {table_name}")
            
            # Check table structure using PostgreSQL-compatible query
            print("\nTable columns:")
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, [table_name])
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            return True
        else:
            print(f"❌ Observer table NOT found: {table_name}")
            print("You need to run migrations:")
            print("python manage.py makemigrations")
            print("python manage.py migrate")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("TASK OBSERVER FIELD CHECK".center(60))
    print("=" * 60)
    
    model_check = check_observer_field()
    db_check = check_observer_database_table()
    
    if model_check and db_check:
        print("\n✅ Observer functionality is properly set up!")
    else:
        print("\n❌ There are issues with observer functionality.")
        print("Please run the following commands:")
        print("1. python manage.py makemigrations members")
        print("2. python manage.py migrate")
        sys.exit(1)
