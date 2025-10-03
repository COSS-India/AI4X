from typing import Optional
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import APIKeyHeader, HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from auth import api_key_provider, auth_token_provider
from auth.token_type import TokenType
from db.postgresql_database import get_app_db_session


def InjectRequestSession(
    credentials_bearer: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    credentials_key: Optional[str] = Depends(APIKeyHeader(name="Authorization")),
    x_auth_source: TokenType = Header(default=TokenType.API_KEY),
    db: Session = Depends(get_app_db_session),
):
    """
    Injects session details from request data into a view function.

    WARNING: Only use in protected routes, otherwise it will throw an error.
    """

    match x_auth_source:
        case TokenType.AUTH_TOKEN:
            if not credentials_bearer:
                raise Exception("Route not protected by authentication")

            session = auth_token_provider.fetch_session(
                credentials_bearer.credentials, db
            )
        case TokenType.API_KEY:
            if not credentials_key:
                raise Exception("Route not protected by authentication")

            session = api_key_provider.fetch_session(credentials_key, db)

    return RequestSession(**session)


class RequestSession(BaseModel):
    id: UUID = Field(alias="_id")
    name: str
    email: EmailStr
    role: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}
