"""Bibliothèque musicale / ambiances locales libres de droits.

Déposez des fichiers audio (mp3/wav/ogg) dans `assets/music/` et `assets/ambience/`
et décrivez-les dans `assets/library.json` :

{
  "music":    [{"file": "music/desert_dawn.mp3", "moods": ["contemplatif", "mystérieux"]}],
  "ambience": [{"file": "ambience/market.ogg",   "tags": ["marché", "foule"]}],
  "sfx":      [{"file": "sfx/bell.wav",          "tags": ["cloche"]}]
}

Si la bibliothèque est vide, une nappe ambiante est synthétisée (FFmpeg) pour
que la production ne soit jamais bloquée. Utilisez uniquement des pistes dont la
licence autorise YouTube (CC0, CC-BY avec crédit, YouTube Audio Library…).
"""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path

from ..config import Settings, get_settings
from ..media.ffmpeg import synth_ambient_pad

log = logging.getLogger("chronoshorts.music")

MOOD_FREQS = {  # fondamentale (Hz) et "couleur" de la nappe synthétisée
    "épique": (55.0, 0.35), "mystérieux": (49.0, 0.5), "contemplatif": (65.4, 0.25),
    "tendu": (46.2, 0.6), "chaleureux": (73.4, 0.2), "mélancolique": (58.3, 0.4),
}


class MusicLibrary:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.root = Path(self.settings.assets_dir)
        self.manifest = self._load()

    def _load(self) -> dict:
        p = self.root / "library.json"
        if p.exists():
            try:
                return json.loads(p.read_text())
            except json.JSONDecodeError:
                log.warning("library.json invalide, ignoré")
        return {"music": [], "ambience": [], "sfx": []}

    def _pick(self, kind: str, wanted: list[str]) -> Path | None:
        entries = [e for e in self.manifest.get(kind, []) if (self.root / e["file"]).exists()]
        if not entries:
            return None
        key = "moods" if kind == "music" else "tags"
        scored = [(len(set(e.get(key, [])) & set(wanted)), e) for e in entries]
        best = max(s for s, _ in scored)
        candidates = [e for s, e in scored if s == best]
        return self.root / random.choice(candidates)["file"]

    async def music_for(self, mood: str, seconds: float, out_dir: Path) -> tuple[Path, str]:
        p = self._pick("music", [mood])
        if p:
            return p, f"bibliothèque:{p.name}"
        freq, color = MOOD_FREQS.get(mood, (55.0, 0.35))
        out = out_dir / "music_synth.wav"
        await synth_ambient_pad(out, seconds + 2, freq, color)
        return out, "nappe synthétisée (aucune piste en bibliothèque)"

    def ambience_for(self, tags: list[str]) -> Path | None:
        return self._pick("ambience", tags)

    def sfx_for(self, tag: str) -> Path | None:
        return self._pick("sfx", [tag])
