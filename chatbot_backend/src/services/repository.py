from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from src.models.schemas import Session, Message


class InMemoryRepository:
    """Simple in-memory storage for sessions and messages.
    Replace with a real database adapter in production.
    """

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.messages: Dict[str, List[Message]] = {}

    # PUBLIC_INTERFACE
    def create_session(self, user_id: str, context: dict | None = None) -> Session:
        """Create a new session with optional initial context."""
        sid = str(uuid.uuid4())
        session = Session(id=sid, user_id=user_id, context=context or {})
        self.sessions[sid] = session
        self.messages[sid] = []
        return session

    # PUBLIC_INTERFACE
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by id."""
        return self.sessions.get(session_id)

    # PUBLIC_INTERFACE
    def update_session_context(self, session_id: str, new_context: dict) -> Optional[Session]:
        """Merge context into existing session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        session.context.update(new_context)
        session.updated_at = datetime.utcnow()
        self.sessions[session_id] = session
        return session

    # PUBLIC_INTERFACE
    def add_message(self, session_id: str, sender: str, content: str, metadata: dict | None = None) -> Message:
        """Append a message to a session."""
        msg = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender=sender,
            content=content,
            metadata=metadata or {},
        )
        if session_id not in self.messages:
            self.messages[session_id] = []
        self.messages[session_id].append(msg)
        # Update session timestamp
        if session_id in self.sessions:
            self.sessions[session_id].updated_at = msg.timestamp
        return msg

    # PUBLIC_INTERFACE
    def get_messages(self, session_id: str, limit: int | None = None) -> List[Message]:
        """Return messages for a session (optionally truncated)."""
        msgs = self.messages.get(session_id, [])
        if limit is not None:
            try:
                n = int(limit)
            except Exception:
                n = 0
            if n > 0:
                return msgs[-n:]
        return list(msgs)


# Singleton repository instance
repo = InMemoryRepository()
