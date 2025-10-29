from typing import Any, Dict, List

from pydantic import BaseModel, Field

from ..common import _ULCATaskType
from ..common.ulca_control_config import _ControlConfig
from .ulca_generic_inference_request import ULCAGenericInferenceRequestWithoutConfig


class _ULCAPipelineTask(BaseModel):
    taskType: _ULCATaskType = Field(..., alias="task_type")
    config: Dict[str, Any]

    class Config:
        populate_by_name = True  # Allow both taskType and task_type


class ULCAPipelineInferenceRequestWithoutControlConfig(BaseModel):
    pipelineTasks: List[_ULCAPipelineTask] = Field(..., alias="pipeline_tasks")
    inputData: ULCAGenericInferenceRequestWithoutConfig = Field(..., alias="input_data")

    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case


class ULCAPipelineInferenceRequest(ULCAPipelineInferenceRequestWithoutControlConfig):
    controlConfig: _ControlConfig = Field(default_factory=_ControlConfig, alias="control_config")

    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case
