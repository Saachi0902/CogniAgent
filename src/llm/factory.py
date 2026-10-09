"""
Factory to instantiate the appropriate LLM provider.
"""
from src.config import settings
from src.llm.base import BaseLLM
from src.llm.simulator import SimulationLLM
from src.llm.gemini import GeminiLLM
from src.llm.openai_provider import OpenAILLM

def get_llm(provider: str = None) -> BaseLLM:
    prov = (provider or settings.llm_provider).lower()
    
    if prov == "gemini":
        if not settings.gemini_api_key:
            print("[CogniAgent Warning] GEMINI_API_KEY missing. Falling back to Simulation mode.")
            return SimulationLLM()
        return GeminiLLM()
    elif prov == "openai":
        if not settings.openai_api_key:
            print("[CogniAgent Warning] OPENAI_API_KEY missing. Falling back to Simulation mode.")
            return SimulationLLM()
        return OpenAILLM()
    elif prov == "ollama":
        return OpenAILLM(api_key="ollama", model=settings.ollama_model, base_url=f"{settings.ollama_base_url}/v1")
    else:
        return SimulationLLM()
