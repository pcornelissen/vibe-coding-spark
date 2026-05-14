import asyncio
import json
import shlex
from pathlib import Path
from uuid import uuid4

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
        suffix = Path(filename).suffix.lower()
        if suffix not in {".pdf", ".docx"}:
            pdf_filename = f"{Path(filename).stem}.pdf"
            text = content.decode("utf-8", errors="replace")
            content = text_to_pdf_bytes(filename, text)
            filename = pdf_filename

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

    async def get_workflow_status(self, workflow_id: str) -> str:
        args = [
            *shlex.split(self.temporal_cli),
            "workflow", "describe",
            "--address", "temporal:7233",
            "--namespace", "default",
            "--workflow-id", workflow_id,
        ]
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
        output = stdout.decode()
        if "Completed" in output:
            return "completed"
        if "Failed" in output or "Terminated" in output or "TimedOut" in output:
            return "failed"
        return "running"

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.dms_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    def workflow_url(self, workflow_id: str) -> str:
        return f"{self.temporal_ui_url}/namespaces/default/workflows/{workflow_id}"


def text_to_pdf_bytes(title: str, text: str) -> bytes:
    lines = [title, "", *text.splitlines()]
    wrapped_lines: list[str] = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        for start in range(0, len(line), 86):
            wrapped_lines.append(line[start : start + 86])

    content_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    for line in wrapped_lines[:52]:
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _escape_pdf_text(value: str) -> str:
    return (
        value.encode("latin-1", errors="replace")
        .decode("latin-1")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )
