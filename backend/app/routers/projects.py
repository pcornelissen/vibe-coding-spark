import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Document, Project, SparkWorkflow
from app.schemas import ProjectCreate, ProjectDetailResponse, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            Project,
            func.count(Document.id).label("document_count"),
        )
        .outerjoin(Document)
        .group_by(Project.id)
        .order_by(Project.created_at.desc())
    )
    rows = (await session.execute(stmt)).all()
    results = []
    for project, doc_count in rows:
        resp = ProjectResponse.model_validate(project)
        resp.document_count = doc_count
        results.append(resp)
    return results


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate, session: AsyncSession = Depends(get_session)):
    project = Project(name=payload.name, description=payload.description)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.documents), selectinload(Project.workflows))
    )
    project = (await session.execute(stmt)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    resp = ProjectDetailResponse.model_validate(project)
    resp.document_count = len(project.documents)
    if project.workflows:
        latest = sorted(project.workflows, key=lambda w: w.started_at, reverse=True)[0]
        resp.latest_workflow_status = latest.status
    return resp
