from typing import List

from ..common import (
    _ULCABaseInferenceRequest,
    _ULCABaseInferenceRequestConfig,
    _ULCAText,
)


class _ULCATextLangDetectionInferenceRequestConfig(_ULCABaseInferenceRequestConfig):
    pass


class ULCATextLangDetectionInferenceRequest(_ULCABaseInferenceRequest):
    input: List[_ULCAText]
    config: _ULCATextLangDetectionInferenceRequestConfig

