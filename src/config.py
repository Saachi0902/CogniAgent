"""
Configuration settings for CogniAgent Multi-Agent Research System.
"""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

class Settings(BaseModel):
    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "simulation").lower()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Agent Loop Control
    max_critic_iterations: int = int(os.getenv("MAX_CRITIC_ITERATIONS", "3"))
    critic_pass_threshold: float = float(os.getenv("CRITIC_PASS_THRESHOLD", "0.75"))
    enable_human_in_the_loop: bool = os.getenv("ENABLE_HUMAN_IN_THE_LOOP", "false").lower() in ("true", "1", "yes")

    # Server Settings
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
