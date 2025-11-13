from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class _ULCAImage(BaseModel):
    imageContent: Optional[str] = None
    imageUri: Optional[AnyHttpUrl] = None

