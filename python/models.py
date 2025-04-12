import bcrypt
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from db import Base

# Task-Project association table (for many-to-many relationship)
task_project = Table(
    'task_projects',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="user")
    projects = relationship("Project", back_populates="user")
    
    def set_password(self, password):
        # Hash password with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, self.password.encode('utf-8'))

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum('todo', 'in-progress', 'completed'), default='todo')
    priority = Column(Enum('low', 'medium', 'high'), default='medium')
    due_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    projects = relationship("Project", secondary=task_project, back_populates="tasks")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", secondary=task_project, back_populates="projects")
