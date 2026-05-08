import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Document, DocumentFormat, Project
from app.schemas import DocumentResponse

router = APIRouter(prefix="/api", tags=["documents"])

FORMAT_MAP = {
    ".pdf": DocumentFormat.PDF,
    ".docx": DocumentFormat.DOCX,
    ".md": DocumentFormat.MD,
    ".txt": DocumentFormat.TXT,
    ".xlsx": DocumentFormat.XLSX,
}


@router.post("/projects/{project_id}/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    suffix = Path(file.filename or "").suffix.lower()
    doc_format = FORMAT_MAP.get(suffix)
    if not doc_format:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {suffix}")

    content = await file.read()
    doc = Document(
        project_id=project_id,
        filename=file.filename or "unknown",
        format=doc_format,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


@router.get("/projects/{project_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stmt = select(Document).where(Document.project_id == project_id).order_by(Document.created_at)
    docs = (await session.execute(stmt)).scalars().all()
    return docs


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
