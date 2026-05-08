import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DocumentFormat(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    MD = "md"
    TXT = "txt"
    XLSX = "xlsx"


class UploadStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class WorkflowStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResultType(str, enum.Enum):
    CONSOLIDATION = "consolidation"
    CONTRADICTION = "contradiction"
    SUMMARY = "summary"


def _utcnow():
    return datetime.now(timezone.utc)


def _new_uuid():
    return uuid.uuid4()


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    workflows: Mapped[list["SparkWorkflow"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    results: Mapped[list["ConsolidationResult"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    filename: Mapped[str] = mapped_column()
    format: Mapped[DocumentFormat] = mapped_column(Enum(DocumentFormat))
    upload_status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus), default=UploadStatus.PENDING)
    spark_document_id: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)

    project: Mapped["Project"] = relationship(back_populates="documents")


class SparkWorkflow(Base):
    __tablename__ = "spark_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    spark_workflow_id: Mapped[str] = mapped_column()
    spark_project_id: Mapped[str] = mapped_column()
    status: Mapped[WorkflowStatus] = mapped_column(Enum(WorkflowStatus), default=WorkflowStatus.RUNNING)
    started_at: Mapped[datetime] = mapped_column(default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    project: Mapped["Project"] = relationship(back_populates="workflows")


class ConsolidationResult(Base):
    __tablename__ = "consolidation_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    query: Mapped[str] = mapped_column(Text)
    result_type: Mapped[ResultType] = mapped_column(Enum(ResultType))
    result_content: Mapped[str] = mapped_column(Text, default="")
    source_documents: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    project: Mapped["Project"] = relationship(back_populates="results")
