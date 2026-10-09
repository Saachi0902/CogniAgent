"""
Base LLM interface for CogniAgent.
"""
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLLM(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate a standard string response."""
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[T]] = None) -> Dict[str, Any]:
        """Generate structured JSON conforming optionally to a Pydantic model."""
        pass
