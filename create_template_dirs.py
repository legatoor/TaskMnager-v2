import os

# Create template directories
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dirs = [
    'templates',
    'members/templates/members',
]

for directory in template_dirs:
    dir_path = os.path.join(base_dir, directory)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

print("\nTemplate directories have been created!")
