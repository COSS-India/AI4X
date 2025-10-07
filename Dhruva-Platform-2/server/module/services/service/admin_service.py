import datetime
import traceback

from exception.base_error import BaseError
from exception.client_error import ClientError
from fastapi import Depends, status
from schema.auth.response.get_all_api_keys_response import GetAllApiKeysDetailsResponse
from schema.services.request import (
    ModelCreateRequest,
    ModelUpdateRequest,
    ServiceCreateRequest,
    ServiceHeartbeatRequest,
    ServiceUpdateRequest,
)

from ...auth.service.auth_service import AuthService
from ..error.errors import Errors
from ..model import ModelCache, Service, ServiceCache
from db.postgresql_models import Model
from ..repository import ModelRepository, ServiceRepository


class AdminService:
    def __init__(
        self,
        service_repository: ServiceRepository = Depends(ServiceRepository),
        model_repository: ModelRepository = Depends(ModelRepository),
        auth_service: AuthService = Depends(AuthService),
    ):
        self.service_repository = service_repository
        self.model_repository = model_repository
        self.auth_service = auth_service

    def view_dashboard(self, page, limit, target_user_id):
        try:
            (
                api_keys,
                total_usage,
                total_pages,
            ) = self.auth_service.get_all_api_keys_with_usage(
                page, limit, target_user_id
            )
        except Exception:
            raise BaseError(Errors.DHRUVA109.value, traceback.format_exc())

        return GetAllApiKeysDetailsResponse(
            api_keys=api_keys,
            total_usage=total_usage,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    def create_service(self, request: ServiceCreateRequest):
        svc = request.dict()
        service = Service(**svc)
        insert_id = self.service_repository.insert_one(service)

        svc.update({"_id": insert_id})
        cache = ServiceCache(**svc)
        cache.save()
        return insert_id

    def _json_safe(self, value):
        # Recursively convert datetime objects to ISO strings inside JSON structures
        import datetime as _dt
        if isinstance(value, dict):
            return {k: self._json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._json_safe(v) for v in value]
        if isinstance(value, _dt.datetime):
            return value.isoformat()
        return value

    def create_model(self, request: ModelCreateRequest):
        mdl = request.dict()
        
        # Transform camelCase to snake_case for PostgreSQL
        postgres_data = {
            "model_id": mdl["modelId"],
            "version": mdl["version"],
            "submitted_on": mdl["submittedOn"],
            "updated_on": mdl["updatedOn"],
            "name": mdl["name"],
            "description": mdl["description"],
            "ref_url": mdl["refUrl"],
            # JSONB fields serialized safely
            "task": self._json_safe(mdl["task"]),
            "languages": self._json_safe(mdl["languages"]),
            "license": mdl["license"],
            "domain": self._json_safe(mdl["domain"]),
            "inference_endpoint": self._json_safe(mdl["inferenceEndPoint"]),
            "benchmarks": self._json_safe(mdl.get("benchmarks")),
            "submitter": self._json_safe(mdl["submitter"])
        }
        
        model = Model(**postgres_data)
        insert_id = self.model_repository.insert_one(model)

        # Do NOT overwrite modelId; cache is keyed by modelId
        cache = ModelCache(**mdl)
        cache.save()
        return insert_id

    def update_service(self, request: ServiceUpdateRequest):
        cache = ServiceCache.get(request.serviceId)
        request_dict = request.dict()

        # Cache ignores all complex fields
        new_cache = cache.dict()
        for key, value in request_dict.items():
            if key in cache.__fields__ and value:
                new_cache[key] = value

        new_cache = ServiceCache(**new_cache)
        new_cache.save()

        return self.service_repository.update_one(request.dict())

    def update_model(self, request: ModelUpdateRequest):
        request_dict = request.dict()

        # Require presence in cache (consistent behavior): 404 if not found
        try:
            cache = ModelCache.get(request.modelId)
        except Exception:
            raise ClientError(status.HTTP_404_NOT_FOUND, message="Model not found in cache")

        # Cache ignores all complex fields
        new_cache = cache.dict()
        for key, value in request_dict.items():
            if key in cache.__fields__ and value:
                new_cache[key] = value
        new_cache = ModelCache(**new_cache)
        new_cache.save()

        # Transform camelCase to snake_case for PostgreSQL
        postgres_data = {}
        for key, value in request_dict.items():
            if value is not None:  # Only include non-null values
                if key == "modelId":
                    # filter will use model_id; do not include in data
                    continue
                elif key == "refUrl":
                    postgres_data["ref_url"] = value
                elif key == "inferenceEndPoint":
                    postgres_data["inference_endpoint"] = self._json_safe(value)
                elif key in ("task", "languages", "domain", "benchmarks", "submitter"):
                    postgres_data[key] = self._json_safe(value)
                else:
                    postgres_data[key] = value

        # Use update_by_filter with model_id filter
        return self.model_repository.update_by_filter({"model_id": request.modelId}, postgres_data)

    def delete_service(self, id):
        ServiceCache.delete(id)
        return self.service_repository.delete_one(id)

    def delete_model(self, id):
        ModelCache.delete(id)
        return self.model_repository.delete_one(id)

    def inference_service_status(self, request_body: ServiceHeartbeatRequest):
        try:
            service = self.service_repository.find_by_id(request_body.serviceId)
            if not service:
                raise BaseError(Errors.DHRUVA104.value)
            service = service.dict()
            if "healthStatus" not in service:
                service["healthStatus"] = {}
            service["healthStatus"]["status"] = request_body.status
            service["healthStatus"]["lastUpdated"] = str(datetime.datetime.now())
            self.service_repository.update_one(service)
            return {"message": "Service status updated successfully"}
        except:
            raise BaseError(Errors.DHRUVA113.value, traceback.format_exc())
