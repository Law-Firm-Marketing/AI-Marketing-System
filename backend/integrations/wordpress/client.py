class WordPressClient:
    """External WordPress integration placeholder; call only from MCP layer."""

    def publish(self, title: str, content: str, meta: dict) -> dict:
        return {'title': title, 'content_length': len(content), 'meta': meta}
