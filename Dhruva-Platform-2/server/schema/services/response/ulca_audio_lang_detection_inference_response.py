from typing import List, Optional

from pydantic import BaseModel

from ..common import _ULCATaskType


class _ULCAAudioLangDetectionAllScores(BaseModel):
    predicted_language: str
    confidence: float
    top_scores: List[float]


class _ULCAAudioLangDetectionOutput(BaseModel):
    language_code: str
    confidence: float
    all_scores: _ULCAAudioLangDetectionAllScores


class _ULCAAudioLangDetectionInferenceResponseConfig(BaseModel):
    serviceId: Optional[str] = None


class ULCAAudioLangDetectionInferenceResponse(BaseModel):
    taskType: _ULCATaskType = _ULCATaskType.AUDIO_LANG_DETECTION
    output: List[_ULCAAudioLangDetectionOutput]
    config: Optional[_ULCAAudioLangDetectionInferenceResponseConfig] = None

