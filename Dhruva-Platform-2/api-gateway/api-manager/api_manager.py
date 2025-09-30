#!/usr/bin/env python3
"""
Kong API Manager
Syncs API keys and services from MongoDB to Kong
"""

import os
import time
import logging
import schedule
from datetime import datetime
from typing import Dict, List, Optional
import requests
from pymongo import MongoClient
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
KONG_ADMIN_URL = os.getenv('KONG_ADMIN_URL', 'http://kong:8001')
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', 30))  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for health checks
app = Flask(__name__)

class KongAPIManager:
    def __init__(self):
        self.mongo_client = MongoClient(MONGODB_URI)
        self.db = self.mongo_client.get_default_database()
        self.kong_admin_url = KONG_ADMIN_URL
        self.synced_consumers = set()
        self.synced_services = set()
        
    def get_kong_consumers(self) -> List[Dict]:
        """Get all consumers from Kong"""
        try:
            response = requests.get(f"{self.kong_admin_url}/consumers")
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to get Kong consumers: {e}")
            return []
    
    def get_kong_services(self) -> List[Dict]:
        """Get all services from Kong"""
        try:
            response = requests.get(f"{self.kong_admin_url}/services")
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to get Kong services: {e}")
            return []
    
    def create_kong_consumer(self, username: str) -> bool:
        """Create a consumer in Kong"""
        try:
            data = {"username": username}
            response = requests.post(f"{self.kong_admin_url}/consumers", json=data)
            response.raise_for_status()
            logger.info(f"Created Kong consumer: {username}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # Already exists
                logger.debug(f"Consumer {username} already exists")
                return True
            logger.error(f"Failed to create Kong consumer {username}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create Kong consumer {username}: {e}")
            return False
    
    def create_kong_api_key(self, consumer_username: str, api_key: str) -> bool:
        """Create an API key for a consumer in Kong"""
        try:
            data = {"key": api_key}
            response = requests.post(
                f"{self.kong_admin_url}/consumers/{consumer_username}/key-auth",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Created API key for consumer: {consumer_username}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # Already exists
                logger.debug(f"API key for {consumer_username} already exists")
                return True
            logger.error(f"Failed to create API key for {consumer_username}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create API key for {consumer_username}: {e}")
            return False
    
    def create_kong_service(self, service_data: Dict) -> bool:
        """Create a service in Kong"""
        try:
            response = requests.post(f"{self.kong_admin_url}/services", json=service_data)
            response.raise_for_status()
            logger.info(f"Created Kong service: {service_data['name']}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # Already exists
                logger.debug(f"Service {service_data['name']} already exists")
                return True
            logger.error(f"Failed to create Kong service {service_data['name']}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create Kong service {service_data['name']}: {e}")
            return False
    
    def create_kong_route(self, service_name: str, route_data: Dict) -> bool:
        """Create a route for a service in Kong"""
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/routes",
                json=route_data
            )
            response.raise_for_status()
            logger.info(f"Created route for service: {service_name}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:  # Already exists
                logger.debug(f"Route for {service_name} already exists")
                return True
            logger.error(f"Failed to create route for {service_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create route for {service_name}: {e}")
            return False
    
    def sync_api_keys(self):
        """Sync API keys from MongoDB to Kong"""
        try:
            # Get all API keys from MongoDB
            api_keys = list(self.db.api_key.find({"active": True}))
            logger.info(f"Found {len(api_keys)} active API keys in MongoDB")
            
            for api_key_doc in api_keys:
                username = f"user_{api_key_doc['user_id']}"
                api_key = api_key_doc['api_key']
                
                # Create consumer if not exists
                if username not in self.synced_consumers:
                    if self.create_kong_consumer(username):
                        self.synced_consumers.add(username)
                
                # Create API key
                self.create_kong_api_key(username, api_key)
                
        except Exception as e:
            logger.error(f"Failed to sync API keys: {e}")
    
    def sync_services(self):
        """Sync services from MongoDB to Kong"""
        try:
            # Get all services from MongoDB
            services = list(self.db.service.find())
            logger.info(f"Found {len(services)} services in MongoDB")
            
            for service_doc in services:
                service_name = f"service_{service_doc['serviceId']}"
                endpoint = service_doc.get('endpoint', '')
                
                if not endpoint:
                    logger.warning(f"Service {service_doc['serviceId']} has no endpoint")
                    continue
                
                # Create service in Kong
                service_data = {
                    "name": service_name,
                    "url": endpoint,
                    "connect_timeout": 60000,
                    "read_timeout": 60000,
                    "write_timeout": 60000
                }
                
                if service_name not in self.synced_services:
                    if self.create_kong_service(service_data):
                        self.synced_services.add(service_name)
                
                # Create route
                route_data = {
                    "name": f"{service_name}-route",
                    "paths": [f"/{service_doc['serviceId']}"],
                    "strip_path": True
                }
                
                self.create_kong_route(service_name, route_data)
                
        except Exception as e:
            logger.error(f"Failed to sync services: {e}")
    
    def sync_all(self):
        """Sync all data from MongoDB to Kong"""
        logger.info("Starting sync from MongoDB to Kong...")
        self.sync_api_keys()
        self.sync_services()
        logger.info("Sync completed")

# Global instance
api_manager = KongAPIManager()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/sync')
def manual_sync():
    """Manual sync endpoint"""
    try:
        api_manager.sync_all()
        return jsonify({"status": "success", "message": "Sync completed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_scheduler():
    """Run the scheduler for periodic sync"""
    schedule.every(SYNC_INTERVAL).seconds.do(api_manager.sync_all)
    
    logger.info(f"Starting scheduler with {SYNC_INTERVAL}s interval")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import threading
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run initial sync
    api_manager.sync_all()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)
