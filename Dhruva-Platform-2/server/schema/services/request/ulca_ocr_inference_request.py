from typing import List

from ..common import (
    _ULCABaseInferenceRequest,
    _ULCAImage,
    _ULCAOCRInferenceConfig,
)


class ULCAOCRInferenceRequest(_ULCABaseInferenceRequest):
    image: List[_ULCAImage]
    config: _ULCAOCRInferenceConfig

