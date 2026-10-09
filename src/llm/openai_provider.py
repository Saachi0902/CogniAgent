"""
OpenAI & Ollama compatible LLM provider implementation.
"""
import json
import httpx
from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel
from src.llm.base import BaseLLM
from src.config import settings

T = TypeVar("T", bound=BaseModel)

class OpenAILLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[T]] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        sys = (system_prompt or "") + "\nYou MUST return valid, parseable JSON matching the requested structure."
        if response_model:
            schema = json.dumps(response_model.model_json_schema(), indent=2)
            sys += f"\nSchema:\n{schema}"

        messages = [
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            return json.loads(raw_text)
