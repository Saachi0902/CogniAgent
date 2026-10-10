"""
Simulation LLM provider: Dynamic, topic-aware heuristic intelligence engine.
Parses actual user topics and tool observations to generate relevant plans, facts, and reports.
"""
import re
import json
import asyncio
from typing import Optional, Type, TypeVar, Dict, Any, List
from pydantic import BaseModel
from src.llm.base import BaseLLM

T = TypeVar("T", bound=BaseModel)

def extract_topic_from_text(text: str) -> str:
    """Extracts the cleanest user topic from a prompt or instruction."""
    for line in text.split("\n"):
        line_clean = line.strip()
        for prefix in ["User Objective:", "Topic:", "Target Research Query:", "User Query:"]:
            if line_clean.lower().startswith(prefix.lower()):
                val = line_clean[len(prefix):].strip()
                if val:
                    val = re.sub(r'^(information about|tell me about|what is|research on|analysis of)\s+', '', val, flags=re.IGNORECASE)
                    return val.strip()

    match = re.search(r'User Objective:\s*([^\n]+)', text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        val = re.sub(r'^(information about|tell me about|what is|research on|analysis of)\s+', '', val, flags=re.IGNORECASE)
        return val.strip()

    clean = re.sub(r'^(information about|tell me about|what is|research on|analysis of)\s+', '', text, flags=re.IGNORECASE)
    return clean[:80].strip() or "Target Subject"

class SimulationLLM(BaseLLM):
    def __init__(self, latency_sim_sec: float = 0.4):
        self.latency = latency_sim_sec

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        await asyncio.sleep(self.latency)
        topic = extract_topic_from_text(prompt)
        return f"Comprehensive investigation and empirical analysis of {topic}."

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[T]] = None) -> Dict[str, Any]:
        await asyncio.sleep(self.latency)
        lower_prompt = prompt.lower()
        lower_sys = (system_prompt or "").lower()
        model_name = response_model.__name__ if response_model else ""
        topic = extract_topic_from_text(prompt)
        topic_title = topic.title()

        # 1. SYNTHESIZER AGENT: Final Comprehensive Deliverable
        if model_name == "FinalReport" or "synthesizer" in lower_sys:
            # Extract citations from prompt if available
            cit_matches = re.findall(r"\[(\d+)\]\s*([^(\n]+)", prompt)
            biblio = []
            if cit_matches:
                for num, src in cit_matches[:4]:
                    biblio.append({
                        "id": f"[{num}]",
                        "source": src.strip(),
                        "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
                        "reliability_score": 0.95
                    })
            if not biblio:
                biblio = [
                    {
                        "id": "[1]",
                        "source": f"Encyclopedia & Research Database: {topic_title}",
                        "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
                        "reliability_score": 0.95
                    },
                    {
                        "id": "[2]",
                        "source": f"Global Scientific Journal: {topic_title} Review",
                        "url": f"https://doi.org/10.1016/{topic.replace(' ', '-')}",
                        "reliability_score": 0.93
                    }
                ]

            return {
                "title": f"Autonomous Intelligence & Empirical Research Report: {topic_title}",
                "topic": topic,
                "executive_summary": f"This comprehensive investigation synthesizes verified empirical findings, observational evidence, and state-of-the-art methodology regarding '{topic}'. Through multi-agent task decomposition, tool-augmented evidence collection, and automated critic reflection, the report provides a rigorously validated overview of core mechanisms, quantitative data, and practical mitigation strategies.",
                "sections": [
                    {
                        "heading": f"1. Foundational Mechanics, Principles & Taxonomy of {topic_title}",
                        "content": f"The scientific foundation of {topic} relies on specific physical, environmental, or systemic principles. Research indicates fundamental mechanisms driving observed phenomena and provides a standardized classification framework.",
                        "subsections": {
                            "Underlying Mechanisms": f"Analysis demonstrates how primary forces and structural factors interact to generate events related to {topic}.",
                            "Taxonomy & Classification": f"Modern frameworks distinguish between different categories, intensities, and scopes of {topic}."
                        }
                    },
                    {
                        "heading": f"2. Observational Datasets, Quantitative Measurement & Benchmarks",
                        "content": f"Quantitative measurement plays a decisive role in analyzing {topic}. Through calibrated sensor arrays, field instrumentation, and statistical metrics, researchers have established reliable measurement scales.",
                        "subsections": {
                            "Measurement Standards": f"Standardized indices allow cross-comparison of occurrences and quantitative severity regarding {topic}.",
                            "Empirical Case Studies": f"Historical data and verified records reveal long-term trends and cyclical patterns in observed datasets."
                        }
                    },
                    {
                        "heading": f"3. Risk Factors, Technological Mitigations & Future Trajectory",
                        "content": f"Addressing the challenges posed by {topic} demands proactive technological interventions, robust safety standards, and early-warning mechanisms to minimize vulnerability and hazard propagation.",
                        "subsections": {
                            "Mitigation Strategies": f"Engineering adaptations, warning protocols, and resilience frameworks significantly reduce negative impacts of {topic}.",
                            "Future Directions": f"Integration of real-time monitoring and computational models offers improved predictive resolution."
                        }
                    }
                ],
                "comparative_matrix": [
                    {
                        "Analysis Dimension": "Detection / Observation",
                        "Traditional Approaches": f"Manual monitoring and retrospective analysis of {topic}",
                        "Modern Computational Methods": f"Real-time sensor arrays and automated predictive modeling for {topic}"
                    },
                    {
                        "Analysis Dimension": "Data Accuracy",
                        "Traditional Approaches": "Qualitative estimates with wide error margins",
                        "Modern Computational Methods": "Calibrated instrumentation with quantitative confidence bounds"
                    },
                    {
                        "Analysis Dimension": "Risk Mitigation",
                        "Traditional Approaches": "Reactive response post-occurrence",
                        "Modern Computational Methods": "Proactive early-warning protocols and structural resilience"
                    }
                ],
                "limitations_and_risks": [
                    f"Inherent variability and non-linear dynamics in real-world observations of {topic}",
                    "Instrumental resolution limits and geographic/temporal sensor sparsity",
                    "Uncertainty in long-term extrapolation from short-term observational datasets"
                ],
                "recommendations": [
                    f"Deploy multi-sensor observational networks for high-resolution tracking of {topic}",
                    "Adopt standardized reporting and open-data protocols for cross-institutional research",
                    "Incorporate continuous validation and self-reflection loops into analytical models"
                ],
                "bibliography": biblio,
                "critic_composite_score": 0.932,
                "total_iterations": 1
            }

        # 2. CRITIC AGENT: Fact-Checking & Reflection Evaluation
        if model_name == "CriticFeedback" or "critic" in lower_sys:
            iteration = 1
            if "iteration: 2" in lower_prompt or "iteration 2" in lower_prompt:
                iteration = 2

            return {
                "passed": True,
                "scores": {
                    "factuality": 0.94,
                    "completeness": 0.91,
                    "citation_validity": 0.93,
                    "coherence": 0.95,
                    "composite_score": 0.932
                },
                "strengths": [
                    f"Verified primary source references directly grounded in {topic}",
                    f"Comprehensive coverage from foundational causes to modern mitigation methods",
                    "High logical coherence and clear empirical claims"
                ],
                "deficiencies": [],
                "revision_instructions": [],
                "iteration_number": iteration
            }

        # 3. PLANNER AGENT: Topic-Specific Task Decomposition
        if model_name == "ResearchPlan" or "planner" in lower_sys:
            return {
                "topic": topic,
                "scope": f"Comprehensive multi-dimensional investigation into {topic}, covering underlying foundations, empirical observations, and future mitigation/applications.",
                "tasks": [
                    {
                        "id": "task_1",
                        "title": f"Foundational Principles, Causes & Mechanics of {topic_title}",
                        "description": f"Examine foundational mechanisms, historical context, underlying physics/principles, and primary taxonomy of {topic}.",
                        "assigned_agent": "researcher",
                        "dependencies": [],
                        "status": "pending"
                    },
                    {
                        "id": "task_2",
                        "title": f"Empirical Data, Measurement & Quantitative Observations in {topic_title}",
                        "description": f"Analyze observational datasets, measurement scales, key statistics, and verified case studies of {topic}.",
                        "assigned_agent": "researcher",
                        "dependencies": ["task_1"],
                        "status": "pending"
                    },
                    {
                        "id": "task_3",
                        "title": f"Risk Factors, Technological Mitigations & Future Trajectory of {topic_title}",
                        "description": f"Evaluate critical impacts, modern prevention/early-warning technologies, safety standards, and future challenges.",
                        "assigned_agent": "researcher",
                        "dependencies": ["task_2"],
                        "status": "pending"
                    }
                ]
            }

        # 4. RESEARCHER AGENT: Tool Evidence & Fact Extraction
        if model_name == "ResearchFindings" or "researcher" in lower_sys:
            facts = []
            citations = []

            # Extract results from tool search results in prompt
            raw_results = re.findall(r"'snippet':\s*['\"]([^'\"]+)['\"]", prompt)
            raw_titles = re.findall(r"'title':\s*['\"]([^'\"]+)['\"]", prompt)
            raw_sources = re.findall(r"'source':\s*['\"]([^'\"]+)['\"]", prompt)
            raw_urls = re.findall(r"'url':\s*['\"]([^'\"]+)['\"]", prompt)

            if raw_results:
                for i, snip in enumerate(raw_results[:3], 1):
                    cit_id = f"[{i}]"
                    title = raw_titles[i-1] if i-1 < len(raw_titles) else f"{topic_title} Study"
                    source_name = raw_sources[i-1] if i-1 < len(raw_sources) else f"Encyclopedia: {title}"
                    url = raw_urls[i-1] if i-1 < len(raw_urls) else f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
                    
                    citations.append({
                        "id": cit_id,
                        "source": source_name,
                        "url": url,
                        "reliability_score": 0.95
                    })
                    facts.append({
                        "claim": snip.strip(),
                        "source_citation": cit_id,
                        "evidence": f"Empirical observation documented under '{title}'."
                    })
            else:
                citations = [
                    {
                        "id": "[1]",
                        "source": f"Encyclopedia & Research Archive: {topic_title}",
                        "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
                        "reliability_score": 0.95
                    },
                    {
                        "id": "[2]",
                        "source": f"International Academic Review: {topic_title}",
                        "url": f"https://doi.org/10.1016/{topic.replace(' ', '-')}",
                        "reliability_score": 0.92
                    }
                ]
                facts = [
                    {
                        "claim": f"Primary empirical investigations into {topic} show direct correlation with natural physical or structural dynamics.",
                        "source_citation": "[1]",
                        "evidence": f"Detailed literature review on foundational mechanisms of {topic}."
                    },
                    {
                        "claim": f"Quantitative measurement models provide predictive accuracy and risk mitigation benchmarks across modern field studies.",
                        "source_citation": "[2]",
                        "evidence": f"Data analysis across verified observational datasets regarding {topic}."
                    }
                ]

            return {
                "topic": topic,
                "task_id": "task_active",
                "summary": f"Synthesized research regarding {topic_title} based on tool-grounded observational evidence and authoritative citations.",
                "key_facts": facts,
                "citations": citations,
                "metrics_or_data": {
                    "observational_confidence": "94.2%",
                    "empirical_coverage": "High",
                    "data_verification": "Verified via Tool Registry"
                },
                "raw_evidence": f"Extracted from live reference documents and observational data on {topic}."
            }

        return {
            "status": "success",
            "message": f"Simulated dynamic response for {topic}",
            "data": prompt[:120]
        }
