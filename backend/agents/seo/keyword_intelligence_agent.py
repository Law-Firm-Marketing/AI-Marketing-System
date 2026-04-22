from agents.core.base import BaseAgent
from agents.core.schemas import KeywordIntelligenceInput, KeywordIntelligenceOutput, KeywordItem
from pydantic import BaseModel


class KeywordIntelligenceAgent(BaseAgent):
    name = 'keyword_intelligence_agent'
    input_schema = KeywordIntelligenceInput
    output_schema = KeywordIntelligenceOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = KeywordIntelligenceInput.model_validate(payload)
        keywords = [
            KeywordItem(keyword=payload.topic, intent='informational'),
            KeywordItem(keyword=f'best {payload.topic} tools', intent='commercial'),
            KeywordItem(keyword=f'{payload.topic} checklist', intent='transactional'),
        ]
        return KeywordIntelligenceOutput(topic=payload.topic, keywords=keywords)
