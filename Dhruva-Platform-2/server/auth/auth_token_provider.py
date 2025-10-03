import os
from typing import Any, Dict
from uuid import UUID

import jwt
from dotenv import load_dotenv
from exception import BaseError
from fastapi import Request
from sqlalchemy.orm import Session

from .errors import Errors

load_dotenv()


def validate_credentials(credentials: str, request: Request, db: Session) -> bool:
    try:
        headers = jwt.get_unverified_header(credentials)
    except Exception:
        return False

    if headers["tok"] != "access":
        return False

    try:
        claims = jwt.decode(
            credentials, key=os.environ["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
    except Exception:
        return False

    from module.auth.repository.session_repository import SessionRepository
    from module.auth.repository.api_key_repository import ApiKeyRepository

    session_repo = SessionRepository(db)
    session = session_repo.find_by_id(UUID(claims["sess_id"]))

    if "inference" in request.url.path or "feedback" in request.url.path:
        user_id = UUID(claims["sub"])
        api_key_repo = ApiKeyRepository(db)
        api_key = api_key_repo.find_one(name="default", user_id=user_id)

        if api_key is None:
            raise BaseError(
                error=Errors.DHRUVA_DEP100.value,
            )

        request.state.api_key_id = str(api_key.id)
        request.state.api_key_type = api_key.type
        request.state.api_key_name = "default"

    request.state.user_id = claims["sub"]

    if not session:
        return False

    return True


def fetch_session(credentials: str, db: Session):
    # This cannot fail, since this was already checked during auth verification
    claims = jwt.decode(
        credentials, key=os.environ["JWT_SECRET_KEY"], algorithms=["HS256"]
    )

    from module.auth.repository.session_repository import SessionRepository
    from module.auth.repository.user_repository import UserRepository

    session_repo = SessionRepository(db)
    user_repo = UserRepository(db)

    # Session has to exist since it was already checked during auth verification
    session = session_repo.find_by_id(UUID(claims["sess_id"]))

    if not session:
        return None

    user = user_repo.find_by_id(session.user_id)

    if not user:
        return None

    # Convert to dict and remove password
    user_dict = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

    return user_dict
