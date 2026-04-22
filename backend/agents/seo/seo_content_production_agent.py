from agents.core.base import BaseAgent
from agents.core.schemas import SEOContentProductionInput, SEOContentProductionOutput
from pydantic import BaseModel


class SEOContentProductionAgent(BaseAgent):
    name = 'seo_content_production_agent'
    input_schema = SEOContentProductionInput
    output_schema = SEOContentProductionOutput

    def process(self, payload: BaseModel) -> BaseModel:
        payload = SEOContentProductionInput.model_validate(payload)
        outline = payload.outline
        title = outline.get('title', 'Untitled')

        article_lines = [f'# {title}']
        for section in outline.get('sections', []):
            article_lines.append(f"\n## {section.get('heading', 'Section')}\n")
            article_lines.append('Actionable guidance aligned with search intent and conversion goals.')

        return SEOContentProductionOutput(article='\n'.join(article_lines), title=title)
