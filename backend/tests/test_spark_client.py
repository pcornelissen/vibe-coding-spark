import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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
    generate_resp = MagicMock()
    generate_resp.status_code = 200
    generate_resp.json.return_value = {
        "uploadUrl": "http://minio:9000/upload",
        "mimeType": "application/pdf",
    }
    generate_resp.raise_for_status = MagicMock()

    confirm_resp = MagicMock()
    confirm_resp.status_code = 200
    confirm_resp.json.return_value = {"id": "file-123"}
    confirm_resp.raise_for_status = MagicMock()

    put_resp = MagicMock()
    put_resp.raise_for_status = MagicMock()

    client_instance = AsyncMock()
    client_instance.post.side_effect = [generate_resp, confirm_resp]
    client_instance.put.return_value = put_resp

    with patch("app.services.spark_client.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        file_id = await spark_client.upload_document("proj-1", "test.pdf", b"fake-pdf")
        assert file_id == "file-123"
        assert client_instance.post.call_count == 2
        client_instance.put.assert_called_once()
