# Task Manager Database Setup (Python)

This folder contains Python scripts to set up the database structure for the Task Management System.

## Setup Instructions

1. Install required dependencies:
```
pip install -r requirements.txt
```

2. Create a `.env` file with your database configuration (optional):
```
DB_USERNAME=root
DB_PASSWORD=yourpassword
DB_NAME=task_manager
DB_HOST=localhost
DB_PORT=3306
```

3. Run the database initialization script:
```
python init_db.py
```

## Database Structure

The script will create the following tables:
- users
- tasks
- projects
- task_projects (junction table)

## Models

- **User**: Stores user information with hashed passwords
- **Task**: Stores task information with properties like status and priority
- **Project**: Stores project information 
- **task_projects**: Junction table for many-to-many relationship between tasks and projects
