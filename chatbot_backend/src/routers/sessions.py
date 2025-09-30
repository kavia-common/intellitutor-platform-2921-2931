from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.models.schemas import SessionCreateRequest, Session, SessionUpdateRequest
from src.services.repository import repo

router = APIRouter()


@router.post(
    "",
    response_model=Session,
    summary="Create session",
    responses={201: {"description": "Session created"}, 400: {"description": "Invalid data"}},
    status_code=201,
)
def create_session(payload: SessionCreateRequest):
    """
    Create a new tutoring session.

    Parameters:
        payload: SessionCreateRequest with user_id and optional subject/level/goals.

    Returns:
        Session object containing id, user_id, context, and timestamps.
    """
    base_context: Dict[str, Any] = {}
    if payload.subject:
        base_context["subject"] = payload.subject
    if payload.level:
        base_context["level"] = payload.level
    if payload.goals:
        base_context["goals"] = payload.goals
    session = repo.create_session(payload.user_id, context=base_context)
    return session


@router.get(
    "/{session_id}",
    response_model=Session,
    summary="Get session details",
    responses={404: {"description": "Session not found"}},
)
def get_session(session_id: str):
    """
    Get session by id.
    """
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


@router.patch(
    "/{session_id}",
    response_model=Session,
    summary="Update session context",
    responses={404: {"description": "Session not found"}},
)
def update_session(session_id: str, payload: SessionUpdateRequest):
    """
    Merge provided context into the session's context.
    """
    s = repo.update_session_context(session_id, payload.context)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s
