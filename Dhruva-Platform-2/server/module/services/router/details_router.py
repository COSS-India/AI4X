import traceback
from typing import List

from auth.api_key_type_authorization_provider import ApiKeyTypeAuthorizationProvider
from auth.auth_provider import AuthProvider
from auth.request_session_provider import InjectRequestSession, RequestSession
from exception.base_error import BaseError
from exception.client_error import ClientError, ClientErrorResponse
from fastapi import APIRouter, Depends, status
from schema.auth.common import ApiKeyType
from schema.services.request import ModelViewRequest, ServiceViewRequest
from schema.services.response import (
    ModelViewResponse,
    ServiceListResponse,
    ServiceViewResponse,
)

from ..error import Errors
from ..repository import ModelRepository
from ..service import DetailsService

router = APIRouter(
    prefix="/details",
    dependencies=[
        Depends(AuthProvider),
        Depends(ApiKeyTypeAuthorizationProvider(ApiKeyType.INFERENCE)),
    ],
    responses={"401": {"model": ClientErrorResponse}},
)


@router.get("/list_services", response_model=List[ServiceListResponse])
async def _list_services(
    details_service: DetailsService = Depends(DetailsService),
):
    services_list = details_service.list_services()
    return services_list


@router.post("/view_service", response_model=ServiceViewResponse)
async def _view_service_details(
    request: ServiceViewRequest,
    details_service: DetailsService = Depends(DetailsService),
    session: RequestSession = Depends(InjectRequestSession),
):
    response = details_service.get_service_details(request, session.id)
    return response


@router.get("/list_models", response_model=List[ModelViewResponse])
async def _list_models(model_repository: ModelRepository = Depends(ModelRepository)):
    try:
        models_list = model_repository.find_all()
    except Exception:
        raise BaseError(Errors.DHRUVA106.value, traceback.format_exc())

    # Transform each model to match ModelViewResponse schema
    transformed_models = []
    for model in models_list:
        try:
            # Transform languages from complex objects to simple strings
            languages = []
            langs_src = getattr(model, 'languages', None)
            if langs_src:
                # Expect list of dicts from JSONB; be defensive
                for lang in (langs_src[:10] if isinstance(langs_src, list) else []):
                    if isinstance(lang, dict):
                        source = lang.get('sourceLanguage', '')
                        target = lang.get('targetLanguage', '')
                        if source and target:
                            languages.append(f"{source}-{target}")
                        elif source:
                            languages.append(source)

            # Transform domain from list to string
            domain = "general"
            domain_src = getattr(model, 'domain', None)
            if domain_src:
                if isinstance(domain_src, list) and len(domain_src) > 0:
                    domain = domain_src[0]
                elif isinstance(domain_src, str):
                    domain = domain_src

            # Transform submitter from object to string (JSONB dict)
            submitter = "Unknown"
            submitter_src = getattr(model, 'submitter', None)
            if isinstance(submitter_src, dict):
                submitter = submitter_src.get('name', 'Unknown')

            # Transform task from object to string (JSONB dict)
            task = "unknown"
            task_src = getattr(model, 'task', None)
            if isinstance(task_src, dict):
                task = task_src.get('type', 'unknown')

            # Transform inferenceEndPoint from DB fields
            inference_endpoint = ""
            ref_url = getattr(model, 'ref_url', None)
            if ref_url:
                inference_endpoint = ref_url
            elif getattr(model, 'inference_endpoint', None):
                inference_endpoint = "Available"

            # Create the transformed model
            transformed_model = ModelViewResponse(
                modelId=getattr(model, 'model_id', ''),
                name=getattr(model, 'name', ''),
                description=getattr(model, 'description', ''),
                languages=languages,
                domain=domain,
                submitter=submitter,
                license=getattr(model, 'license', 'Unknown'),
                inferenceEndPoint=inference_endpoint,
                source="dhruva",  # Add default source
                task=task
            )
            transformed_models.append(transformed_model)
        except Exception as e:
            # Log the error but continue with other models
            print(f"Error transforming model {getattr(model, 'model_id', 'unknown')}: {str(e)}")
            continue

    return transformed_models


@router.post("/view_model", response_model=ModelViewResponse)
async def _view_model_details(
    request: ModelViewRequest,
    model_repository: ModelRepository = Depends(ModelRepository),
):
    try:
        model = model_repository.find_by_id(request.modelId)
    except Exception:
        raise BaseError(Errors.DHRUVA105.value, traceback.format_exc())

    if not model:
        raise ClientError(status.HTTP_404_NOT_FOUND, message="Invalid Model Id")

    # Transform the model to match ModelViewResponse schema
    try:
        # Transform languages from JSONB list of dicts to simple strings
        languages = []
        langs_src = getattr(model, 'languages', None)
        if langs_src:
            for lang in (langs_src[:10] if isinstance(langs_src, list) else []):
                if isinstance(lang, dict):
                    source = lang.get('sourceLanguage', '')
                    target = lang.get('targetLanguage', '')
                    if source and target:
                        languages.append(f"{source}-{target}")
                    elif source:
                        languages.append(source)

        # Transform domain from list/string to single string
        domain = "general"
        domain_src = getattr(model, 'domain', None)
        if domain_src:
            if isinstance(domain_src, list) and len(domain_src) > 0:
                domain = domain_src[0]
            elif isinstance(domain_src, str):
                domain = domain_src

        # Submitter name from JSONB dict
        submitter = "Unknown"
        submitter_src = getattr(model, 'submitter', None)
        if isinstance(submitter_src, dict):
            submitter = submitter_src.get('name', 'Unknown')

        # Task type from JSONB dict
        task = "unknown"
        task_src = getattr(model, 'task', None)
        if isinstance(task_src, dict):
            task = task_src.get('type', 'unknown')

        # Inference endpoint string
        inference_endpoint = ""
        ref_url = getattr(model, 'ref_url', None)
        if ref_url:
            inference_endpoint = ref_url
        elif getattr(model, 'inference_endpoint', None):
            inference_endpoint = "Available"

        # Create the transformed model using snake_case fields
        transformed_model = ModelViewResponse(
            modelId=getattr(model, 'model_id', ''),
            name=getattr(model, 'name', ''),
            description=getattr(model, 'description', ''),
            languages=languages,
            domain=domain,
            submitter=submitter,
            license=getattr(model, 'license', 'Unknown'),
            inferenceEndPoint=inference_endpoint,
            source="dhruva",
            task=task,
        )

        return transformed_model
    except Exception as e:
        raise BaseError(Errors.DHRUVA105.value, f"Error transforming model: {str(e)}")
