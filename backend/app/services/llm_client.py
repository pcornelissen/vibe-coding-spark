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
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
            resp = await client.post(f"{self.url}/v1/embeddings", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
