import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Project

router = APIRouter(prefix="/api/projects", tags=["chat"])


@router.get("/{project_id}/chat")
async def chat(
    project_id: uuid.UUID,
    question: str = Query(min_length=1),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    async def generate():
        dummy = f"Dies ist eine Dummy-Antwort auf die Frage: '{question}'. In Phase 2 wird hier die echte Qdrant-Suche und LLM-Anbindung eingebaut."
        for word in dummy.split():
            yield {"event": "token", "data": word + " "}
            await asyncio.sleep(0.05)
        yield {"event": "done", "data": ""}

    return EventSourceResponse(generate())
