from typing import List

from ..common import (
    _ULCABaseInferenceRequest,
    _ULCAAudio,
    _ULCABaseInferenceRequestConfig,
)


class _ULCALanguageDiarizationInferenceRequestConfig(_ULCABaseInferenceRequestConfig):
    serviceId: str


class ULCALanguageDiarizationInferenceRequest(_ULCABaseInferenceRequest):
    audio: List[_ULCAAudio]
    config: _ULCALanguageDiarizationInferenceRequestConfig

