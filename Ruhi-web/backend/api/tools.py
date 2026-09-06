from fastapi import APIRouter
from backend.models.schemas import ToolExecutionRequest, ToolExecutionResponse
from backend.services.tools.registry import tool_manager

router = APIRouter(tags=["Tools"])


@router.get("/tools")
async def list_tools():
    """
    Returns registered safe web tools and metadata on upcoming desktop tools.
    """
    return tool_manager.list_all_capabilities()


@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool_endpoint(payload: ToolExecutionRequest):
    """
    Executes an active registered tool.
    """
    res = await tool_manager.execute_tool(payload.tool_name, payload.arguments)
    return ToolExecutionResponse(
        tool_name=payload.tool_name,
        success=res.get("success", False),
        result=res.get("result"),
        error=res.get("error")
    )
