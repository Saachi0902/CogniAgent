"""
Base agent definition and common utilities.
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.llm.base import BaseLLM
from src.models.state import AgentState

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str, llm: BaseLLM):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm = llm

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        """Execute the agent step and mutate or update the workflow state."""
        pass
