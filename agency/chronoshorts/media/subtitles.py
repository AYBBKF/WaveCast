"""Sous-titres ASS synchronisés mot à mot (style Shorts : gros, lisibles,
mot courant surligné), compatibles RTL (arabe) via libass."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..providers.tts import WordTiming

STYLES = {
    "moderne": dict(font_size=66, primary="&H00FFFFFF", highlight="&H0000D7FF", outline=4, shadow=0, bold=-1),
    "classique": dict(font_size=60, primary="&H00F4F1EA", highlight="&H00A4D8FF", outline=3, shadow=1, bold=-1),
    "documentaire": dict(font_size=58, primary="&H00F0F0F0", highlight="&H0070D0FF", outline=3, shadow=1, bold=0),
}


@dataclass
class Cue:
    words: list[WordTiming]

    @property
    def start(self) -> float:
        return self.words[0].start

    @property
    def end(self) -> float:
        return self.words[-1].end


def group_cues(words: list[WordTiming], max_words: int = 4, max_chars: int = 26) -> list[Cue]:
    cues: list[Cue] = []
    cur: list[WordTiming] = []
    chars = 0
    for w in words:
        if cur and (len(cur) >= max_words or chars + len(w.word) > max_chars
                    or cur[-1].word.rstrip().endswith((".", "!", "?", "…", "،", "؟", ":"))):
            cues.append(Cue(cur))
            cur, chars = [], 0
        cur.append(w)
        chars += len(w.word) + 1
    if cur:
        cues.append(Cue(cur))
    return cues


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("{", "(").replace("}", ")").replace("\n", " ")


def build_ass(words: list[WordTiming], path: Path, *, width: int, height: int, font: str,
              style: str = "moderne", rtl: bool = False) -> Path:
    st = STYLES.get(style, STYLES["moderne"])
    # Les mots arrivent déjà décalés sur la timeline globale ; on comble les trous
    # entre mots pour que le surlignage ne clignote pas.
    words = [WordTiming(w.word, w.start, w.end) for w in words if w.word.strip()]
    for i in range(len(words) - 1):
        gap = words[i + 1].start - words[i].end
        if 0 < gap < 0.6:
            words[i].end = words[i + 1].start
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{st['font_size']},{st['primary']},{st['highlight']},&H00141414,&H80000000,{st['bold']},0,0,0,100,100,1,0,1,{st['outline']},{st['shadow']},2,80,80,{int(height * 0.25)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for cue in group_cues(words):
        for k, w in enumerate(cue.words):
            end = cue.words[k + 1].start if k + 1 < len(cue.words) else w.end
            if end <= w.start:
                end = w.start + 0.12
            parts = []
            for j, ww in enumerate(cue.words):
                txt = _esc(ww.word)
                parts.append(f"{{\\c{st['highlight']}}}{txt}{{\\c{st['primary']}}}" if j == k else txt)
            sep = " "
            text = sep.join(parts)
            if rtl:
                text = "‫" + text  # RLE : force le rendu droite→gauche
            lines.append(f"Dialogue: 0,{_ts(w.start)},{_ts(end)},Sub,,0,0,0,,{text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_srt(words: list[WordTiming], path: Path) -> Path:
    """SRT (pour YouTube Studio / accessibilité)."""
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{(ms % 3600000) // 60000:02d}:{(ms % 60000) // 1000:02d},{ms % 1000:03d}"
    out = []
    for i, cue in enumerate(group_cues(words, max_words=7, max_chars=42), 1):
        out.append(f"{i}\n{ts(cue.start)} --> {ts(cue.end)}\n{' '.join(w.word for w in cue.words)}\n")
    path.write_text("\n".join(out), encoding="utf-8")
    return path
