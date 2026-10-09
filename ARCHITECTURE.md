# System Architecture & Technical Specification: CogniAgent

CogniAgent is an open, production-grade **Autonomous Multi-Agent Research and Fact-Checking Engine** built from first principles in Python.

---

## 1. Architectural Philosophy

Standard large language models operate as one-shot stochastic predictors, making them susceptible to hallucinations, logical drift, and unverified citations. 

CogniAgent adopts the **Hierarchical Supervisor Multi-Agent Design Pattern** combined with **Closed-Loop Reflection (Self-Correction)** and **Human-in-the-Loop (HITL)** safeguards to ensure high empirical rigor.

### Key Architectural Pillars:
1. **Dynamic Task Decomposition (Planner Agent)**: Translates fuzzy user objectives into bounded, directed acyclic graphs (DAGs) of sub-tasks.
2. **Tool-Augmented Execution (Researcher Agent)**: Equips the agent with active perception tools (web queries, sandboxed mathematics, local file readers).
3. **Automated Reflection & Fact-Checking (Critic Agent)**: A dedicated peer agent evaluates findings across four dimensions ($F, C, V, H$) and triggers revision loops if quality criteria are unmet.
4. **Dual-Tier Memory Architecture**: Combines volatile thread working memory with persistent semantic knowledge caching.
5. **Universal LLM Abstraction**: Operates seamlessly with Google Gemini 2.5/2.0, OpenAI GPT-4o-mini, Local Ollama, and a zero-configuration Deterministic Simulation Engine for offline evaluation.

---

## 2. Component Taxonomy

```
CogniAgent
├── Execution Engine (src/engine/)
│   ├── ResearchWorkflowEngine: Finite State Machine coordinator & loop executor
│   └── MemoryStore: Volatile thread cache & persistent disk JSON store
│
├── Agents (src/agents/)
│   ├── Supervisor Planner Agent: Task decomposition & DAG scheduling
│   ├── Autonomous Research Agent: Multi-tool investigator & fact extractor
│   ├── Fact-Checking Critic Agent: Multi-dimensional reflection auditor
│   └── Intelligence Synthesis Agent: Executive deliverable & bibliography author
│
├── Tools (src/tools/)
│   ├── WebSearchTool: Live Wikipedia API & scholarly fallback
│   ├── CalculatorTool: AST-audited safe mathematical computation
│   ├── DocumentAnalysisTool: Local knowledge base file parser
│   └── ToolRegistry: Centralized dispatcher & schema generator
│
├── LLM Providers (src/llm/)
│   ├── SimulationLLM: Heuristic engine for offline & grading evaluation
│   ├── GeminiLLM: Direct REST connector to Google Gemini models
│   ├── OpenAILLM: REST connector to OpenAI & Ollama endpoints
│   └── LLMFactory: Dynamic runtime provider resolver
│
└── Interfaces
    ├── Web UI (src/web/): FastAPI backend + Tailwind CSS Glassmorphism Dashboard
    └── CLI (src/cli.py): Terminal interface with colored agent telemetry
```

---

## 3. Detailed Agent Specifications

### 3.1 Supervisor Planner Agent
- **Input**: User objective string $Q$.
- **Operation**: Formulates an execution scope and partitions $Q$ into $K \in [2, 4]$ sub-tasks $T_1, T_2, \dots, T_K$.
- **Output**: `ResearchPlan` conforming to JSON Schema.

### 3.2 Autonomous Research Agent
- **Input**: `ResearchPlan` and optional `CriticFeedback.revision_instructions`.
- **Operation**:
  - Iterates through scheduled sub-tasks.
  - Queries `ToolRegistry` to discover relevant tools.
  - Calls `web_search` for domain evidence.
  - Calls `calculator` for growth rates, delta calculations, and statistical consistency.
  - Extracts empirical facts with attribution markers $[1], [2], \dots$.
- **Output**: `List[ResearchFindings]`.

### 3.3 Fact-Checking Critic Agent (Reflection Loop)
- **Input**: `accumulated_findings` and current iteration counter.
- **Evaluation Criteria**:
  - **Factuality ($w=0.35$)**: Verifies claims against extracted evidence.
  - **Completeness ($w=0.25$)**: Checks that all sub-tasks were answered.
  - **Citation Validity ($w=0.25$)**: Validates primary sources and links.
  - **Coherence ($w=0.15$)**: Ensures logical clarity and structural consistency.
- **Decision Logic**:
  - If Composite Score $\ge 0.75 \implies \text{Approve}$.
  - If Composite Score $< 0.75$ and Iterations $< 3 \implies \text{Reject & issue revision directives}$.
  - If Iterations $\ge 3 \implies \text{Force approval with documented risk caveats}$.

### 3.4 Intelligence Synthesis Agent
- **Input**: Approved findings and audit score.
- **Operation**:
  - Formats an executive summary.
  - Builds structured report sections with empirical grounding.
  - Generates comparative analysis matrices.
  - Compiles IEEE/APA formatted bibliography.
  - Exports artifacts to `output/report_<workflow_id>.md` and `output/latest_report.md`.

---

## 4. Dual-Tier Memory System

The memory tier ensures that agents do not repeat work and can recall findings across runs:
1. **Working Memory (`_working_memory`)**:
   - In-memory key-value dictionary tied to the active workflow ID.
   - Cleared upon task finalization.
2. **Persistent Memory (`_long_term_store`)**:
   - Persisted to disk at `output/long_term_memory.json`.
   - Before planning a query, the workflow engine queries `recall_knowledge(query)`.
   - If prior research exists, prior executive summaries are provided to downstream agents as context.
   - Upon completion, the synthesized executive summary is indexed.

---

## 5. Security & Sandboxing Boundaries

- **Safe Calculator Execution**: The math evaluator runs via Python's `eval()` using an empty builtins dictionary `{"__builtins__": {}}` and whitelisted math primitives (`math.sqrt`, `min`, `max`, `round`, etc.). Dangerous strings (`__import__`, `os`, `exec`, `open`) are rejected before execution.
- **Local File Inspection**: The document reader validates absolute/relative boundaries and caps output characters (`max_chars=4000`) to avoid token window overflow.
- **Bounded Reflection Iterations**: The critique loop is hard-capped at `MAX_CRITIC_ITERATIONS = 3` to prevent infinite loops and runaway API costs.
- **Human-in-the-Loop Checkpoint**: When enabled, the system halts before synthesis and exposes approval endpoints (`POST /api/hitl/{id}`).

---

## 6. Extensibility: Adding Custom Tools

To add a new tool to CogniAgent:
1. Create a class inheriting from `src.tools.base.BaseTool`.
2. Define `name`, `description`, and `parameters`.
3. Implement `async def execute(self, **kwargs) -> Dict[str, Any]`.
4. Register the tool in `src/tools/registry.py`:
   ```python
   self.register(MyCustomTool())
   ```
The Researcher Agent will automatically discover and utilize the new tool schema.
