"""
End-to-end integration tests for ResearchWorkflowEngine and memory store.
"""
import pytest
from src.llm.simulator import SimulationLLM
from src.engine.workflow import ResearchWorkflowEngine
from src.engine.memory import memory_store

@pytest.mark.asyncio
async def test_full_workflow_execution():
    llm = SimulationLLM(latency_sim_sec=0.01)
    engine = ResearchWorkflowEngine(llm=llm)

    state = await engine.execute_query(
        user_query="Empirical Evaluation of Agentic AI Frameworks",
        hitl_pause=False
    )

    assert state.current_phase == "completed"
    assert state.plan is not None
    assert len(state.accumulated_findings) > 0
    assert len(state.critic_history) > 0
    assert state.critic_approved is True
    assert state.final_report is not None
    assert state.final_report.critic_composite_score > 0.70

    # Verify memory persistence
    recalled = memory_store.recall_knowledge("Empirical Evaluation of Agentic AI Frameworks")
    assert recalled is not None
    assert "summary" in recalled

@pytest.mark.asyncio
async def test_workflow_hitl_pause_and_resume():
    llm = SimulationLLM(latency_sim_sec=0.01)
    engine = ResearchWorkflowEngine(llm=llm)

    state = await engine.execute_query(
        user_query="HITL Verification in Healthcare Agents",
        hitl_pause=True
    )

    assert state.current_phase == "awaiting_hitl"
    assert state.final_report is None

    # Resume workflow
    resumed_state = await engine.resume_hitl(state, approved=True)
    assert resumed_state.current_phase == "completed"
    assert resumed_state.final_report is not None
