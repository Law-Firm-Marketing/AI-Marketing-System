import logging

from mcp.base.tool import MCPTool


class MCPToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(self, name: str, tool: MCPTool) -> None:
        self._tools[name] = tool
        self.logger.info('mcp.tool.registered', extra={'tool': name})

    def execute(self, name: str, payload: dict) -> dict:
        if name not in self._tools:
            raise ValueError(f'MCP tool not found: {name}')

        self.logger.info('mcp.tool.executing', extra={'tool': name, 'payload_keys': list(payload.keys())})
        try:
            result = self._tools[name].execute(payload)
            self.logger.info('mcp.tool.executed', extra={'tool': name})
            return result
        except Exception as exc:
            self.logger.exception('mcp.execution.failed', extra={'tool': name})
            raise RuntimeError(f'MCP tool execution failed: {name}') from exc
