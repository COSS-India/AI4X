#!/usr/bin/env python3
"""
Script to insert OCR model and service entries into MongoDB
Run this script from the server directory: python3 db/insert_ocr_to_db.py
"""

import json
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def insert_ocr_entries():
    """Insert OCR model and service into MongoDB"""
    
    # Connect to MongoDB
    connection_string = os.environ.get("APP_DB_CONNECTION_STRING", "mongodb://dhruva-platform-app-db:27017")
    db_name = os.environ.get("APP_DB_NAME", "dhruva-app")
    
    print(f"Connecting to MongoDB: {connection_string}")
    client = MongoClient(connection_string)
    db = client[db_name]
    
    # Load model entry
    model_file = os.path.join(os.path.dirname(__file__), "ocr_model_entry.json")
    with open(model_file, 'r', encoding='utf-8') as f:
        model_data = json.load(f)
    
    # Load service entry
    service_file = os.path.join(os.path.dirname(__file__), "ocr_service_entry.json")
    with open(service_file, 'r', encoding='utf-8') as f:
        service_data = json.load(f)
    
    # Check if model already exists
    existing_model = db.model.find_one({"modelId": model_data["modelId"]})
    if existing_model:
        print(f"⚠️  Model '{model_data['modelId']}' already exists. Updating...")
        db.model.update_one(
            {"modelId": model_data["modelId"]},
            {"$set": model_data}
        )
        print(f"✅ Model updated: {model_data['modelId']}")
    else:
        result = db.model.insert_one(model_data)
        print(f"✅ Model inserted: {model_data['modelId']} (ID: {result.inserted_id})")
    
    # Check if service already exists
    existing_service = db.service.find_one({"serviceId": service_data["serviceId"]})
    if existing_service:
        print(f"⚠️  Service '{service_data['serviceId']}' already exists. Updating...")
        db.service.update_one(
            {"serviceId": service_data["serviceId"]},
            {"$set": service_data}
        )
        print(f"✅ Service updated: {service_data['serviceId']}")
    else:
        result = db.service.insert_one(service_data)
        print(f"✅ Service inserted: {service_data['serviceId']} (ID: {result.inserted_id})")
    
    print("\n" + "="*70)
    print("✅ OCR MODEL AND SERVICE SUCCESSFULLY ADDED TO DATABASE!")
    print("="*70)
    print(f"\nModel ID: {model_data['modelId']}")
    print(f"Service ID: {service_data['serviceId']}")
    print(f"Endpoint: {service_data['endpoint']}")
    print("\nYou can now test the OCR service using:")
    print(f"  serviceId: {service_data['serviceId']}")
    print("="*70)
    
    client.close()

if __name__ == "__main__":
    try:
        insert_ocr_entries()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

