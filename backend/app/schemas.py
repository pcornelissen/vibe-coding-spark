import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import DocumentFormat, ResultType, UploadStatus, WorkflowStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    latest_workflow_status: WorkflowStatus | None = None

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    filename: str
    format: DocumentFormat
    upload_status: UploadStatus
    spark_document_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    spark_workflow_id: str
    spark_project_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ProjectDetailResponse(ProjectResponse):
    documents: list[DocumentResponse] = []
    workflows: list[WorkflowResponse] = []


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


class ConsolidateRequest(BaseModel):
    result_type: ResultType
    query: str = Field(min_length=1)


class ConsolidationResultResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    query: str
    result_type: ResultType
    result_content: str
    source_documents: list
    created_at: datetime

    model_config = {"from_attributes": True}
