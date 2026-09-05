from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str  # "system" | "file" | "web" | "app"
    requires_desktop: bool = True
    requires_permission: bool = True
    parameters: Dict[str, Any] = {}

class ToolRegistry:
    """
    RUHI Tool Registry.
    
    In the Web version, tools are listed as capabilities and metadata.
    In the Installed Desktop version, tools register concrete execution handlers
    guarded by the RUHI Permission Engine.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_definitions()

    def _register_default_definitions(self):
        self.register(ToolDefinition(
            name="file_search",
            description="Search authorized local files and indexed documents.",
            category="file",
            requires_desktop=True,
            requires_permission=True,
            parameters={"query": "string", "file_types": "array"}
        ))
        self.register(ToolDefinition(
            name="app_launcher",
            description="Launch authorized applications (e.g. VS Code, Terminal).",
            category="app",
            requires_desktop=True,
            requires_permission=True,
            parameters={"app_name": "string", "arguments": "array"}
        ))
        self.register(ToolDefinition(
            name="web_retrieval",
            description="Fetch information and documentation from authorized web URLs.",
            category="web",
            requires_desktop=False,
            requires_permission=False,
            parameters={"url": "string"}
        ))
        self.register(ToolDefinition(
            name="task_orchestrator",
            description="Sequence multiple tools into an auditable execution plan.",
            category="system",
            requires_desktop=True,
            requires_permission=True,
            parameters={"plan": "array"}
        ))

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())


tool_registry = ToolRegistry()
