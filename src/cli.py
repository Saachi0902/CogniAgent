"""
Interactive Command-Line Interface for CogniAgent.
"""
import sys
import asyncio
import argparse
from typing import Optional
from src.engine.workflow import ResearchWorkflowEngine
from src.llm.factory import get_llm
from src.models.state import StepLog
from src.config import settings

# ANSI color codes for rich terminal display
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def cli_step_logger(log: StepLog):
    badge_colors = {
        "WorkflowEngine": CYAN,
        "Supervisor Planner Agent": MAGENTA,
        "Autonomous Research Agent": CYAN,
        "Fact-Checking & Reflection Critic": YELLOW,
        "Intelligence Synthesis Agent": GREEN,
        "HITL_Gate": RED,
        "MemoryStore": BOLD
    }
    color = badge_colors.get(log.agent_name, CYAN)
    print(f"{color}[{log.agent_name}]{RESET} {log.message}")
    if log.details:
        for k, v in log.details.items():
            print(f"   -> {BOLD}{k}:{RESET} {v}")

async def run_cli(topic: str, provider: Optional[str] = None, hitl: bool = False):
    print(f"\n{BOLD}{CYAN}==================================================================={RESET}")
    print(f"{BOLD}{CYAN}      CogniAgent : Autonomous Multi-Agent Research Engine          {RESET}")
    print(f"{BOLD}{CYAN}==================================================================={RESET}")
    print(f"{BOLD}Topic:{RESET} {topic}")
    print(f"{BOLD}LLM Provider:{RESET} {provider or settings.llm_provider}")
    print(f"{BOLD}Human-In-The-Loop:{RESET} {'Enabled' if hitl else 'Disabled'}")
    print("-" * 67)

    llm = get_llm(provider)
    engine = ResearchWorkflowEngine(llm=llm, on_step_callback=cli_step_logger)

    state = await engine.execute_query(topic, hitl_pause=hitl)

    # If paused for HITL
    if state.current_phase == "awaiting_hitl":
        print(f"\n{YELLOW}{BOLD}⚠️ [HITL Gate] Workflow Paused for Human Approval.{RESET}")
        print(f"Current Findings collected: {len(state.accumulated_findings)} sections.")
        print(f"Critic Score: {state.critic_history[-1].scores.composite_score:.2f}")
        resp = input("\nApprove and generate final report? (y/n/feedback): ").strip()
        if resp.lower() in ("y", "yes", ""):
            state = await engine.resume_hitl(state, approved=True)
        else:
            state = await engine.resume_hitl(state, approved=False, user_feedback=resp)

    if state.final_report:
        print(f"\n{GREEN}{BOLD}==================================================================={RESET}")
        print(f"{GREEN}{BOLD}                   RESEARCH WORKFLOW COMPLETED                     {RESET}")
        print(f"{GREEN}{BOLD}==================================================================={RESET}")
        print(f"\n{BOLD}Report Title:{RESET} {state.final_report.title}")
        print(f"{BOLD}Critic Composite Score:{RESET} {state.final_report.critic_composite_score:.3f} / 1.000")
        print(f"{BOLD}Reflection Iterations:{RESET} {state.final_report.total_iterations}")
        print(f"\n{BOLD}Executive Summary:{RESET}\n{state.final_report.executive_summary}\n")
        print(f"{BOLD}Report exported to:{RESET} output/report_{state.workflow_id}.md")
        print(f"{BOLD}Latest copy available at:{RESET} output/latest_report.md")
    else:
        print(f"\n{RED}Workflow ended without generating final report.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="CogniAgent: Autonomous Multi-Agent Research System")
    parser.add_argument("--topic", "-t", type=str, default="Architectural Paradigms in Agentic AI Systems", help="Research objective or topic")
    parser.add_argument("--provider", "-p", type=str, default=None, help="LLM backend: simulation, gemini, openai, ollama")
    parser.add_argument("--hitl", action="store_true", help="Enable human-in-the-loop approval checkpoint")
    args = parser.parse_args()

    asyncio.run(run_cli(args.topic, args.provider, args.hitl))

if __name__ == "__main__":
    main()
