#!/usr/bin/env python3
"""
Data migration script from MongoDB to PostgreSQL
Migrates all collections from Dhruva Platform MongoDB to PostgreSQL
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import pymongo
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_APP_DB_CONNECTION = os.environ.get(
    "APP_DB_CONNECTION_STRING",
    "mongodb://dhruvaadmin:dhruva123@localhost:27017/admin?authSource=admin"
)

# PostgreSQL connection for app database
POSTGRES_APP_DB_CONNECTION = {
    'host': 'localhost',
    'port': 5433,
    'database': 'dhruva_app',
    'user': 'dhruvaadmin',
    'password': 'dhruva123'
}

# PostgreSQL connection for log database
POSTGRES_LOG_DB_CONNECTION = {
    'host': 'localhost',
    'port': 5434,
    'database': 'dhruva_log',
    'user': 'dhruvalogadmin',
    'password': 'dhruvalog123'
}

class DataMigrator:
    def __init__(self):
        self.mongo_client = None
        self.mongo_db = None
        self.pg_app_conn = None
        self.pg_log_conn = None
        self.object_id_mapping = {}  # Maps MongoDB ObjectIds to PostgreSQL UUIDs
        
    def connect_databases(self):
        """Connect to MongoDB and PostgreSQL databases"""
        try:
            # Connect to MongoDB
            self.mongo_client = pymongo.MongoClient(MONGO_APP_DB_CONNECTION)
            self.mongo_db = self.mongo_client[os.environ.get("APP_DB_NAME", "admin")]
            print("✓ Connected to MongoDB")
            
            # Connect to PostgreSQL app database
            self.pg_app_conn = psycopg2.connect(**POSTGRES_APP_DB_CONNECTION)
            self.pg_app_conn.autocommit = False
            print("✓ Connected to PostgreSQL app database")
            
            # Connect to PostgreSQL log database
            self.pg_log_conn = psycopg2.connect(**POSTGRES_LOG_DB_CONNECTION)
            self.pg_log_conn.autocommit = False
            print("✓ Connected to PostgreSQL log database")
            
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    def convert_object_id(self, obj_id: ObjectId) -> str:
        """Convert MongoDB ObjectId to PostgreSQL UUID, maintaining consistency"""
        if obj_id is None:
            return None
            
        obj_id_str = str(obj_id)
        if obj_id_str not in self.object_id_mapping:
            self.object_id_mapping[obj_id_str] = str(uuid.uuid4())
        return self.object_id_mapping[obj_id_str]
    
    def clean_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Clean MongoDB document for PostgreSQL insertion"""
        if doc is None:
            return None
            
        cleaned = {}
        for key, value in doc.items():
            if key == '_id':
                continue  # Skip _id, we'll handle it separately
            elif isinstance(value, ObjectId):
                cleaned[key] = self.convert_object_id(value)
            elif isinstance(value, dict):
                cleaned[key] = self.clean_document(value)
            elif isinstance(value, list):
                cleaned[key] = [self.clean_document(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        return cleaned
    
    def migrate_users(self):
        """Migrate users collection"""
        print("\n🔄 Migrating users...")
        
        users = list(self.mongo_db.user.find())
        if not users:
            print("  No users found to migrate")
            return
            
        cursor = self.pg_app_conn.cursor()
        
        for user in users:
            user_id = self.convert_object_id(user['_id'])
            cleaned_user = self.clean_document(user)
            
            cursor.execute("""
                INSERT INTO users (id, name, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, (
                user_id,
                cleaned_user.get('name'),
                cleaned_user.get('email'),
                cleaned_user.get('password'),
                cleaned_user.get('role', 'USER')
            ))
        
        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(users)} users")
    
    def migrate_models(self):
        """Migrate models collection"""
        print("\n🔄 Migrating models...")
        
        models = list(self.mongo_db.model.find())
        if not models:
            print("  No models found to migrate")
            return
            
        cursor = self.pg_app_conn.cursor()
        
        for model in models:
            model_id = self.convert_object_id(model['_id'])
            cleaned_model = self.clean_document(model)
            
            cursor.execute("""
                INSERT INTO models (
                    id, model_id, version, submitted_on, updated_on, name, description,
                    ref_url, task, languages, license, domain, inference_endpoint,
                    benchmarks, submitter
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (model_id) DO NOTHING
            """, (
                model_id,
                cleaned_model.get('modelId'),
                cleaned_model.get('version'),
                cleaned_model.get('submittedOn'),
                cleaned_model.get('updatedOn'),
                cleaned_model.get('name'),
                cleaned_model.get('description'),
                cleaned_model.get('refUrl'),
                Json(cleaned_model.get('task', {})),
                Json(cleaned_model.get('languages', [])),
                cleaned_model.get('license'),
                Json(cleaned_model.get('domain', [])),
                Json(cleaned_model.get('inferenceEndPoint', {})),
                Json(cleaned_model.get('benchmarks')) if cleaned_model.get('benchmarks') else None,
                Json(cleaned_model.get('submitter', {}))
            ))
        
        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(models)} models")
    
    def migrate_services(self):
        """Migrate services collection"""
        print("\n🔄 Migrating services...")
        
        services = list(self.mongo_db.service.find())
        if not services:
            print("  No services found to migrate")
            return
            
        cursor = self.pg_app_conn.cursor()
        
        for service in services:
            service_id = self.convert_object_id(service['_id'])
            cleaned_service = self.clean_document(service)
            
            cursor.execute("""
                INSERT INTO services (
                    id, service_id, name, service_description, hardware_description,
                    published_on, model_id, endpoint, api_key, health_status, benchmarks
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (service_id) DO NOTHING
            """, (
                service_id,
                cleaned_service.get('serviceId'),
                cleaned_service.get('name'),
                cleaned_service.get('serviceDescription'),
                cleaned_service.get('hardwareDescription'),
                cleaned_service.get('publishedOn'),
                cleaned_service.get('modelId'),
                cleaned_service.get('endpoint'),
                cleaned_service.get('api_key'),
                Json(cleaned_service.get('healthStatus')) if cleaned_service.get('healthStatus') else None,
                Json(cleaned_service.get('benchmarks')) if cleaned_service.get('benchmarks') else None
            ))
        
        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(services)} services")

    def migrate_api_keys(self):
        """Migrate api_key collection"""
        print("\n🔄 Migrating API keys...")

        api_keys = list(self.mongo_db.api_key.find())
        if not api_keys:
            print("  No API keys found to migrate")
            return

        cursor = self.pg_app_conn.cursor()

        for api_key in api_keys:
            api_key_id = self.convert_object_id(api_key['_id'])
            cleaned_api_key = self.clean_document(api_key)

            # Convert user_id ObjectId to UUID
            user_id = self.convert_object_id(api_key.get('user_id'))

            cursor.execute("""
                INSERT INTO api_keys (
                    id, name, api_key, masked_key, active, user_id, type,
                    created_timestamp, usage, hits, data_tracking, services
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (api_key) DO NOTHING
            """, (
                api_key_id,
                cleaned_api_key.get('name'),
                cleaned_api_key.get('api_key'),
                cleaned_api_key.get('masked_key'),
                cleaned_api_key.get('active', True),
                user_id,
                cleaned_api_key.get('type', 'INFERENCE'),
                cleaned_api_key.get('created_timestamp', datetime.now()),
                cleaned_api_key.get('usage', 0),
                cleaned_api_key.get('hits', 0),
                cleaned_api_key.get('data_tracking', False),
                Json(cleaned_api_key.get('services', []))
            ))

        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(api_keys)} API keys")

    def migrate_sessions(self):
        """Migrate session collection"""
        print("\n🔄 Migrating sessions...")

        sessions = list(self.mongo_db.session.find())
        if not sessions:
            print("  No sessions found to migrate")
            return

        cursor = self.pg_app_conn.cursor()

        for session in sessions:
            session_id = self.convert_object_id(session['_id'])
            cleaned_session = self.clean_document(session)

            # Convert user_id ObjectId to UUID
            user_id = self.convert_object_id(session.get('user_id'))

            cursor.execute("""
                INSERT INTO sessions (id, user_id, type, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                user_id,
                cleaned_session.get('type'),
                cleaned_session.get('timestamp', datetime.now())
            ))

        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(sessions)} sessions")

    def migrate_feedback(self):
        """Migrate feedback collection"""
        print("\n🔄 Migrating feedback...")

        feedback_items = list(self.mongo_db.feedback.find())
        if not feedback_items:
            print("  No feedback found to migrate")
            return

        cursor = self.pg_app_conn.cursor()

        for feedback in feedback_items:
            feedback_id = self.convert_object_id(feedback['_id'])
            cleaned_feedback = self.clean_document(feedback)

            # Convert user_id ObjectId to UUID
            user_id = self.convert_object_id(feedback.get('user_id'))

            cursor.execute("""
                INSERT INTO feedback (
                    id, user_id, api_key_name, pipeline_input, pipeline_output,
                    suggested_pipeline_output, pipeline_feedback
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                feedback_id,
                user_id,
                cleaned_feedback.get('api_key_name'),
                Json(cleaned_feedback.get('pipelineInput')) if cleaned_feedback.get('pipelineInput') else None,
                Json(cleaned_feedback.get('pipelineOutput')) if cleaned_feedback.get('pipelineOutput') else None,
                Json(cleaned_feedback.get('suggestedPipelineOutput')) if cleaned_feedback.get('suggestedPipelineOutput') else None,
                Json(cleaned_feedback.get('pipelineFeedback')) if cleaned_feedback.get('pipelineFeedback') else None
            ))

        self.pg_app_conn.commit()
        print(f"  ✓ Migrated {len(feedback_items)} feedback items")

    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting MongoDB to PostgreSQL migration...")

        try:
            self.connect_databases()

            # Migrate in order of dependencies
            self.migrate_users()
            self.migrate_models()
            self.migrate_services()
            self.migrate_api_keys()
            self.migrate_sessions()
            self.migrate_feedback()

            print("\n✅ Migration completed successfully!")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            if self.pg_app_conn:
                self.pg_app_conn.rollback()
            if self.pg_log_conn:
                self.pg_log_conn.rollback()
            raise
        finally:
            # Close connections
            if self.mongo_client:
                self.mongo_client.close()
            if self.pg_app_conn:
                self.pg_app_conn.close()
            if self.pg_log_conn:
                self.pg_log_conn.close()

if __name__ == "__main__":
    migrator = DataMigrator()
    migrator.run_migration()
