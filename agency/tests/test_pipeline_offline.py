"""Production complète hors ligne : agents factices, TTS silencieux, images
procédurales, composition animée, FFmpeg réel → MP4 vérifié."""

import json
from pathlib import Path

import pytest

from chronoshorts.media.ffmpeg import video_info
from chronoshorts.pipeline import Pipeline
from chronoshorts.providers.telegram import Telegram

from .fake_llm import FakeLLM, NARRATION


class FakeTelegram(Telegram):
    def __init__(self, settings):
        super().__init__(settings)
        self.sent: list[tuple[str, str]] = []

    @property
    def enabled(self) -> bool:
        return True

    async def send_message(self, text, chat_id=None):
        self.sent.append(("message", text))

    async def send_video(self, video, caption, width, height, duration, chat_id=None):
        assert Path(video).exists()
        self.sent.append(("video", caption))
        return {"ok": True}

    async def send_document(self, path, caption="", chat_id=None):
        self.sent.append(("document", str(path)))


@pytest.mark.asyncio
async def test_full_production_offline(offline_settings):
    llm = FakeLLM(approve_script_after=1, approve_visuals=False)
    tg = FakeTelegram(offline_settings)
    p = Pipeline(offline_settings, llm=llm, telegram=tg)
    res = await p.produce(seed="Cordoue")

    assert res.video and res.video.exists()
    info = await video_info(res.video)
    assert (info.width, info.height) == (offline_settings.width, offline_settings.height)
    assert info.has_audio and info.audio_codec == "aac" and info.video_codec == "h264"
    assert 30 < info.duration < 75  # narration silencieuse ~0.42 s/mot + respirations
    assert res.delivered and [k for k, _ in tg.sent].count("video") == 1

    # Boucles de révision : 2 revues de script (1 refus + 1 accord), 2 passes d'animation
    agents = [a for a, _ in llm.calls]
    assert agents.count("scénariste") == 2
    assert agents.count("animateur") == 2
    # directeur : choix du sujet, 2 revues de script, revue visuels, décision finale
    assert agents.count("directeur") == 5
    assert llm.calls.count(("directeur", "FinalDecision")) == 1

    root = res.production.root
    state = json.loads((root / "state.json").read_text())
    assert state["technical_report"]["ratio_ok"] and state["technical_report"]["scenes_rendered"] == len(NARRATION)
    assert state["technical_report"]["scenes_fallback_kenburns"] == len(NARRATION)
    meta = json.loads((root / "metadata.json").read_text())
    assert meta["reconstructed_without_direct_evidence"]  # signalé dans les métadonnées
    assert (root / "subtitles.ass").exists() and (root / "subtitles.srt").exists()
    assert state["costs"]["total_usd"] > 0

    # Reprise : rien n'est recalculé, aucun nouvel appel LLM avant la QA
    n_calls = len(llm.calls)
    res2 = await Pipeline(offline_settings, llm=llm, telegram=tg).produce(resume=root)
    assert res2.video == res.video
    new_calls = [c for c in llm.calls[n_calls:]]
    assert all(c[1] in ("QAReport", "FinalDecision") for c in new_calls)


@pytest.mark.asyncio
async def test_director_can_block_delivery(offline_settings):
    llm = FakeLLM(authorize=False)
    tg = FakeTelegram(offline_settings)
    res = await Pipeline(offline_settings, llm=llm, telegram=tg).produce()
    assert res.video and not res.delivered
    assert not [k for k, _ in tg.sent if k == "video"]
