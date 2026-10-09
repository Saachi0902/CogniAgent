"""
Workflow Engine: State Graph coordinator with Reflection Loops and HITL gates.
"""
import uuid
import asyncio
from typing import Callable, Optional, Dict, Any
from src.models.state import AgentState, StepLog
from src.llm.base import BaseLLM
from src.llm.factory import get_llm
from src.agents.planner import PlannerAgent
from src.agents.researcher import ResearcherAgent
from src.agents.critic import CriticAgent
from src.agents.synthesizer import SynthesizerAgent
from src.engine.memory import memory_store
from src.config import settings

StepCallback = Callable[[StepLog], Any]

class ResearchWorkflowEngine:
    def __init__(self, llm: Optional[BaseLLM] = None, on_step_callback: Optional[StepCallback] = None):
        self.llm = llm or get_llm()
        self.planner = PlannerAgent(self.llm)
        self.researcher = ResearcherAgent(self.llm)
        self.critic = CriticAgent(self.llm)
        self.synthesizer = SynthesizerAgent(self.llm)
        self.callback = on_step_callback

    def _notify(self, log: StepLog):
        if self.callback:
            try:
                self.callback(log)
            except Exception as e:
                print(f"[Workflow Callback Error] {e}")

    async def execute_query(self, user_query: str, hitl_pause: Optional[bool] = None) -> AgentState:
        """
        Executes the full agentic loop:
        Query -> Memory Recall -> Planning -> Research -> Critic Reflection Loop -> HITL Gate -> Synthesis -> Memory Store
        """
        workflow_id = str(uuid.uuid4())[:8]
        enable_hitl = settings.enable_human_in_the_loop if hitl_pause is None else hitl_pause

        state = AgentState(
            workflow_id=workflow_id,
            user_query=user_query,
            max_iterations=settings.max_critic_iterations
        )

        state.log_step("WorkflowEngine", "init", f"Initialized research workflow session [{workflow_id}]")
        self._notify(state.logs[-1])

        # Step 0: Check Long-Term Memory for prior insights
        prior = memory_store.recall_knowledge(user_query)
        if prior:
            state.log_step(
                "MemoryStore",
                "recall",
                f"Recalled relevant long-term memory for topic '{prior['topic']}'",
                details={"prior_summary": prior["summary"][:120]}
            )
            self._notify(state.logs[-1])

        # Step 1: Supervisor Planner Agent
        state = await self.planner.run(state)
        self._notify(state.logs[-1])

        # Step 2 & 3: Research <-> Critic Reflection Loop
        while not state.critic_approved and state.current_iteration < state.max_iterations:
            # 2. Researcher Agent
            state = await self.researcher.run(state)
            self._notify(state.logs[-1])

            # 3. Critic Agent (Audits & Fact Checks)
            state = await self.critic.run(state)
            self._notify(state.logs[-1])

            if not state.critic_approved:
                state.log_step(
                    "WorkflowEngine",
                    "loop_back",
                    f"Critic requested revision. Looping back to Researcher Agent (Cycle {state.current_iteration + 1})"
                )
                self._notify(state.logs[-1])

        # Step 4: Optional Human-in-the-Loop Checkpoint
        if enable_hitl:
            state.current_phase = "awaiting_hitl"
            state.log_step(
                "HITL_Gate",
                "pause",
                "Workflow paused for Human-in-the-Loop review and sign-off."
            )
            self._notify(state.logs[-1])
            # Return current state paused for user interaction
            return state

        # Step 5: Synthesizer Agent
        state = await self.synthesizer.run(state)
        self._notify(state.logs[-1])

        # Step 6: Store final insights in Long-Term Memory
        if state.final_report:
            memory_store.store_knowledge(
                topic=state.user_query,
                summary=state.final_report.executive_summary,
                tags=[state.user_query]
            )
            state.log_step(
                "MemoryStore",
                "persist",
                "Persisted synthesized executive insights into long-term knowledge repository."
            )
            self._notify(state.logs[-1])

        return state

    async def resume_hitl(self, state: AgentState, approved: bool = True, user_feedback: Optional[str] = None) -> AgentState:
        """Resumes workflow after Human-in-the-Loop approval."""
        state.hitl_approved = approved
        state.hitl_user_notes = user_feedback

        if not approved:
            state.current_phase = "rejected"
            state.log_step("HITL_Gate", "rejected", f"User rejected synthesis: {user_feedback}")
            self._notify(state.logs[-1])
            return state

        state.log_step("HITL_Gate", "approved", "User approved draft. Proceeding to synthesis.")
        self._notify(state.logs[-1])

        # Proceed to Synthesis
        state = await self.synthesizer.run(state)
        self._notify(state.logs[-1])

        if state.final_report:
            memory_store.store_knowledge(
                topic=state.user_query,
                summary=state.final_report.executive_summary
            )
        return state
