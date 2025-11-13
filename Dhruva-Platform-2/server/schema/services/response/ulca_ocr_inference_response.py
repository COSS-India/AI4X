from typing import List, Optional

from pydantic import BaseModel

from ..common import _ULCATaskType, _ULCATextPair, _ULCAOCRInferenceConfig


class ULCAOCRInferenceResponse(BaseModel):
    taskType: _ULCATaskType = _ULCATaskType.OCR
    output: List[_ULCATextPair]
    config: Optional[_ULCAOCRInferenceConfig] = None

