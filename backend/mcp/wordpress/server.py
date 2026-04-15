from datetime import datetime

from mcp.base.tool import MCPTool


class PublishPostTool(MCPTool):
    name = 'wordpress.publish_post'

    def execute(self, input_data: dict) -> dict:
        return {
            'post_id': 1001,
            'status': 'published',
            'published_at': datetime.utcnow().isoformat(),
            'title': input_data.get('title'),
        }


class UpdatePostTool(MCPTool):
    name = 'wordpress.update_post'

    def execute(self, input_data: dict) -> dict:
        return {
            'post_id': input_data.get('post_id'),
            'status': 'updated',
            'updated_fields': list(input_data.get('data', {}).keys()),
        }
