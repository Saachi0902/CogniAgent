"""
FastAPI web application & REST API for CogniAgent.
"""
import uuid
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.engine.workflow import ResearchWorkflowEngine
from src.llm.factory import get_llm
from src.models.state import AgentState, StepLog
from src.models.schemas import SubTask, ResearchPlan, CriticFeedback, FinalReport
from src.config import settings, OUTPUT_DIR

app = FastAPI(title="CogniAgent API", version="1.0.0", description="Autonomous Multi-Agent Research Engine")

# Static files directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# In-memory store of active/completed workflows
active_workflows: Dict[str, AgentState] = {}
workflow_engines: Dict[str, ResearchWorkflowEngine] = {}

class StartResearchRequest(BaseModel):
    topic: str
    provider: Optional[str] = None
    hitl: Optional[bool] = False

class HitlResponseRequest(BaseModel):
    approved: bool = True
    feedback: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>CogniAgent UI Loading...</h1>")

@app.post("/api/research")
async def start_research(req: StartResearchRequest, background_tasks: BackgroundTasks):
    wf_id = str(uuid.uuid4())[:8]
    initial_state = AgentState(
        workflow_id=wf_id,
        user_query=req.topic,
        max_iterations=settings.max_critic_iterations
    )
    active_workflows[wf_id] = initial_state

    # Instantiate engine with live state mutator
    llm = get_llm(req.provider)
    engine = ResearchWorkflowEngine(llm=llm)
    workflow_engines[wf_id] = engine

    # Run workflow asynchronously
    async def _runner():
        try:
            finished_state = await engine.execute_query(req.topic, hitl_pause=req.hitl)
            active_workflows[wf_id] = finished_state
        except Exception as e:
            active_workflows[wf_id].current_phase = "failed"
            active_workflows[wf_id].log_step("WorkflowEngine", "error", f"Execution error: {str(e)}")

    background_tasks.add_task(_runner)

    return {
        "status": "started",
        "workflow_id": wf_id,
        "topic": req.topic,
        "provider": req.provider or settings.llm_provider
    }

@app.get("/api/status/{workflow_id}")
async def get_status(workflow_id: str):
    state = active_workflows.get(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow ID not found")
    return state.model_dump()

@app.post("/api/hitl/{workflow_id}")
async def submit_hitl(workflow_id: str, req: HitlResponseRequest, background_tasks: BackgroundTasks):
    state = active_workflows.get(workflow_id)
    engine = workflow_engines.get(workflow_id)
    if not state or not engine:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if state.current_phase != "awaiting_hitl":
        raise HTTPException(status_code=400, detail="Workflow is not currently waiting for HITL approval")

    async def _resume():
        resumed = await engine.resume_hitl(state, approved=req.approved, user_feedback=req.feedback)
        active_workflows[workflow_id] = resumed

    background_tasks.add_task(_resume)
    return {"status": "resumed", "workflow_id": workflow_id}

@app.get("/api/schema")
async def get_schemas():
    """Returns the JSON schema of development models for the assignment."""
    return {
        "SubTask": SubTask.model_json_schema() if "SubTask" in globals() else {},
        "ResearchPlan": ResearchPlan.model_json_schema(),
        "CriticFeedback": CriticFeedback.model_json_schema(),
        "FinalReport": FinalReport.model_json_schema(),
        "AgentState": AgentState.model_json_schema()
    }

@app.get("/api/reports")
async def list_reports():
    reports = []
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("report_*.md"):
            reports.append({
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "modified": f.stat().st_mtime
            })
    return {"reports": reports}
