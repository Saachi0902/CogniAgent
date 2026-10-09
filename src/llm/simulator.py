"""
Simulation LLM provider for zero-API-key testing and offline evaluation.
Generates realistic, domain-grounded responses based on agent heuristics.
"""
import json
import asyncio
from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel
from src.llm.base import BaseLLM

T = TypeVar("T", bound=BaseModel)

class SimulationLLM(BaseLLM):
    def __init__(self, latency_sim_sec: float = 0.5):
        self.latency = latency_sim_sec

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        await asyncio.sleep(self.latency)
        lower_prompt = prompt.lower()
        if "summary" in lower_prompt or "executive" in lower_prompt:
            return "This research assessment details current empirical paradigms, state-of-the-art methodology, and industry benchmarks."
        return f"Autonomous analysis generated for query: {prompt[:120]}..."

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[T]] = None) -> Dict[str, Any]:
        await asyncio.sleep(self.latency)
        lower_prompt = prompt.lower()
        lower_sys = (system_prompt or "").lower()

        # 1. Planner Agent Response Simulation
        if "planner" in lower_sys or "research plan" in lower_prompt or "subtask" in lower_prompt:
            return {
                "topic": "Autonomous Agentic AI in Modern Systems",
                "scope": "Comprehensive architectural analysis, empirical benchmarks, safety boundaries, and deployment patterns.",
                "tasks": [
                    {
                        "id": "task_1",
                        "title": "Architectural Paradigms & Core Foundations",
                        "description": "Analyze multi-agent state machines, planner-actor-critic loops, and memory hierarchies.",
                        "assigned_agent": "researcher",
                        "dependencies": [],
                        "status": "pending"
                    },
                    {
                        "id": "task_2",
                        "title": "Empirical Performance & Tool Augmentation",
                        "description": "Investigate tool invocation accuracy, retrieval latency, and context window efficiency.",
                        "assigned_agent": "researcher",
                        "dependencies": ["task_1"],
                        "status": "pending"
                    },
                    {
                        "id": "task_3",
                        "title": "Safety, Hallucination Mitigation & Risk Evaluation",
                        "description": "Assess reflection protocols, human-in-the-loop checkpoints, and guardrails.",
                        "assigned_agent": "researcher",
                        "dependencies": ["task_2"],
                        "status": "pending"
                    }
                ]
            }

        # 2. Critic Agent Response Simulation
        if "critic" in lower_sys or "factuality" in lower_prompt or "evaluation" in lower_prompt:
            # Check if this is a first iteration or revision
            iteration = 1
            if "iteration: 1" in lower_prompt or "first iteration" in lower_prompt or "iteration 1" in lower_prompt:
                iteration = 1
            elif "iteration 2" in lower_prompt:
                iteration = 2

            # Give a high passing score or progressive refinement
            return {
                "passed": True,
                "scores": {
                    "factuality": 0.94,
                    "completeness": 0.89,
                    "citation_validity": 0.92,
                    "coherence": 0.95,
                    "composite_score": 0.925
                },
                "strengths": [
                    "Empirical citations from IEEE and ACM venues are properly cited",
                    "Clear distinction between single-agent ReAct and multi-agent supervisory architectures",
                    "Concrete quantification of tool invocation latency"
                ],
                "deficiencies": [
                    "Could highlight additional real-world case studies in enterprise fintech"
                ],
                "revision_instructions": [
                    "Integrate real-world deployment metrics for edge hardware"
                ],
                "iteration_number": iteration
            }

        # 3. Researcher Findings Simulation
        if "researcher" in lower_sys or "findings" in lower_prompt or "key_facts" in lower_prompt:
            return {
                "topic": "State of Agentic AI Systems",
                "task_id": "task_active",
                "summary": "Agentic AI systems transition classical static LLMs into goal-driven autonomous actors capable of iterative tool execution and self-correction.",
                "key_facts": [
                    {
                        "claim": "Multi-agent reflection architectures reduce hallucination rates by up to 34% compared to standard zero-shot prompting.",
                        "source_citation": "[1] Zhang et al., 2025, Journal of Autonomous AI Agents",
                        "evidence": "Controlled benchmarking over 1,200 complex multi-step reasoning tasks showed a jump from 62.4% to 88.1% accuracy."
                    },
                    {
                        "claim": "Hierarchical Supervisor architectures prevent cascading agent deadlocks by enforcing deterministic directed acyclic task graphs.",
                        "source_citation": "[2] DeepMind Agentic Systems Survey, 2026",
                        "evidence": "Supervisor agents dynamically prune invalid subtasks and reallocate resources across subagents."
                    },
                    {
                        "claim": "Dynamic tool retrieval reduces context window token consumption by 52%.",
                        "source_citation": "[3] Modern LLM Tool Integration Benchmarks, 2025",
                        "evidence": "Selecting only the top-3 relevant tools on demand prevents context saturation and distraction."
                    }
                ],
                "citations": [
                    {
                        "id": "[1]",
                        "source": "Zhang et al., 2025. Reflection Architectures in Autonomous AI Agents",
                        "url": "https://arxiv.org/abs/2403.00100",
                        "reliability_score": 0.96
                    },
                    {
                        "id": "[2]",
                        "source": "DeepMind Agentic Systems Survey 2026",
                        "url": "https://deepmind.google/research/agentic-ai",
                        "reliability_score": 0.98
                    },
                    {
                        "id": "[3]",
                        "source": "Modern LLM Tool Integration Benchmarks",
                        "url": "https://ieee.org/ai-systems/benchmarks-2025",
                        "reliability_score": 0.92
                    }
                ],
                "metrics_or_data": {
                    "accuracy_improvement": "+25.7%",
                    "hallucination_reduction": "34.0%",
                    "context_efficiency": "52.0%"
                },
                "raw_evidence": "Empirical datasets validated across multi-hop reasoning questions and synthetic environment benchmarks."
            }

        # 4. Final Report Simulation
        if "synthesizer" in lower_sys or "final report" in lower_prompt or "executive_summary" in lower_prompt:
            return {
                "title": "Autonomous Agentic AI: Architecture, Reflection Loops & Verification",
                "topic": "Agentic AI Development and Systems",
                "executive_summary": "Agentic AI represents a paradigm shift from passive predictive text completion to autonomous, goal-directed reasoning systems. By integrating hierarchical planning, iterative tool execution, cyclic reflection critique loops, and dual-layer memory stores, modern agentic frameworks achieve high reliability on complex reasoning tasks.",
                "sections": [
                    {
                        "heading": "1. Architectural Paradigm & Supervisor-Worker Topology",
                        "content": "Unlike flat autonomous agents, modern production architectures utilize a Hierarchical Supervisor topology. The Supervisor decomposes open-ended user objectives into Directed Acyclic Graphs (DAGs) of discrete tasks. Worker agents execute specialized tool operations under deterministic state bounds, ensuring task convergence.",
                        "subsections": {
                            "State Machine Formulation": "The workflow is modeled as a formal 5-tuple (S, A, T, R, Ω) where state transitions are tracked with immutable audit logs."
                        }
                    },
                    {
                        "heading": "2. Reflection Loops & Self-Correction Mechanisms",
                        "content": "The cornerstone of agentic reliability is the Reflection Loop (Critic Agent). When a research output is produced, the Critic verifies factual consistency, checks references, and assigns a composite confidence score. If the score falls below a defined threshold, execution loops back with targeted revision directives.",
                        "subsections": {
                            "Scoring Vector": "The evaluation matrix incorporates factuality, completeness, citation verifiability, and logical coherence."
                        }
                    },
                    {
                        "heading": "3. Tool Integration & Dynamic Function Calling",
                        "content": "Agents interact with the physical and digital world via specialized tool APIs: live web search, document parsing, and sandboxed code execution. Dynamic tool retrieval prevents context pollution.",
                        "subsections": {
                            "Latency Optimizations": "Selective tool binding achieves a 52% reduction in prompt token bloat."
                        }
                    }
                ],
                "comparative_matrix": [
                    {"Feature": "Autonomy Level", "Zero-Shot Prompting": "None", "Chain-of-Thought (CoT)": "Low", "Agentic Reflection System": "High (Self-Directed)"},
                    {"Feature": "Tool Calling", "Zero-Shot Prompting": "Unsupported", "Chain-of-Thought (CoT)": "Static / Linear", "Agentic Reflection System": "Dynamic & Closed-Loop"},
                    {"Feature": "Hallucination Resistance", "Zero-Shot Prompting": "Poor", "Chain-of-Thought (CoT)": "Moderate", "Agentic Reflection System": "Very High (Critic Loop)"},
                    {"Feature": "Human-in-the-Loop", "Zero-Shot Prompting": "Not Applicable", "Chain-of-Thought (CoT)": "Manual prompt only", "Agentic Reflection System": "Native Checkpoint Gate"}
                ],
                "limitations_and_risks": [
                    "Non-deterministic execution cycles if maximum loop limits are not enforced",
                    "Token consumption overhead from multi-turn agent deliberations",
                    "Susceptibility to adversarial prompt injection via untrusted tool outputs"
                ],
                "recommendations": [
                    "Enforce strict execution bounds (max reflection iterations = 3)",
                    "Implement a Human-in-the-Loop (HITL) gatekeeper before critical write operations",
                    "Maintain structured JSON communication contracts between all communicating agents"
                ],
                "bibliography": [
                    {
                        "id": "[1]",
                        "source": "Zhang et al., 2025. Reflection Architectures in Autonomous AI Agents",
                        "url": "https://arxiv.org/abs/2403.00100",
                        "reliability_score": 0.96
                    },
                    {
                        "id": "[2]",
                        "source": "DeepMind Agentic Systems Survey 2026",
                        "url": "https://deepmind.google/research/agentic-ai",
                        "reliability_score": 0.98
                    },
                    {
                        "id": "[3]",
                        "source": "Modern LLM Tool Integration Benchmarks",
                        "url": "https://ieee.org/ai-systems/benchmarks-2025",
                        "reliability_score": 0.92
                    }
                ],
                "critic_composite_score": 0.93,
                "total_iterations": 1
            }

        # Fallback generic JSON
        return {
            "status": "success",
            "message": "Simulated structured response",
            "data": prompt[:100]
        }
