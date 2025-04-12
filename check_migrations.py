import os
import sys
from pathlib import Path

def main():
    # Check if migrations directory exists
    base_dir = Path(__file__).resolve().parent
    migrations_dir = base_dir / 'members' / 'migrations'
    
    if not migrations_dir.exists():
        print("Creating migrations directory...")
        os.makedirs(migrations_dir)
        
        # Create an empty __init__.py file
        with open(migrations_dir / '__init__.py', 'w') as f:
            f.write("# This file is required for Python to recognize this directory as a package.")
    
    # Create an initial migration file if it doesn't exist
    initial_migration = list(migrations_dir.glob('0001_*.py'))
    
    if not initial_migration:
        print("No initial migration found.")
        print("You should run: python manage.py makemigrations members")
    else:
        print(f"Found initial migration: {initial_migration[0].name}")
    
    print("\nTo apply migrations, run: python manage.py migrate")

if __name__ == "__main__":
    main()
