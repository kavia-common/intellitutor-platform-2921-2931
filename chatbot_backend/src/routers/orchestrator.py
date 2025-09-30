from fastapi import APIRouter, HTTPException

from src.models.schemas import OrchestrateRequest, OrchestrateResponse, Message
from src.services.repository import repo
from src.services.agents import orchestrate as run_orchestrator

router = APIRouter()


@router.post(
    "",
    response_model=OrchestrateResponse,
    summary="Orchestrate multi-agent solution",
    responses={200: {"description": "Orchestrated response"}, 404: {"description": "Session not found"}},
)
async def orchestrate(payload: OrchestrateRequest):
    """
    Run multi-agent orchestration over a task with optional RAG synthesis.

    Parameters:
        payload: OrchestrateRequest with session_id, task, optional agents subset, and use_rag flag.

    Returns:
        OrchestrateResponse with final synthesized assistant message, agents involved, and step details.
    """
    session = repo.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    context = dict(session.context)
    final, steps, sources = await run_orchestrator(payload.task, context, payload.agents, payload.use_rag)

    assistant_msg = repo.add_message(payload.session_id, "assistant", final, metadata={"sources": sources})
    result_msg = Message(
        id=assistant_msg.id,
        session_id=assistant_msg.session_id,
        sender=assistant_msg.sender,
        content=assistant_msg.content,
        timestamp=assistant_msg.timestamp,
        metadata=assistant_msg.metadata,
    )

    return OrchestrateResponse(
        result=result_msg,
        agents_involved=[s.get("agent") for s in steps],
        steps=steps,
    )
