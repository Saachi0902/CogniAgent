"""
Planner Agent (Supervisor): Decomposes objectives into structured task DAGs.
"""
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.llm.base import BaseLLM
from src.models.state import AgentState
from src.models.schemas import ResearchPlan, SubTask

PLANNER_SYSTEM_PROMPT = """You are the Supervisor Planner Agent for an autonomous research and intelligence engine.
Your mission is to take an open-ended user topic or research query and decompose it into an actionable,
directed sequence of specific sub-tasks (2 to 4 tasks).
For each sub-task:
- id: e.g. "task_1", "task_2", etc.
- title: concise title
- description: clear, empirical directive for what to investigate
- assigned_agent: "researcher"
- dependencies: list of task IDs that must be completed first
- status: "pending"

Return strictly structured JSON conforming to the ResearchPlan schema.
"""

class PlannerAgent(BaseAgent):
    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="Supervisor Planner Agent",
            role="Hierarchical Task Planner & Orchestrator",
            system_prompt=PLANNER_SYSTEM_PROMPT,
            llm=llm
        )

    async def run(self, state: AgentState) -> AgentState:
        state.current_phase = "planning"
        state.log_step(
            agent=self.name,
            action="plan_start",
            msg=f"Decomposing research query: '{state.user_query}'"
        )

        prompt = f"""User Objective: {state.user_query}

Please produce a comprehensive ResearchPlan with a defined scope and ordered subtasks.
"""
        try:
            data = await self.llm.generate_json(
                prompt=prompt,
                system_prompt=self.system_prompt,
                response_model=ResearchPlan
            )
            plan = ResearchPlan.model_validate(data)
            # Ensure topic matches state query if generic
            if not plan.topic or plan.topic == "string":
                plan.topic = state.user_query
            state.plan = plan
            state.log_step(
                agent=self.name,
                action="plan_generated",
                msg=f"Created research plan with {len(plan.tasks)} sub-tasks across scope: {plan.scope}",
                details={"tasks": [t.title for t in plan.tasks]}
            )
        except Exception as e:
            # Fallback robust default plan if parsing fails
            default_tasks = [
                SubTask(
                    id="task_1",
                    title=f"Core Foundations & Literature on {state.user_query}",
                    description=f"Investigate foundational background, definitions, and recent state of the art for {state.user_query}."
                ),
                SubTask(
                    id="task_2",
                    title=f"Empirical Data, Benchmarks & Metrics for {state.user_query}",
                    description=f"Collect empirical statistics, performance benchmarks, and measurable outcomes."
                ),
                SubTask(
                    id="task_3",
                    title=f"Comparative Analysis, Challenges & Future Trajectory",
                    description=f"Analyze limitations, risks, tradeoffs, and future roadmap.",
                    dependencies=["task_1", "task_2"]
                )
            ]
            state.plan = ResearchPlan(
                topic=state.user_query,
                scope=f"Empirical investigation and state-of-the-art analysis of {state.user_query}",
                tasks=default_tasks
            )
            state.log_step(
                agent=self.name,
                action="plan_fallback",
                msg=f"Generated structured fallback plan with {len(default_tasks)} sub-tasks."
            )

        return state
