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
