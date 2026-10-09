"""
Data schemas and exchange models for the Multi-Agent System.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SubTask(BaseModel):
    id: str = Field(..., description="Unique identifier for the sub-task, e.g. task_1")
    title: str = Field(..., description="Concise goal of the sub-task")
    description: str = Field(..., description="Detailed instructions for the research agent")
    assigned_agent: str = Field(default="researcher", description="Agent responsible for execution")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete first")
    status: str = Field(default="pending", description="Status: pending, in_progress, completed, failed")
    output: Optional[str] = Field(default=None, description="Resulting output from sub-task execution")

class ResearchPlan(BaseModel):
    topic: str = Field(..., description="Main user research prompt/topic")
    scope: str = Field(..., description="Defined research boundary and core objective")
    tasks: List[SubTask] = Field(default_factory=list, description="Ordered decomposition of tasks")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CitationItem(BaseModel):
    id: str = Field(..., description="e.g. [1], [2]")
    source: str = Field(..., description="Source title, organization, or URL")
    url: Optional[str] = Field(default=None, description="Direct URL if available")
    reliability_score: float = Field(default=0.9, description="Confidence in source validity 0.0 - 1.0")

class FactItem(BaseModel):
    claim: str = Field(..., description="Key fact or empirical finding")
    source_citation: str = Field(..., description="Citation marker referencing the source")
    evidence: str = Field(..., description="Supporting excerpt or data point")

class ResearchFindings(BaseModel):
    topic: str
    task_id: str
    summary: str
    key_facts: List[FactItem] = Field(default_factory=list)
    citations: List[CitationItem] = Field(default_factory=list)
    metrics_or_data: Dict[str, Any] = Field(default_factory=dict)
    raw_evidence: str = ""

class CriticScore(BaseModel):
    factuality: float = Field(..., ge=0.0, le=1.0, description="Verification of facts and lack of hallucination")
    completeness: float = Field(..., ge=0.0, le=1.0, description="Coverage of sub-topics and depth")
    citation_validity: float = Field(..., ge=0.0, le=1.0, description="Presence of verifiable references")
    coherence: float = Field(..., ge=0.0, le=1.0, description="Logical clarity and rigor")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Weighted average score")

class CriticFeedback(BaseModel):
    passed: bool = Field(..., description="True if composite_score >= threshold")
    scores: CriticScore
    strengths: List[str] = Field(default_factory=list)
    deficiencies: List[str] = Field(default_factory=list)
    revision_instructions: List[str] = Field(default_factory=list, description="Specific actions needed if failed")
    iteration_number: int = 1

class SectionReport(BaseModel):
    heading: str
    content: str
    subsections: Dict[str, str] = Field(default_factory=dict)

class FinalReport(BaseModel):
    title: str
    topic: str
    executive_summary: str
    sections: List[SectionReport] = Field(default_factory=list)
    comparative_matrix: Optional[List[Dict[str, Any]]] = None
    limitations_and_risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    bibliography: List[CitationItem] = Field(default_factory=list)
    critic_composite_score: float = 0.0
    total_iterations: int = 1
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
