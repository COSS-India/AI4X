from typing import List, Optional

from pydantic import BaseModel

from ..common import _ULCATaskType, _ULCAText


class _ULCATextLangDetectionPrediction(BaseModel):
    langCode: str
    confidence: float
    model: Optional[str] = None
    language: Optional[str] = None


class _ULCATextLangDetectionOutput(_ULCAText):
    langPrediction: List[_ULCATextLangDetectionPrediction]


class ULCATextLangDetectionInferenceResponse(BaseModel):
    taskType: _ULCATaskType = _ULCATaskType.TXT_LANG_DETECTION
    output: List[_ULCATextLangDetectionOutput]

