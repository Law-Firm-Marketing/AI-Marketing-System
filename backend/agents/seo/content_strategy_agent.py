from agents.core.base import BaseAgent
from agents.core.schemas import ContentStrategyInput, ContentStrategyOutput, OutlineSection
from pydantic import BaseModel


class ContentStrategyAgent(BaseAgent):
    name = 'content_strategy_agent'
    input_schema = ContentStrategyInput
    output_schema = ContentStrategyOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = ContentStrategyInput.model_validate(payload)
        outline = {
            'title': f'Complete Guide: {payload.topic}',
            'sections': [
                OutlineSection(heading='Introduction', keywords=payload.keywords[:1]).model_dump(),
                OutlineSection(heading='Core Tactics', keywords=payload.keywords[1:2]).model_dump(),
                OutlineSection(heading='Implementation Checklist', keywords=payload.keywords[2:]).model_dump(),
                OutlineSection(heading='Conclusion', keywords=payload.keywords[:1]).model_dump(),
            ],
        }
        return ContentStrategyOutput(outline=outline)
