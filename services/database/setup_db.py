#!/usr/bin/env python3
"""
Database Setup Script
Creates the database schema for the notification system
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the database with the required schema."""
    print("🔧 Setting up database...")
    
    # Load database configuration from environment variables
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'notify_postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        # Connect to PostgreSQL (without specifying database first)
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database='postgres',  # Connect to default postgres database
            user=db_config['user'],
            password=db_config['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config['database'],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_config['database']}")
            print(f"✅ Created database: {db_config['database']}")
        else:
            print(f"✅ Database already exists: {db_config['database']}")
        
        cursor.close()
        conn.close()
        
        # Now connect to the specific database and create schema
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop existing schema if it exists
        cursor.execute('DROP TABLE IF EXISTS eng_interactions CASCADE')
        cursor.execute('DROP TYPE IF EXISTS engagement_status_enum CASCADE')
        cursor.execute('DROP TYPE IF EXISTS channel_closing_reason CASCADE')
        cursor.execute('DROP TYPE IF EXISTS direction CASCADE')
        print("✅ Cleaned existing schema")
        
        # Read and execute the schema file
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        print("✅ Database schema created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if setup_database():
        print("\n🎉 Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
