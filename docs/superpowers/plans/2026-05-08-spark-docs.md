# Spark Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web application for consolidating technical documentation via SPARK — upload documents, process them, query them, and find contradictions.

**Architecture:** FastAPI backend with SSE streaming + Vue 3 SPA with PrimeVue. The backend orchestrates SPARK (DMS upload, Temporal workflows), Qdrant (vector search), and LiteLLM (LLM calls). PostgreSQL stores project metadata and results.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, Alembic, httpx, sse-starlette — Vue 3, TypeScript, Vite, PrimeVue, Pinia, Vue Router

## Status (Stand: 2026-05-08 16:20)

| Task | Beschreibung | Status |
|------|-------------|--------|
| 1 | Monorepo + Backend-Setup | ✅ Done |
| 2 | DB-Modelle + Alembic | ✅ Done |
| 3 | Pydantic Schemas + Projekt-CRUD | ✅ Done |
| 4 | Vue 3 Frontend-Setup | ✅ Done |
| 5 | TypeScript Types + API Client | ✅ Done |
| 6 | Pinia Store | ✅ Done |
| 7 | [A] Document Upload Endpoint | ✅ Done |
| 8 | [A] ProjectList View | ✅ Done |
| 9 | [B] Chat SSE Endpoint (Dummy) | ✅ Done |
| 10 | [B] Chat UI View | ✅ Done |
| 11 | [A] SPARK Client Service | ✅ Done |
| 12 | [A] Process Endpoint | ✅ Done |
| 13 | [A] ProjectDetail View | ✅ Done |
| 14 | [B] Qdrant + LiteLLM Clients | ✅ Done |
| 15 | [B] Chat → echte Qdrant/LLM | ✅ Done |
| 16 | [B] Consolidation Endpoint | ✅ Done |
| 17 | [B] Consolidation UI | ✅ Done |
| 18 | [A] Workflow Status SSE | ✅ Done |
| 19 | Navigation + Layout Polish | ✅ Done |
| 20 | DB-Migration + E2E-Test | ⏳ Offen — braucht laufendes SPARK/Postgres |

**Nächster Schritt:** Task 20 — PostgreSQL-DB anlegen, Alembic-Migration laufen lassen, End-to-End testen.

---

## Phase 0 — Gemeinsame Basis (zusammen)

> Nach dieser Phase: Sync 0 — Push auf `main`, beide auf gleichem Stand.

### Task 1: Monorepo-Struktur und Backend-Setup

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
node_modules/
dist/
.env
*.db
```

- [ ] **Step 2: Create `backend/pyproject.toml`**

```toml
[project]
name = "spark-docs-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn>=0.34.0",
  "sqlalchemy[asyncio]>=2.0.0",
  "asyncpg>=0.30.0",
  "alembic>=1.15.0",
  "httpx>=0.28.0",
  "pydantic>=2.10.0",
  "pydantic-settings>=2.7.0",
  "python-multipart>=0.0.20",
  "sse-starlette>=2.2.0",
]

