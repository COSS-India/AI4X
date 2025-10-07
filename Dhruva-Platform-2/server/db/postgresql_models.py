"""
SQLAlchemy models for PostgreSQL database
Replaces MongoDB collections with relational tables
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Boolean, Integer, BigInteger, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .postgresql_database import AppDBBase, LogDBBase


class User(AppDBBase):
    """User model - replaces MongoDB 'user' collection"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='USER')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class Model(AppDBBase):
    """Model model - replaces MongoDB 'model' collection"""
    __tablename__ = "models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), unique=True, nullable=False)
    version = Column(String(100), nullable=False)
    submitted_on = Column(BigInteger, nullable=False)
    updated_on = Column(BigInteger, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    ref_url = Column(String(500))
    task = Column(JSONB, nullable=False)
    languages = Column(JSONB, nullable=False, default=list)
    license = Column(String(255))
    domain = Column(JSONB, nullable=False, default=list)
    inference_endpoint = Column(JSONB, nullable=False)
    benchmarks = Column(JSONB)
    submitter = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    services = relationship("Service", back_populates="model")


class Service(AppDBBase):
    """Service model - replaces MongoDB 'service' collection"""
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    service_description = Column(Text)
    hardware_description = Column(Text)
    published_on = Column(BigInteger, nullable=False)
    model_id = Column(String(255), ForeignKey('models.model_id'))
    endpoint = Column(String(500), nullable=False)
    api_key = Column(String(255))
    health_status = Column(JSONB)
    benchmarks = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    model = relationship("Model", back_populates="services")


class ApiKey(AppDBBase):
    """API Key model - replaces MongoDB 'api_key' collection"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    masked_key = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False, default='INFERENCE')
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    usage = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    data_tracking = Column(Boolean, default=False)
    services = Column(JSONB, default=list)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Session(AppDBBase):
    """Session model - replaces MongoDB 'session' collection"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    type = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class Feedback(AppDBBase):
    """Feedback model - replaces MongoDB 'feedback' collection"""
    __tablename__ = "feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    api_key_name = Column(String(255))
    feedback_timestamp = Column(Integer)  # Store the original feedbackTimeStamp
    feedback_language = Column(String(50))  # Store the feedbackLanguage
    pipeline_input = Column(JSONB)
    pipeline_output = Column(JSONB)
    suggested_pipeline_output = Column(JSONB)
    pipeline_feedback = Column(JSONB)
    task_feedback = Column(JSONB)  # Store taskFeedback as JSONB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="feedback")


# Log database models (if needed for future log data)
class LogEntry(LogDBBase):
    """Log entry model for log database"""
    __tablename__ = "log_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String(50))
    message = Column(Text)
    service = Column(String(100))
    user_id = Column(String(255))  # Store as string since it might reference app DB
    api_key_id = Column(String(255))
    request_data = Column(JSONB)
    response_data = Column(JSONB)
    error_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
