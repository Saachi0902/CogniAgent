"""
Unit tests for agent decision making and outputs.
"""
import pytest
from src.llm.simulator import SimulationLLM
from src.models.state import AgentState
from src.agents.planner import PlannerAgent
from src.agents.researcher import ResearcherAgent
from src.agents.critic import CriticAgent
from src.agents.synthesizer import SynthesizerAgent

@pytest.fixture
def sim_llm():
    return SimulationLLM(latency_sim_sec=0.01)

@pytest.mark.asyncio
async def test_planner_agent(sim_llm):
    planner = PlannerAgent(sim_llm)
    state = AgentState(workflow_id="test_plan", user_query="Multi-Agent Systems")
    state = await planner.run(state)
    assert state.plan is not None
    assert len(state.plan.tasks) >= 2
    assert state.current_phase == "planning"

@pytest.mark.asyncio
async def test_researcher_agent(sim_llm):
    planner = PlannerAgent(sim_llm)
    researcher = ResearcherAgent(sim_llm)
    state = AgentState(workflow_id="test_res", user_query="Multi-Agent Systems")
    state = await planner.run(state)
    state = await researcher.run(state)
    assert len(state.accumulated_findings) > 0
    assert state.current_phase == "researching"

@pytest.mark.asyncio
async def test_critic_agent(sim_llm):
    planner = PlannerAgent(sim_llm)
    researcher = ResearcherAgent(sim_llm)
    critic = CriticAgent(sim_llm)
    state = AgentState(workflow_id="test_crit", user_query="Multi-Agent Systems")
    state = await planner.run(state)
    state = await researcher.run(state)
    state = await critic.run(state)
    assert len(state.critic_history) == 1
    assert state.critic_history[0].scores.composite_score >= 0.0
    assert state.current_iteration == 1

@pytest.mark.asyncio
async def test_synthesizer_agent(sim_llm):
    planner = PlannerAgent(sim_llm)
    researcher = ResearcherAgent(sim_llm)
    critic = CriticAgent(sim_llm)
    synthesizer = SynthesizerAgent(sim_llm)
    state = AgentState(workflow_id="test_synth", user_query="Multi-Agent Systems")
    state = await planner.run(state)
    state = await researcher.run(state)
    state = await critic.run(state)
    state = await synthesizer.run(state)
    assert state.final_report is not None
    assert len(state.final_report.sections) > 0
    assert state.current_phase == "completed"
