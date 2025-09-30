from __future__ import annotations
from typing import Dict, Any, List

from src.services.llm_client import LLMClient
from src.services.rag import generate_with_rag


class BaseAgent:
    name: str = "base"

    def __init__(self):
        self.client = LLMClient()

    # PUBLIC_INTERFACE
    async def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent on a task and return its result dict."""
        messages = [
            {"role": "system", "content": f"You are {self.name}, an expert educational assistant."},
            {"role": "user", "content": f"Task: {task}\nContext: {context}"},
        ]
        output = await self.client.chat(messages)
        return {"agent": self.name, "output": output}


class MathAgent(BaseAgent):
    name = "math-agent"


class ScienceAgent(BaseAgent):
    name = "science-agent"


class SocraticAgent(BaseAgent):
    name = "socratic-agent"

    async def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "You ask guiding, Socratic questions to help learners reason."},
            {"role": "user", "content": f"Prompt the student with questions to approach: {task}. Context: {context}"},
        ]
        output = await self.client.chat(messages)
        return {"agent": self.name, "output": output}


AGENT_REGISTRY = {
    "math-agent": MathAgent,
    "science-agent": ScienceAgent,
    "socratic-agent": SocraticAgent,
}


# PUBLIC_INTERFACE
async def orchestrate(task: str, context: Dict[str, Any], agent_names: List[str] | None, use_rag: bool | None):
    """Simple round-robin orchestration with optional RAG synthesis."""
    selected = agent_names or list(AGENT_REGISTRY.keys())
    steps: List[Dict[str, Any]] = []
    for name in selected:
        agent_cls = AGENT_REGISTRY.get(name)
        if not agent_cls:
            continue
        agent = agent_cls()
        res = await agent.run(task, context)
        steps.append(res)

    # Synthesize final result (optionally with RAG)
    if use_rag:
        rag_answer, sources = await generate_with_rag(task, context)
        final = "Synthesis:\n" + "\n\n".join([f"[{s['agent']}] {s['output']}" for s in steps]) + f"\n\nRAG:\n{rag_answer}"
        return final, steps, sources
    else:
        final = "Synthesis:\n" + "\n\n".join([f"[{s['agent']}] {s['output']}" for s in steps])
        return final, steps, []
