import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm_client import LLMClient


@pytest.fixture
def llm_client():
    return LLMClient(url="http://fake-llm:4000", api_key="test-key", model="test-model")


@pytest.mark.asyncio
async def test_stream_chat(llm_client):
    lines = [
        'data: {"choices":[{"delta":{"content":"Hello"}}]}',
        'data: {"choices":[{"delta":{"content":" World"}}]}',
        "data: [DONE]",
    ]

    async def fake_aiter_lines():
        for line in lines:
            yield line

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.aiter_lines = fake_aiter_lines

    stream_cm = AsyncMock()
    stream_cm.__aenter__ = AsyncMock(return_value=mock_response)
    stream_cm.__aexit__ = AsyncMock(return_value=False)

    client_instance = AsyncMock()
    client_instance.stream = MagicMock(return_value=stream_cm)

    with patch("app.services.llm_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        tokens = []
        async for token in llm_client.stream_chat("Hallo", "Du bist ein Assistent."):
            tokens.append(token)

        assert tokens == ["Hello", " World"]
