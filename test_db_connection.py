"""
Test database connection for PostgreSQL
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    
    # Get connection parameters from environment variables
    db_params = {
        'dbname': os.environ.get('DB_NAME', 'taskmanager'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
    }
    
    # Get schema name
    schema = os.environ.get('DB_SCHEMA', 'public')
    
    print(f"Attempting to connect to PostgreSQL database:")
    print(f"Database: {db_params['dbname']}")
    print(f"User: {db_params['user']}")
    print(f"Host: {db_params['host']}")
    print(f"Port: {db_params['port']}")
    print(f"Schema: {schema}")
    
    try:
        # Test the connection
        conn = psycopg2.connect(**db_params)
        print("Connection successful!")
        
        # Get PostgreSQL version
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Check schema permissions
        cursor.execute(f"SELECT has_schema_privilege('{db_params['user']}', '{schema}', 'CREATE');")
        has_create = cursor.fetchone()[0]
        print(f"Has CREATE privilege on schema '{schema}': {has_create}")
        
        cursor.execute(f"SELECT has_schema_privilege('{db_params['user']}', '{schema}', 'USAGE');")
        has_usage = cursor.fetchone()[0]
        print(f"Has USAGE privilege on schema '{schema}': {has_usage}")
        
        # Create schema if it doesn't exist and we have privileges
        try:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            conn.commit()
            print(f"Schema '{schema}' created or already exists.")
        except Exception as e:
            print(f"Could not create schema: {e}")
            
            # Suggest SQL commands to fix permissions
            print("\nTo fix permissions, connect as a superuser and run:")
            print(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            print(f"GRANT ALL ON SCHEMA {schema} TO {db_params['user']};")
            print(f"ALTER ROLE {db_params['user']} SET search_path TO {schema};")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("Connection closed.")
        return True
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        
        print("\nPossible solutions:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your credentials in the .env file")
        print("3. Run the following SQL commands as a superuser:")
        print(f"   CREATE ROLE {db_params['user']} WITH LOGIN PASSWORD '{db_params['password']}';")
        print(f"   CREATE DATABASE {db_params['dbname']} OWNER {db_params['user']};")
        print(f"   GRANT ALL PRIVILEGES ON DATABASE {db_params['dbname']} TO {db_params['user']};")
        
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
