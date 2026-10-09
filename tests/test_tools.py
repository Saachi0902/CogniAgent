"""
Unit tests for tool definitions and execution.
"""
import pytest
from src.tools.registry import registry
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

@pytest.mark.asyncio
async def test_calculator_tool_valid():
    calc = CalculatorTool()
    res = await calc.execute(expression="(88.1 - 62.4) / 62.4 * 100")
    assert res["status"] == "success"
    assert round(res["result"], 2) == 41.19

@pytest.mark.asyncio
async def test_calculator_tool_security():
    calc = CalculatorTool()
    res = await calc.execute(expression="__import__('os').system('dir')")
    assert res["status"] == "error"
    assert "Disallowed" in res["message"]

@pytest.mark.asyncio
async def test_web_search_tool():
    search = WebSearchTool()
    res = await search.execute(query="Artificial Intelligence", max_results=2)
    assert res["status"] == "success"
    assert len(res["results"]) > 0
    assert "title" in res["results"][0]

@pytest.mark.asyncio
async def test_registry_dispatch():
    res = await registry.execute_tool("calculator", expression="10 + 25")
    assert res["status"] == "success"
    assert res["result"] == 35
