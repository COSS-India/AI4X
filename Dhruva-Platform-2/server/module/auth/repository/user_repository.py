from fastapi import Depends
from sqlalchemy.orm import Session

from db.PostgreSQLBaseRepository import PostgreSQLBaseRepository
from db.postgresql_database import get_app_db_session
from db.postgresql_models import User as SQLUser

from ..model.user import User


class UserRepository(PostgreSQLBaseRepository[SQLUser]):
    def __init__(self, db: Session = Depends(get_app_db_session)) -> None:
        super().__init__(db, SQLUser)

    def find_by_email(self, email: str) -> SQLUser:
        """Find user by email address"""
        return self.find_one(email=email)

    def create_user_from_pydantic(self, user_data: User) -> str:
        """Create user from Pydantic model"""
        user_dict = user_data.dict(exclude={'id'})
        return self.insert_one(user_dict)
