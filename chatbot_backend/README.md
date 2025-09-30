# IntelliTutor Chatbot Backend

FastAPI backend exposing RESTful APIs for sessions, chat, retrieval (RAG), and multi-agent orchestration.

Run locally:
- Python 3.11+
- Install deps: pip install -r requirements.txt
- Optional: copy .env.example to .env and set keys (LLM_API_KEY etc.)
- Start: uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Key endpoints:
- GET / : health
- POST /sessions : create session
- GET /sessions/{session_id} : get session
- PATCH /sessions/{session_id} : update context
- POST /chat : send a message (use_rag optional)
- POST /retrieval/query : query KB
- POST /orchestrator : run multi-agent orchestration on a task

OpenAPI:
- python -m src.api.generate_openapi -> interfaces/openapi.json

Environment:
- See .env.example for required variables.
