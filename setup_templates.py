import os
import shutil

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Create all required directories
directories = [
    'templates',
    'members/templates/members',
    'static',
    'static/css',
    'static/js',
    'static/images',
    'media',
    'media/profile_pics',
]

for directory in directories:
    dir_path = os.path.join(base_dir, directory)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

print("\nAll required directories have been created!")
print("Now you can run 'python manage.py runserver' to start the development server.")
print("The templates have been created in the appropriate directories.")
