from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from src.routers import chat, sessions, retrieval, orchestrator

# Load environment variables from .env if present
load_dotenv()

app = FastAPI(
    title="IntelliTutor Chatbot Backend",
    description=(
        "RESTful APIs for a multi-agent educational tutor platform. "
        "Provides chat endpoints, session/context management, retrieval-augmented generation (RAG), "
        "and agent orchestration integrating external LLMs. "
        "Theme: Ocean Professional."
    ),
    version="1.0.0",
    contact={
        "name": "IntelliTutor Platform",
        "url": "https://example.com",
        "email": "support@example.com",
    },
    license_info={"name": "MIT"},
    terms_of_service="https://example.com/terms",
    openapi_tags=[
        {"name": "Health", "description": "Service health and metadata"},
        {"name": "Sessions", "description": "Create and manage tutoring sessions and context"},
        {"name": "Chat", "description": "Chat message APIs for tutor conversations"},
        {"name": "Retrieval", "description": "Knowledge base retrieval and RAG utilities"},
        {"name": "Orchestrator", "description": "Multi-agent orchestration APIs"},
    ],
)

# CORS: allow all for dev; in prod, restrict origins via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """
    Returns a simple health status.

    Returns:
        JSON object with message: "Healthy"
    """
    return {"message": "Healthy"}


# Register routers
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(retrieval.router, prefix="/retrieval", tags=["Retrieval"])
app.include_router(orchestrator.router, prefix="/orchestrator", tags=["Orchestrator"])


def custom_openapi():
    """
    Customize OpenAPI schema to include additional metadata.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-theme"] = {
        "name": "Ocean Professional",
        "primary": "#2563EB",
        "secondary": "#F59E0B",
        "background": "#f9fafb",
        "surface": "#ffffff",
        "text": "#111827",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
