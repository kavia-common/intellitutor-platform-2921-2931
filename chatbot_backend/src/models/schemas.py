from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentRole(str):
    """Agent role identifier."""


# PUBLIC_INTERFACE
class Message(BaseModel):
    """A single chat message."""
    id: str = Field(..., description="Unique message id")
    session_id: str = Field(..., description="Session id this message belongs to")
    sender: str = Field(..., description="sender id: 'user' or agent name")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")
    metadata: Dict[str, Any] | None = Field(default=None, description="Optional message metadata")


# PUBLIC_INTERFACE
class ChatRequest(BaseModel):
    """Chat request payload."""
    session_id: str = Field(..., description="Existing session id")
    content: str = Field(..., description="User message content")
    agent: Optional[str] = Field(default=None, description="Target agent; orchestrator may override")
    use_rag: Optional[bool] = Field(default=None, description="Force enable/disable RAG for this turn")
    context_overrides: Optional[Dict[str, Any]] = Field(default=None, description="Ephemeral context overrides")


# PUBLIC_INTERFACE
class ChatResponse(BaseModel):
    """Chat response payload containing assistant message and sources."""
    message: Message = Field(..., description="Assistant message")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="RAG source citations")
    intermediate_steps: Optional[List[Dict[str, Any]]] = Field(default=None, description="Agent reasoning breadcrumbs")


# PUBLIC_INTERFACE
class SessionCreateRequest(BaseModel):
    """Create a new tutoring session with optional initial context."""
    user_id: str = Field(..., description="User id creating the session")
    subject: Optional[str] = Field(default=None, description="Subject focus (e.g., Algebra, Biology)")
    level: Optional[str] = Field(default=None, description="Student level (e.g., Grade 10)")
    goals: Optional[List[str]] = Field(default=None, description="Learning goals")


# PUBLIC_INTERFACE
class Session(BaseModel):
    """A session with context and messages."""
    id: str = Field(..., description="Session id")
    user_id: str = Field(..., description="Owner user id")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session-wide context")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="UTC creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="UTC last update time")


# PUBLIC_INTERFACE
class SessionUpdateRequest(BaseModel):
    """Update session context."""
    context: Dict[str, Any] = Field(..., description="Partial or full context to merge")


# PUBLIC_INTERFACE
class RetrievalQuery(BaseModel):
    """Query for the retrieval system."""
    query: str = Field(..., description="Natural language query for retrieval")
    top_k: Optional[int] = Field(default=4, description="Top K documents to return")


# PUBLIC_INTERFACE
class RetrievalDocument(BaseModel):
    """A retrieved document chunk."""
    id: str = Field(..., description="Document id")
    text: str = Field(..., description="Document chunk text")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] | None = Field(default=None, description="Optional metadata")


# PUBLIC_INTERFACE
class OrchestrateRequest(BaseModel):
    """Request to orchestrate multiple agents."""
    session_id: str = Field(..., description="Session id")
    task: str = Field(..., description="Task to solve")
    agents: Optional[List[str]] = Field(default=None, description="Subset of agents to involve")
    use_rag: Optional[bool] = Field(default=None, description="Enable/disable RAG for orchestration")


# PUBLIC_INTERFACE
class OrchestrateResponse(BaseModel):
    """Response from orchestrator."""
    result: Message = Field(..., description="Final aggregated assistant message")
    agents_involved: List[str] = Field(..., description="List of agents that contributed")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Intermediary steps and rationales")
