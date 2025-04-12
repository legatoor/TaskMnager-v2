#!/usr/bin/env python
"""
Script to help set up PostgreSQL for the taskmanager project.
"""
import os
import sys
import subprocess
import getpass
from pathlib import Path

def run_command(command, show_output=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if show_output:
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        if result.stderr:
            print("Error:")
            print(result.stderr)
    
    return result.returncode == 0, result.stdout, result.stderr

def check_postgres_cli():
    """Check if PostgreSQL CLI tools are available."""
    print("Checking for PostgreSQL command-line tools...")
    success, _, _ = run_command(["psql", "--version"], show_output=False)
    if not success:
        print("PostgreSQL command-line tools not found.")
        print("Please install PostgreSQL and ensure 'psql' is in your PATH.")
        return False
    return True

def create_env_file():
    """Create or update .env file with database settings."""
    print("\nConfiguring environment variables...")
    
    # Check if .env file exists
    env_path = Path(".env")
    if env_path.exists():
        print(".env file already exists. Do you want to update it? (y/n)")
        if input().lower() != 'y':
            return
    
    # Get database settings from user
    db_name = input("Database name [taskmanager]: ") or "taskmanager"
    db_user = input("Database user [postgres]: ") or "postgres"
    db_password = getpass.getpass("Database password: ")
    db_host = input("Database host [localhost]: ") or "localhost"
    db_port = input("Database port [5432]: ") or "5432"
    
    # Create .env file
    with open(env_path, "w") as f:
        f.write(f"DEBUG=True\n")
        f.write(f"SECRET_KEY=django-insecure-changethisinproduction\n")
        f.write(f"DB_NAME={db_name}\n")
        f.write(f"DB_USER={db_user}\n")
        f.write(f"DB_PASSWORD={db_password}\n")
        f.write(f"DB_HOST={db_host}\n")
        f.write(f"DB_PORT={db_port}\n")
    
    print(".env file created successfully.")
    return db_name, db_user, db_password, db_host, db_port

def create_database(db_name, db_user, db_password):
    """Create PostgreSQL database if it doesn't exist."""
    print("\nChecking if database already exists...")
    
    # Check if database exists
    check_cmd = ["psql", "-lqt"]
    success, output, _ = run_command(check_cmd, show_output=False)
    if not success:
        print("Failed to check if database exists. Please create it manually.")
        return False
    
    # Parse output to check if database exists
    if db_name in output:
        print(f"Database '{db_name}' already exists.")
        return True
    
    print(f"Creating database '{db_name}'...")
    
    # Create database
    create_cmd = ["psql", "-c", f"CREATE DATABASE {db_name};"]
    success, _, _ = run_command(create_cmd)
    if not success:
        print(f"Failed to create database '{db_name}'. Please create it manually.")
        return False
    
    # Grant privileges if a different user is specified
    if db_user != "postgres":
        grant_cmd = ["psql", "-c", f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"]
        success, _, _ = run_command(grant_cmd)
        if not success:
            print(f"Failed to grant privileges to '{db_user}'. Please do this manually.")
            return False
    
    print(f"Database '{db_name}' created successfully.")
    return True

def install_dependencies():
    """Install required Python dependencies."""
    print("\nInstalling required Python dependencies...")
    requirements_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    success, _, _ = run_command(requirements_cmd)
    if not success:
        print("Failed to install dependencies. Please install them manually.")
        return False
    return True

def run_migrations():
    """Run Django migrations."""
    print("\nRunning Django migrations...")
    
    # Make migrations
    makemigrations_cmd = [sys.executable, "manage.py", "makemigrations"]
    success, _, _ = run_command(makemigrations_cmd)
    if not success:
        print("Failed to make migrations. Please fix any errors and try again.")
        return False
    
    # Apply migrations
    migrate_cmd = [sys.executable, "manage.py", "migrate"]
    success, _, _ = run_command(migrate_cmd)
    if not success:
        print("Failed to apply migrations. Please fix any errors and try again.")
        return False
    
    print("Migrations applied successfully.")
    return True

def create_superuser():
    """Create a Django superuser."""
    print("\nDo you want to create a superuser? (y/n)")
    if input().lower() != 'y':
        return True
    
    create_cmd = [sys.executable, "manage.py", "createsuperuser"]
    success, _, _ = run_command(create_cmd)
    if not success:
        print("Failed to create superuser. Please create one manually.")
        return False
    return True

def main():
    """Main function."""
    print("=" * 70)
    print("PostgreSQL Setup for Task Manager".center(70))
    print("=" * 70)
    
    # Check if PostgreSQL CLI tools are available
    if not check_postgres_cli():
        return
    
    # Create or update .env file
    db_info = create_env_file()
    if not db_info:
        return
    
    db_name, db_user, db_password, db_host, db_port = db_info
    
    # Create database if it doesn't exist
    if not create_database(db_name, db_user, db_password):
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    # Create superuser
    if not create_superuser():
        return
    
    print("\n" + "=" * 70)
    print("Setup completed successfully!".center(70))
    print("=" * 70)
    print("\nYou can now run the development server:")
    print(f"  {sys.executable} manage.py runserver")

if __name__ == "__main__":
    main()
