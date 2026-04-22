from mcp.base.tool import MCPTool


class KeywordResearchTool(MCPTool):
    name = 'seo.keyword_research'

    def execute(self, input_data: dict) -> dict:
        topic = input_data.get('topic', 'marketing')
        return {'keywords': [topic, f'{topic} strategy', f'{topic} template']}


class TopicGenerationTool(MCPTool):
    name = 'seo.topic_generation'

    def execute(self, input_data: dict) -> dict:
        keyword = input_data.get('keyword', 'marketing strategy')
        return {'topics': [f'How to build a {keyword} plan', f'{keyword} mistakes to avoid']}
