from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.orchestrator.orchestrator import WorkflowOrchestrator
from core.schemas.workflow import (
    WorkflowInstanceResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowTraceEventResponse,
    WorkflowTraceResponse,
)
from core.state.database import get_db
from core.state.models import WorkflowInstance, WorkflowStepExecution

router = APIRouter(prefix='/workflow', tags=['workflow'])


@router.post('/run', response_model=WorkflowRunResponse)
def run_workflow(request: WorkflowRunRequest, db: Session = Depends(get_db)):
    orchestrator = WorkflowOrchestrator(db)
    workflow = orchestrator.run_workflow(request.workflow_name, request.input_data)
    return WorkflowRunResponse(workflow_id=workflow.id, status=workflow.status)


@router.get('/{workflow_id}', response_model=WorkflowInstanceResponse)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowInstance).filter(WorkflowInstance.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail='Workflow not found')
    steps = db.query(WorkflowStepExecution).filter(WorkflowStepExecution.workflow_instance_id == workflow_id).all()

    return WorkflowInstanceResponse(
        id=workflow.id,
        workflow_name=workflow.workflow_name,
        status=workflow.status,
        current_step_id=workflow.current_step_id,
        context_json=workflow.context_json,
        retry_count=workflow.retry_count,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        steps=steps,
    )


@router.get('/{workflow_id}/trace', response_model=WorkflowTraceResponse)
def get_trace(workflow_id: str, db: Session = Depends(get_db)):
    orchestrator = WorkflowOrchestrator(db)
    try:
        trace = orchestrator.get_workflow_trace(workflow_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return WorkflowTraceResponse(
        workflow=WorkflowInstanceResponse(
            id=trace['workflow'].id,
            workflow_name=trace['workflow'].workflow_name,
            status=trace['workflow'].status,
            current_step_id=trace['workflow'].current_step_id,
            context_json=trace['workflow'].context_json,
            retry_count=trace['workflow'].retry_count,
            created_at=trace['workflow'].created_at,
            updated_at=trace['workflow'].updated_at,
            steps=trace['steps'],
        ),
        events=[
            WorkflowTraceEventResponse(
                event_id=e.event_id,
                workflow_instance_id=e.workflow_instance_id,
                step_id=e.step_id,
                event_type=e.event_type,
                payload=e.payload,
                timestamp=e.timestamp,
            )
            for e in trace['events']
        ],
    )
