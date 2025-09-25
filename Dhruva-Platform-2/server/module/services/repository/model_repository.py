from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from db.postgresql_models import Model as SQLModel

from ..model import Model


class ModelRepository(PostgreSQLBaseRepository[SQLModel]):
    def __init__(self, db: Session = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLModel)

    def find_by_model_id(self, model_id: str) -> Optional[SQLModel]:
        """Find model by model_id (business key)"""
        return self.find_one(model_id=model_id)

    def get_by_model_id(self, model_id: str) -> SQLModel:
        """Get model by model_id, raise exception if not found"""
        return self.get_one(model_id=model_id)

    def delete_by_model_id(self, model_id: str) -> int:
        """Delete model by model_id"""
        model = self.find_by_model_id(model_id)
        if model:
            return self.delete_one(model.id)
        return 0

    def update_by_model_id(self, model_id: str, data: dict) -> int:
        """Update model by model_id"""
        model = self.find_by_model_id(model_id)
        if model:
            return self.update_one(model.id, data)
        return 0
