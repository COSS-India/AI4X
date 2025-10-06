from typing import Optional

from auth import api_key_provider, auth_token_provider
from auth.token_type import TokenType
from db.postgresql_database import get_app_db_session
from exception.client_error import ClientError
from fastapi import Depends, Header, Request, status
from sqlalchemy.orm import Session


def AuthProvider(
    request: Request,
    # This header specifies the origin of the request which
    # can either be API_KEY or AUTH_TOKEN
    x_auth_source: TokenType = Header(default=TokenType.API_KEY),
    db: Session = Depends(get_app_db_session),
):
    # Get Authorization header manually to avoid conflicts between HTTPBearer and APIKeyHeader
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise ClientError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Not authenticated",
        )

    match x_auth_source:
        case TokenType.AUTH_TOKEN:
            # For AUTH_TOKEN, expect "Bearer <token>" format
            if not auth_header.startswith("Bearer "):
                raise ClientError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Not authenticated",
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            validate_status = auth_token_provider.validate_credentials(
                token, request, db
            )
        case TokenType.API_KEY:
            # For API_KEY, expect the raw API key (no Bearer prefix)
            validate_status = api_key_provider.validate_credentials(
                auth_header, request, db
            )

    if not validate_status:  # type: ignore
        raise ClientError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Not authenticated",
        )
