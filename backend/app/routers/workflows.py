import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Document, Project, SparkWorkflow, UploadStatus, WorkflowStatus
from app.schemas import WorkflowResponse
from app.services.spark_client import SparkClient

router = APIRouter(prefix="/api/projects", tags=["workflows"])


@router.post("/{project_id}/process", response_model=WorkflowResponse, status_code=201)
async def start_processing(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    docs_stmt = select(Document).where(Document.project_id == project_id)
    documents = (await session.execute(docs_stmt)).scalars().all()
    if not documents:
        raise HTTPException(status_code=400, detail="No documents in project")

    spark = SparkClient()
    spark_project_id = str(project_id)

    file_ids = []
    for doc in documents:
        file_id = await spark.upload_document(spark_project_id, doc.filename, b"placeholder")
        file_ids.append(file_id)
        doc.upload_status = UploadStatus.UPLOADED
        doc.spark_document_id = file_id

    workflow_id = await spark.start_workflow(spark_project_id, file_ids)

    workflow = SparkWorkflow(
        project_id=project_id,
        spark_workflow_id=workflow_id,
        spark_project_id=spark_project_id,
        status=WorkflowStatus.RUNNING,
    )
    session.add(workflow)

    for doc in documents:
        doc.upload_status = UploadStatus.PROCESSING

    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.get("/{project_id}/workflow-status")
async def workflow_status(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    async def generate():
        for _ in range(60):
            stmt = (
                select(SparkWorkflow)
                .where(SparkWorkflow.project_id == project_id)
                .order_by(SparkWorkflow.started_at.desc())
                .limit(1)
            )
            await session.expire_all()
            workflow = (await session.execute(stmt)).scalar_one_or_none()

            if workflow:
                data = {
                    "workflow_id": workflow.spark_workflow_id,
                    "status": workflow.status.value,
                    "started_at": workflow.started_at.isoformat(),
                    "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                }
                yield {"event": "status", "data": json.dumps(data)}

                if workflow.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
                    yield {"event": "done", "data": workflow.status.value}
                    return
            else:
                yield {"event": "status", "data": json.dumps({"status": "no_workflow"})}

            await asyncio.sleep(5)

        yield {"event": "done", "data": "timeout"}

    return EventSourceResponse(generate())
