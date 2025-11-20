from typing import List, Optional

from pydantic import BaseModel

from ..common import _ULCATaskType


class _ULCALanguageDiarizationSegment(BaseModel):
    start_time: float
    end_time: float
    duration: float
    language: str
    confidence: float


class _ULCALanguageDiarizationOutput(BaseModel):
    total_segments: int
    segments: List[_ULCALanguageDiarizationSegment]
    target_language: str


class _ULCALanguageDiarizationInferenceResponseConfig(BaseModel):
    serviceId: Optional[str] = None


class ULCALanguageDiarizationInferenceResponse(BaseModel):
    taskType: _ULCATaskType = _ULCATaskType.LANGUAGE_DIARIZATION
    output: List[_ULCALanguageDiarizationOutput]
    config: Optional[_ULCALanguageDiarizationInferenceResponseConfig] = None

