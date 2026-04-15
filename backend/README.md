# AI Marketing Orchestration System

## Highlights
- Strict layered architecture: Agents -> Orchestrator -> MCP Servers -> Integrations.
- Stateless JSON-based agent interface with strict Pydantic schema validation (`extra=forbid`, strict mode).
- Central orchestrator with sequential execution, retry handling, and structured logs persisted in PostgreSQL.
- Workflow + task + log + result persistence in PostgreSQL.
- Redis + Celery for asynchronous workflow execution.
- FastAPI endpoints: `/workflow/run`, `/workflow/status/{id}`, `/workflow/logs`.

## Run locally
```bash
docker compose up --build
```

## Example API call
```bash
curl -X POST http://localhost:8000/workflow/run \
  -H 'Content-Type: application/json' \
  -d '{"workflow_name":"keyword_pipeline","input_data":{"topic":"ai marketing"}}'
```
