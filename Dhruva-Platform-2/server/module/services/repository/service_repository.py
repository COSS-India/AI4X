from typing import Optional

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from fastapi import Depends
from sqlalchemy.orm import Session

from ..model import Service
from db.postgresql_models import Service as SQLService


class ServiceRepository(PostgreSQLBaseRepository[SQLService]):
    def __init__(self, db: Session = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLService)

    def find_by_service_id(self, service_id: str) -> Optional[SQLService]:
        """Find service by service_id (business key)"""
        return self.find_one(service_id=service_id)

    def get_by_service_id(self, service_id: str) -> SQLService:
        """Get service by service_id, raise exception if not found"""
        return self.get_one(service_id=service_id)

    def delete_by_service_id(self, service_id: str) -> int:
        """Delete service by service_id"""
        service = self.find_by_service_id(service_id)
        if service:
            return self.delete_one(service.id)
        return 0

    def update_by_service_id(self, service_id: str, data: dict) -> int:
        """Update service by service_id"""
        service = self.find_by_service_id(service_id)
        if service:
            return self.update_one(service.id, data)
        return 0
