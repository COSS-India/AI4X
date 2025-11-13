from typing import Optional

from pydantic import BaseModel

from .ulca_language import _ULCALanguage


class _ULCAOCRInferenceConfig(BaseModel):
    serviceId: str
    language: _ULCALanguage
    textDetection: Optional[bool] = False

