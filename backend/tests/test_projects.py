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
