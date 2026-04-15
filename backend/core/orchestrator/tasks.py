from celery import Celery

from core.orchestrator.orchestrator import WorkflowOrchestrator
from core.state.config import settings
from core.state.database import SessionLocal


celery_app = Celery('marketing_orchestrator', broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name='run_workflow_task')
def run_workflow_task(workflow_name: str, input_data: dict):
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = orchestrator.run_workflow(workflow_name, input_data)
        return {'workflow_id': workflow.id, 'status': workflow.status}
    finally:
        db.close()
