from typing import List, Optional

from pydantic import BaseModel

from ..common import _ULCATaskType, _ULCALanguage


class _ULCASpeakerDiarizationSegment(BaseModel):
    start_time: float
    end_time: float
    duration: float
    speaker: str


class _ULCASpeakerDiarizationOutput(BaseModel):
    total_segments: int
    num_speakers: int
    speakers: List[str]
    segments: List[_ULCASpeakerDiarizationSegment]


class _ULCASpeakerDiarizationInferenceResponseConfig(BaseModel):
    serviceId: Optional[str] = None
    language: Optional[_ULCALanguage] = None


class ULCASpeakerDiarizationInferenceResponse(BaseModel):
    taskType: _ULCATaskType = _ULCATaskType.SPEAKER_DIARIZATION
    output: List[_ULCASpeakerDiarizationOutput]
    config: Optional[_ULCASpeakerDiarizationInferenceResponseConfig] = None

