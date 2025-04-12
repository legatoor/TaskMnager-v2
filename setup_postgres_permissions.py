"""
Script to set up PostgreSQL permissions for Django
"""
import os
import sys
import psycopg2
from getpass import getpass
from dotenv import load_dotenv

def setup_permissions():
    load_dotenv()
    
    # Get environment variables
    db_name = os.environ.get('DB_NAME', 'taskmanager')
    db_user = os.environ.get('DB_USER', 'taskmanager_user')
    db_password = os.environ.get('DB_PASSWORD', 'root')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_schema = os.environ.get('DB_SCHEMA', 'taskmanager')
    
    print("PostgreSQL Permission Setup")
    print("===========================")
    print(f"This script will set up permissions for:")
    print(f"- Database: {db_name}")
    print(f"- User: {db_user}")
    print(f"- Schema: {db_schema}")
    print()
    print("You need to run this script with PostgreSQL superuser credentials")
    
    # Get superuser credentials
    super_user = input("PostgreSQL superuser name [postgres]: ") or "postgres"
    super_password = getpass("PostgreSQL superuser password: ")
    
    try:
        # Connect as superuser
        conn = psycopg2.connect(
            dbname="postgres",
            user=super_user,
            password=super_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{db_user}';")
        user_exists = cursor.fetchone() is not None
        
        # Create user if it doesn't exist
        if not user_exists:
            print(f"Creating user '{db_user}'...")
            cursor.execute(f"CREATE ROLE {db_user} WITH LOGIN PASSWORD '{db_password}';")
        else:
            print(f"User '{db_user}' already exists")
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        db_exists = cursor.fetchone() is not None
        
        # Create database if it doesn't exist
        if not db_exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
        else:
            print(f"Database '{db_name}' already exists")
            # Set owner
            cursor.execute(f"ALTER DATABASE {db_name} OWNER TO {db_user};")
        
        # Connect to the database to create schema
        cursor.close()
        conn.close()
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=super_user,
            password=super_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create schema and grant permissions
        print(f"Creating schema '{db_schema}' and granting privileges...")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {db_schema} AUTHORIZATION {db_user};")
        cursor.execute(f"GRANT ALL ON SCHEMA {db_schema} TO {db_user};")
        cursor.execute(f"ALTER ROLE {db_user} SET search_path TO {db_schema}, public;")
        
        # Grant privileges on public schema (needed for migrations)
        print("Granting privileges on public schema...")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user};")
        
        print("Setup completed successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = setup_permissions()
    sys.exit(0 if success else 1)
