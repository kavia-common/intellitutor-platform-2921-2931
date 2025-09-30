from __future__ import annotations
from typing import Dict, Any, List

from src.services.llm_client import LLMClient
from src.services.rag import generate_with_rag


SYSTEM_PROMPT = (
    "You are IntelliTutor, a friendly, structured educational tutor. "
    "Respond clearly with steps, definitions, and examples. Be concise."
)


# PUBLIC_INTERFACE
async def respond(
    user_message: str,
    session_context: Dict[str, Any],
    history: List[Dict[str, str]] | None = None,
    use_rag: bool | None = None,
) -> tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate a response with optional RAG, returning (answer, sources, breadcrumbs)."""
    breadcrumbs: List[Dict[str, Any]] = []
    if use_rag is True:
        answer, sources = await generate_with_rag(user_message, session_context)
        breadcrumbs.append({"stage": "rag", "sources": sources})
        return answer, sources, breadcrumbs

    # Use history + system prompt when not forcing RAG
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-12:])  # limit tokens
    messages.append({"role": "user", "content": user_message})

    client = LLMClient()
    answer = await client.chat(messages)
    return answer, [], breadcrumbs
