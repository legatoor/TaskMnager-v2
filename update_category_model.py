import os
import sys
import subprocess

def run_command(command):
    """Run a command and display its output."""
    print(f"\nRunning: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print("Output:")
        print(result.stdout)
    
    if result.stderr:
        print("Error:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """Create and apply migrations for the Category model."""
    print("=" * 70)
    print("UPDATING CATEGORY MODEL".center(70))
    print("=" * 70)
    
    # Use the current Python executable
    python = sys.executable
    
    # Commands to run
    commands = [
        [python, "manage.py", "makemigrations", "members", "--name", "add_created_by_to_category"],
        [python, "manage.py", "migrate", "members"],
    ]
    
    success = True
    for cmd in commands:
        if not run_command(cmd):
            print(f"\n❌ Command failed: {' '.join(cmd)}")
            success = False
            break
    
    if success:
        print("\n✅ Category model updated successfully!")
        print("\nYou can now access the categories page without errors.")
        print("\nTo run the development server:")
        print(f"  {python} manage.py runserver")
    else:
        print("\n❌ Failed to update the Category model.")
        print("\nTry running these commands manually:")
        print("  python manage.py makemigrations members --name add_created_by_to_category")
        print("  python manage.py migrate members")

if __name__ == "__main__":
    main()
