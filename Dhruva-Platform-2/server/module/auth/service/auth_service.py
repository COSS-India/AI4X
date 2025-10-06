import math
import os
import secrets
import time
import traceback
import uuid
from datetime import datetime
from typing import List

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from exception import ClientError
from exception.base_error import BaseError
from exception.ulca_delete_api_key_client_error import ULCADeleteApiKeyClientError
from exception.ulca_delete_api_key_server_error import ULCADeleteApiKeyServerError
from exception.ulca_set_api_key_tracking_client_error import (
    ULCASetApiKeyTrackingClientError,
)
from exception.ulca_set_api_key_tracking_server_error import (
    ULCASetApiKeyTrackingServerError,
)
from fastapi import Depends, status
from fastapi_sqlalchemy import db
from db.postgresql_models import Session
from schema.auth.request import (
    CreateApiKeyRequest,
    GetAllApiKeysRequest,
    GetApiKeyQuery,
    ModifyApiKeyParamsQuery,
    RefreshRequest,
    SignInRequest,
    SignUpRequest,
    ULCADeleteApiKeyRequest,
    ULCASetApiKeyTrackingRequest,
)
from schema.auth.response import (
    GetAllApiKeysDetailsResponse,
    GetServiceLevelApiKeysResponse,
    SignInResponse,
    SignUpResponse,
    ULCAApiKeyDeleteResponse,
    ULCAApiKeyTrackingResponse,
)
from schema.auth.response.ulca_api_key_tracking_response import (
    ULCAApiKeyTrackingResponseStatus,
)

from ...services.model import ApiKeyMetering
from ..error import Errors
from ..model.api_key import ApiKey, ApiKeyCache
from ..model.user import User
from ..repository import ApiKeyRepository, SessionRepository, UserRepository
from schema.auth.common import ApiKeyType, RoleType

