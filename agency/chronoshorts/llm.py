"""Couche d'accès à Claude : résolution des modèles, sorties structurées,
recherche web, suivi des coûts.

Un seul point d'entrée : `LLM.structured(...)` qui renvoie une instance Pydantic
validée. Les agents n'appellent jamais le SDK directement.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

import anthropic
from anthropic.lib._parse._transform import transform_schema
from pydantic import BaseModel, TypeAdapter, ValidationError

from .config import Settings, get_settings

log = logging.getLogger("chronoshorts.llm")

T = TypeVar("T", bound=BaseModel)

# Tarifs USD / 1M tokens (entrée, sortie) — pour le rapport de coût.
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-haiku-4-5": (1.0, 5.0),
}

# Modèles dont l'API accepte `thinking: adaptive` + `output_config.effort`.
ADAPTIVE_THINKING_MODELS = {
    "claude-opus-5-5", "claude-opus-5", "claude-opus-4-8", "claude-opus-4-7",
    "claude-opus-4-6", "claude-sonnet-5-5", "claude-sonnet-5", "claude-sonnet-4-6",
    "claude-haiku-5-5", "claude-fable-5-1", "claude-fable-5",
}
# Modèles acceptant la variante de recherche web avec filtrage dynamique.
DYNAMIC_WEB_SEARCH_MODELS = {
    "claude-opus-5-5", "claude-opus-5", "claude-opus-4-8", "claude-opus-4-7",
    "claude-opus-4-6", "claude-sonnet-5-5", "claude-sonnet-5", "claude-sonnet-4-6",
}
# Modèles bénéficiant du repli serveur `fallbacks: "default"`.
SERVER_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-1"}


class RefusalError(RuntimeError):
    """Le modèle a refusé la requête (stop_reason = refusal)."""


@dataclass
class UsageRecord:
    agent: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read: int
    cache_write: int
    seconds: float

    @property
    def cost_usd(self) -> float:
        pin, pout = PRICES.get(self.model, (5.0, 25.0))
        uncached = self.input_tokens
        return (uncached * pin + self.cache_write * pin * 1.25 + self.cache_read * pin * 0.1
                + self.output_tokens * pout) / 1_000_000


@dataclass
class CostTracker:
    records: list[UsageRecord] = field(default_factory=list)

    def add(self, rec: UsageRecord) -> None:
        self.records.append(rec)

    def total_usd(self) -> float:
        return sum(r.cost_usd for r in self.records)

    def report(self) -> dict[str, Any]:
        per_agent: dict[str, dict[str, float]] = {}
        for r in self.records:
            a = per_agent.setdefault(r.agent, {"calls": 0, "input": 0, "output": 0, "usd": 0.0})
            a["calls"] += 1
            a["input"] += r.input_tokens + r.cache_read + r.cache_write
            a["output"] += r.output_tokens
            a["usd"] += r.cost_usd
        return {"total_usd": round(self.total_usd(), 4), "per_agent": per_agent}


class LLMBackend(Protocol):
    director_model: str
    worker_model: str
    costs: CostTracker

    async def structured(
        self,
        *,
        agent: str,
        role: str,
        system: str,
        user: str,
        output_format: type[T],
        web_search: bool = False,
        max_tokens: int = 16000,
    ) -> T: ...


class LLM:
    """Implémentation réelle (SDK Anthropic asynchrone)."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        kwargs: dict[str, Any] = {"max_retries": 4}
        if self.settings.anthropic_api_key:
            kwargs["api_key"] = self.settings.anthropic_api_key
        self.client = anthropic.AsyncAnthropic(**kwargs)
        self.costs = CostTracker()
        self.director_model = self.settings.director_model
        self.worker_model = self.settings.worker_model
        self._resolved = False
        self._sem = asyncio.Semaphore(self.settings.max_concurrency)

    # ------------------------------------------------------------------ modèles
    async def resolve_models(self) -> tuple[str, str]:
        """Vérifie via /v1/models que les modèles configurés existent sur le compte.

        Ne fabrique jamais d'identifiant : si le modèle préféré est absent, on
        prend le premier de la chaîne de repli qui existe réellement.
        """
        if self._resolved:
            return self.director_model, self.worker_model
        if not self.settings.verify_models:
            self._resolved = True
            return self.director_model, self.worker_model
        try:
            available: set[str] = set()
            async for m in self.client.models.list():
                available.add(m.id)
        except anthropic.APIError as e:  # pragma: no cover - dépend du réseau
            log.warning("Impossible de lister les modèles (%s) ; on garde la configuration.", e)
            self._resolved = True
            return self.director_model, self.worker_model

        def pick(preferred: str, chain: list[str], label: str) -> str:
            if preferred in available:
                return preferred
            for alt in chain:
                if alt in available:
                    log.warning("%s : %s indisponible → repli sur %s", label, preferred, alt)
                    return alt
            log.warning("%s : aucun modèle de la chaîne n'est listé ; on tente %s", label, preferred)
            return preferred

        self.director_model = pick(self.settings.director_model, self.settings.director_fallback_models, "Directeur")
        self.worker_model = pick(self.settings.worker_model, self.settings.worker_fallback_models, "Agents")
        self._resolved = True
        log.info("Modèles : directeur=%s, agents=%s", self.director_model, self.worker_model)
        return self.director_model, self.worker_model

    # ------------------------------------------------------------------ appels
    def _model_for(self, role: str) -> str:
        return self.director_model if role == "director" else self.worker_model

    def _request_options(self, model: str, role: str, web_search: bool) -> dict[str, Any]:
        opts: dict[str, Any] = {}
        effort = self.settings.director_effort if role == "director" else self.settings.worker_effort
        if model in ADAPTIVE_THINKING_MODELS:
            opts["thinking"] = {"type": "adaptive"}
            opts["output_config"] = {"effort": effort}
        if web_search and self.settings.web_search:
            tool_type = "web_search_20260209" if model in DYNAMIC_WEB_SEARCH_MODELS else "web_search_20250305"
            opts["tools"] = [{
                "type": tool_type,
                "name": "web_search",
                "max_uses": self.settings.web_search_max_uses,
            }]
        if self.settings.server_side_fallbacks and model in SERVER_FALLBACK_MODELS:
            opts["extra_headers"] = {"anthropic-beta": "server-side-fallback-2026-07-01"}
            opts["extra_body"] = {"fallbacks": "default"}
        return opts

    async def structured(
        self,
        *,
        agent: str,
        role: str,
        system: str,
        user: str,
        output_format: type[T],
        web_search: bool = False,
        max_tokens: int = 16000,
    ) -> T:
        await self.resolve_models()
        model = self._model_for(role)
        opts = self._request_options(model, role, web_search)
        # Sortie structurée : schéma JSON strict dérivé du modèle Pydantic. On n'utilise
        # pas `messages.parse()` car il valide le texte même sur `pause_turn`/`refusal`.
        adapter = TypeAdapter(output_format)
        fmt = {"type": "json_schema", "schema": transform_schema(adapter.json_schema())}
        opts["output_config"] = {**opts.get("output_config", {}), "format": fmt}
        system_blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

        async with self._sem:
            t0 = time.monotonic()
            for _attempt in range(8):  # boucles pause_turn (recherche web)
                try:
                    resp = await self.client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        system=system_blocks,
                        messages=messages,
                        **opts,
                    )
                except anthropic.BadRequestError as e:
                    # Repli robuste : certains comptes/proxys refusent les champs beta.
                    if "fallbacks" in str(e) and "extra_body" in opts:
                        log.warning("Repli serveur refusé par l'API, on continue sans (%s)", e)
                        opts.pop("extra_body", None)
                        opts.pop("extra_headers", None)
                        continue
                    raise
                self._record(agent, model, resp, time.monotonic() - t0)

                if resp.stop_reason == "pause_turn":
                    messages.append({"role": "assistant", "content": _serialize_content(resp.content)})
                    continue
                if resp.stop_reason == "refusal":
                    detail = getattr(resp, "stop_details", None)
                    raise RefusalError(f"{agent}: refus du modèle ({detail})")
                if resp.stop_reason == "max_tokens":
                    raise RuntimeError(f"{agent}: réponse tronquée (max_tokens={max_tokens})")
                texts = [b.text for b in resp.content if b.type == "text" and b.text.strip()]
                if not texts:
                    raise RuntimeError(f"{agent}: aucune sortie structurée reçue")
                try:
                    return adapter.validate_json(texts[-1])
                except ValidationError as e:
                    raise RuntimeError(f"{agent}: sortie JSON invalide — {e}") from e
            raise RuntimeError(f"{agent}: trop de reprises (pause_turn)")

    def _record(self, agent: str, model: str, resp: Any, seconds: float) -> None:
        u = resp.usage
        self.costs.add(UsageRecord(
            agent=agent,
            model=getattr(resp, "model", model) or model,
            input_tokens=u.input_tokens or 0,
            output_tokens=u.output_tokens or 0,
            cache_read=getattr(u, "cache_read_input_tokens", 0) or 0,
            cache_write=getattr(u, "cache_creation_input_tokens", 0) or 0,
            seconds=seconds,
        ))


def _serialize_content(content: list[Any]) -> list[dict[str, Any]]:
    """Convertit les blocs de réponse en paramètres réinjectables (pause_turn)."""
    out = []
    for block in content:
        if hasattr(block, "model_dump"):
            out.append(block.model_dump(exclude_none=True))
        else:  # pragma: no cover
            out.append(json.loads(json.dumps(block, default=str)))
    return out
