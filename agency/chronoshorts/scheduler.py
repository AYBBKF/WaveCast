"""Planificateur : produit `daily_videos` Shorts par jour aux heures `schedule_hours`."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from .config import get_settings

log = logging.getLogger("chronoshorts.scheduler")


def next_run(now: datetime, hours: list[int]) -> datetime:
    candidates = []
    for d in (0, 1):
        for h in sorted(hours):
            t = (now + timedelta(days=d)).replace(hour=h, minute=0, second=0, microsecond=0)
            if t > now:
                candidates.append(t)
    return min(candidates)


async def run_scheduler() -> int:
    from .pipeline import Pipeline
    s = get_settings()
    hours = s.schedule_hours or [9]
    log.info("planificateur : %d vidéo(s)/jour à %s", s.daily_videos, hours)
    while True:
        t = next_run(datetime.now(), hours)
        wait = (t - datetime.now()).total_seconds()
        log.info("prochaine production à %s (dans %.0f min)", t.isoformat(timespec="minutes"), wait / 60)
        await asyncio.sleep(max(1, wait))
        per_slot = max(1, s.daily_videos // len(hours))
        for k in range(per_slot):
            try:
                res = await Pipeline().produce()
                log.info("production %d/%d terminée : %s (livrée=%s)", k + 1, per_slot, res.video, res.delivered)
            except Exception:  # noqa: BLE001
                log.exception("production échouée")
                await asyncio.sleep(60)