[dependency-groups]
dev = [
  "pytest>=8.3.0",
  "pytest-asyncio>=0.25.0",
  "aiosqlite>=0.21.0",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Create `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/sparkdocs"
    test_database_url: str = "sqlite+aiosqlite:///./test.db"
    spark_dms_url: str = "http://127.0.0.1:8002"
    spark_temporal_cli: str = "docker exec spark-workflow-temporal-admin-tools-1 temporal"
    spark_temporal_ui_url: str = "http://127.0.0.1:8080"
    litellm_url: str = "http://127.0.0.1:4000"
    litellm_api_key: str = "y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q"
    litellm_model: str = "gpt-oss-120b"
    litellm_embedding_model: str = "BAAI/bge-m3"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "data_ollama"

    model_config = {"env_prefix": "SPARK_DOCS_"}


settings = Settings()
```

- [ ] **Step 4: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Spark Docs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Create `backend/app/__init__.py` and `backend/tests/__init__.py`**

Both files are empty.

- [ ] **Step 6: Create `backend/tests/conftest.py`**

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 7: Write health check test**

Create `backend/tests/test_health.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 8: Install dependencies and run test**

```bash
cd backend && uv sync && uv run pytest tests/test_health.py -v
```

Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add -A && git commit -m "feat: backend project setup with FastAPI and health endpoint"
```

### Task 2: Database models and migrations

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/database.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/` (directory)

- [ ] **Step 1: Create `backend/app/database.py`**

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session() as session:
        yield session
```

- [ ] **Step 2: Create `backend/app/models.py`**

```python
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
```

- [ ] **Step 3: Initialize Alembic**

```bash
cd backend && uv run alembic init alembic
```

- [ ] **Step 4: Edit `backend/alembic.ini`**

Set `sqlalchemy.url` to empty (we override from env.py):

```ini
sqlalchemy.url =
```

- [ ] **Step 5: Edit `backend/alembic/env.py`**

Replace the generated `env.py` with:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.config import settings
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")


def run_migrations_online():
    connectable = create_engine(sync_url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
```

- [ ] **Step 6: Create initial migration**

```bash
cd backend && uv run alembic revision --autogenerate -m "initial schema"
```

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: database models and Alembic migrations"
```

### Task 3: Pydantic schemas and project CRUD endpoints

**Files:**
- Create: `backend/app/schemas.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/projects.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_projects.py`

- [ ] **Step 1: Create `backend/app/schemas.py`**

```python
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
```

- [ ] **Step 2: Create `backend/app/routers/__init__.py`**

Empty file.

- [ ] **Step 3: Create `backend/app/routers/projects.py`**

```python
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
    return project
```

- [ ] **Step 4: Register router in `backend/app/main.py`**

Replace `backend/app/main.py` with:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import projects

app = FastAPI(title="Spark Docs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Write test for project CRUD**

Create `backend/tests/test_projects.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_and_list_projects(client):
    resp = await client.post("/api/projects", json={"name": "Testprojekt", "description": "Beschreibung"})
    assert resp.status_code == 201
    project = resp.json()
    assert project["name"] == "Testprojekt"
    project_id = project["id"]

    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert any(p["id"] == project_id for p in resp.json())


@pytest.mark.asyncio
async def test_get_project_detail(client):
    resp = await client.post("/api/projects", json={"name": "Detail-Test"})
    project_id = resp.json()["id"]

    resp = await client.get(f"/api/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Detail-Test"
    assert resp.json()["documents"] == []


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    resp = await client.get("/api/projects/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
```

- [ ] **Step 6: Run tests**

```bash
cd backend && uv run pytest tests/test_projects.py -v
```

Expected: 3 tests PASS

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: project CRUD API with schemas and tests"
```

### Task 4: Vue 3 frontend setup with PrimeVue

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router.ts`
- Create: `frontend/src/env.d.ts`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "spark-docs-frontend",
  "private": true,
  "scripts": {
    "dev": "vite --host 127.0.0.1",
    "build": "vue-tsc --noEmit && vite build",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "pinia": "^3.0.0",
    "primevue": "^4.3.0",
    "@primeuix/themes": "^1.0.0",
    "primeicons": "^7.0.0",
    "marked": "^15.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "typescript": "^5.8.0",
    "vite": "^7.0.0",
    "vue-tsc": "^2.2.0"
  }
}
```

- [ ] **Step 2: Create `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Spark Docs</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 3: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "sourceMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
```

- [ ] **Step 4: Create `frontend/vite.config.ts`**

```typescript
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
```

- [ ] **Step 5: Create `frontend/src/env.d.ts`**

```typescript
/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
```

- [ ] **Step 6: Create `frontend/src/router.ts`**

```typescript
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "projects",
      component: () => import("@/views/ProjectList.vue"),
    },
    {
      path: "/projects/:id",
      name: "project-detail",
      component: () => import("@/views/ProjectDetail.vue"),
    },
    {
      path: "/projects/:id/chat",
      name: "project-chat",
      component: () => import("@/views/ProjectChat.vue"),
    },
    {
      path: "/projects/:id/consolidate",
      name: "project-consolidate",
      component: () => import("@/views/ProjectConsolidate.vue"),
    },
  ],
});

export default router;
```

- [ ] **Step 7: Create `frontend/src/main.ts`**

```typescript
import Aura from "@primeuix/themes/aura";
import "primeicons/primeicons.css";
import PrimeVue from "primevue/config";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(router);
app.use(createPinia());
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});
app.mount("#app");
```

- [ ] **Step 8: Create `frontend/src/App.vue`**

```vue
<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <div class="layout">
    <header class="layout-header">
      <h1>Spark Docs</h1>
    </header>
    <main class="layout-main">
      <RouterView />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: var(--p-font-family);
  background: var(--p-surface-ground);
  color: var(--p-text-color);
}

.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  padding: 1rem 2rem;
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
}

.layout-header h1 {
  margin: 0;
  font-size: 1.25rem;
}

.layout-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
```

- [ ] **Step 9: Create placeholder views**

Create `frontend/src/views/ProjectList.vue`:

```vue
<template>
  <div>
    <h2>Projekte</h2>
    <p>Projektliste wird hier angezeigt.</p>
  </div>
</template>
```

Create `frontend/src/views/ProjectDetail.vue`:

```vue
<template>
  <div>
    <h2>Projektdetails</h2>
    <p>Wird geladen...</p>
  </div>
</template>
```

Create `frontend/src/views/ProjectChat.vue`:

```vue
<template>
  <div>
    <h2>Chat</h2>
    <p>Chat-Oberflaeche wird hier angezeigt.</p>
  </div>
</template>
```

Create `frontend/src/views/ProjectConsolidate.vue`:

```vue
<template>
  <div>
    <h2>Konsolidierung</h2>
    <p>Konsolidierungs-Oberflaeche wird hier angezeigt.</p>
  </div>
</template>
```

- [ ] **Step 10: Install dependencies and verify**

```bash
cd frontend && npm install && npm run type-check
```

Expected: No errors.

- [ ] **Step 11: Commit**

```bash
git add -A && git commit -m "feat: Vue 3 frontend setup with PrimeVue, router, and placeholder views"
```

### Task 5: Shared TypeScript types and API client

**Files:**
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`

- [ ] **Step 1: Create `frontend/src/types.ts`**

