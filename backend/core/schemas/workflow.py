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
    workflow_id: str
    status: str


class WorkflowStepResponse(StrictSchemaModel):
    id: str
    step_name: str
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    error_message: str | None
    retry_count: int
    started_at: datetime | None
    completed_at: datetime | None


class WorkflowInstanceResponse(StrictSchemaModel):
    id: str
    workflow_name: str
    status: str
    current_step_id: str | None
    context_json: dict[str, Any]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    steps: list[WorkflowStepResponse] = Field(default_factory=list)


class WorkflowTraceEventResponse(StrictSchemaModel):
    event_id: str
    workflow_instance_id: str
    step_id: str | None
    event_type: str
    payload: dict[str, Any]
    timestamp: datetime


class WorkflowTraceResponse(StrictSchemaModel):
    workflow: WorkflowInstanceResponse
    events: list[WorkflowTraceEventResponse]
