# AI Marketing Orchestration System

## Production-grade execution engine capabilities
- Persistent workflow state machine stored in PostgreSQL (`workflow_instance`, `workflow_step_execution`, `event_log`).
- DAG-based execution with dependency-aware ready-step resolution and parallel step execution when dependencies are satisfied.
- Restartable orchestration with retry handling and failed-workflow recovery.
- Strict layered architecture: Agents -> Orchestrator -> MCP Service/Registry -> Integrations.
- Strict Pydantic validation (`strict=True`, `extra=forbid`) for workflow and agent contracts.
- Full observability via event emission: workflow lifecycle, step lifecycle, agent execution, MCP calls.
- MVP workflow path implemented:
  - `keyword_agent` -> `content_strategy_agent` -> `seo_content_agent` -> `wordpress_publish_mcp`
- FastAPI endpoints:
  - `POST /workflow/run`
  - `GET /workflow/{id}`
  - `GET /workflow/{id}/trace`

## Run locally
```bash
docker compose up --build
```

## Example API call
```bash
curl -X POST http://localhost:8000/workflow/run \
  -H 'Content-Type: application/json' \
  -d '{"workflow_name":"seo_pipeline","input_data":{"topic":"ai marketing"}}'
```
