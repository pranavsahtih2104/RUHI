from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class BaseTool(ABC):
    """
    Abstract Tool interface for RUHI.
    
    Every real tool provides:
    - name: Unique tool identifier
    - description: What the tool does and when to call it
    - category: System, calculation, time, web, or file
    - requires_desktop: True if requires local system environment
    - input_schema: Schema describing accepted arguments
    - execute: Async execution method returning structured output
    """

    name: str
    description: str
    category: str = "utility"
    requires_desktop: bool = False

    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON Schema or parameter definition for the tool."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool safely and return results."""
        pass
