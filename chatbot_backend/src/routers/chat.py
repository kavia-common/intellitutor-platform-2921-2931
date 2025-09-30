from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from src.models.schemas import ChatRequest, ChatResponse
from src.services.repository import repo
from src.services.chat_pipeline import respond

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send chat message",
    responses={200: {"description": "Assistant response"}, 404: {"description": "Session not found"}},
)
async def chat(payload: ChatRequest):
    """
    Send a user message to the tutor and receive an assistant response.

    Parameters:
        payload: ChatRequest containing session_id, content, optional agent, use_rag flag, and context_overrides.

    Returns:
        ChatResponse with assistant Message, sources (if RAG), and intermediate steps.
    """
    session = repo.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history_msgs = repo.get_messages(payload.session_id, limit=20)
    history: List[Dict[str, str]] = [{"role": "user" if m.sender == "user" else "assistant", "content": m.content}
                                     for m in history_msgs]

    context: Dict[str, Any] = dict(session.context)
    if payload.context_overrides:
        context.update(payload.context_overrides)

    # Store user message
    repo.add_message(payload.session_id, "user", payload.content)

    answer, sources, breadcrumbs = await respond(
        payload.content, session_context=context, history=history, use_rag=payload.use_rag
    )

    assistant_msg = repo.add_message(payload.session_id, "assistant", answer, metadata={"sources": sources})
    return ChatResponse(message=assistant_msg, sources=sources, intermediate_steps=breadcrumbs)
