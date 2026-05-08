import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Document, Project
from app.services.llm_client import LLMClient
from app.services.qdrant_client import QdrantClient

router = APIRouter(prefix="/api/projects", tags=["chat"])

SYSTEM_PROMPT = """Du bist ein Assistent fuer technische Dokumentation. Du beantwortest Fragen basierend auf den bereitgestellten Dokumentenauszuegen.

Regeln:
- Beantworte nur auf Basis der bereitgestellten Kontextinformationen.
- Wenn die Antwort nicht im Kontext zu finden ist, sage das ehrlich.
- Gib Quellenreferenzen an (Dokumentname und Abschnitt), wenn moeglich.
- Antworte auf Deutsch, es sei denn, der Nutzer fragt auf Englisch."""


@router.get("/{project_id}/chat")
async def chat(
    project_id: uuid.UUID,
    question: str = Query(min_length=1),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    llm = LLMClient()
    qdrant = QdrantClient()

    try:
        embeddings = await llm.get_embeddings([question])
        query_vector = embeddings[0]
    except Exception:
        async def error_stream():
            yield {"event": "token", "data": "Fehler: Konnte keine Embeddings erzeugen. Ist LiteLLM erreichbar?"}
            yield {"event": "done", "data": ""}
        return EventSourceResponse(error_stream())

    try:
        results = await qdrant.search(query_vector, limit=8)
    except Exception:
        results = []

    context_parts = []
    for i, result in enumerate(results, 1):
        payload = result.get("payload", {})
        text = payload.get("text", payload.get("content", ""))
        source = payload.get("source", payload.get("filename", f"Quelle {i}"))
        context_parts.append(f"[{source}]: {text}")

    context = "\n\n---\n\n".join(context_parts) if context_parts else "Kein Kontext verfuegbar."
    user_message = f"Kontext:\n{context}\n\nFrage: {question}"

    async def generate():
        try:
            async for token in llm.stream_chat(user_message, SYSTEM_PROMPT):
                yield {"event": "token", "data": token}
        except Exception as e:
            yield {"event": "token", "data": f"\n\nFehler beim LLM-Aufruf: {e}"}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(generate())
