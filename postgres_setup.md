# PostgreSQL Migration Guide

This guide will help you migrate your Task Manager application from SQLite to PostgreSQL.

## Prerequisites

1. Install PostgreSQL on your machine or use a cloud-hosted PostgreSQL instance
2. Make sure you have the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Setup Steps

### 1. Create a PostgreSQL Database

```sql
CREATE DATABASE taskmanager;
CREATE USER taskmanager_user WITH PASSWORD 'your_password';
ALTER ROLE taskmanager_user SET client_encoding TO 'utf8';
ALTER ROLE taskmanager_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE taskmanager_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskmanager_user;
```

### 2. Configure Environment Variables

Create or update your `.env` file with the following information:

