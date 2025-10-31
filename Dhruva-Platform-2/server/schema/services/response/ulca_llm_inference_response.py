from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class LLMResponseOutput(BaseModel):
    name: str
    datatype: str
    shape: List[int]
    data: List[Union[str, int, float]]


class ULCALLMInferenceResponse(BaseModel):
    model_name: str
    model_version: str
    outputs: List[LLMResponseOutput]
