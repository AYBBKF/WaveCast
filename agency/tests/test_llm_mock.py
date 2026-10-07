"""Vérifie la forme exacte des requêtes envoyées à l'API Claude (transport HTTP
simulé) : sorties structurées, thinking adaptatif, effort, repli serveur,
recherche web et reprise après `pause_turn`."""

import json

import httpx2 as httpx
import pytest

from chronoshorts import schemas as S
from chronoshorts.config import Settings
from chronoshorts.llm import LLM, RefusalError


def _message(payload: dict, stop_reason: str = "end_turn", model: str = "claude-haiku-5-5") -> dict:
    return {
        "id": "msg_1", "type": "message", "role": "assistant", "model": model,
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "stop_reason": stop_reason, "stop_sequence": None,
        "usage": {"input_tokens": 120, "output_tokens": 40,
                  "cache_read_input_tokens": 0, "cache_creation_input_tokens": 100},
    }


def _llm(handler) -> LLM:
    s = Settings(_env_file=None, verify_models=False, anthropic_api_key="sk-test")
    llm = LLM(s)
    llm.client = llm.client.with_options(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    return llm


@pytest.mark.asyncio
async def test_structured_request_shape_director():
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json=_message(
            {"authorize_telegram": True, "verdict": "ok", "improvements_for_next_time": []},
            model="claude-opus-5-5"))

    llm = _llm(handler)
    out = await llm.structured(agent="directeur", role="director", system="sys", user="u",
                               output_format=S.FinalDecision, web_search=True)
    assert out.authorize_telegram is True
    body = json.loads(seen[0].content)
    assert body["model"] == "claude-opus-5-5"
    assert body["thinking"] == {"type": "adaptive"}
    assert body["output_config"]["effort"] == "high"
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert body["output_config"]["format"]["schema"]["properties"]["verdict"]
    assert body["fallbacks"] == "default"
    assert "server-side-fallback-2026-07-01" in seen[0].headers["anthropic-beta"]
    assert body["tools"][0]["type"] == "web_search_20260209"
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"}
    rec = llm.costs.records[0]
    assert rec.model == "claude-opus-5-5" and rec.cache_write == 100 and llm.costs.total_usd() > 0


@pytest.mark.asyncio
async def test_pause_turn_is_resumed_and_refusal_raises():
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(200, json=_message({}, stop_reason="pause_turn"))
        body = json.loads(req.content)
        assert body["messages"][1]["role"] == "assistant"  # contenu réinjecté
        return httpx.Response(200, json=_message({"passed": True, "score": 90, "issues": [], "summary": "ok"}))

    llm = _llm(handler)
    rep = await llm.structured(agent="historien", role="worker", system="s", user="u",
                               output_format=S.QAReport, web_search=True)
    assert rep.passed and calls == 2

    def refusing(req: httpx.Request) -> httpx.Response:
        m = _message({}, stop_reason="refusal")
        m["stop_details"] = {"type": "refusal", "category": "cyber", "explanation": "x"}
        return httpx.Response(200, json=m)

    with pytest.raises(RefusalError):
        await _llm(refusing).structured(agent="a", role="worker", system="s", user="u", output_format=S.QAReport)


@pytest.mark.asyncio
async def test_models_resolution_falls_back_to_existing_ids():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/v1/models"):
            return httpx.Response(200, json={"data": [{"id": "claude-opus-4-8", "type": "model",
                                                      "display_name": "x", "created_at": "2026-01-01T00:00:00Z"},
                                                     {"id": "claude-haiku-5-5", "type": "model",
                                                      "display_name": "y", "created_at": "2026-01-01T00:00:00Z"}],
                                            "has_more": False, "first_id": None, "last_id": None})
        raise AssertionError(req.url)

    s = Settings(_env_file=None, verify_models=True, anthropic_api_key="sk-test")
    llm = LLM(s)
    llm.client = llm.client.with_options(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    d, w = await llm.resolve_models()
    assert (d, w) == ("claude-opus-4-8", "claude-haiku-5-5")