```typescript
export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  document_count: number;
  latest_workflow_status: "running" | "completed" | "failed" | null;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  format: "pdf" | "docx" | "md" | "txt" | "xlsx";
  upload_status: "pending" | "uploaded" | "processing" | "ready" | "failed";
  spark_document_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: string;
  project_id: string;
  spark_workflow_id: string;
  spark_project_id: string;
  status: "running" | "completed" | "failed";
  started_at: string;
  completed_at: string | null;
}

export interface ProjectDetail extends Project {
  documents: Document[];
  workflows: Workflow[];
}

export type ResultType = "consolidation" | "contradiction" | "summary";

export interface ConsolidationResult {
  id: string;
  project_id: string;
  query: string;
  result_type: ResultType;
  result_content: string;
  source_documents: string[];
  created_at: string;
}
```

- [ ] **Step 2: Create `frontend/src/api.ts`**

```typescript
import type { ConsolidationResult, Project, ProjectDetail, ResultType } from "./types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || response.statusText);
  }
  return response.json();
}

export const api = {
  listProjects: () => request<Project[]>("/projects"),

  createProject: (name: string, description?: string) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),

  getProject: (id: string) => request<ProjectDetail>(`/projects/${id}`),

  uploadDocuments: async (projectId: string, files: File[]) => {
    const results = [];
    for (const file of files) {
      const form = new FormData();
      form.append("file", file);
      const response = await fetch(`${BASE}/projects/${projectId}/documents`, {
        method: "POST",
        body: form,
      });
      if (!response.ok) throw new Error(`Upload failed: ${file.name}`);
      results.push(await response.json());
    }
    return results;
  },

  startProcessing: (projectId: string) =>
    request<void>(`/projects/${projectId}/process`, { method: "POST" }),

  getResults: (projectId: string) =>
    request<ConsolidationResult[]>(`/projects/${projectId}/results`),

  streamChat: (projectId: string, question: string): EventSource => {
    const params = new URLSearchParams({ question });
    return new EventSource(`${BASE}/projects/${projectId}/chat?${params}`);
  },

  streamConsolidate: (projectId: string, resultType: ResultType, query: string): EventSource => {
    const params = new URLSearchParams({ result_type: resultType, query });
    return new EventSource(`${BASE}/projects/${projectId}/consolidate?${params}`);
  },

  workflowStatus: (projectId: string): EventSource => {
    return new EventSource(`${BASE}/projects/${projectId}/workflow-status`);
  },
};
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: shared TypeScript types and API client"
```

### Task 6: Pinia store for projects

**Files:**
- Create: `frontend/src/stores/projects.ts`

- [ ] **Step 1: Create `frontend/src/stores/projects.ts`**

```typescript
import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api";
import type { Project, ProjectDetail } from "@/types";

export const useProjectsStore = defineStore("projects", () => {
  const projects = ref<Project[]>([]);
  const currentProject = ref<ProjectDetail | null>(null);
  const loading = ref(false);

  async function fetchProjects() {
    loading.value = true;
    try {
      projects.value = await api.listProjects();
    } finally {
      loading.value = false;
    }
  }

  async function fetchProject(id: string) {
    loading.value = true;
    try {
      currentProject.value = await api.getProject(id);
    } finally {
      loading.value = false;
    }
  }

  async function createProject(name: string, description?: string) {
    const project = await api.createProject(name, description);
    projects.value.unshift(project);
    return project;
  }

  return { projects, currentProject, loading, fetchProjects, fetchProject, createProject };
});
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: Pinia projects store"
```

> **Sync 0 komplett.** Push auf `main`, beide auf gleichem Stand.

---

## Phase 1 — Grundgeruest (parallel)

> Nach dieser Phase: Sync 1 — Merge, gemeinsam testen, Layout-Konsistenz pruefen.

### Task 7: [Person A] Document upload endpoint

**Files:**
- Create: `backend/app/routers/documents.py`
- Modify: `backend/app/main.py` (add router)
- Create: `backend/tests/test_documents.py`

- [ ] **Step 1: Write test for document upload and listing**

Create `backend/tests/test_documents.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_and_list_documents(client):
    project = (await client.post("/api/projects", json={"name": "Upload-Test"})).json()
    project_id = project["id"]

    resp = await client.post(
        f"/api/projects/{project_id}/documents",
        files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert resp.status_code == 201
    doc = resp.json()
    assert doc["filename"] == "test.pdf"
    assert doc["format"] == "pdf"
    assert doc["upload_status"] == "pending"

    resp = await client.get(f"/api/projects/{project_id}/documents")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_documents.py -v
```

Expected: FAIL (router not registered)

- [ ] **Step 3: Create `backend/app/routers/documents.py`**

```python
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
```

- [ ] **Step 4: Register router in `backend/app/main.py`**

Add after the projects import:

```python
from app.routers import documents
```

Add after `app.include_router(projects.router)`:

```python
app.include_router(documents.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && uv run pytest tests/test_documents.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: document upload and listing endpoints"
```

### Task 8: [Person A] ProjectList view with create dialog

**Files:**
- Modify: `frontend/src/views/ProjectList.vue`

- [ ] **Step 1: Implement ProjectList.vue**

