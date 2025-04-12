import os
import sys
import django
import subprocess

def main():
    """Run Django migrations to create database tables."""
    print("Starting database migration process...")
    
    # Use the current Python executable
    python = sys.executable
    
    # Commands to run
    commands = [
        [python, "manage.py", "makemigrations", "members"],
        [python, "manage.py", "migrate"],
    ]
    
    # Run each command
    for cmd in commands:
        print(f"\nRunning: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        if result.stderr:
            print("Error:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
            return False
    
    print("\n✅ Migrations completed successfully!")
    print("\nYou should now be able to register and login without errors.")
    print("Run the development server with:")
    print(f"{python} manage.py runserver")
    
    return True

if __name__ == "__main__":
    main()
