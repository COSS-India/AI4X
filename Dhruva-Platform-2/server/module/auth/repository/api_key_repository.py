from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from db.postgresql_models import ApiKey as SQLApiKey

from ..model.api_key import ApiKey


class ApiKeyRepository(PostgreSQLBaseRepository[SQLApiKey]):
    def __init__(self, db: Session = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLApiKey)

    def find_by_api_key(self, api_key: str) -> Optional[SQLApiKey]:
        """Find API key by key value"""
        return self.find_one(api_key=api_key)

    def find_by_user_id(self, user_id: UUID) -> List[SQLApiKey]:
        """Find all API keys for a user"""
        return self.find(user_id=user_id)

    def find_active_by_user_id(self, user_id: UUID) -> List[SQLApiKey]:
        """Find all active API keys for a user"""
        return self.find(user_id=user_id, active=True)

    def find_by_name_and_user(self, name: str, user_id: UUID) -> Optional[SQLApiKey]:
        """Find API key by name and user"""
        return self.find_one(name=name, user_id=user_id)

    def increment_usage(self, api_key_id: UUID, usage_increment: int = 1, hits_increment: int = 1) -> int:
        """Increment usage and hits for an API key"""
        return self.db.query(SQLApiKey).filter(
            SQLApiKey.id == api_key_id
        ).update({
            SQLApiKey.usage: SQLApiKey.usage + usage_increment,
            SQLApiKey.hits: SQLApiKey.hits + hits_increment
        })
        self.db.commit()