```vue
<script setup lang="ts">
import Button from "primevue/button";
import Card from "primevue/card";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useProjectsStore } from "@/stores/projects";

const store = useProjectsStore();
const router = useRouter();
const showDialog = ref(false);
const newName = ref("");
const newDescription = ref("");

onMounted(() => store.fetchProjects());

async function createProject() {
  if (!newName.value.trim()) return;
  const project = await store.createProject(newName.value.trim(), newDescription.value.trim() || undefined);
  showDialog.value = false;
  newName.value = "";
  newDescription.value = "";
  router.push({ name: "project-detail", params: { id: project.id } });
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem">
      <h2 style="margin: 0">Projekte</h2>
      <Button label="Neues Projekt" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div v-if="store.loading">Laedt...</div>

    <div v-else-if="store.projects.length === 0" style="text-align: center; padding: 3rem; color: var(--p-text-muted-color)">
      <p>Noch keine Projekte vorhanden.</p>
      <Button label="Erstes Projekt anlegen" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem">
      <Card
        v-for="project in store.projects"
        :key="project.id"
        style="cursor: pointer"
        @click="router.push({ name: 'project-detail', params: { id: project.id } })"
      >
        <template #title>{{ project.name }}</template>
        <template #subtitle>{{ project.document_count }} Dokument(e)</template>
        <template #content>
          <p v-if="project.description">{{ project.description }}</p>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showDialog" header="Neues Projekt" modal style="width: 30rem">
      <div style="display: flex; flex-direction: column; gap: 1rem">
        <div>
          <label for="name">Name</label>
          <InputText id="name" v-model="newName" style="width: 100%" autofocus />
        </div>
        <div>
          <label for="desc">Beschreibung (optional)</label>
          <Textarea id="desc" v-model="newDescription" rows="3" style="width: 100%" />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showDialog = false" />
        <Button label="Anlegen" @click="createProject" :disabled="!newName.trim()" />
      </template>
    </Dialog>
  </div>
</template>
```

- [ ] **Step 2: Verify in browser**

```bash
cd frontend && npm run dev
```

