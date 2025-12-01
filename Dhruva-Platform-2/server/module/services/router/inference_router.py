import json
import time
from typing import Any, Callable, Dict, Optional, Union

from auth.api_key_type_authorization_provider import ApiKeyTypeAuthorizationProvider
from auth.auth_provider import AuthProvider
from celery_backend.tasks import log_data
from exception.base_error import BaseError
from exception.client_error import ClientErrorResponse
from fastapi import APIRouter, Depends, Request
from fastapi.routing import APIRoute, Request, Response
from schema.auth.common import ApiKeyType
from schema.services.request import (
    ULCAAsrInferenceRequest,
    ULCAInferenceQuery,
    ULCALLMInferenceRequest,
    ULCANerInferenceRequest,
    ULCAOCRInferenceRequest,
    ULCAPipelineInferenceRequest,
    ULCAS2SInferenceRequest,
    ULCASpeakerDiarizationInferenceRequest,
    ULCALanguageDiarizationInferenceRequest,
    ULCAAudioLangDetectionInferenceRequest,
    ULCATextLangDetectionInferenceRequest,
    ULCATranslationInferenceRequest,
    ULCATransliterationInferenceRequest,
    ULCATtsInferenceRequest,
    ULCAVadInferenceRequest,
)
from schema.services.response import (
    ULCAAsrInferenceResponse,
    ULCALLMInferenceResponse,
    ULCANerInferenceResponse,
    ULCAOCRInferenceResponse,
    ULCAPipelineInferenceResponse,
    ULCAS2SInferenceResponse,
    ULCASpeakerDiarizationInferenceResponse,
    ULCALanguageDiarizationInferenceResponse,
    ULCAAudioLangDetectionInferenceResponse,
    ULCATextLangDetectionInferenceResponse,
    ULCATranslationInferenceResponse,
    ULCATransliterationInferenceResponse,
    ULCATtsInferenceResponse,
    ULCAVadInferenceResponse,
)

from ..error import Errors

# from ..repository import ServiceRepository, ModelRepository
from ..service.inference_service import InferenceService


class InferenceLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            req_body_bytes = await request.body()
            req_body = req_body_bytes.decode("utf-8")
            enable_tracking = False

            start_time = time.time()
            api_key_id, res_body, error_msg = None, None, None
            try:
                response: Response = await original_route_handler(request)
                res_body = response.body
                api_key_id = str(
                    request.state.api_key_id
                )  # Having this here to capture all errors

            except BaseError as exc:
                if exc.error_kind in (
                    Errors.DHRUVA101.value["kind"],
                    Errors.DHRUVA102.value["kind"],
                ):
                    error_msg = exc.error_kind + "_" + exc.error_message
                raise exc

            except Exception as other_exception:
                error_msg = str(other_exception)
                raise other_exception

            finally:
                req_json: Dict[str, Any] = json.loads(req_body)
                if request.state._state.get("api_key_data_tracking"):
                    controlConfig: Dict[str, Any] = req_json.get("controlConfig", {})
                    enable_tracking = controlConfig.get("dataTracking", True)

                config = req_json.get("config", {})
                service_id = config.get("serviceId")

                url_components = request.url._url.split("?serviceId=")
                if len(url_components) == 2:
                    service_component = url_components[1]
                    service_id = service_component.replace("%2F", "/")

                usage_type = url_components[0].split("/")[-1]

                log_data.apply_async(
                    (
                        usage_type,
                        service_id,
                        request.headers.get("X-Forwarded-For", request.client.host),
                        enable_tracking,
                        error_msg,
                        api_key_id,
                        request.state._state.get("input", req_body),
                        res_body.decode("utf-8") if res_body else None,
                        time.time() - start_time,
                    ),
                    queue="data-log",
                )

            return response

        return logging_route_handler


router = APIRouter(
    prefix="/inference",
    route_class=InferenceLoggingRoute,
    dependencies=[
        Depends(AuthProvider),
        Depends(ApiKeyTypeAuthorizationProvider(ApiKeyType.INFERENCE)),
    ],
    responses={
        "401": {"model": ClientErrorResponse},
        "403": {"model": ClientErrorResponse},
    },
)


