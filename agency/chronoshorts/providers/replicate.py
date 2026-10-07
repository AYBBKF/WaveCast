"""Client minimal Replicate (HTTP) : création d'une prédiction, attente, téléchargement."""

from __future__ import annotations

import asyncio
import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger("chronoshorts.replicate")
API = "https://api.replicate.com/v1"


class ReplicateError(RuntimeError):
    pass


class ReplicateClient:
    def __init__(self, token: str):
        if not token:
            raise ReplicateError("REPLICATE_API_TOKEN manquant")
        self.token = token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def run(self, model: str, inputs: dict[str, Any], timeout: float = 900) -> Any:
        """Lance `owner/name` et renvoie `output` (URL ou liste d'URLs)."""
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{API}/models/{model}/predictions",
                json={"input": inputs},
                headers={**self._headers(), "Prefer": "wait=60"},
            )
            if r.status_code >= 400:
                raise ReplicateError(f"{model}: HTTP {r.status_code} {r.text[:400]}")
            pred = r.json()
            get_url = pred["urls"]["get"]
            waited = 0.0
            while pred["status"] not in ("succeeded", "failed", "canceled"):
                await asyncio.sleep(4)
                waited += 4
                if waited > timeout:
                    raise ReplicateError(f"{model}: délai dépassé ({timeout}s)")
                pred = (await client.get(get_url, headers=self._headers())).json()
        if pred["status"] != "succeeded":
            raise ReplicateError(f"{model}: {pred['status']} — {pred.get('error')}")
        return pred["output"]

    @staticmethod
    async def download(url: str, dest: Path) -> Path:
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return dest


def file_to_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def first_url(output: Any) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, list) and output:
        return str(output[0])
    if isinstance(output, dict):
        for k in ("video", "url", "output"):
            if k in output:
                return str(output[k])
    raise ReplicateError(f"sortie inattendue : {output!r}")
