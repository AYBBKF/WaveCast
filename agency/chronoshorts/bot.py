"""Bot Telegram (long polling) : pilotage de l'agence depuis le téléphone.

Commandes :
  /produce [thème]   lance une production (livraison dans ce chat)
  /status            production en cours ?
  /history           derniers sujets produits
  /costs             coût LLM de la dernière production
  /help
Seul le chat configuré (`TELEGRAM_CHAT_ID`) est autorisé si défini.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import httpx

from .config import get_settings
from .storage import History

log = logging.getLogger("chronoshorts.bot")


class Bot:
    def __init__(self):
        self.s = get_settings()
        if not self.s.telegram_bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN manquant")
        self.base = f"https://api.telegram.org/bot{self.s.telegram_bot_token}"
        self.current: asyncio.Task | None = None
        self.current_label = ""
        self.last_costs: dict | None = None

    async def send(self, chat_id: str, text: str) -> None:
        async with httpx.AsyncClient(timeout=60) as c:
            await c.post(f"{self.base}/sendMessage", json={"chat_id": chat_id, "text": text[:4000]})

    def authorized(self, chat_id: str) -> bool:
        return not self.s.telegram_chat_id or str(chat_id) == str(self.s.telegram_chat_id)

    async def handle(self, chat_id: str, text: str) -> None:
        cmd, _, arg = text.strip().partition(" ")
        cmd = cmd.split("@")[0].lower()
        if cmd == "/produce":
            if self.current and not self.current.done():
                await self.send(chat_id, f"⏳ Une production est déjà en cours : {self.current_label}")
                return
            self.current_label = arg or "sujet libre"
            self.current = asyncio.create_task(self._run(chat_id, arg or None))
            await self.send(chat_id, f"✅ Production lancée ({self.current_label}). Je vous livre ici.")
        elif cmd == "/status":
            if self.current and not self.current.done():
                await self.send(chat_id, f"⏳ En cours : {self.current_label}")
            else:
                await self.send(chat_id, "💤 Aucune production en cours.")
        elif cmd == "/history":
            titles = History(self.s).titles(15)
            await self.send(chat_id, "📚 Derniers sujets :\n" + ("\n".join(f"• {t}" for t in titles) or "aucun"))
        elif cmd == "/costs":
            await self.send(chat_id, json.dumps(self.last_costs or {"info": "aucune production"}, ensure_ascii=False, indent=1))
        else:
            await self.send(chat_id, __doc__ or "")

    async def _run(self, chat_id: str, seed: str | None) -> None:
        from .pipeline import Pipeline
        try:
            p = Pipeline()
            res = await p.produce(seed=seed, notify_chat=chat_id)
            self.last_costs = p.llm.costs.report()
            if not res.delivered:
                await self.send(chat_id, f"ℹ️ Vidéo produite mais non livrée : {res.production.root}")
        except Exception as e:  # noqa: BLE001
            log.exception("production échouée")
            await self.send(chat_id, f"❌ Échec : {e}")

    async def poll(self) -> None:
        offset = 0
        log.info("bot démarré")
        async with httpx.AsyncClient(timeout=70) as c:
            while True:
                try:
                    r = await c.get(f"{self.base}/getUpdates", params={"timeout": 50, "offset": offset})
                    for upd in r.json().get("result", []):
                        offset = upd["update_id"] + 1
                        msg = upd.get("message") or upd.get("channel_post") or {}
                        text = msg.get("text")
                        chat_id = str(msg.get("chat", {}).get("id", ""))
                        if not text or not chat_id:
                            continue
                        if not self.authorized(chat_id):
                            await self.send(chat_id, "⛔ Chat non autorisé.")
                            continue
                        await self.handle(chat_id, text)
                except (httpx.HTTPError, ValueError) as e:
                    log.warning("polling : %s", e)
                    await asyncio.sleep(5)


async def run_bot() -> int:
    await Bot().poll()
    return 0
