from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..common.ulca_base_inference_request_config import _ULCABaseInferenceRequestConfig


class _ULCALLMInferenceResponseConfig(_ULCABaseInferenceRequestConfig):
    pass


class ULCALLMInferenceResponse(BaseModel):
    config: _ULCALLMInferenceResponseConfig
    output: List[Dict[str, Any]]
    pipelineResponse: Optional[List[Dict[str, Any]]] = None
