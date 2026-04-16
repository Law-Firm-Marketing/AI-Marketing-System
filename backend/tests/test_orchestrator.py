import pytest
from pydantic import ValidationError

from agents.seo.keyword_intelligence_agent import KeywordIntelligenceAgent
from core.orchestrator.orchestrator import WorkflowOrchestrator
from core.schemas.workflow import AgentInput
from core.state.database import Base, SessionLocal, engine
from core.state.models import EventLog, WorkflowInstance, WorkflowStepExecution


def test_workflow_persistence_and_completion():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = orchestrator.run_workflow('keyword_pipeline', {'topic': 'ai marketing orchestration'})

        persisted = db.query(WorkflowInstance).filter_by(id=workflow.id).first()
        steps = db.query(WorkflowStepExecution).filter_by(workflow_instance_id=workflow.id).all()

        assert persisted is not None
        assert persisted.status == 'completed'
        assert len(steps) == 4
        assert all(step.status == 'success' for step in steps)
    finally:
        db.close()


def test_dag_dependency_resolution_returns_first_root_step():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = WorkflowInstance(workflow_name='keyword_pipeline', status='running', context_json={'topic': 'ai'})
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        orchestrator._ensure_steps_initialized(workflow.id, workflow.workflow_name)

        ready = orchestrator.resolve_next_steps(workflow.id)
        assert ready == ['keyword_agent']
    finally:
        db.close()


def test_schema_validation_enforcement():
    agent = KeywordIntelligenceAgent()
    with pytest.raises(ValidationError):
        agent.run(AgentInput(task='keyword_agent', data={'topic': 'ai', 'unexpected': 'x'}))


def test_mcp_call_event_logging():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = orchestrator.run_workflow('keyword_pipeline', {'topic': 'ai marketing orchestration'})
        events = db.query(EventLog).filter_by(workflow_instance_id=workflow.id).all()
        event_types = {event.event_type for event in events}

        assert 'MCP_CALL_STARTED' in event_types
        assert 'MCP_CALL_COMPLETED' in event_types
    finally:
        db.close()


def test_workflow_resume_after_failure():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = WorkflowInstance(workflow_name='keyword_pipeline', status='failed', context_json={'topic': 'ai'})
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        orchestrator._ensure_steps_initialized(workflow.id, workflow.workflow_name)

        recovered = orchestrator.recover_failed_workflow(workflow.id)
        assert recovered.status in {'running', 'completed'}
    finally:
        db.close()
