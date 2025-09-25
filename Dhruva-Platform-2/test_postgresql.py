#!/usr/bin/env python3
"""
Test PostgreSQL connection and basic operations
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_postgresql_connection():
    """Test PostgreSQL connection and basic operations"""
    print("🧪 Testing PostgreSQL connection...")
    
    try:
        # Connect to app database
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='dhruva_app',
            user='dhruvaadmin',
            password='dhruva123'
        )
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # Test table existence
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Test table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"✅ Users table has {len(columns)} columns:")
        for column in columns:
            print(f"   - {column[0]}: {column[1]}")
        
        # Test data count
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table has {user_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM api_keys;")
        api_key_count = cursor.fetchone()[0]
        print(f"✅ API keys table has {api_key_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM models;")
        model_count = cursor.fetchone()[0]
        print(f"✅ Models table has {model_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM services;")
        service_count = cursor.fetchone()[0]
        print(f"✅ Services table has {service_count} records")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 PostgreSQL connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection test failed: {e}")
        return False

def test_log_database():
    """Test log database connection"""
    print("\n🧪 Testing log database connection...")
    
    try:
        # Connect to log database
        conn = psycopg2.connect(
            host='localhost',
            port=5434,
            database='dhruva_log',
            user='dhruvalogadmin',
            password='dhruvalog123'
        )
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Log database PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Log database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Log database connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_postgresql_connection()
    log_success = test_log_database()
    
    if success and log_success:
        print("\n🎉 All database tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some database tests failed!")
        sys.exit(1)
