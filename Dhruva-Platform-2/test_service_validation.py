#!/usr/bin/env python3
"""
Script to test Service document validation
This helps identify which service documents are causing validation errors
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = Path(__file__).parent / "Dhruva-Platform-2" / "server"
sys.path.insert(0, str(server_path))

try:
    from pymongo import MongoClient
    from module.services.model.service import Service
    from db.database import AppDatabase
    import traceback
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the correct directory and dependencies are installed")
    sys.exit(1)


def test_service_validation():
    """Test validation of all service documents in MongoDB"""
    
    # Get database connection
    try:
        db = AppDatabase()
        collection = db["service"]
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure MongoDB is running and environment variables are set correctly")
        return
    
    print("=== Testing Service Document Validation ===\n")
    
    # Get all services
    services = list(collection.find())
    print(f"Found {len(services)} service documents\n")
    
    valid_count = 0
    invalid_count = 0
    
    for i, service_doc in enumerate(services, 1):
        service_id = service_doc.get("serviceId", f"Unknown-{i}")
        print(f"[{i}/{len(services)}] Testing: {service_id}")
        
        try:
            # Try to parse the document as a Service model
            service = Service.parse_obj(service_doc)
            print(f"  ✅ VALID")
            valid_count += 1
        except Exception as e:
            print(f"  ❌ INVALID")
            print(f"  Error: {str(e)}")
            print(f"  Document keys: {list(service_doc.keys())}")
            
            # Show specific field issues
            if "api_key" not in service_doc:
                print(f"  - Missing required field: api_key")
            if "endpoint" not in service_doc:
                print(f"  - Missing required field: endpoint")
            if "publishedOn" in service_doc and not isinstance(service_doc["publishedOn"], int):
                print(f"  - publishedOn should be int, got: {type(service_doc['publishedOn'])}")
            
            invalid_count += 1
            print()
    
    print("\n=== Summary ===")
    print(f"Valid services: {valid_count}")
    print(f"Invalid services: {invalid_count}")
    
    if invalid_count > 0:
        print("\n⚠️  Invalid services are causing the list_services endpoint to fail!")
        print("Fix or remove the invalid service documents to resolve the issue.")
    else:
        print("\n✅ All service documents are valid!")


if __name__ == "__main__":
    test_service_validation()

