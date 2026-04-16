from pydantic import BaseModel

from agents.core.base import BaseAgent
from agents.core.schemas import AgentSchema


class SocialPromotionInput(AgentSchema):
    title: str


class SocialPromotionOutput(AgentSchema):
    social_copy: str


class SocialPromotionAgent(BaseAgent):
    name = 'social_promotion_agent'
    input_schema = SocialPromotionInput
    output_schema = SocialPromotionOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = SocialPromotionInput.model_validate(payload)
        return SocialPromotionOutput(social_copy=f'New post live: {payload.title}')