@router.post("/translation", response_model=ULCATranslationInferenceResponse)
async def _run_inference_translation(
    request: ULCATranslationInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_translation_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/transliteration", response_model=ULCATransliterationInferenceResponse)
async def _run_inference_transliteration(
    request: ULCATransliterationInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_transliteration_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/asr", response_model=ULCAAsrInferenceResponse)
async def _run_inference_asr(
    request: ULCAAsrInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_asr_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/tts", response_model=ULCATtsInferenceResponse)
async def _run_inference_tts(
    request: ULCATtsInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_tts_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/vad", response_model=ULCAVadInferenceResponse)
async def _run_inference_vad(
    request: ULCAVadInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_vad_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/ner", response_model=ULCANerInferenceResponse)
async def _run_inference_ner(
    request: ULCANerInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_ner_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/txt-lang-detection", response_model=ULCATextLangDetectionInferenceResponse)
async def _run_inference_text_lang_detection(
    request: ULCATextLangDetectionInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    if params.serviceId:
        request.set_service_id(params.serviceId)

    return await inference_service.run_text_lang_detection_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


# Temporary endpoint; will be removed/standardized soon


@router.post("/s2s", response_model=ULCAS2SInferenceResponse)
async def _run_inference_sts(
    request: ULCAS2SInferenceRequest,
    request_state: Request,
    inference_service: InferenceService = Depends(InferenceService),
):
    if request.config.language.sourceLanguage == "en":
        serviceId = "ai4bharat/whisper--gpu-t4"
    elif request.config.language.sourceLanguage == "hi":
        serviceId = "ai4bharat/conformer-hi--gpu-t4"
    elif request.config.language.sourceLanguage in {"kn", "ml", "ta", "te"}:
        serviceId = "ai4bharat/conformer-multilingual-dravidian--gpu-t4"
    else:
        serviceId = "ai4bharat/conformer-multilingual-indo-aryan--gpu-t4"

    asr_request = ULCAAsrInferenceRequest(
        audio=request.audio,
        config=request.config,
        controlConfig=request.controlConfig,
    )
    asr_request.set_service_id(serviceId)

    asr_response = await inference_service.run_asr_triton_inference(
        asr_request, request_state.state.api_key_name, request_state.state.user_id
    )

    translation_request = ULCATranslationInferenceRequest(
        config=request.config,
        input=asr_response.output,
        controlConfig=request.controlConfig,
    )

    translation_request.set_service_id("ai4bharat/indictrans--gpu-t4")

    translation_response = await inference_service.run_translation_triton_inference(
        translation_request,
        request_state.state.api_key_name,
        request_state.state.user_id,
    )

    for i in range(len(translation_response.output)):
        translation_response.output[i].source, translation_response.output[i].target = (
            translation_response.output[i].target,
            translation_response.output[i].source,
        )

    request.config.language.sourceLanguage = request.config.language.targetLanguage
    if request.config.language.sourceLanguage in {"kn", "ml", "ta", "te"}:
        serviceId = "ai4bharat/indic-tts-dravidian--gpu-t4"
    elif request.config.language.sourceLanguage in {"en", "brx", "mni"}:
        serviceId = "ai4bharat/indic-tts-misc--gpu-t4"
    else:
        serviceId = "ai4bharat/indic-tts-indo-aryan--gpu-t4"

    tts_request = ULCATtsInferenceRequest(
        config=request.config,
        input=translation_response.output,
        controlConfig=request.controlConfig,
    )

    tts_request.set_service_id(serviceId)

    tts_response = await inference_service.run_tts_triton_inference(
        tts_request, request_state.state.api_key_name, request_state.state.user_id
    )

    for i in range(len(translation_response.output)):
        translation_response.output[i].source, translation_response.output[i].target = (
            translation_response.output[i].target,
            translation_response.output[i].source,
        )

    response = ULCAS2SInferenceResponse(
        output=translation_response.output,
        audio=tts_response.audio,
        config=tts_response.config,
    )

    return response


@router.post("/pipeline", response_model=ULCAPipelineInferenceResponse)
async def _run_inference_pipeline(
    request: ULCAPipelineInferenceRequest,
    request_state: Request,
    inference_service: InferenceService = Depends(InferenceService),
):
    return await inference_service.run_pipeline_inference(request, request_state)


@router.post("/llm", response_model=ULCALLMInferenceResponse)
async def _run_inference_llm(
    request: ULCALLMInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    return await inference_service.run_llm_inference(
        request,
        params.serviceId,
        request_state.state.api_key_name,
        request_state.state.user_id,
    )


@router.post("/pipeline/transliteration", response_model=ULCAPipelineInferenceResponse)
async def _run_pipeline_transliteration(
    request: ULCAPipelineInferenceRequest,
    request_state: Request,
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    Pipeline transliteration endpoint.
    Calls Triton inference service (currently with mock response until real endpoint is available).
    """
    return await inference_service.run_pipeline_transliteration_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/ocr", response_model=ULCAOCRInferenceResponse)
async def _run_inference_ocr(
    request: ULCAOCRInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    OCR endpoint with specific OCR request/response schema.
    Extracts text from images using Surya OCR model via Triton.
    """
    if params.serviceId:
        request.config.serviceId = params.serviceId

    return await inference_service.run_ocr_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


# @router.post("/pipeline/ocr", response_model=ULCAPipelineInferenceResponse)
# async def _run_pipeline_ocr(
#     request: ULCAPipelineInferenceRequest,
#     request_state: Request,
#     inference_service: InferenceService = Depends(InferenceService),
# ):
    """
    Pipeline OCR endpoint.
    Calls Triton inference service (currently with mock response until real endpoint is available).
    """
    return await inference_service.run_pipeline_ocr_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/pipeline/txt-lang-detection", response_model=ULCAPipelineInferenceResponse)
async def _run_pipeline_text_lang_detection(
    request: ULCAPipelineInferenceRequest,
    request_state: Request,
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    Pipeline text language detection endpoint.
    Calls Triton inference service (currently with mock response until real endpoint is available).
    """
    return await inference_service.run_pipeline_text_lang_detection_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


# @router.post("/pipeline/audio-lang-detection", response_model=ULCAPipelineInferenceResponse)
# async def _run_pipeline_audio_lang_detection(
#     request: ULCAPipelineInferenceRequest,
#     request_state: Request,
#     inference_service: InferenceService = Depends(InferenceService),
# ):
#     """
#     Pipeline audio language detection endpoint.
#     Calls Triton inference service (currently with mock response until real endpoint is available).
#     """
#     return await inference_service.run_pipeline_audio_lang_detection_inference(
#         request, request_state.state.api_key_name, request_state.state.user_id
#     )


@router.post("/speaker-diarization", response_model=ULCASpeakerDiarizationInferenceResponse)
async def _run_inference_speaker_diarization(
    request: ULCASpeakerDiarizationInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    Speaker diarization endpoint with dedicated SD request/response format.
    Identifies different speakers in audio and returns their segments.
    """
    if params.serviceId:
        request.config.serviceId = params.serviceId

    return await inference_service.run_speaker_diarization_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/language-diarization", response_model=ULCALanguageDiarizationInferenceResponse)
async def _run_inference_language_diarization(
    request: ULCALanguageDiarizationInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    Language diarization endpoint with dedicated LD request/response format.
    Identifies different languages in audio and returns their segments.
    """
    if params.serviceId:
        request.config.serviceId = params.serviceId

    return await inference_service.run_language_diarization_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


@router.post("/audio-lang-detection", response_model=ULCAAudioLangDetectionInferenceResponse)
async def _run_inference_audio_lang_detection(
    request: ULCAAudioLangDetectionInferenceRequest,
    request_state: Request,
    params: ULCAInferenceQuery = Depends(),
    inference_service: InferenceService = Depends(InferenceService),
):
    """
    Audio language detection endpoint with dedicated ALD request/response format.
    Detects the language of audio content and returns language code, confidence, and all scores.
    """
    if params.serviceId:
        request.config.serviceId = params.serviceId

    return await inference_service.run_audio_lang_detection_triton_inference(
        request, request_state.state.api_key_name, request_state.state.user_id
    )


# @router.post("/pipeline/language-diarization", response_model=ULCAPipelineInferenceResponse)
# async def _run_pipeline_language_diarization(
#     request: ULCAPipelineInferenceRequest,
#     request_state: Request,
#     inference_service: InferenceService = Depends(InferenceService),
# ):
#     """
#     Pipeline language diarization endpoint.
#     Calls Triton inference service (currently with mock response until real endpoint is available).
#     """
#     return await inference_service.run_pipeline_language_diarization_inference(
#         request, request_state.state.api_key_name, request_state.state.user_id
#     )


# @router.post("/pipeline/speaker-verification", response_model=ULCAPipelineInferenceResponse)
# async def _run_pipeline_speaker_verification(
#     request: ULCAPipelineInferenceRequest,
#     request_state: Request,
#     inference_service: InferenceService = Depends(InferenceService),
# ):
#     """
#     Pipeline speaker enrollment & verification endpoint.
#     Calls Triton inference service (currently with mock response until real endpoint is available).
#     Supports both enrollment and verification operations.
#     """
#     return await inference_service.run_pipeline_speaker_verification_inference(
#         request, request_state.state.api_key_name, request_state.state.user_id
#     )
