import pytest
from pydantic import ValidationError

from agents.seo.keyword_intelligence_agent import KeywordIntelligenceAgent
from core.orchestrator.orchestrator import WorkflowOrchestrator
from core.schemas.workflow import AgentInput
from core.state.database import Base, SessionLocal, engine


def test_keyword_pipeline_runs():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = WorkflowOrchestrator(db)
        workflow = orchestrator.run_workflow('keyword_pipeline', {'topic': 'ai marketing orchestration'})
        assert workflow.status == 'completed'
        assert 'published_post' in workflow.output_data
    finally:
        db.close()


def test_agent_schema_validation_rejects_unknown_keys():
    agent = KeywordIntelligenceAgent()
    with pytest.raises(ValidationError):
        agent.run(AgentInput(task='keyword_intelligence_agent', data={'topic': 'ai', 'unexpected': 'x'}))
