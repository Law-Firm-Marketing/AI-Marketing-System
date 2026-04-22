from mcp.base.tool import MCPTool


class TrafficReportTool(MCPTool):
    name = 'analytics.traffic_report'

    def execute(self, input_data: dict) -> dict:
        return {'sessions': 1240, 'pageviews': 4200, 'period': input_data.get('period', 'last_30_days')}


class ConversionMetricsTool(MCPTool):
    name = 'analytics.conversion_metrics'

    def execute(self, input_data: dict) -> dict:
        return {'conversion_rate': 0.032, 'leads': 40, 'period': input_data.get('period', 'last_30_days')}
