WORKFLOWS = {
    'seo_pipeline': {
        'name': 'seo_pipeline',
        'steps': [
            {'name': 'keyword_agent', 'depends_on': []},
            {'name': 'content_strategy_agent', 'depends_on': ['keyword_agent']},
            {'name': 'seo_content_agent', 'depends_on': ['content_strategy_agent']},
            {'name': 'wordpress_publish_mcp', 'depends_on': ['seo_content_agent']},
        ],
    },
    'keyword_pipeline': {
        'name': 'keyword_pipeline',
        'steps': [
            {'name': 'keyword_agent', 'depends_on': []},
            {'name': 'content_strategy_agent', 'depends_on': ['keyword_agent']},
            {'name': 'seo_content_agent', 'depends_on': ['content_strategy_agent']},
            {'name': 'wordpress_publish_mcp', 'depends_on': ['seo_content_agent']},
        ],
    },
}
