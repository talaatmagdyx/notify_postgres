#!/usr/bin/env python3
"""
Clear and Generate Fresh Data
"""

import psycopg2
import os
import sys

# Add notification-engine directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_and_generate():
    """Clear existing data and generate fresh sample data."""
    print("🧹 Clearing existing data...")
    
    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'notify_postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM eng_interactions')
    conn.commit()
    print("✅ Cleared existing data")
    
    cursor.close()
    conn.close()
    
    # Generate new data
    print("🔄 Generating fresh sample data...")
    os.system('python quick_generate.py')

if __name__ == "__main__":
    clear_and_generate()
