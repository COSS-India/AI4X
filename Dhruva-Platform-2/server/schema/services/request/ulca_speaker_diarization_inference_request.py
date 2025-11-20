from typing import List

from ..common import (
    _ULCABaseInferenceRequest,
    _ULCAAudio,
    _ULCABaseInferenceRequestConfig,
)


class _ULCASpeakerDiarizationInferenceRequestConfig(_ULCABaseInferenceRequestConfig):
    serviceId: str


class ULCASpeakerDiarizationInferenceRequest(_ULCABaseInferenceRequest):
    audio: List[_ULCAAudio]
    config: _ULCASpeakerDiarizationInferenceRequestConfig

