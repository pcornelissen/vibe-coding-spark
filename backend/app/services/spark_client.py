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
