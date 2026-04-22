from mcp.base.registry import MCPToolRegistry


class MCPService:
    """Abstraction layer to allow future migration to remote MCP transport."""

    def __init__(self, registry: MCPToolRegistry):
        self.registry = registry

    def call(self, tool_name: str, payload: dict) -> dict:
        return self.registry.execute(tool_name, payload)
