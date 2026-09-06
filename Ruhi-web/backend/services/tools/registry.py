import logging
from typing import Dict, List, Optional, Any
from backend.services.tools.base import BaseTool
from backend.services.tools.calculator import CalculatorTool
from backend.services.tools.datetime_tool import DateTimeTool
from backend.services.tools.web_search import WebRetrievalTool
from backend.models.schemas import ToolDefinitionSchema

logger = logging.getLogger("ruhi.tools.registry")


class ToolManager:
    """
    Central Tool Registry and Dispatcher for RUHI.
    
    In RUHI Web v1:
    - Provides real, safe backend tools (calculator, datetime, web retrieval)
    - Provides structured metadata on future desktop tools without simulating fake local executions
    """

    def __init__(self):
        self._active_tools: Dict[str, BaseTool] = {}
        self._planned_desktop_tools: List[Dict[str, Any]] = []
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. Register Real Active Web / Backend Tools
        self.register_tool(CalculatorTool())
        self.register_tool(DateTimeTool())
        self.register_tool(WebRetrievalTool())

        # 2. Register Metadata for Planned Desktop Tools (Clearly demarcated)
        self._planned_desktop_tools = [
            {
                "name": "local_file_search",
                "description": "Index and search authorized local folders and workspaces.",
                "category": "desktop_file",
                "requires_desktop": True,
                "status": "coming_to_desktop",
                "parameters": {"query": "string", "workspace_path": "string"}
            },
            {
                "name": "app_orchestration",
                "description": "Launch and interact with authorized developer tools and applications.",
                "category": "desktop_system",
                "requires_desktop": True,
                "status": "coming_to_desktop",
                "parameters": {"application": "string", "action": "string"}
            },
            {
                "name": "guarded_terminal_exec",
                "description": "Execute permission-gated build pipelines and scripts.",
                "category": "desktop_terminal",
                "requires_desktop": True,
                "status": "coming_to_desktop",
                "parameters": {"command": "string", "working_dir": "string"}
            }
        ]

    def register_tool(self, tool: BaseTool):
        self._active_tools[tool.name] = tool
        logger.info(f"Registered active tool: '{tool.name}' ({tool.category})")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._active_tools.get(name)

    def list_active_tools(self) -> List[ToolDefinitionSchema]:
        results = []
        for tool in self._active_tools.values():
            results.append(
                ToolDefinitionSchema(
                    name=tool.name,
                    description=tool.description,
                    category=tool.category,
                    requires_desktop=tool.requires_desktop,
                    parameters=tool.get_input_schema()
                )
            )
        return results

    def list_all_capabilities(self) -> Dict[str, Any]:
        return {
            "active_tools": [t.model_dump() for t in self.list_active_tools()],
            "planned_desktop_tools": self._planned_desktop_tools,
        }

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "tool_name": tool_name,
                "success": False,
                "error": f"Tool '{tool_name}' is not registered or requires installed RUHI Desktop runtime."
            }
        
        try:
            result = await tool.execute(**arguments)
            return {
                "tool_name": tool_name,
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e)
            }


# Singleton Tool Manager
tool_manager = ToolManager()
