from fastapi import Depends
from sqlalchemy.orm import Session as DBSession
from typing import List
from uuid import UUID

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from db.postgresql_models import Session as SQLSession

from ..model import Session
from ..model.user import User


class SessionRepository(PostgreSQLBaseRepository[SQLSession]):
    def __init__(self, db: DBSession = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLSession)

    def find_by_user_id(self, user_id: UUID) -> List[SQLSession]:
        """Find all sessions for a user"""
        return self.find(user_id=user_id)

    def find_by_type(self, session_type: str) -> List[SQLSession]:
        """Find sessions by type"""
        return self.find(type=session_type)
