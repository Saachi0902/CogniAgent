"""
Google Gemini LLM provider implementation using direct REST API.
"""
import json
import httpx
from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel
from src.llm.base import BaseLLM
from src.config import settings

T = TypeVar("T", bound=BaseModel)

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature}
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}?key={self.api_key}", json=payload)
            resp.raise_for_status()
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise RuntimeError(f"Unexpected response structure from Gemini: {data}")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[T]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Request JSON output
        sys_instructions = (system_prompt or "") + "\nYou MUST reply with strictly valid JSON only. Do not enclose in markdown codeblocks."
        if response_model:
            schema_json = json.dumps(response_model.model_json_schema(), indent=2)
            sys_instructions += f"\nYour response must strictly match this JSON Schema:\n{schema_json}"

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": sys_instructions}]},
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}?key={self.api_key}", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            # Clean possible markdown wrap
            raw_text = raw_text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
