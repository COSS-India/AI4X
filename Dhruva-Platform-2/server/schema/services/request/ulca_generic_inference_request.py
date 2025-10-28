from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..common import _ULCAAudio, _ULCABaseInferenceRequest, _ULCAText


class ULCAGenericInferenceRequestWithoutConfig(BaseModel):
    input: Optional[List[_ULCAText]]
    audio: Optional[List[_ULCAAudio]]
    image: Optional[List[Dict[str, Any]]]


class ULCAGenericInferenceRequest(
    ULCAGenericInferenceRequestWithoutConfig, _ULCABaseInferenceRequest
):
    pass