load_dotenv()


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        session_repository: SessionRepository = Depends(SessionRepository),
        api_key_repository: ApiKeyRepository = Depends(ApiKeyRepository),
    ) -> None:
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.api_key_repository = api_key_repository

    def validate_user(self, request: SignInRequest):
        try:
            user = self.user_repository.find_one(email=request.email)
        except:
            raise BaseError(Errors.DHRUVA201.value, traceback.format_exc())

        if not user:
            raise ClientError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid credentials",
            )

        ph = PasswordHasher()
        ph.check_needs_rehash(user.password)

        try:
            ph.verify(user.password, request.password)
        except VerifyMismatchError:
            raise ClientError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid credentials",
            )
        except Exception:
            raise BaseError(Errors.DHRUVA202.value, traceback.format_exc())

        session_data = {
            "user_id": user.id,
            "type": "refresh",
            "timestamp": datetime.now(),
        }

        try:
            id = self.session_repository.insert_one(session_data)
        except Exception:
            raise BaseError(Errors.DHRUVA203.value, traceback.format_exc())

        token = jwt.encode(
            {
                "sub": str(user.id),
                "name": user.name,
                "exp": (time.time() + 31536000),
                "iat": time.time(),
                "sess_id": str(id),
            },
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
            headers={"tok": "refresh"},
        )

        # create and return jwt
        return SignInResponse(
            id=str(user.id), email=user.email, token=token, role=user.role
        )

    def register_user(self, request: SignUpRequest):
        # Check if user already exists
        try:
            existing_user = self.user_repository.find_one(email=request.email)
        except Exception:
            raise BaseError(Errors.DHRUVA201.value, traceback.format_exc())

        if existing_user:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User with this email already exists",
            )

        # Hash password
        ph = PasswordHasher()
        hashed_password = ph.hash(request.password)

        # Create new user with CONSUMER role
        new_user = User(
            name=request.name,
            email=request.email,
            password=hashed_password,
            role=RoleType.CONSUMER,  # Automatically assign CONSUMER role
        )

        try:
            user_id = self.user_repository.create_user_from_pydantic(new_user)
        except Exception:
            raise BaseError(Errors.DHRUVA207.value, traceback.format_exc())

        # Get the created user
        try:
            created_user = self.user_repository.get_by_id(user_id)
        except Exception:
            raise BaseError(Errors.DHRUVA206.value, traceback.format_exc())

        # Auto-generate default API key
        try:
            api_request = CreateApiKeyRequest(
                name="default",
                type=ApiKeyType.INFERENCE,
                regenerate=False,
                target_user_id=str(created_user.id),
                data_tracking=False,  # Set to false as default for new users
            )

            api_key = self.create_api_key(
                request=api_request,
                id=str(created_user.id),
            )
        except Exception:
            raise BaseError(Errors.DHRUVA207.value, traceback.format_exc())

        return SignUpResponse(
            id=str(created_user.id),
            name=created_user.name,
            email=created_user.email,
            role=created_user.role,
            api_key=api_key,
        )

    def get_refresh_token(self, request: RefreshRequest):
        try:
            headers = jwt.get_unverified_header(request.token)
        except Exception:
            raise ClientError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid refresh token",
            )

        if headers.get("tok") != "refresh":
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid refresh token",
            )

        try:
            claims = jwt.decode(
                request.token, key=os.environ["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
        except Exception:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid refresh token",
            )

        session_data = {
            "user_id": uuid.UUID(claims["sub"]),
            "type": "access",
            "timestamp": datetime.now(),
        }

        try:
            id = self.session_repository.insert_one(session_data)
        except Exception:
            raise BaseError(Errors.DHRUVA203.value, traceback.format_exc())

        token = jwt.encode(
            {
                "sub": claims["sub"],
                "name": claims["name"],
                "exp": (time.time() + 2592000),
                "iat": time.time(),
                "sess_id": str(id),
            },
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
            headers={"tok": "access"},
        )

        return token

    def create_api_key(self, request: CreateApiKeyRequest, id: str):
        try:
            user_id = (
                id if not request.target_user_id else request.target_user_id
            )
        except Exception:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid target user id",
            )

        try:
            existing_api_key = self.api_key_repository.find_one(
                name=request.name, user_id=user_id
            )
        except Exception:
            raise BaseError(Errors.DHRUVA208.value, traceback.format_exc())

        if existing_api_key and request.regenerate:
            key = self.__regenerate_api_key(existing_api_key)
        elif existing_api_key and not request.regenerate:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="API Key name already exists",
            )
        else:
            key = self.__generate_new_api_key(request, user_id)

        return key

    def __mask_key(self, key: str):
        masked_key = key[:4] + (len(key) - 8) * "*" + key[-4:]
        return masked_key

    def __generate_new_api_key(self, request: CreateApiKeyRequest, id: str):
        key = secrets.token_urlsafe(48)
        api_key_data = {
            "name": request.name,
            "api_key": key,
            "masked_key": self.__mask_key(key),
            "active": True,
            "user_id": uuid.UUID(id) if isinstance(id, str) else id,
            "type": request.type.value if hasattr(request.type, 'value') else request.type,
            "created_timestamp": datetime.now(),
            "data_tracking": request.data_tracking,
        }

        try:
            inserted_id = self.api_key_repository.insert_one(api_key_data)
            
            # Create ApiKey object for caching
            api_key = ApiKey(**api_key_data)
            api_key.id = inserted_id

            # Cache write
            api_key_cache = ApiKeyCache(**api_key.dict())
            api_key_cache.save()
        except Exception:
            raise BaseError(Errors.DHRUVA204.value, traceback.format_exc())

        return key

    def __regenerate_api_key(self, existing_api_key):
        key = secrets.token_urlsafe(48)
        existing_api_key.api_key = key
        existing_api_key.masked_key = self.__mask_key(key)
        existing_api_key.created_timestamp = datetime.now()

        try:
            self.api_key_repository.save(existing_api_key)

            # Convert to Pydantic model for caching
            api_key_data = {
                "id": str(existing_api_key.id),
                "name": existing_api_key.name,
                "api_key": existing_api_key.api_key,
                "masked_key": existing_api_key.masked_key,
                "active": existing_api_key.active,
                "user_id": str(existing_api_key.user_id),
                "type": existing_api_key.type,
                "created_timestamp": existing_api_key.created_timestamp,
                "data_tracking": existing_api_key.data_tracking,
                "services": existing_api_key.services or []
            }
            
            # Cache write
            api_key_cache = ApiKeyCache(**api_key_data)
            api_key_cache.save()
        except Exception:
            raise BaseError(Errors.DHRUVA204.value, traceback.format_exc())

        return key

    def get_api_key(self, params: GetApiKeyQuery, id: str):
        try:
            user_id = (
                id if not params.target_user_id else params.target_user_id
            )
        except Exception:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid target user id",
            )

        try:
            key = self.api_key_repository.find_one(
                name=params.api_key_name, user_id=user_id
            )
        except Exception:
            raise BaseError(Errors.DHRUVA208.value, traceback.format_exc())

        if not key:
            raise ClientError(
                status_code=status.HTTP_404_NOT_FOUND,
                message="API Key does not exist",
            )
        # Create the GetApiKeyResponse model with proper field mapping
        from schema.auth.response.get_api_key_response import GetApiKeyResponse
        
        return GetApiKeyResponse(
            _id=str(key.id),  # Use _id as the key (due to alias)
            name=key.name,
            masked_key=key.masked_key,
            active=key.active,
            type=key.type,
            created_timestamp=key.created_timestamp,
            data_tracking=key.data_tracking,
            services=[]  # Start with empty list for now
        )

    def __filter_service_id(self, keys: List[dict], service_id: str):
        from schema.auth.common import ServiceLevelApiKeyDisplay
        
        total_usage = 0
        filtered_keys = []
        
        for key in keys:
            service = list(
                filter(lambda service: service.get('service_id') == service_id, key.get('services', []))
            )
            if service:
                usage = service[0].get('usage', 0)
                total_usage += usage
            else:
                usage = 0

            # Convert ApiKey to ServiceLevelApiKeyDisplay
            service_level_key = ServiceLevelApiKeyDisplay(
                name=key.get('name', ''),
                usage=usage
            )
            filtered_keys.append(service_level_key)

        return filtered_keys, total_usage

    def get_all_api_keys(self, params: GetAllApiKeysRequest, id: str):
        try:
            user_id = (
                id if not params.target_user_id else params.target_user_id
            )
            # Convert string to UUID if needed
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except Exception:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid target user id",
            )

        try:
            sql_keys = self.api_key_repository.find_by_user_id(user_id)
            
            # Convert SQLAlchemy objects to Pydantic models
            keys = []
            for sql_key in sql_keys:
                # Convert services to the expected format
                services = []
                if hasattr(sql_key, 'services') and sql_key.services:
                    for service in sql_key.services:
                        services.append({
                            "service_id": service.get('service_id', ''),
                            "usage": service.get('usage', 0)
                        })
                
                key_data = {
                    "id": str(sql_key.id),
                    "name": sql_key.name,
                    "masked_key": sql_key.masked_key,
                    "active": sql_key.active,
                    "type": sql_key.type,
                    "created_timestamp": sql_key.created_timestamp,
                    "services": services,
                    "data_tracking": sql_key.data_tracking
                }
                keys.append(key_data)
            
            if hasattr(params, "target_service_id") and params.target_service_id:
                keys, total_usage = self.__filter_service_id(
                    keys, params.target_service_id
                )
                return GetServiceLevelApiKeysResponse(
                    api_keys=keys, total_usage=total_usage
                )
        except Exception:
            raise BaseError(Errors.DHRUVA205.value, traceback.format_exc())

        return GetAllApiKeysDetailsResponse(api_keys=keys)

    def get_all_api_keys_with_usage(self, page, limit, target_user_id: str) -> List:
        """
        Fetches all API keys from the collection and calculates the total usage
        Args:
            - page: Current page
            - limit: Number of documents per page
            - target_user_id: User id to filter api keys with
        Returns:
            - List[APIKeys]
            - total_usage
            - total_pages
        """
        # Convert string to UUID if needed
        if isinstance(target_user_id, str):
            target_user_id = uuid.UUID(target_user_id)
            
        sql_keys = self.api_key_repository.find(user_id=target_user_id)
        total_usage = sum(k.usage for k in sql_keys)
        
        # Convert SQLAlchemy objects to Pydantic models
        keys = []
        for sql_key in sql_keys:
            # Convert services to the expected format
            services = []
            if hasattr(sql_key, 'services') and sql_key.services:
                for service in sql_key.services:
                    services.append({
                        "service_id": service.get('service_id', ''),
                        "usage": service.get('usage', 0)
                    })
            
            key_data = {
                "id": str(sql_key.id),
                "name": sql_key.name,
                "masked_key": sql_key.masked_key,
                "active": sql_key.active,
                "type": sql_key.type,
                "created_timestamp": sql_key.created_timestamp,
                "services": services,
                "data_tracking": sql_key.data_tracking
            }
            keys.append(key_data)

        return (
            keys[(page - 1) * limit : page * limit],
            total_usage,
            math.ceil(len(keys) / limit),
        )

    def modify_api_key(self, params: ModifyApiKeyParamsQuery, id: str):
        try:
            user_id = (
                id if not params.target_user_id else params.target_user_id
            )
        except Exception:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid target user id",
            )

        try:
            api_key = self.api_key_repository.find_one(
                name=params.api_key_name, user_id=user_id
            )
        except Exception:
            raise BaseError(Errors.DHRUVA208.value, traceback.format_exc())

        if not api_key:
            raise ClientError(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Api key not found",
            )

        if params.data_tracking is not None:
            api_key.data_tracking = params.data_tracking

        if params.active is not None:
            api_key.active = params.active

        try:
            self.api_key_repository.save(api_key)

            # Cache write
            api_key_cache = ApiKeyCache(**api_key.dict())
            api_key_cache.save()
        except Exception:
            raise BaseError(Errors.DHRUVA211.value, traceback.format_exc())

        return api_key

    def set_api_key_status_ulca(self, request: ULCADeleteApiKeyRequest, id: str):
        api_key_name = request.emailId + "/" + request.appName

        try:
            api_key = self.api_key_repository.find_one(
                name=api_key_name, user_id=id
            )
        except Exception:
            raise ULCADeleteApiKeyServerError(
                Errors.DHRUVA208.value, traceback.format_exc()
            )

        if not api_key:
            raise ULCADeleteApiKeyClientError(
                status.HTTP_404_NOT_FOUND, "API Key not found"
            )

        api_key.active = False

        try:
            self.api_key_repository.save(api_key)

            # Convert to Pydantic model for caching
            api_key_data = {
                "id": str(api_key.id),
                "name": api_key.name,
                "api_key": api_key.api_key,
                "masked_key": api_key.masked_key,
                "active": api_key.active,
                "user_id": str(api_key.user_id),
                "type": api_key.type,
                "created_timestamp": api_key.created_timestamp,
                "data_tracking": api_key.data_tracking,
                "services": api_key.services or []
            }
            
            # Cache write
            api_key_cache = ApiKeyCache(**api_key_data)
            api_key_cache.save()
        except Exception:
            raise ULCADeleteApiKeyServerError(
                Errors.DHRUVA209.value, traceback.format_exc()
            )

        return ULCAApiKeyDeleteResponse(
            isRevoked=True, message="API Key successfully deleted"
        )

    def set_api_key_tracking_ulca(
        self, request: ULCASetApiKeyTrackingRequest, id: str
    ):
        api_key_name = request.emailId + "/" + request.appName

        try:
            api_key = self.api_key_repository.find_one(
                name=api_key_name, user_id=id
            )
        except Exception:
            raise ULCASetApiKeyTrackingServerError(
                Errors.DHRUVA208.value, traceback.format_exc()
            )

        if not api_key:
            raise ULCASetApiKeyTrackingClientError(
                status.HTTP_404_NOT_FOUND, "API Key not found"
            )

        api_key.data_tracking = request.dataTracking

        try:
            self.api_key_repository.save(api_key)

            # Convert to Pydantic model for caching
            api_key_data = {
                "id": str(api_key.id),
                "name": api_key.name,
                "api_key": api_key.api_key,
                "masked_key": api_key.masked_key,
                "active": api_key.active,
                "user_id": str(api_key.user_id),
                "type": api_key.type,
                "created_timestamp": api_key.created_timestamp,
                "data_tracking": api_key.data_tracking,
                "services": api_key.services or []
            }
            
            # Cache write
            api_key_cache = ApiKeyCache(**api_key_data)
            api_key_cache.save()
        except Exception:
            raise ULCASetApiKeyTrackingServerError(
                Errors.DHRUVA210.value, traceback.format_exc()
            )

        return ULCAApiKeyTrackingResponse(
            status=ULCAApiKeyTrackingResponseStatus.SUCCESS,
            message="API Key tracking status successfully changed",
        )
