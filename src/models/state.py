"""
Agent state representation across the workflow lifecycle.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.models.schemas import ResearchPlan, ResearchFindings, CriticFeedback, FinalReport

class StepLog(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent_name: str
    action_type: str # e.g. "plan", "tool_call", "critique", "synthesize", "hitl_wait"
    message: str
    details: Optional[Dict[str, Any]] = None

class AgentState(BaseModel):
    workflow_id: str
    user_query: str
    current_phase: str = "initialized" # initialized, planning, researching, critiquing, awaiting_hitl, synthesizing, completed, failed
    
    plan: Optional[ResearchPlan] = None
    accumulated_findings: List[ResearchFindings] = Field(default_factory=list)
    critic_history: List[CriticFeedback] = Field(default_factory=list)
    final_report: Optional[FinalReport] = None
    
    # Iteration & Reflection tracking
    current_iteration: int = 0
    max_iterations: int = 3
    critic_approved: bool = False
    
    # Human-in-the-loop tracking
    hitl_approved: bool = True
    hitl_user_notes: Optional[str] = None
    
    # Audit log
    logs: List[StepLog] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def log_step(self, agent: str, action: str, msg: str, details: Optional[Dict[str, Any]] = None):
        self.logs.append(StepLog(
            agent_name=agent,
            action_type=action,
            message=msg,
            details=details
        ))
        self.updated_at = datetime.now(timezone.utc).isoformat()
