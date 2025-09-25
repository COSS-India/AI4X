from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from db.postgresql_models import Feedback as SQLFeedback

from ..model import Feedback


class FeedbackRepository(PostgreSQLBaseRepository[SQLFeedback]):
    def __init__(self, db: Session = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLFeedback)

    def find_by_user_id(self, user_id: UUID) -> List[SQLFeedback]:
        """Find all feedback for a user"""
        return self.find(user_id=user_id)

    def find_by_api_key_name(self, api_key_name: str) -> List[SQLFeedback]:
        """Find feedback by API key name"""
        return self.find(api_key_name=api_key_name)