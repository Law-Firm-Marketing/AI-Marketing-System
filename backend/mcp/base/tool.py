from abc import ABC, abstractmethod


class MCPTool(ABC):
    name: str = 'base_tool'

    @abstractmethod
    def execute(self, input_data: dict) -> dict:
        raise NotImplementedError
