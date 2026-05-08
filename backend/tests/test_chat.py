from unittest.mock import AsyncMock, MagicMock, patch

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


async def _fake_stream(user_message, system_prompt):
    for token in ["Hallo", " Welt"]:
        yield token


@pytest.mark.asyncio
async def test_chat_returns_sse(client):
    project = (await client.post("/api/projects", json={"name": "Chat-Test"})).json()
    project_id = project["id"]

    with (
        patch("app.routers.chat.LLMClient") as MockLLM,
        patch("app.routers.chat.QdrantClient") as MockQdrant,
    ):
        mock_llm = MagicMock()
        mock_llm.get_embeddings = AsyncMock(return_value=[[0.1] * 4])
        mock_llm.stream_chat = _fake_stream
        MockLLM.return_value = mock_llm

        mock_qdrant = MagicMock()
        mock_qdrant.search = AsyncMock(return_value=[])
        MockQdrant.return_value = mock_qdrant

        resp = await client.get(f"/api/projects/{project_id}/chat?question=Hallo")

    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "data:" in resp.text
