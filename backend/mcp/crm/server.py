from mcp.base.tool import MCPTool


class CreateContactTool(MCPTool):
    name = 'crm.create_contact'

    def execute(self, input_data: dict) -> dict:
        return {'contact_id': 'mock-contact-001', 'input': input_data}


class CreateOpportunityTool(MCPTool):
    name = 'crm.create_opportunity'

    def execute(self, input_data: dict) -> dict:
        return {'opportunity_id': 'mock-opp-001', 'input': input_data}


class TriggerWorkflowTool(MCPTool):
    name = 'crm.trigger_workflow'

    def execute(self, input_data: dict) -> dict:
        return {'workflow_triggered': True, 'workflow_name': input_data.get('workflow_name')}
