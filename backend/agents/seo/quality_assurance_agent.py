from agents.core.base import BaseAgent
from agents.core.schemas import QAStatus, QualityAssuranceInput, QualityAssuranceOutput
from pydantic import BaseModel


class QualityAssuranceAgent(BaseAgent):
    name = 'quality_assurance_agent'
    input_schema = QualityAssuranceInput
    output_schema = QualityAssuranceOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = QualityAssuranceInput.model_validate(payload)
        qa = QAStatus(
            has_title=bool(payload.title),
            has_meta_title=bool(payload.meta_title),
            has_meta_description=bool(payload.meta_description),
            has_minimum_content=len(payload.content) > 100,
            approved=False,
        )
        qa.approved = all([
            qa.has_title,
            qa.has_meta_title,
            qa.has_meta_description,
            qa.has_minimum_content,
        ])
        return QualityAssuranceOutput(qa=qa, publishable_payload=payload.model_dump())
