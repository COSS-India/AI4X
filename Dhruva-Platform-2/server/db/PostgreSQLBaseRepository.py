"""
PostgreSQL Base Repository
Replaces MongoDB BaseRepository with SQLAlchemy-based implementation
"""

from typing import Generic, List, Optional, Type, TypeVar, Union, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from .postgresql_database import get_app_db_session
from .postgresql_models import AppDBBase

T = TypeVar("T", bound=AppDBBase)
P = TypeVar("P", bound=BaseModel)


class PostgreSQLBaseRepository(Generic[T]):
    """Base repository for PostgreSQL operations using SQLAlchemy"""
    
    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class
    
    def find_by_id(self, id: Union[str, UUID]) -> Optional[T]:
        """Find a record by its UUID"""
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return None
        
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_by_id(self, id: Union[str, UUID]) -> T:
        """Get a record by its UUID, raise exception if not found"""
        result = self.find_by_id(id)
        if result is None:
            raise ValueError(f"Record with id {id} not found")
        return result
    
    def find_one(self, **filters) -> Optional[T]:
        """Find one record matching the filters"""
        query = self.db.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.first()
    
    def get_one(self, **filters) -> T:
        """Get one record matching the filters, raise exception if not found"""
        result = self.find_one(**filters)
        if result is None:
            raise ValueError(f"Record not found with filters: {filters}")
        return result
    
    def find(self, **filters) -> List[T]:
        """Find all records matching the filters"""
        query = self.db.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.all()
    
    def find_all(self) -> List[T]:
        """Find all records"""
        return self.db.query(self.model_class).all()
    
    def insert_one(self, data: Union[T, Dict[str, Any]]) -> str:
        """Insert a new record"""
        if isinstance(data, dict):
            # Convert dict to model instance
            record = self.model_class(**data)
        else:
            record = data
        
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return str(record.id)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to insert record: {e}")
    
    def update_one(self, id: Union[str, UUID], data: Dict[str, Any]) -> int:
        """Update a record by ID"""
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return 0
        
        try:
            result = self.db.query(self.model_class).filter(
                self.model_class.id == id
            ).update(data)
            self.db.commit()
            return result
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update record: {e}")
    
    def update_by_filter(self, filters: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Update records matching filters"""
        query = self.db.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        
        try:
            result = query.update(data)
            self.db.commit()
            return result
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update records: {e}")
    
    def delete_one(self, id: Union[str, UUID]) -> int:
        """Delete a record by ID"""
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return 0
        
        result = self.db.query(self.model_class).filter(
            self.model_class.id == id
        ).delete()
        self.db.commit()
        return result
    
    def delete_many(self, **filters) -> int:
        """Delete records matching filters"""
        query = self.db.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        
        result = query.delete()
        self.db.commit()
        return result
    
    def save(self, record: T) -> T:
        """Save (insert or update) a record"""
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to save record: {e}")
    
    def count(self, **filters) -> int:
        """Count records matching filters"""
        query = self.db.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.count()
    
    def exists(self, **filters) -> bool:
        """Check if any record exists matching filters"""
        return self.count(**filters) > 0


# Utility functions for converting between Pydantic models and SQLAlchemy models
def pydantic_to_sqlalchemy(pydantic_obj: BaseModel, sqlalchemy_class: Type[T], exclude_fields: List[str] = None) -> T:
    """Convert Pydantic model to SQLAlchemy model"""
    if exclude_fields is None:
        exclude_fields = ['id']
    
    data = pydantic_obj.dict(exclude=set(exclude_fields))
    return sqlalchemy_class(**data)


def sqlalchemy_to_dict(sqlalchemy_obj: T, exclude_fields: List[str] = None) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    if exclude_fields is None:
        exclude_fields = []
    
    result = {}
    for column in sqlalchemy_obj.__table__.columns:
        if column.name not in exclude_fields:
            value = getattr(sqlalchemy_obj, column.name)
            # Convert UUID to string for JSON serialization
            if isinstance(value, UUID):
                value = str(value)
            result[column.name] = value
    
    return result
