import os
from sqlalchemy.orm import Session

from dotenv import load_dotenv
from db.postgresql_database import AppDBSessionLocal, init_postgresql_connections

load_dotenv()

# Initialize PostgreSQL connections
init_postgresql_connections()


def AppDatabase() -> Session:
    """Get PostgreSQL app database session"""
    return AppDBSessionLocal()
