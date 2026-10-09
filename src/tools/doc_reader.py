"""
Document reader tool for parsing local text and markdown files.
"""
from pathlib import Path
from typing import Dict, Any, List
from src.tools.base import BaseTool, ToolParameter

class DocumentAnalysisTool(BaseTool):
    @property
    def name(self) -> str:
        return "document_reader"

    @property
    def description(self) -> str:
        return "Reads local markdown, text, or data files from workspace knowledge repositories."

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="file_path", param_type="string", description="Relative path of file to inspect", required=True),
            ToolParameter(name="max_chars", param_type="integer", description="Max characters to read", required=False)
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        file_path_str = kwargs.get("file_path", "")
        max_chars = int(kwargs.get("max_chars", 4000))
        target = Path(file_path_str)

        if not target.is_absolute():
            target = Path.cwd() / target

        if not target.exists():
            return {
                "status": "error",
                "message": f"File not found at: {file_path_str}",
                "exists": False
            }

        try:
            content = target.read_text(encoding="utf-8")
            truncated = len(content) > max_chars
            return {
                "status": "success",
                "file_path": str(target),
                "length": len(content),
                "truncated": truncated,
                "content": content[:max_chars]
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to read file: {str(e)}"}
