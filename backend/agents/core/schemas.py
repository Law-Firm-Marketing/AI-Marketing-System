from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class KeywordIntelligenceInput(AgentSchema):
    topic: str


class KeywordItem(AgentSchema):
    keyword: str
    intent: Literal['informational', 'commercial', 'transactional', 'navigational']


class KeywordIntelligenceOutput(AgentSchema):
    topic: str
    keywords: list[KeywordItem]


class ContentStrategyInput(AgentSchema):
    topic: str
    keywords: list[KeywordItem]


class OutlineSection(AgentSchema):
    heading: str
    keywords: list[KeywordItem] = Field(default_factory=list)


class ContentStrategyOutput(AgentSchema):
    outline: dict


class SEOContentProductionInput(AgentSchema):
    outline: dict


class SEOContentProductionOutput(AgentSchema):
    article: str
    title: str


class OnPageOptimizationInput(AgentSchema):
    title: str
    article: str


class OnPageOptimizationOutput(AgentSchema):
    meta_title: str
    meta_description: str
    internal_links: list[str]
    content: str
    title: str


class QualityAssuranceInput(AgentSchema):
    title: str
    meta_title: str
    meta_description: str
    content: str
    internal_links: list[str] = Field(default_factory=list)


class QAStatus(AgentSchema):
    has_title: bool
    has_meta_title: bool
    has_meta_description: bool
    has_minimum_content: bool
    approved: bool


class QualityAssuranceOutput(AgentSchema):
    qa: QAStatus
    publishable_payload: dict
