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
