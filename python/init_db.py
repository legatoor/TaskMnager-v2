from db import engine, SessionLocal, Base
from models import User, Task, Project

def init_database():
    try:
        # Create all tables in the database
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Create an admin user for testing
        db = SessionLocal()
        admin = User(
            name="Admin User",
            email="admin@example.com"
        )
        admin.set_password("admin123")
        
        db.add(admin)
        db.commit()
        print("Admin user created")
        
        db.close()
        
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database()
