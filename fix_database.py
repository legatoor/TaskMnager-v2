"""
This script will run the necessary Django migrations to fix the database issue.
"""
import os
import sys
import subprocess

def run_command(command):
    """Run a command and print its output."""
    print(f"\nRunning: {' '.join(command)}")
    process = subprocess.run(command, capture_output=True, text=True)
    
    if process.stdout:
        print("Output:")
        print(process.stdout)
    
    if process.stderr:
        print("Error:")
        print(process.stderr)
    
    return process.returncode == 0

def main():
    print("=" * 60)
    print("TASK MANAGER DATABASE SETUP".center(60))
    print("=" * 60)
    print("This script will create the database tables needed for your app.")
    
    # Get the Python executable
    python = sys.executable
    
    # First, make migrations for the members app
    if not run_command([python, "manage.py", "makemigrations", "members"]):
        print("\n❌ Failed to create migrations. Check the error above.")
        return False
    
    # Then apply all migrations
    if not run_command([python, "manage.py", "migrate"]):
        print("\n❌ Failed to apply migrations. Check the error above.")
        return False
    
    print("\n✅ SUCCESS! Database tables have been created.")
    print("\nYou should now be able to register and login without errors.")
    print("\nTo start the development server, run:")
    print(f"  {python} manage.py runserver")
    
    # Ask if they want to create a superuser
    create_superuser = input("\nDo you want to create an admin user now? (y/n): ")
    if create_superuser.lower() in ['y', 'yes']:
        run_command([python, "manage.py", "createsuperuser"])
    
    return True

if __name__ == "__main__":
    main()
