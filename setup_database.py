import os
import subprocess
import sys

def run_command(command):
    """Run a command and print its output."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print("Output:")
        print(result.stdout)
    
    if result.stderr:
        print("Error:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    # Get the Python executable used to run this script
    python_executable = sys.executable
    
    # Commands to run
    commands = [
        [python_executable, "manage.py", "makemigrations"],
        [python_executable, "manage.py", "migrate"],
    ]
    
    # Run each command
    success = True
    for command in commands:
        if not run_command(command):
            success = False
            print(f"Command failed: {' '.join(command)}")
            break
    
    if success:
        print("\nDatabase setup completed successfully!")
        print("\nYou can now run the development server with:")
        print(f"{python_executable} manage.py runserver")
        
        # Ask if user wants to create a superuser
        create_superuser = input("\nDo you want to create a superuser? (y/n): ")
        if create_superuser.lower() == 'y':
            run_command([python_executable, "manage.py", "createsuperuser"])
    else:
        print("\nDatabase setup failed.")

if __name__ == "__main__":
    main()
