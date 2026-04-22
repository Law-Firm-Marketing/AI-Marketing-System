from agents.core.base import BaseAgent
from agents.core.schemas import OnPageOptimizationInput, OnPageOptimizationOutput
from pydantic import BaseModel


class OnPageOptimizationAgent(BaseAgent):
    name = 'on_page_optimization_agent'
    input_schema = OnPageOptimizationInput
    output_schema = OnPageOptimizationOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = OnPageOptimizationInput.model_validate(payload)
        return OnPageOptimizationOutput(
            meta_title=f'{payload.title} | Expert Playbook',
            meta_description='Learn practical strategies to increase traffic and conversions with this step-by-step guide.',
            internal_links=['/blog', '/services/content-strategy', '/contact'],
            content=payload.article,
            title=payload.title,
        )
