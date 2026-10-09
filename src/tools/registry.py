"""
Tool registry to manage and execute tools safely.
"""
from typing import Dict, Any, List, Optional
from src.tools.base import BaseTool, ToolDefinition
from src.tools.web_search import WebSearchTool
from src.tools.calculator import CalculatorTool
from src.tools.doc_reader import DocumentAnalysisTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Register standard tools
        self.register(WebSearchTool())
        self.register(CalculatorTool())
        self.register(DocumentAnalysisTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_definitions(self) -> List[ToolDefinition]:
        return [tool.to_schema() for tool in self._tools.values()]

    def list_names(self) -> List[str]:
        return list(self._tools.keys())

    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {
                "status": "error",
                "message": f"Tool '{name}' is not registered. Available tools: {self.list_names()}"
            }
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            return {
                "status": "error",
                "tool": name,
                "message": f"Execution error in tool '{name}': {str(e)}"
            }

# Global singleton
registry = ToolRegistry()
