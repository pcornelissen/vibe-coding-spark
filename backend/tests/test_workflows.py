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
