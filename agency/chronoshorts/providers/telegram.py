"""Livraison Telegram (Bot API) : vidéo finale + métadonnées."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from ..config import Settings, get_settings

log = logging.getLogger("chronoshorts.telegram")


class Telegram:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.base = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}"

    @property
    def enabled(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    async def send_message(self, text: str, chat_id: str | None = None) -> None:
        if not self.settings.telegram_bot_token:
            return
        async with httpx.AsyncClient(timeout=60) as c:
            for chunk in _chunks(text, 4000):
                r = await c.post(f"{self.base}/sendMessage",
                                 json={"chat_id": chat_id or self.settings.telegram_chat_id, "text": chunk})
                r.raise_for_status()

    async def send_video(self, video: Path, caption: str, width: int, height: int,
                         duration: float, chat_id: str | None = None) -> dict:
        if not self.enabled and not chat_id:
            raise RuntimeError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID manquants")
        async with httpx.AsyncClient(timeout=600) as c:
            with open(video, "rb") as f:
                r = await c.post(
                    f"{self.base}/sendVideo",
                    data={
                        "chat_id": chat_id or self.settings.telegram_chat_id,
                        "caption": caption[:1024],
                        "width": width, "height": height,
                        "duration": int(round(duration)),
                        "supports_streaming": "true",
                    },
                    files={"video": (video.name, f, "video/mp4")},
                )
            r.raise_for_status()
            return r.json()

    async def send_document(self, path: Path, caption: str = "", chat_id: str | None = None) -> None:
        async with httpx.AsyncClient(timeout=300) as c:
            with open(path, "rb") as f:
                r = await c.post(
                    f"{self.base}/sendDocument",
                    data={"chat_id": chat_id or self.settings.telegram_chat_id, "caption": caption[:1024]},
                    files={"document": (path.name, f)},
                )
            r.raise_for_status()


def _chunks(text: str, n: int) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)] or [""]
