import logging
from datetime import datetime

from agents.core.registry import build_agent_registry
from core.schemas.workflow import AgentInput
from core.state.config import settings
from core.state.models import AgentLog, ResultRecord, TaskRun, WorkflowRun
from mcp.base.registry import MCPToolRegistry
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

    def _log(self, workflow_id: int, task_id: int | None, component: str, event_type: str, payload: dict) -> None:
        self.db.add(
            AgentLog(
                workflow_id=workflow_id,
                task_id=task_id,
                component=component,
                event_type=event_type,
                payload=payload,
            )
        )
        self.db.commit()

    def _execute_agent(self, step: str, context: dict) -> dict:
        self.logger.info('orchestrator.agent.execute', extra={'step': step})
        output = self.agents[step].run(AgentInput(task=step, data=context)).model_dump()
        context.update(output.get('result', {}))
        return output

    def _execute_mcp(self, step: str, context: dict) -> dict:
        self.logger.info('orchestrator.mcp.execute', extra={'step': step})
        if step == 'wordpress.publish_post':
            publish_input = {
                'title': context.get('title'),
                'content': context.get('content'),
                'meta': {
                    'meta_title': context.get('meta_title'),
                    'meta_description': context.get('meta_description'),
                },
            }
            output = self.mcp_registry.execute(step, publish_input)
            context['published_post'] = output
            return output
        return self.mcp_registry.execute(step, context)

    def _execute_step(self, step: str, context: dict) -> dict:
        if step in self.agents:
            return self._execute_agent(step, context)
        return self._execute_mcp(step, context)

    def run_workflow(self, workflow_name: str, input_data: dict) -> WorkflowRun:
        if workflow_name not in WORKFLOWS:
            raise ValueError(f'Unknown workflow: {workflow_name}')

        workflow = WorkflowRun(name=workflow_name, status='running', input_data=input_data)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        self.logger.info('workflow.started', extra={'workflow_id': workflow.id, 'workflow_name': workflow_name})
        context = dict(input_data)

        try:
            for step in WORKFLOWS[workflow_name]:
                task = TaskRun(
                    workflow_id=workflow.id,
                    step_name=step,
                    status='running',
                    input_data=context,
                    started_at=datetime.utcnow(),
                )
                self.db.add(task)
                self.db.commit()
                self.db.refresh(task)

                self._log(workflow.id, task.id, step, 'input', context)

                output = None
                retries = 0
                while retries <= self.max_retries:
                    try:
                        output = self._execute_step(step, context)
                        break
                    except Exception as exc:
                        retries += 1
                        self.logger.warning(
                            'step.execution.retry',
                            extra={'workflow_id': workflow.id, 'task_id': task.id, 'step': step, 'attempt': retries},
                        )
                        self._log(
                            workflow.id,
                            task.id,
                            step,
                            'retry',
                            {'attempt': retries, 'error': str(exc)},
                        )
                        if retries > self.max_retries:
                            raise

                task.status = 'completed'
                task.output_data = output or {}
                task.completed_at = datetime.utcnow()
                self.db.add(task)
                self.db.commit()

                self._log(workflow.id, task.id, step, 'output', output or {})

            workflow.status = 'completed'
            workflow.output_data = context
            self.db.add(workflow)
            self.db.add(ResultRecord(workflow_id=workflow.id, key='final_output', value=context))
            self.db.commit()
            self.db.refresh(workflow)
            self.logger.info('workflow.completed', extra={'workflow_id': workflow.id})
            return workflow

        except Exception as exc:
            self.logger.exception('workflow.failed')
            workflow.status = 'failed'
            workflow.output_data = {'error': str(exc)}
            self.db.add(workflow)
            self.db.commit()
            self._log(workflow.id, None, 'orchestrator', 'error', {'error': str(exc)})
            raise
