from __future__ import annotations
from typing import List, Dict, Any

from src.services.retrieval import retrieval_index
from src.services.llm_client import LLMClient
from src.core.config import settings


SYSTEM_BASE = (
    "You are IntelliTutor, a helpful educational tutor. "
    "Provide clear, step-by-step explanations with examples. Cite sources when available."
)


# PUBLIC_INTERFACE
async def generate_with_rag(
    question: str,
    session_context: Dict[str, Any],
    top_k: int | None = None,
) -> tuple[str, List[Dict[str, Any]]]:
    """Generate an answer using simple retrieval then LLM completion.

    Args:
        question: The user's question.
        session_context: Context information for the current tutoring session.
        top_k: Number of documents to retrieve.

    Returns:
        Tuple of (assistant_message, sources)
    """
    k = top_k or settings.rag_top_k
    docs = retrieval_index.query(question, top_k=k) if settings.rag_enabled else []

    context_bits: List[str] = []
    if session_context:
        context_bits.append("Session Context: " + str(session_context))
    if docs:
        joined_docs = "\n---\n".join([d.text[:600] for d in docs])
        context_bits.append("Retrieved Knowledge:\n" + joined_docs)

    prompt_parts: List[str] = []
    prompt_parts.append(SYSTEM_BASE)
    prompt_parts.append("Use the provided context to answer the user's question accurately.")
    if context_bits:
        prompt_parts.extend(context_bits)
    prompt_parts.append("User Question: " + question)
    prompt_parts.append("Provide a concise, well-structured answer with steps and references.")
    prompt = "\n".join(prompt_parts)

    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    client = LLMClient()
    answer = await client.chat(messages)
    sources = [{"id": d.id, "score": d.score, "metadata": d.metadata} for d in docs]
    return answer, sources
