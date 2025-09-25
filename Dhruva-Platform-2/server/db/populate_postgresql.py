"""
PostgreSQL Database Seeding
Replaces MongoDB populate_db.py with PostgreSQL equivalent
"""

import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .postgresql_models import User, ApiKey, Service, Model, Feedback, Session as UserSession


def seed_postgresql_database(db: Session):
    """Seed PostgreSQL database with initial data"""
    print("🌱 Seeding PostgreSQL database...")
    
    # Check if database is already seeded
    if db.query(User).count() > 0:
        print("  Database already seeded, skipping...")
        return
    
    try:
        # Seed users first (required for foreign keys)
        default_user_id = seed_users(db)
        
        # Seed models
        seed_models(db)
        
        # Seed services
        seed_services(db)
        
        # Seed API keys (requires user)
        if default_user_id:
            seed_api_keys(db, default_user_id)
        
        # Create empty collections for feedback and sessions
        # (these will be populated as the application is used)
        
        db.commit()
        print("✅ PostgreSQL database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise


def seed_users(db: Session) -> str:
    """Seed users table"""
    print("  Seeding users...")
    
    # Try to load from fixture file first
    fixture_path = "./db/fixtures/users_registry.json"
    if os.path.exists(fixture_path):
        try:
            with open(fixture_path, 'r') as f:
                user_data = json.load(f)
            
            user = User(
                name=user_data.get('name', 'Default User'),
                email=user_data.get('email', 'admin@dhruva.co'),
                password=user_data.get('password', 'hashed_password'),
                role=user_data.get('role', 'ADMIN')
            )
            
            db.add(user)
            db.flush()  # Get the ID without committing
            return str(user.id)
            
        except Exception as e:
            print(f"    Warning: Could not load user fixture: {e}")
    
    # Create default user if fixture doesn't exist
    default_user = User(
        name="Default Admin",
        email="admin@dhruva.co",
        password="$argon2id$v=19$m=65536,t=3,p=4$hashed_password",  # Replace with actual hash
        role="ADMIN"
    )
    
    db.add(default_user)
    db.flush()
    print(f"    Created default user: {default_user.email}")
    return str(default_user.id)


def seed_models(db: Session):
    """Seed models table"""
    print("  Seeding models...")
    
    fixture_path = "./db/fixtures/models_registry.json"
    if not os.path.exists(fixture_path):
        print("    No models fixture found, skipping...")
        return
    
    try:
        with open(fixture_path, 'r') as f:
            models_data = json.load(f)
        
        if isinstance(models_data, list):
            for model_data in models_data:
                model = Model(
                    model_id=model_data.get('modelId'),
                    version=model_data.get('version', '1.0'),
                    submitted_on=model_data.get('submittedOn', int(datetime.now().timestamp())),
                    updated_on=model_data.get('updatedOn', int(datetime.now().timestamp())),
                    name=model_data.get('name'),
                    description=model_data.get('description'),
                    ref_url=model_data.get('refUrl'),
                    task=model_data.get('task', {}),
                    languages=model_data.get('languages', []),
                    license=model_data.get('license'),
                    domain=model_data.get('domain', []),
                    inference_endpoint=model_data.get('inferenceEndPoint', {}),
                    benchmarks=model_data.get('benchmarks'),
                    submitter=model_data.get('submitter', {})
                )
                db.add(model)
        
        print(f"    Loaded {len(models_data) if isinstance(models_data, list) else 1} models")
        
    except Exception as e:
        print(f"    Warning: Could not load models fixture: {e}")


def seed_services(db: Session):
    """Seed services table"""
    print("  Seeding services...")
    
    fixture_path = "./db/fixtures/services_registry.json"
    if not os.path.exists(fixture_path):
        print("    No services fixture found, skipping...")
        return
    
    try:
        with open(fixture_path, 'r') as f:
            services_data = json.load(f)
        
        if isinstance(services_data, list):
            for service_data in services_data:
                service = Service(
                    service_id=service_data.get('serviceId'),
                    name=service_data.get('name'),
                    service_description=service_data.get('serviceDescription'),
                    hardware_description=service_data.get('hardwareDescription'),
                    published_on=service_data.get('publishedOn', int(datetime.now().timestamp())),
                    model_id=service_data.get('modelId'),
                    endpoint=service_data.get('endpoint'),
                    api_key=service_data.get('api_key'),
                    health_status=service_data.get('healthStatus'),
                    benchmarks=service_data.get('benchmarks')
                )
                db.add(service)
        
        print(f"    Loaded {len(services_data) if isinstance(services_data, list) else 1} services")
        
    except Exception as e:
        print(f"    Warning: Could not load services fixture: {e}")


def seed_api_keys(db: Session, user_id: str):
    """Seed API keys table"""
    print("  Seeding API keys...")
    
    fixture_path = "./db/fixtures/api_key_registry.json"
    if not os.path.exists(fixture_path):
        print("    No API keys fixture found, skipping...")
        return
    
    try:
        with open(fixture_path, 'r') as f:
            api_keys_data = json.load(f)
        
        if isinstance(api_keys_data, list):
            for api_key_data in api_keys_data:
                api_key = ApiKey(
                    name=api_key_data.get('name'),
                    api_key=api_key_data.get('api_key'),
                    masked_key=api_key_data['api_key'][:4] + '*' * (len(api_key_data['api_key']) - 8) + api_key_data['api_key'][-4:],
                    active=True,
                    user_id=user_id,
                    type='INFERENCE',
                    usage=0,
                    hits=0,
                    data_tracking=api_key_data.get('data_tracking', False),
                    services=[]
                )
                db.add(api_key)
        
        print(f"    Loaded {len(api_keys_data) if isinstance(api_keys_data, list) else 1} API keys")
        
    except Exception as e:
        print(f"    Warning: Could not load API keys fixture: {e}")
