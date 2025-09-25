import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from db.postgresql_database import AppDBSessionLocal, init_postgresql_connections

load_dotenv(override=True)

# Initialize PostgreSQL connections
init_postgresql_connections()

def AppDatabase() -> Session:
    """Get PostgreSQL app database session"""
    return AppDBSessionLocal()


def LogDatastore():
    """Placeholder for cloud storage - disabled in sandbox mode"""
    print("[SANDBOX MODE] Cloud storage disabled - LogDatastore not available")
    return None
