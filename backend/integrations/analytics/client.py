class AnalyticsClient:
    """External analytics integration placeholder; call only from MCP layer."""

    def get_report(self, report_type: str, params: dict) -> dict:
        return {'report_type': report_type, 'params': params}
