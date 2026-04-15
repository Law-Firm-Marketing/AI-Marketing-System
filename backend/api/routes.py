from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.orchestrator.orchestrator import WorkflowOrchestrator
from core.schemas.workflow import LogResponse, WorkflowRunRequest, WorkflowRunResponse, WorkflowStatusResponse
from core.state.database import get_db
from core.state.models import AgentLog, WorkflowRun

router = APIRouter(prefix='/workflow', tags=['workflow'])


@router.post('/run', response_model=WorkflowRunResponse)
def run_workflow(request: WorkflowRunRequest, db: Session = Depends(get_db)):
    orchestrator = WorkflowOrchestrator(db)
    workflow = orchestrator.run_workflow(request.workflow_name, request.input_data)
    return WorkflowRunResponse(workflow_id=workflow.id, status=workflow.status)


@router.get('/status/{workflow_id}', response_model=WorkflowStatusResponse)
def get_workflow_status(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return workflow


@router.get('/logs', response_model=list[LogResponse])
def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit).all()
    return logs
