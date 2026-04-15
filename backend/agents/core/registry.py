from agents.core.base import BaseAgent
from agents.seo.content_strategy_agent import ContentStrategyAgent
from agents.seo.keyword_intelligence_agent import KeywordIntelligenceAgent
from agents.seo.on_page_optimization_agent import OnPageOptimizationAgent
from agents.seo.quality_assurance_agent import QualityAssuranceAgent
from agents.seo.seo_content_production_agent import SEOContentProductionAgent


def build_agent_registry() -> dict[str, BaseAgent]:
    return {
        'keyword_intelligence_agent': KeywordIntelligenceAgent(),
        'content_strategy_agent': ContentStrategyAgent(),
        'seo_content_production_agent': SEOContentProductionAgent(),
        'on_page_optimization_agent': OnPageOptimizationAgent(),
        'quality_assurance_agent': QualityAssuranceAgent(),
    }
