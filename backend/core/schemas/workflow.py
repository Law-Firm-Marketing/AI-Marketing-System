from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictSchemaModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class AgentInput(StrictSchemaModel):
    task: str
    data: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(StrictSchemaModel):
    result: dict[str, Any] = Field(default_factory=dict)
    next_step: str | None = None


class WorkflowRunRequest(StrictSchemaModel):
    workflow_name: str
    input_data: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunResponse(StrictSchemaModel):
    workflow_id: int
    status: str


class WorkflowStatusResponse(StrictSchemaModel):
    id: int
    name: str
    status: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LogResponse(StrictSchemaModel):
    id: int
    workflow_id: int
    task_id: int | None
    component: str
    event_type: str
    payload: dict[str, Any]
    created_at: datetime
