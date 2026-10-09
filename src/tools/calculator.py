"""
Safe arithmetic, percentage, and statistical calculator tool.
"""
import math
from typing import Dict, Any, List
from src.tools.base import BaseTool, ToolParameter

class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Performs safe arithmetic calculations, percentage differences, growth rates, and statistical averages."

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="expression", param_type="string", description="Mathematical expression (e.g., '(88.1 - 62.4) / 62.4 * 100')", required=True)
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        expr = kwargs.get("expression", "").strip()
        # Whitelist safe mathematical functions and operators
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "log": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e
        }
        
        # Check against dangerous tokens
        disallowed = ["__", "import", "exec", "eval", "open", "os", "sys", "subprocess", "compile"]
        if any(token in expr for token in disallowed):
            return {"status": "error", "message": "Disallowed expression or unsafe tokens detected."}

        try:
            # Evaluate using restricted globals and safe names
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return {
                "status": "success",
                "expression": expr,
                "result": result,
                "formatted": f"{result:.4f}" if isinstance(result, float) else str(result)
            }
        except Exception as e:
            return {"status": "error", "expression": expr, "message": f"Calculation error: {str(e)}"}
