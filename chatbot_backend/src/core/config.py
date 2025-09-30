import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment."""

    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"), description="Runtime environment")
    # External LLM config - require user to set these in .env
    default_llm_provider: str = Field(default=os.getenv("LLM_PROVIDER", "openai"))
    llm_api_key: str | None = Field(default=os.getenv("LLM_API_KEY"))
    llm_model: str = Field(default=os.getenv("LLM_MODEL", "gpt-4o-mini"))
    # RAG config
    rag_enabled: bool = Field(default=os.getenv("RAG_ENABLED", "true").lower() == "true")
    rag_top_k: int = Field(default=int(os.getenv("RAG_TOP_K", "4")))
    # Retrieval source (simple file-based index in this starter)
    knowledge_dir: str = Field(default=os.getenv("KNOWLEDGE_DIR", "knowledge_base"))
    # Session storage: in-memory fallback
    persistence: str = Field(default=os.getenv("PERSISTENCE", "memory"))
    # CORS
    cors_allow_origins: str = Field(default=os.getenv("CORS_ALLOW_ORIGINS", "*"))

    class Config:
        arbitrary_types_allowed = True


settings = Settings()
