from datetime import datetime

from mcp.base.tool import MCPTool


class SocialPublishPostTool(MCPTool):
    name = 'social.publish_post'

    def execute(self, input_data: dict) -> dict:
        return {'social_post_id': 'social-001', 'status': 'published', 'channel': input_data.get('channel', 'linkedin')}


class SocialSchedulePostTool(MCPTool):
    name = 'social.schedule_post'

    def execute(self, input_data: dict) -> dict:
        return {
            'social_post_id': 'social-002',
            'status': 'scheduled',
            'scheduled_for': input_data.get('scheduled_for', datetime.utcnow().isoformat()),
        }
