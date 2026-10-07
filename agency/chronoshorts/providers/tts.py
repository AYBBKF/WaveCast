"""Synthèse vocale avec horodatage des mots (pour les sous-titres synchronisés).

Fournisseurs :
- `elevenlabs` : endpoint /with-timestamps (alignement caractère → mots).
- `edge`       : edge-tts (gratuit, FR/EN/AR) avec événements WordBoundary.
- `silent`     : silence + horodatage estimé (tests hors ligne).

Aucun fournisseur n'accélère artificiellement la voix : la durée mesurée fait foi
et c'est le script qui s'adapte (voir pipeline.fit_duration).
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from ..config import Settings, get_settings
from ..media.ffmpeg import make_silence, probe_duration

log = logging.getLogger("chronoshorts.tts")

# Débit approximatif d'un narrateur posé (secondes par mot), utilisé uniquement
# pour l'estimation initiale et le mode `silent`.
DEFAULT_SECONDS_PER_WORD = {"fr": 0.42, "en": 0.40, "ar": 0.48}


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class TTSResult:
    audio_path: Path
    duration: float
    words: list[WordTiming] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "audio_path": str(self.audio_path),
            "duration": self.duration,
            "words": [w.__dict__ for w in self.words],
        }

    @classmethod
    def from_json(cls, d: dict) -> "TTSResult":
        return cls(Path(d["audio_path"]), d["duration"], [WordTiming(**w) for w in d["words"]])


def split_words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text.strip()) if w]


class TTSProvider:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def synthesize(self, text: str, out_path: Path) -> TTSResult:
        raise NotImplementedError


# ---------------------------------------------------------------------------
class ElevenLabsTTS(TTSProvider):
    BASE = "https://api.elevenlabs.io/v1"

    async def synthesize(self, text: str, out_path: Path) -> TTSResult:
        s = self.settings
        if not s.elevenlabs_api_key or not s.elevenlabs_voice_id:
            raise RuntimeError("ELEVENLABS_API_KEY et CHRONO_ELEVENLABS_VOICE_ID sont requis")
        url = f"{self.BASE}/text-to-speech/{s.elevenlabs_voice_id}/with-timestamps"
        body = {
            "text": text,
            "model_id": s.elevenlabs_model_id,
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.25,
                               "use_speaker_boost": True},
        }
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(url, json=body, params={"output_format": "mp3_44100_128"},
                                  headers={"xi-api-key": s.elevenlabs_api_key})
            r.raise_for_status()
            data = r.json()
        mp3 = out_path.with_suffix(".mp3")
        mp3.write_bytes(base64.b64decode(data["audio_base64"]))
        words = _words_from_char_alignment(data.get("alignment") or data.get("normalized_alignment") or {})
        await _to_wav(mp3, out_path)
        duration = await probe_duration(out_path)
        if not words:
            words = estimate_word_timings(text, duration)
        return TTSResult(out_path, duration, words)


def _words_from_char_alignment(al: dict) -> list[WordTiming]:
    chars = al.get("characters") or []
    starts = al.get("character_start_times_seconds") or []
    ends = al.get("character_end_times_seconds") or []
    words: list[WordTiming] = []
    cur, w_start, w_end = "", None, None
    for ch, st, en in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append(WordTiming(cur, w_start, w_end))
                cur, w_start = "", None
            continue
        if w_start is None:
            w_start = st
        w_end = en
        cur += ch
    if cur:
        words.append(WordTiming(cur, w_start, w_end))
    return words


# ---------------------------------------------------------------------------
class EdgeTTS(TTSProvider):
    async def synthesize(self, text: str, out_path: Path) -> TTSResult:
        import edge_tts  # dépendance optionnelle

        voice = self.settings.edge_voice()
        mp3 = out_path.with_suffix(".mp3")
        words: list[WordTiming] = []
        communicate = edge_tts.Communicate(text, voice, rate="-5%")
        with open(mp3, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 1e7
                    words.append(WordTiming(chunk["text"], start, start + chunk["duration"] / 1e7))
        await _to_wav(mp3, out_path)
        duration = await probe_duration(out_path)
        if not words:
            words = estimate_word_timings(text, duration)
        return TTSResult(out_path, duration, words)


# ---------------------------------------------------------------------------
class SilentTTS(TTSProvider):
    """Tests hors ligne : piste silencieuse de durée réaliste."""

    async def synthesize(self, text: str, out_path: Path) -> TTSResult:
        spw = DEFAULT_SECONDS_PER_WORD[self.settings.language]
        n = len(split_words(text))
        duration = max(0.6, n * spw)
        await make_silence(out_path, duration)
        return TTSResult(out_path, duration, estimate_word_timings(text, duration))


def estimate_word_timings(text: str, duration: float) -> list[WordTiming]:
    words = split_words(text)
    if not words:
        return []
    total_chars = sum(len(w) + 1 for w in words)
    t = 0.0
    out = []
    for w in words:
        d = duration * (len(w) + 1) / total_chars
        out.append(WordTiming(w, t, t + d))
        t += d
    return out


async def _to_wav(src: Path, dst: Path) -> None:
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ar", "48000", "-ac", "1",
        "-c:a", "pcm_s16le", str(dst),
    )
    if await proc.wait() != 0:
        raise RuntimeError(f"conversion wav échouée : {src}")


def get_tts(settings: Settings | None = None) -> TTSProvider:
    s = settings or get_settings()
    return {"elevenlabs": ElevenLabsTTS, "edge": EdgeTTS, "silent": SilentTTS}[s.tts_provider](s)


def save_result(res: TTSResult, path: Path) -> None:
    path.write_text(json.dumps(res.to_json(), ensure_ascii=False, indent=1))
