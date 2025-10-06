from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from auth import api_key_provider, auth_token_provider
from auth.token_type import TokenType
from db.postgresql_database import get_app_db_session


def InjectRequestSession(
    request: Request,
    x_auth_source: TokenType = Header(default=TokenType.API_KEY),
    db: Session = Depends(get_app_db_session),
):
    """
    Injects session details from request data into a view function.

    WARNING: Only use in protected routes, otherwise it will throw an error.
    """

    # Get Authorization header manually to avoid conflicts between HTTPBearer and APIKeyHeader
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise Exception("Route not protected by authentication")

    match x_auth_source:
        case TokenType.AUTH_TOKEN:
            # For AUTH_TOKEN, expect "Bearer <token>" format
            if not auth_header.startswith("Bearer "):
                raise Exception("Route not protected by authentication")
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            session = auth_token_provider.fetch_session(token, db)
        case TokenType.API_KEY:
            # For API_KEY, expect the raw API key (no Bearer prefix)
            session = api_key_provider.fetch_session(auth_header, db)

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
