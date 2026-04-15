import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel

from core.schemas.workflow import AgentInput, AgentOutput


class BaseAgent(ABC):
    name: str = 'base_agent'
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def process(self, payload: BaseModel) -> BaseModel:
        raise NotImplementedError

    def run(self, payload: AgentInput) -> AgentOutput:
        validated_input = self.input_schema.model_validate(payload.data)
        self.logger.info('agent.input.validated', extra={'agent': self.name})

        raw_output = self.process(validated_input)
        validated_output = self.output_schema.model_validate(raw_output)
        self.logger.info('agent.output.validated', extra={'agent': self.name})

        return AgentOutput(result=validated_output.model_dump(), next_step=None)
