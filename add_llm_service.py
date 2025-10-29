"""
Script to add LLM service and model to MongoDB
Run this from the Dhruva-Platform-2/server directory
"""

import os
from pymongo import MongoClient
from datetime import datetime

# Get MongoDB connection from environment or use default
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "dhruva")  # Adjust to your database name

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Add Service
service_doc = {
    "serviceId": "ai-llm/gpt-neox-20b",
    "name": "GPT-NeoX 20B LLM Service",
    "serviceDescription": "Text generation using GPT-NeoX 20B model",
    "hardwareDescription": "GPU optimized for large language models",
    "publishedOn": int(datetime.now().timestamp()),
    "modelId": "gpt-neox-20b-model",
    "endpoint": "http://13.203.154.110:9000/pipeline",  # Replace with actual endpoint
    "api_key": "your_service_api_key_here",  # Generate a secure API key
    "healthStatus": None,
    "benchmarks": None
}

# Add Model
model_doc = {
    "modelId": "gpt-neox-20b-model",
    "version": "1.0",
    "submittedOn": int(datetime.now().timestamp()),
    "updatedOn": int(datetime.now().timestamp()),
    "name": "GPT-NeoX 20B",
    "description": "GPT-NeoX 20B large language model for text generation",
    "refUrl": "https://github.com/EleutherAI/gpt-neox",
    "task": {"type": "text-generation"},
    "languages": [{"sourceLanguage": "en", "targetLanguage": None}],
    "license": "Apache-2.0",
    "domain": ["general", "code", "summarization"],
    "inferenceEndPoint": {
        "task": "text-generation",
        "endpointURL": "http://13.203.154.110:9000/pipeline",
        "schema": {
            "request": {
                "type": "object",
                "properties": {
                    "input": {"type": "array", "items": {"type": "string"}},
                    "temperature": {"type": "number"},
                    "max_tokens": {"type": "number"}
                }
            },
            "response": {
                "type": "object",
                "properties": {
                    "output": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    "benchmarks": [],
    "submitter": {
        "name": "AI4Bharat",
        "email": "contact@ai4bharat.org",
        "oauthId": None
    }
}

try:
    # Insert service
    result_service = db.service.insert_one(service_doc)
    print(f"✅ Service inserted with ID: {result_service.inserted_id}")
    
    # Insert model
    result_model = db.model.insert_one(model_doc)
    print(f"✅ Model inserted with ID: {result_model.inserted_id}")
    
    print("\n✅ LLM service and model added successfully to MongoDB!")
    print(f"Service ID: ai-llm/gpt-neox-20b")
    print(f"Model ID: gpt-neox-20b-model")
    
except Exception as e:
    print(f"❌ Error inserting documents: {e}")

