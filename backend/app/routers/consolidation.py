import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import ConsolidationResult, Project, ResultType
from app.schemas import ConsolidationResultResponse
from app.services.llm_client import LLMClient
from app.services.prompts import PROMPTS
from app.services.qdrant_client import QdrantClient

router = APIRouter(prefix="/api/projects", tags=["consolidation"])


@router.get("/{project_id}/consolidate")
async def consolidate(
    project_id: uuid.UUID,
    result_type: str = Query(pattern="^(summary|contradiction|consolidation)$"),
    query: str = Query(min_length=1),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    system_prompt = PROMPTS[result_type]
    llm = LLMClient()
    qdrant = QdrantClient()

    try:
        embeddings = await llm.get_embeddings([query])
        results = await qdrant.search(embeddings[0], limit=15)
    except Exception:
        results = []

    context_parts = []
    source_docs = set()
    for result in results:
        payload = result.get("payload", {})
        text = payload.get("text", payload.get("content", ""))
        source = payload.get("source", payload.get("filename", "Unbekannt"))
        context_parts.append(f"[{source}]: {text}")
        doc_id = payload.get("document_id")
        if doc_id:
            source_docs.add(doc_id)

    context = "\n\n---\n\n".join(context_parts) if context_parts else "Kein Kontext verfuegbar."
    user_message = f"Kontext:\n{context}\n\nAufgabe: {query}"

    collected_content: list[str] = []

    async def generate():
        try:
            async for token in llm.stream_chat(user_message, system_prompt):
                collected_content.append(token)
                yield {"event": "token", "data": token}
        except Exception as e:
            yield {"event": "token", "data": f"\n\nFehler: {e}"}

        full_content = "".join(collected_content)
        result_enum = ResultType(result_type.upper())
        result_obj = ConsolidationResult(
            project_id=project_id,
            query=query,
            result_type=result_enum,
            result_content=full_content,
            source_documents=list(source_docs),
        )
        session.add(result_obj)
        await session.commit()

        yield {"event": "done", "data": str(result_obj.id)}

    return EventSourceResponse(generate())


@router.get("/{project_id}/results", response_model=list[ConsolidationResultResponse])
async def list_results(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stmt = (
        select(ConsolidationResult)
        .where(ConsolidationResult.project_id == project_id)
        .order_by(ConsolidationResult.created_at.desc())
    )
    return (await session.execute(stmt)).scalars().all()
