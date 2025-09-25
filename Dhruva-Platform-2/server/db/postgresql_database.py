import os
from typing import Dict, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection engines
app_db_engine = None
log_db_engine = None

# Session makers
AppDBSessionLocal = None
LogDBSessionLocal = None

# Base classes for SQLAlchemy models
AppDBBase = declarative_base()
LogDBBase = declarative_base()

def init_postgresql_connections():
    """Initialize PostgreSQL database connections"""
    global app_db_engine, log_db_engine, AppDBSessionLocal, LogDBSessionLocal
    
    # App database connection
    app_db_connection_string = os.environ.get(
        "APP_DB_CONNECTION_STRING_PG",
        "postgresql://dhruvaadmin:dhruva123@dhruva-platform-app-db-pg:5432/dhruva_app"
    )
    
    app_db_engine = create_engine(
        app_db_connection_string,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )
    
    AppDBSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=app_db_engine
    )
    
    # Log database connection
    log_db_connection_string = os.environ.get(
        "LOG_DB_CONNECTION_STRING_PG",
        "postgresql://dhruvalogadmin:dhruvalog123@dhruva-platform-log-db-pg:5432/dhruva_log"
    )
    
    log_db_engine = create_engine(
        log_db_connection_string,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
    
    LogDBSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=log_db_engine
    )

def get_app_db_session() -> Session:
    """Get a database session for the app database"""
    if AppDBSessionLocal is None:
        init_postgresql_connections()
    
    db = AppDBSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_log_db_session() -> Session:
    """Get a database session for the log database"""
    if LogDBSessionLocal is None:
        init_postgresql_connections()
    
    db = LogDBSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in both databases"""
    if app_db_engine is None or log_db_engine is None:
        init_postgresql_connections()
    
    # Create tables for app database
    AppDBBase.metadata.create_all(bind=app_db_engine)
    
    # Create tables for log database
    LogDBBase.metadata.create_all(bind=log_db_engine)

# Legacy compatibility function for existing code
def AppDatabase() -> Session:
    """Legacy compatibility function - returns app database session"""
    if AppDBSessionLocal is None:
        init_postgresql_connections()
    return AppDBSessionLocal()

# Initialize connections on module import
init_postgresql_connections()
