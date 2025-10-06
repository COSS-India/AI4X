from typing import Any, Dict, List
from uuid import UUID

from db.postgresql_database import get_app_db_session
from db.postgresql_models import User as SQLUser
from exception import ClientError
from fastapi import Depends, Request, status
from sqlalchemy.orm import Session
from schema.auth.common import RoleType


class RoleAuthorizationProvider:
    def __init__(self, roles: List[RoleType]) -> None:
        self.roles = roles

    def __call__(self, request: Request, db: Session = Depends(get_app_db_session)):
        # Get user from PostgreSQL using SQLAlchemy
        user = db.query(SQLUser).filter(SQLUser.id == request.state.user_id).first()
        
        if not user:
            raise ClientError(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found",
            )

        user_role = RoleType[user.role]

        if user_role == RoleType.ADMIN:
            return

        if user_role not in self.roles:
            raise ClientError(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Not authorized",
            )
