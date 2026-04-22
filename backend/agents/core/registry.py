from agents.core.base import BaseAgent
from agents.seo.content_strategy_agent import ContentStrategyAgent
from agents.seo.keyword_intelligence_agent import KeywordIntelligenceAgent
from agents.seo.on_page_optimization_agent import OnPageOptimizationAgent
from agents.seo.quality_assurance_agent import QualityAssuranceAgent
from agents.seo.seo_content_production_agent import SEOContentProductionAgent
from agents.social.social_promotion_agent import SocialPromotionAgent


def build_agent_registry() -> dict[str, BaseAgent]:
    keyword = KeywordIntelligenceAgent()
    strategy = ContentStrategyAgent()
    content = SEOContentProductionAgent()
    onpage = OnPageOptimizationAgent()
    qa = QualityAssuranceAgent()
    social = SocialPromotionAgent()

    return {
        'keyword_agent': keyword,
        'keyword_intelligence_agent': keyword,
        'content_strategy_agent': strategy,
        'seo_content_agent': content,
        'seo_content_production_agent': content,
        'on_page_optimization_agent': onpage,
        'quality_assurance_agent': qa,
        'social_agent': social,
    }
