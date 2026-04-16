import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from agents.core.registry import build_agent_registry
from core.schemas.workflow import AgentInput
from core.state.config import settings
from core.state.database import SessionLocal
from core.state.models import EventLog, WorkflowInstance, WorkflowStepExecution
from mcp.base.registry import MCPToolRegistry
from mcp.base.service import MCPService
from mcp.wordpress.server import PublishPostTool, UpdatePostTool
from workflows.definitions import WORKFLOWS


class WorkflowOrchestrator:
    def __init__(self, db_session):
        self.db = db_session
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_retries = settings.workflow_max_retries

        self.agents = build_agent_registry()
        self.mcp_registry = MCPToolRegistry()
        self.mcp_registry.register('wordpress.publish_post', PublishPostTool())
        self.mcp_registry.register('wordpress.update_post', UpdatePostTool())
        self.mcp_service = MCPService(self.mcp_registry)

    def _emit_event(self, workflow_id: str, event_type: str, payload: dict, step_id: str | None = None) -> None:
        self.db.add(
            EventLog(
                workflow_instance_id=workflow_id,
                step_id=step_id,
                event_type=event_type,
                payload=payload,
            )
        )
        self.db.commit()

    def _build_dependency_map(self, workflow_name: str) -> dict[str, list[str]]:
        workflow = WORKFLOWS[workflow_name]
        return {step['name']: step.get('depends_on', []) for step in workflow['steps']}

    def _ensure_steps_initialized(self, workflow_id: str, workflow_name: str) -> None:
        existing = self.db.query(WorkflowStepExecution).filter_by(workflow_instance_id=workflow_id).count()
        if existing:
            return

        for step in WORKFLOWS[workflow_name]['steps']:
            self.db.add(
                WorkflowStepExecution(
                    workflow_instance_id=workflow_id,
                    step_name=step['name'],
                    status='pending',
                )
            )
        self.db.commit()

    def resolve_next_steps(self, workflow_instance_id: str) -> list[str]:
        instance = self.db.query(WorkflowInstance).filter_by(id=workflow_instance_id).first()
        if not instance:
            raise ValueError('Workflow instance not found')

        dependency_map = self._build_dependency_map(instance.workflow_name)
        steps = self.db.query(WorkflowStepExecution).filter_by(workflow_instance_id=workflow_instance_id).all()
        status_by_name = {step.step_name: step.status for step in steps}

        ready_steps = []
        for step_name, dependencies in dependency_map.items():
            current_status = status_by_name.get(step_name)
            deps_satisfied = all(status_by_name.get(dep) == 'success' for dep in dependencies)
            retryable_failed = current_status == 'failed' and self._step_retryable(steps, step_name)
            if deps_satisfied and current_status == 'pending':
                ready_steps.append(step_name)
            elif deps_satisfied and retryable_failed:
                ready_steps.append(step_name)

        return ready_steps

    def _step_retryable(self, steps: list[WorkflowStepExecution], step_name: str) -> bool:
        step = next((s for s in steps if s.step_name == step_name), None)
        return bool(step and step.retry_count < self.max_retries)

    def _execute_agent_step(self, step_name: str, context: dict) -> dict:
        self.logger.info('agent.execute.start', extra={'step_name': step_name})
        return self.agents[step_name].run(AgentInput(task=step_name, data=context)).model_dump()

    def _execute_mcp_step(self, step_name: str, context: dict) -> dict:
        mcp_tool = 'wordpress.publish_post' if step_name == 'wordpress_publish_mcp' else step_name
        payload = {
            'title': context.get('title'),
            'content': context.get('article', context.get('content')),
            'meta': {
                'meta_title': context.get('meta_title'),
                'meta_description': context.get('meta_description'),
            },
        }
        return self.mcp_service.call(mcp_tool, payload)

    def execute_step(self, workflow_instance_id: str, step_name: str) -> None:
        db = SessionLocal()
        try:
            instance = db.query(WorkflowInstance).filter_by(id=workflow_instance_id).first()
            step = db.query(WorkflowStepExecution).filter_by(workflow_instance_id=workflow_instance_id, step_name=step_name).first()
            if not instance or not step:
                raise ValueError('Invalid workflow instance or step')

            context = dict(instance.context_json or {})
            step.status = 'running'
            step.input_payload = context
            step.started_at = datetime.utcnow()
            db.add(step)
            db.commit()

            self._emit_event(workflow_instance_id, 'STEP_STARTED', {'step_name': step_name}, step.id)

            try:
                if step_name in self.agents:
                    self._emit_event(workflow_instance_id, 'AGENT_EXECUTION_STARTED', {'step_name': step_name}, step.id)
                    output = self._execute_agent_step(step_name, context)
                    self._emit_event(workflow_instance_id, 'AGENT_EXECUTION_COMPLETED', {'step_name': step_name}, step.id)
                    context.update(output.get('result', {}))
                else:
                    self._emit_event(workflow_instance_id, 'MCP_CALL_STARTED', {'step_name': step_name}, step.id)
                    output = self._execute_mcp_step(step_name, context)
                    self._emit_event(workflow_instance_id, 'MCP_CALL_COMPLETED', {'step_name': step_name}, step.id)
                    context[step_name] = output

                step.status = 'success'
                step.output_payload = output
                step.error_message = None
                step.completed_at = datetime.utcnow()
                db.add(step)

                instance.current_step_id = step.id
                instance.context_json = context
                instance.updated_at = datetime.utcnow()
                db.add(instance)
                db.commit()

                self._emit_event(workflow_instance_id, 'STEP_COMPLETED', {'step_name': step_name}, step.id)
            except Exception as exc:
                step.status = 'failed'
                step.retry_count += 1
                step.error_message = str(exc)
                step.completed_at = datetime.utcnow()
                db.add(step)

                instance.retry_count += 1
                instance.updated_at = datetime.utcnow()
                db.add(instance)
                db.commit()

                if step_name in self.agents:
                    self._emit_event(workflow_instance_id, 'AGENT_EXECUTION_FAILED', {'step_name': step_name, 'error': str(exc)}, step.id)
                else:
                    self._emit_event(workflow_instance_id, 'MCP_CALL_FAILED', {'step_name': step_name, 'error': str(exc)}, step.id)
                self._emit_event(workflow_instance_id, 'STEP_FAILED', {'step_name': step_name, 'error': str(exc)}, step.id)
                raise
        finally:
            db.close()

    def run_workflow(self, workflow_name: str, input_data: dict) -> WorkflowInstance:
        if workflow_name not in WORKFLOWS:
            raise ValueError(f'Unknown workflow: {workflow_name}')

        instance = WorkflowInstance(
            workflow_name=workflow_name,
            status='running',
            context_json=dict(input_data),
        )
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)

        self._ensure_steps_initialized(instance.id, workflow_name)
        self._emit_event(instance.id, 'WORKFLOW_STARTED', {'workflow_name': workflow_name})

        while True:
            ready_steps = self.resolve_next_steps(instance.id)
            if ready_steps:
                with ThreadPoolExecutor(max_workers=max(1, len(ready_steps))) as executor:
                    futures = [executor.submit(self.execute_step, instance.id, step_name) for step_name in ready_steps]
                    for future in futures:
                        future.result()
                continue

            all_steps = self.db.query(WorkflowStepExecution).filter_by(workflow_instance_id=instance.id).all()
            statuses = {step.status for step in all_steps}

            if statuses.issubset({'success', 'skipped'}):
                instance.status = 'completed'
                self.db.add(instance)
                self.db.commit()
                self._emit_event(instance.id, 'WORKFLOW_COMPLETED', {'workflow_name': workflow_name})
                break

            if 'failed' in statuses and not any(self._step_retryable(all_steps, s.step_name) for s in all_steps if s.status == 'failed'):
                instance.status = 'failed'
                self.db.add(instance)
                self.db.commit()
                self._emit_event(instance.id, 'WORKFLOW_FAILED', {'workflow_name': workflow_name})
                break

            # No ready steps yet some failed are retryable; loop will pick them next.

        self.db.refresh(instance)
        return instance

    def recover_failed_workflow(self, workflow_instance_id: str) -> WorkflowInstance:
        instance = self.db.query(WorkflowInstance).filter_by(id=workflow_instance_id).first()
        if not instance:
            raise ValueError('Workflow instance not found')
        if instance.status != 'failed':
            return instance

        instance.status = 'running'
        self.db.add(instance)
        self.db.commit()
        self._emit_event(workflow_instance_id, 'WORKFLOW_STARTED', {'recovered': True})

        return self.run_existing_workflow(workflow_instance_id)

    def run_existing_workflow(self, workflow_instance_id: str) -> WorkflowInstance:
        instance = self.db.query(WorkflowInstance).filter_by(id=workflow_instance_id).first()
        if not instance:
            raise ValueError('Workflow instance not found')

        while True:
            ready_steps = self.resolve_next_steps(instance.id)
            if not ready_steps:
                break
            for step_name in ready_steps:
                self.execute_step(instance.id, step_name)

        self.db.refresh(instance)
        return instance

    def get_workflow_trace(self, workflow_instance_id: str) -> dict:
        workflow = self.db.query(WorkflowInstance).filter_by(id=workflow_instance_id).first()
        if not workflow:
            raise ValueError('Workflow instance not found')

        steps = (
            self.db.query(WorkflowStepExecution)
            .filter_by(workflow_instance_id=workflow_instance_id)
            .order_by(WorkflowStepExecution.started_at.asc().nullsfirst())
            .all()
        )
        events = (
            self.db.query(EventLog)
            .filter_by(workflow_instance_id=workflow_instance_id)
            .order_by(EventLog.timestamp.asc())
            .all()
        )

        return {
            'workflow': workflow,
            'steps': steps,
            'events': events,
        }
