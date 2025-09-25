"""
PostgreSQL Base Model
Replaces MongoBaseModel with UUID-based Pydantic models
"""

from typing import Optional, Dict, Any
from uuid import UUID
import uuid

from pydantic import BaseModel, Field
from schema.auth.common import RoleType


class UUIDField:
    """Custom field for UUID validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError:
                raise ValueError("Invalid UUID format")
        raise ValueError("Invalid UUID type")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", format="uuid")


class PostgreSQLBaseModel(BaseModel):
    """Base model for PostgreSQL-backed entities"""
    id: Optional[UUID] = Field(default=None, description="UUID primary key")

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary, handling UUID serialization"""
        kwargs.update({"exclude_none": True})
        data = super().dict(**kwargs)
        
        # Convert UUID to string for JSON serialization
        if 'id' in data and data['id'] is not None:
            data['id'] = str(data['id'])
            
        return data

    class Config:
        # Allow population by field name and alias
        allow_population_by_field_name = True
        # Allow arbitrary types (like UUID)
        arbitrary_types_allowed = True
        # JSON encoders for special types
        json_encoders = {
            UUID: str,
            RoleType: str
        }
        # Use enum values instead of enum names
        use_enum_values = True


class TimestampMixin(BaseModel):
    """Mixin for models that need timestamp fields"""
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


# Legacy compatibility - alias for existing code
MongoBaseModel = PostgreSQLBaseModel
