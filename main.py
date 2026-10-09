"""
CogniAgent: Main Application Launcher.
Provides entry points for both Web Dashboard and Interactive CLI.
"""
import sys
import argparse
import asyncio
import uvicorn
from src.config import settings
from src.cli import run_cli

def main():
    parser = argparse.ArgumentParser(description="CogniAgent: Autonomous Multi-Agent Research System")
    parser.add_argument("--cli", action="store_true", help="Launch in interactive CLI mode instead of Web UI")
    parser.add_argument("--topic", "-t", type=str, default="Architectural Paradigms in Agentic AI Systems", help="Research objective (for CLI mode)")
    parser.add_argument("--provider", "-p", type=str, default=None, help="LLM Provider (simulation, gemini, openai, ollama)")
    parser.add_argument("--hitl", action="store_true", help="Enable Human-in-the-Loop review")
    parser.add_argument("--host", type=str, default=settings.host, help="Host for Web UI (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=settings.port, help="Port for Web UI (default: 8000)")

    args = parser.parse_args()

    if args.cli:
        print(f"Launching CogniAgent in CLI mode for topic: {args.topic}")
        asyncio.run(run_cli(topic=args.topic, provider=args.provider, hitl=args.hitl))
    else:
        print(f"===================================================================")
        print(f"       CogniAgent: Autonomous Multi-Agent Research System          ")
        print(f"===================================================================")
        print(f"🌐 Web Dashboard starting at: http://{args.host}:{args.port}")
        print(f"📖 API Documentation at:     http://{args.host}:{args.port}/docs")
        print(f"⚙️  Default Provider:         {settings.llm_provider}")
        print(f"-------------------------------------------------------------------")
        uvicorn.run("src.web.app:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