Open `http://127.0.0.1:5173`. Verify: project list loads, create dialog opens and works.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: ProjectList view with create project dialog"
```

### Task 9: [Person B] Chat endpoint with SSE (dummy LLM)

**Files:**
- Create: `backend/app/routers/chat.py`
- Modify: `backend/app/main.py` (add router)
- Create: `backend/tests/test_chat.py`

- [ ] **Step 1: Write test for chat endpoint**

Create `backend/tests/test_chat.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_returns_sse(client):
    project = (await client.post("/api/projects", json={"name": "Chat-Test"})).json()
    project_id = project["id"]

    resp = await client.get(f"/api/projects/{project_id}/chat?question=Hallo")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "data:" in resp.text
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_chat.py -v
```

Expected: FAIL

- [ ] **Step 3: Create `backend/app/routers/chat.py`**

```python
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
```

- [ ] **Step 4: Register router in `backend/app/main.py`**

Add:

```python
from app.routers import chat
app.include_router(chat.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && uv run pytest tests/test_chat.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: chat SSE endpoint with dummy LLM response"
```

### Task 10: [Person B] Chat UI view

**Files:**
- Modify: `frontend/src/views/ProjectChat.vue`

- [ ] **Step 1: Implement ProjectChat.vue**

```vue
<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/api";

const route = useRoute();
const projectId = route.params.id as string;

interface Message {
  role: "user" | "assistant";
  content: string;
}

const messages = ref<Message[]>([]);
const input = ref("");
const streaming = ref(false);

function sendMessage() {
  const question = input.value.trim();
  if (!question || streaming.value) return;

  messages.value.push({ role: "user", content: question });
  input.value = "";
  streaming.value = true;

  const assistantMsg: Message = { role: "assistant", content: "" };
  messages.value.push(assistantMsg);

  const source = api.streamChat(projectId, question);

  source.addEventListener("token", (e: MessageEvent) => {
    assistantMsg.content += e.data;
  });

  source.addEventListener("done", () => {
    source.close();
    streaming.value = false;
  });

  source.onerror = () => {
    source.close();
    streaming.value = false;
    if (!assistantMsg.content) {
      assistantMsg.content = "Fehler bei der Verbindung zum Server.";
    }
  };
}
</script>

<template>
  <div style="display: flex; flex-direction: column; height: calc(100vh - 10rem)">
    <h2>Chat</h2>

    <div style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem 0">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :style="{
          alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
          background: msg.role === 'user' ? 'var(--p-primary-color)' : 'var(--p-surface-200)',
          color: msg.role === 'user' ? 'var(--p-primary-contrast-color)' : 'var(--p-text-color)',
          padding: '0.75rem 1rem',
          borderRadius: '0.75rem',
          maxWidth: '70%',
          whiteSpace: 'pre-wrap',
        }"
      >
        {{ msg.content }}<span v-if="streaming && i === messages.length - 1 && msg.role === 'assistant'" class="cursor">|</span>
      </div>
    </div>

    <div style="display: flex; gap: 0.5rem; padding-top: 0.5rem">
      <InputText
        v-model="input"
        placeholder="Frage an die Dokumente..."
        style="flex: 1"
        @keyup.enter="sendMessage"
        :disabled="streaming"
      />
      <Button icon="pi pi-send" @click="sendMessage" :disabled="!input.trim() || streaming" />
    </div>
  </div>
</template>

<style>
.cursor {
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>
```

- [ ] **Step 2: Verify in browser**

Start backend and frontend. Create a project, navigate to `/projects/{id}/chat`, type a question. Verify: dummy SSE response streams in word by word.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: Chat UI view with SSE streaming"
```

> **Sync 1 komplett.** Beide Branches mergen, gemeinsam testen.

---

## Phase 2 — SPARK-Anbindung + echte Daten (parallel)

> Nach dieser Phase: Sync 2 — End-to-End: Dokument hochladen, verarbeiten, abfragen.

### Task 11: [Person A] SPARK client service

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/spark_client.py`
- Create: `backend/tests/test_spark_client.py`

- [ ] **Step 1: Write test for SPARK client**

Create `backend/tests/test_spark_client.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.spark_client import SparkClient


@pytest.fixture
def spark_client():
    return SparkClient(
        dms_url="http://fake-dms:8002",
        temporal_cli="echo",
        temporal_ui_url="http://fake-temporal:8080",
    )


@pytest.mark.asyncio
async def test_upload_document(spark_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "uploadUrl": "http://minio:9000/upload",
        "mimeType": "application/pdf",
    }
    mock_response.raise_for_status = MagicMock()

    confirm_response = AsyncMock()
    confirm_response.status_code = 200
    confirm_response.json.return_value = {"id": "file-123"}
    confirm_response.raise_for_status = MagicMock()

    put_response = AsyncMock()
    put_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        client_instance = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        client_instance.post.side_effect = [mock_response, confirm_response]
        client_instance.put.return_value = put_response

        file_id = await spark_client.upload_document("proj-1", "test.pdf", b"fake-pdf")
        assert file_id == "file-123"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_spark_client.py -v
```

Expected: FAIL

- [ ] **Step 3: Create `backend/app/services/__init__.py`**

Empty file.

- [ ] **Step 4: Create `backend/app/services/spark_client.py`**

```python
import asyncio
import json
import shlex

import httpx

from app.config import settings


class SparkClient:
    def __init__(
        self,
        dms_url: str | None = None,
        temporal_cli: str | None = None,
        temporal_ui_url: str | None = None,
    ):
        self.dms_url = (dms_url or settings.spark_dms_url).rstrip("/")
        self.temporal_cli = temporal_cli or settings.spark_temporal_cli
        self.temporal_ui_url = (temporal_ui_url or settings.spark_temporal_ui_url).rstrip("/")

    async def upload_document(self, project_id: str, filename: str, content: bytes) -> str:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
            payload = {"type": "document", "filename": filename, "projectId": project_id}

            resp = await client.post(f"{self.dms_url}/v2/files/generate-upload-url", json=payload)
            resp.raise_for_status()
            upload_data = resp.json()

            mime_type = upload_data.get("mimeType", "application/octet-stream")
            put_resp = await client.put(
                upload_data["uploadUrl"],
                content=content,
                headers={"Content-Type": mime_type},
            )
            put_resp.raise_for_status()

            confirm = await client.post(f"{self.dms_url}/v2/files/confirm-upload", json=payload)
            confirm.raise_for_status()
            return confirm.json()["id"]

    async def start_workflow(self, project_id: str, file_ids: list[str]) -> str:
        workflow_id = f"sparky-{project_id}"
        payload = {
            "project_id": project_id,
            "file_ids": file_ids,
            "document_types": [],
        }
        args = [
            *shlex.split(self.temporal_cli),
            "workflow", "start",
            "--address", "temporal:7233",
            "--namespace", "default",
            "--workflow-id", workflow_id,
            "--type", "IsolatedFVPWorkflow",
            "--task-queue", "orchestration",
            "--input", json.dumps(payload),
        ]
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        if proc.returncode != 0:
            raise RuntimeError(stderr.decode().strip() or stdout.decode().strip())
        return workflow_id

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.dms_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    def workflow_url(self, workflow_id: str) -> str:
        return f"{self.temporal_ui_url}/namespaces/default/workflows/{workflow_id}"
```

- [ ] **Step 5: Run tests**

```bash
cd backend && uv run pytest tests/test_spark_client.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: SPARK client service for DMS upload and Temporal workflows"
```

### Task 12: [Person A] Process endpoint (upload to SPARK + start workflow)

**Files:**
- Create: `backend/app/routers/workflows.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_workflows.py`

- [ ] **Step 1: Write test for process endpoint**

Create `backend/tests/test_workflows.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_process_creates_workflow(client):
    project = (await client.post("/api/projects", json={"name": "WF-Test"})).json()
    pid = project["id"]

    await client.post(
        f"/api/projects/{pid}/documents",
        files={"file": ("test.pdf", b"%PDF-1.4 content", "application/pdf")},
    )

    with patch("app.routers.workflows.SparkClient") as MockClient:
        instance = AsyncMock()
        instance.upload_document.return_value = "spark-file-1"
        instance.start_workflow.return_value = f"sparky-{pid}"
        MockClient.return_value = instance

        resp = await client.post(f"/api/projects/{pid}/process")
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "running"
        assert data["spark_workflow_id"] == f"sparky-{pid}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_workflows.py -v
```

Expected: FAIL

- [ ] **Step 3: Create `backend/app/routers/workflows.py`**

```python
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
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
```

- [ ] **Step 4: Register router in `backend/app/main.py`**

Add:

```python
from app.routers import workflows
app.include_router(workflows.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && uv run pytest tests/test_workflows.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: process endpoint to upload documents to SPARK and start workflow"
```

### Task 13: [Person A] ProjectDetail view with documents and upload

**Files:**
- Modify: `frontend/src/views/ProjectDetail.vue`

- [ ] **Step 1: Implement ProjectDetail.vue**

```vue
<script setup lang="ts">
import Badge from "primevue/badge";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import FileUpload from "primevue/fileupload";
import Tag from "primevue/tag";
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api";
import { useProjectsStore } from "@/stores/projects";

const route = useRoute();
const router = useRouter();
const store = useProjectsStore();
const projectId = route.params.id as string;
const uploading = ref(false);
const processing = ref(false);

onMounted(() => store.fetchProject(projectId));

const project = computed(() => store.currentProject);

const statusSeverity: Record<string, string> = {
  pending: "warn",
  uploaded: "info",
  processing: "info",
  ready: "success",
  failed: "danger",
};

async function onUpload(event: { files: File[] }) {
  uploading.value = true;
  try {
    await api.uploadDocuments(projectId, event.files);
    await store.fetchProject(projectId);
  } finally {
    uploading.value = false;
  }
}

async function startProcessing() {
  processing.value = true;
  try {
    await api.startProcessing(projectId);
    await store.fetchProject(projectId);
  } finally {
    processing.value = false;
  }
}
</script>

<template>
  <div v-if="project">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem">
      <div>
        <h2 style="margin: 0">{{ project.name }}</h2>
        <p v-if="project.description" style="color: var(--p-text-muted-color); margin: 0.25rem 0 0">
          {{ project.description }}
        </p>
      </div>
      <div style="display: flex; gap: 0.5rem">
        <Button
          label="Chat"
          icon="pi pi-comments"
          severity="secondary"
          @click="router.push({ name: 'project-chat', params: { id: projectId } })"
        />
        <Button
          label="Konsolidierung"
          icon="pi pi-sync"
          severity="secondary"
          @click="router.push({ name: 'project-consolidate', params: { id: projectId } })"
        />
      </div>
    </div>

    <div style="margin-bottom: 1.5rem">
      <h3>Dokumente</h3>
      <FileUpload
        mode="basic"
        :multiple="true"
        accept=".pdf,.docx,.md,.txt,.xlsx"
        :auto="true"
        choose-label="Dokumente hochladen"
        :disabled="uploading"
        @select="onUpload"
      />
    </div>

    <DataTable :value="project.documents" v-if="project.documents.length > 0">
      <Column field="filename" header="Dateiname" />
      <Column field="format" header="Format">
        <template #body="{ data }">
          <Badge :value="data.format" />
        </template>
      </Column>
      <Column field="upload_status" header="Status">
        <template #body="{ data }">
          <Tag :value="data.upload_status" :severity="statusSeverity[data.upload_status]" />
        </template>
      </Column>
    </DataTable>

    <div v-if="project.documents.length > 0" style="margin-top: 1rem">
      <Button
        label="Verarbeitung starten"
        icon="pi pi-play"
        :loading="processing"
        @click="startProcessing"
      />
    </div>

    <div v-if="project.workflows.length > 0" style="margin-top: 1.5rem">
      <h3>Workflows</h3>
      <DataTable :value="project.workflows">
        <Column field="spark_workflow_id" header="Workflow ID" />
        <Column field="status" header="Status">
          <template #body="{ data }">
            <Tag
              :value="data.status"
              :severity="data.status === 'completed' ? 'success' : data.status === 'failed' ? 'danger' : 'info'"
            />
          </template>
        </Column>
        <Column field="started_at" header="Gestartet" />
      </DataTable>
    </div>
  </div>

  <div v-else>Laedt...</div>
</template>
```

- [ ] **Step 2: Verify in browser**

Create a project, upload a PDF, verify table shows the document.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: ProjectDetail view with document upload and workflow status"
```

### Task 14: [Person B] Qdrant and LiteLLM client services

**Files:**
- Create: `backend/app/services/qdrant_client.py`
- Create: `backend/app/services/llm_client.py`
- Create: `backend/tests/test_llm_client.py`

- [ ] **Step 1: Write test for LLM client**

Create `backend/tests/test_llm_client.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.llm_client import LLMClient


@pytest.fixture
def llm_client():
    return LLMClient(url="http://fake-llm:4000", api_key="test-key", model="test-model")


@pytest.mark.asyncio
async def test_stream_chat(llm_client):
    chunks = [
        b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
        b'data: {"choices":[{"delta":{"content":" World"}}]}\n\n',
        b"data: [DONE]\n\n",
    ]

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.aiter_lines = AsyncMock(return_value=iter([c.decode().strip() for c in chunks]))

    with patch("httpx.AsyncClient") as mock_cls:
        client_instance = AsyncMock()
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        client_instance.stream.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        client_instance.stream.return_value.__aexit__ = AsyncMock(return_value=False)

        tokens = []
        async for token in llm_client.stream_chat("Hallo", "Du bist ein Assistent."):
            tokens.append(token)

        assert "Hello" in tokens
        assert " World" in tokens
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/test_llm_client.py -v
```

Expected: FAIL

- [ ] **Step 3: Create `backend/app/services/llm_client.py`**

```python
import json
from typing import AsyncIterator

import httpx

from app.config import settings


class LLMClient:
    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.url = (url or settings.litellm_url).rstrip("/")
        self.api_key = api_key or settings.litellm_api_key
        self.model = model or settings.litellm_model

    async def stream_chat(self, user_message: str, system_prompt: str) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": True,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
            async with client.stream("POST", f"{self.url}/v1/chat/completions", json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    chunk = json.loads(data)
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    if content:
                        yield content

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": settings.litellm_embedding_model, "input": texts}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.url}/v1/embeddings", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
```

- [ ] **Step 4: Create `backend/app/services/qdrant_client.py`**

```python
import httpx

from app.config import settings


class QdrantClient:
    def __init__(self, url: str | None = None, collection: str | None = None):
        self.url = (url or settings.qdrant_url).rstrip("/")
        self.collection = collection or settings.qdrant_collection

    async def search(self, vector: list[float], limit: int = 10, filter_conditions: dict | None = None) -> list[dict]:
        payload: dict = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if filter_conditions:
            payload["filter"] = filter_conditions

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.url}/collections/{self.collection}/points/search",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json().get("result", [])

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.url}/healthz")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
```

- [ ] **Step 5: Run tests**

```bash
cd backend && uv run pytest tests/test_llm_client.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: Qdrant and LiteLLM client services"
```

### Task 15: [Person B] Wire chat endpoint to real Qdrant + LiteLLM

**Files:**
- Modify: `backend/app/routers/chat.py`

- [ ] **Step 1: Replace dummy chat with real implementation**

Replace `backend/app/routers/chat.py`:

```python
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
```

- [ ] **Step 2: Verify manually**

Start SPARK services, upload a document, let it process, then test the chat.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: wire chat endpoint to Qdrant search and LiteLLM streaming"
```

> **Sync 2 komplett.** Merge, End-to-End-Test: Upload, SPARK, Abfrage.

---

## Phase 3 — Konsolidierung + Polish (parallel)

> Nach dieser Phase: Sync 3 — Merge, Gesamttest.

### Task 16: [Person B] Consolidation endpoint

**Files:**
- Create: `backend/app/routers/consolidation.py`
- Create: `backend/app/services/prompts.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create `backend/app/services/prompts.py`**

```python
SUMMARY_PROMPT = """Du bist ein Experte fuer technische Dokumentation. Deine Aufgabe ist es, die Kernaussagen der bereitgestellten Dokumentenauszuege zu einem bestimmten Thema zusammenzufassen.

Regeln:
- Fasse die wichtigsten Punkte zusammen, gruppiert nach Thema.
- Gib zu jeder Aussage die Quelle an (Dokumentname).
- Nutze Markdown-Formatierung.
- Antworte auf Deutsch."""

CONTRADICTION_PROMPT = """Du bist ein Experte fuer technische Dokumentation. Deine Aufgabe ist es, Widersprueche zwischen den bereitgestellten Dokumentenauszuegen zu finden.

Regeln:
- Identifiziere Aussagen, die sich widersprechen oder in Konflikt stehen.
- Zeige fuer jeden Widerspruch: die widersprüchlichen Aussagen, die jeweiligen Quellen, und warum sie im Konflikt stehen.
- Wenn keine Widersprueche gefunden werden, sage das klar.
- Nutze Markdown-Formatierung.
- Antworte auf Deutsch."""

CONSOLIDATION_PROMPT = """Du bist ein Experte fuer technische Dokumentation. Deine Aufgabe ist es, eine konsolidierte Sicht auf das Thema zu erstellen.

Regeln:
- Erstelle ein einheitliches, widerspruchsfreies Dokument aus den bereitgestellten Quellen.
- Kennzeichne Stellen, an denen die Quellen uneins sind, und triff eine begruendete Entscheidung.
- Gib Quellenreferenzen an.
- Nutze Markdown-Formatierung mit klarer Struktur (Ueberschriften, Listen).
- Antworte auf Deutsch."""

PROMPTS = {
    "summary": SUMMARY_PROMPT,
    "contradiction": CONTRADICTION_PROMPT,
    "consolidation": CONSOLIDATION_PROMPT,
}
```

- [ ] **Step 2: Create `backend/app/routers/consolidation.py`**

```python
import json
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
```

- [ ] **Step 3: Register router in `backend/app/main.py`**

Add:

```python
from app.routers import consolidation
app.include_router(consolidation.router)
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: consolidation endpoint with prompt templates and result persistence"
```

### Task 17: [Person B] Consolidation UI view

**Files:**
- Modify: `frontend/src/views/ProjectConsolidate.vue`

- [ ] **Step 1: Implement ProjectConsolidate.vue**

```vue
<script setup lang="ts">
import Button from "primevue/button";
import Card from "primevue/card";
import InputText from "primevue/inputtext";
import SelectButton from "primevue/selectbutton";
import Tag from "primevue/tag";
import { marked } from "marked";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/api";
import type { ConsolidationResult, ResultType } from "@/types";

const route = useRoute();
const projectId = route.params.id as string;

const resultTypeOptions = [
  { label: "Zusammenfassung", value: "summary" },
  { label: "Widersprueche", value: "contradiction" },
  { label: "Konsolidierung", value: "consolidation" },
];

const selectedType = ref<ResultType>("summary");
const query = ref("");
const streaming = ref(false);
const streamContent = ref("");
const savedResults = ref<ConsolidationResult[]>([]);

onMounted(loadResults);

async function loadResults() {
  savedResults.value = await api.getResults(projectId);
}

function startConsolidation() {
  if (!query.value.trim() || streaming.value) return;
  streaming.value = true;
  streamContent.value = "";

  const source = api.streamConsolidate(projectId, selectedType.value, query.value.trim());

  source.addEventListener("token", (e: MessageEvent) => {
    streamContent.value += e.data;
  });

  source.addEventListener("done", () => {
    source.close();
    streaming.value = false;
    loadResults();
  });

  source.onerror = () => {
    source.close();
    streaming.value = false;
  };
}

function renderMarkdown(content: string): string {
  return marked.parse(content) as string;
}

const resultTypeLabels: Record<string, string> = {
  summary: "Zusammenfassung",
  contradiction: "Widerspruchsanalyse",
  consolidation: "Konsolidierung",
};
</script>

<template>
  <div>
    <h2>Konsolidierung</h2>

    <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem">
      <SelectButton v-model="selectedType" :options="resultTypeOptions" option-label="label" option-value="value" />

      <div style="display: flex; gap: 0.5rem">
        <InputText
          v-model="query"
          :placeholder="
            selectedType === 'contradiction'
              ? 'Welches Thema soll auf Widersprueche geprueft werden?'
              : selectedType === 'summary'
                ? 'Welches Thema soll zusammengefasst werden?'
                : 'Was soll konsolidiert werden?'
          "
          style="flex: 1"
          @keyup.enter="startConsolidation"
          :disabled="streaming"
        />
        <Button label="Starten" icon="pi pi-play" @click="startConsolidation" :loading="streaming" :disabled="!query.trim()" />
      </div>
    </div>

    <Card v-if="streamContent" style="margin-bottom: 2rem">
      <template #title>Aktuelles Ergebnis</template>
      <template #content>
        <div v-html="renderMarkdown(streamContent)" />
        <span v-if="streaming" class="cursor">|</span>
      </template>
    </Card>

    <div v-if="savedResults.length > 0">
      <h3>Gespeicherte Ergebnisse</h3>
      <Card v-for="result in savedResults" :key="result.id" style="margin-bottom: 1rem">
        <template #title>
          <Tag :value="resultTypeLabels[result.result_type] || result.result_type" />
          {{ result.query }}
        </template>
        <template #subtitle>{{ new Date(result.created_at).toLocaleString("de-DE") }}</template>
        <template #content>
          <div v-html="renderMarkdown(result.result_content)" />
        </template>
      </Card>
    </div>
  </div>
</template>

<style>
.cursor {
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>
```

- [ ] **Step 2: Verify in browser**

Navigate to `/projects/{id}/consolidate`. Select a type, enter a query, verify streaming works and results are saved.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: Consolidation UI with type selection, streaming, and saved results"
```

### Task 18: [Person A] Workflow status SSE endpoint

**Files:**
- Modify: `backend/app/routers/workflows.py`

- [ ] **Step 1: Add SSE status endpoint to `backend/app/routers/workflows.py`**

Add these imports at the top of the file:

```python
import asyncio

from sse_starlette.sse import EventSourceResponse
```

Add this endpoint at the end of the file:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: workflow status SSE endpoint with polling"
```

> **Sync 3 komplett.** Merge, Gesamttest.

---

## Phase 4 — Feinschliff (zusammen)

### Task 19: Navigation und Layout-Polish

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Add header navigation to App.vue**

Replace `frontend/src/App.vue`:

```vue
<script setup lang="ts">
import Button from "primevue/button";
import { RouterView, useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="layout">
    <header class="layout-header">
      <Button
        text
        style="color: var(--p-primary-contrast-color); font-size: 1.25rem; font-weight: bold"
        @click="router.push('/')"
      >
        Spark Docs
      </Button>
    </header>
    <main class="layout-main">
      <RouterView />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: var(--p-font-family);
  background: var(--p-surface-ground);
  color: var(--p-text-color);
}

.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  padding: 0.5rem 2rem;
  background: var(--p-primary-color);
  display: flex;
  align-items: center;
}

.layout-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add -A && git commit -m "feat: polished app layout with header navigation"
```

### Task 20: Run database migration and final verification

- [ ] **Step 1: Create the sparkdocs database**

```bash
docker exec spark-workflow-postgres-1 psql -U postgres -c "CREATE DATABASE sparkdocs;"
```

- [ ] **Step 2: Run Alembic migration**

```bash
cd backend && uv run alembic upgrade head
```

- [ ] **Step 3: Start backend**

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 4: Start frontend**

```bash
cd frontend && npm run dev
```

- [ ] **Step 5: End-to-end verification**

1. Open `http://127.0.0.1:5173`
2. Create a project
3. Upload a document (PDF or TXT)
4. Start processing — verify workflow is created
5. Navigate to Chat — ask a question — verify SSE streaming
6. Navigate to Consolidation — run a contradiction check — verify streaming and result saved

- [ ] **Step 6: Run all backend tests**

```bash
cd backend && uv run pytest -v
```

Expected: All tests PASS

- [ ] **Step 7: Final commit**

```bash
git add -A && git commit -m "feat: database migration and final integration"
```
