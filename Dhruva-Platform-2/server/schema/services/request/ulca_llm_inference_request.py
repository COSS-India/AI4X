from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..common.ulca_base_inference_request import _ULCABaseInferenceRequest
from ..common.ulca_base_inference_request_config import _ULCABaseInferenceRequestConfig


class _ULCALLMInferenceRequestConfig(_ULCABaseInferenceRequestConfig):
    serviceId: str
    model_parameters: Optional[Dict[str, Any]] = {}


class ULCALLMInferenceRequest(_ULCABaseInferenceRequest):
    config: _ULCALLMInferenceRequestConfig
    input_data: Dict[str, Any]
