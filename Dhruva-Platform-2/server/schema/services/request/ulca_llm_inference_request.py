from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class LLMInput(BaseModel):
    name: str
    datatype: str
    shape: List[int]
    data: List[Union[str, int, float]]


class LLMOutput(BaseModel):
    name: str


class ULCALLMInferenceRequest(BaseModel):
    inputs: List[LLMInput]
    outputs: List[LLMOutput]
