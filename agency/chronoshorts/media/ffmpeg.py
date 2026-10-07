"""Enveloppe FFmpeg/ffprobe (asynchrone) : sondage, normalisation des clips,
enchaînement avec transitions, mixage audio avec ducking, encodage final."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("chronoshorts.ffmpeg")

# Transition storyboard → (nom xfade, durée en secondes)
TRANSITIONS: dict[str, tuple[str, float]] = {
    "cut": ("fade", 0.08),
    "fondu enchaîné": ("fade", 0.5),
    "fondu noir": ("fadeblack", 0.6),
    "volet": ("wipeleft", 0.4),
    "zoom": ("zoomin", 0.45),
    "raccord mouvement": ("smoothleft", 0.35),
}


class FFmpegError(RuntimeError):
    pass


async def run(args: list[str], *, timeout: float = 1800) -> str:
    """Exécute ffmpeg/ffprobe, renvoie stderr (ffmpeg y écrit ses journaux)."""
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise FFmpegError(f"délai dépassé : {' '.join(args[:6])}…")
    if proc.returncode != 0:
        raise FFmpegError(f"{' '.join(args[:3])} a échoué ({proc.returncode}) :\n{err.decode(errors='replace')[-2500:]}")
    return (out or b"").decode(errors="replace") + (err or b"").decode(errors="replace")


def ff(*args: str) -> list[str]:
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]


# ---------------------------------------------------------------------------
# Sondage
# ---------------------------------------------------------------------------
async def probe(path: Path) -> dict:
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise FFmpegError(f"ffprobe {path}: {err.decode(errors='replace')}")
    return json.loads(out)


async def probe_duration(path: Path) -> float:
    info = await probe(path)
    d = info.get("format", {}).get("duration")
    if d is None:
        for s in info.get("streams", []):
            if s.get("duration"):
                d = s["duration"]
                break
    return float(d or 0.0)


@dataclass
class VideoInfo:
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool
    audio_channels: int
    video_codec: str
    audio_codec: str


async def video_info(path: Path) -> VideoInfo:
    info = await probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        raise FFmpegError(f"pas de flux vidéo : {path}")
    num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    return VideoInfo(
        duration=float(info["format"].get("duration", 0)),
        width=int(v["width"]), height=int(v["height"]), fps=fps,
        has_audio=a is not None, audio_channels=int(a["channels"]) if a else 0,
        video_codec=v.get("codec_name", ""), audio_codec=a.get("codec_name", "") if a else "",
    )


async def measure_loudness(path: Path) -> float | None:
    """LUFS intégré (EBU R128) de la piste audio."""
    try:
        log_txt = await run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                             "loudnorm=print_format=json", "-f", "null", "-"])
    except FFmpegError:
        return None
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", log_txt, re.S)
    if not m:
        return None
    try:
        return float(json.loads(m.group(0))["input_i"])
    except (KeyError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Audio utilitaires
# ---------------------------------------------------------------------------
async def make_silence(path: Path, seconds: float) -> None:
    await run(ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{seconds:.3f}",
                 "-c:a", "pcm_s16le", str(path)))


async def synth_ambient_pad(path: Path, seconds: float, freq: float, color: float) -> None:
    """Nappe ambiante douce (accord + respiration lente) — repli sans bibliothèque."""
    f = freq
    expr = (
        f"0.10*sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.05*t))"
        f"+0.06*sin(2*PI*{f * 1.5:.3f}*t)*(0.5+0.5*sin(2*PI*0.037*t+1.3))"
        f"+0.045*sin(2*PI*{f * 2.0:.3f}*t)*(0.5+0.5*sin(2*PI*0.061*t+2.1))"
        f"+{0.02 + 0.03 * color:.3f}*sin(2*PI*{f * 2.997:.3f}*t)*(0.5+0.5*sin(2*PI*0.023*t))"
    )
    await run(ff("-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={seconds:.2f}",
                 "-af", "lowpass=f=900,aecho=0.6:0.4:120|240:0.25|0.12,afade=t=in:d=2,aformat=channel_layouts=stereo",
                 "-c:a", "pcm_s16le", str(path)))


# ---------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------
async def normalize_clip(src: Path, dst: Path, seconds: float, width: int, height: int, fps: int) -> float:
    """Met un clip au format exact (9:16, fps, durée) sans accélérer la narration.

    Si le clip généré est plus court que la scène : ralenti doux (≤ 1.35×) puis
    gel du dernier plan ; s'il est plus long : coupe.
    """
    src_dur = await probe_duration(src)
    filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}",
        f"fps={fps}",
        "format=yuv420p",
    ]
    if src_dur > 0 and src_dur < seconds - 0.05:
        factor = min(1.35, seconds / src_dur)
        filters.insert(0, f"setpts={factor:.4f}*PTS")
        if src_dur * factor < seconds - 0.05:
            filters.append(f"tpad=stop_mode=clone:stop_duration={seconds - src_dur * factor + 0.1:.3f}")
    await run(ff("-i", str(src), "-an", "-vf", ",".join(filters), "-t", f"{seconds:.3f}",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(dst)))
    return await probe_duration(dst)


@dataclass
class TimelineEntry:
    path: Path
    duration: float
    transition: str  # transition de SORTIE de ce clip


async def concat_with_transitions(entries: list[TimelineEntry], dst: Path, fps: int) -> tuple[list[float], float]:
    """Enchaîne les clips avec xfade. Renvoie (offset de début de chaque clip, durée totale)."""
    if not entries:
        raise FFmpegError("timeline vide")
    offsets = [0.0]
    cum = entries[0].duration
    args: list[str] = []
    for e in entries:
        args += ["-i", str(e.path)]
    if len(entries) == 1:
        await run(ff(*args, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps), str(dst)))
        return offsets, cum
    chain: list[str] = []
    prev = "[0:v]"
    frame = 1.0 / fps
    for i in range(1, len(entries)):
        name, d = TRANSITIONS.get(entries[i - 1].transition, ("fade", 0.4))
        d = max(2 * frame, min(d, entries[i - 1].duration / 2, entries[i].duration / 2))
        # xfade exige offset + duration strictement avant la dernière image du
        # flux précédent, sinon la sortie est tronquée : marge de 2 images.
        offset = cum - d - 2 * frame
        out_label = f"[v{i}]" if i < len(entries) - 1 else "[vout]"
        chain.append(f"{prev}[{i}:v]xfade=transition={name}:duration={d:.3f}:offset={offset:.3f}{out_label}")
        offsets.append(offset)
        cum = offset + entries[i].duration
        prev = out_label
    await run(ff(*args, "-filter_complex", ";".join(chain), "-map", "[vout]", "-r", str(fps),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)))
    return offsets, cum


# ---------------------------------------------------------------------------
# Mixage
# ---------------------------------------------------------------------------
async def mix_audio(
    voice_segments: list[tuple[Path, float]],
    music: Path | None,
    ambience: Path | None,
    sfx: list[tuple[Path, float]],
    dst: Path,
    total: float,
    music_db: float = -17.0,
    ambience_db: float = -24.0,
) -> None:
    """Voix placées à leurs offsets, musique sous ducking, ambiance et SFX, loudnorm -14 LUFS."""
    inputs: list[str] = []
    graph: list[str] = []
    idx = 0
    voice_labels = []
    for path, start in voice_segments:
        inputs += ["-i", str(path)]
        ms = int(round(start * 1000))
        graph.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[vo{idx}]")
        voice_labels.append(f"[vo{idx}]")
        idx += 1
    graph.append(f"{''.join(voice_labels)}amix=inputs={len(voice_labels)}:normalize=0:dropout_transition=0,"
                 f"apad=whole_dur={total:.3f},atrim=0:{total:.3f}[voice]")
    mix_inputs = ["[voice_mix]"]
    graph.append("[voice]asplit=2[voice_mix][voice_sc]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        graph.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{total:.3f},"
            f"volume={music_db}dB,afade=t=in:d=1.5,afade=t=out:st={max(0.0, total - 2.5):.3f}:d=2.5[music_raw]"
        )
        graph.append("[music_raw][voice_sc]sidechaincompress=threshold=0.015:ratio=7:attack=25:release=700:makeup=1[music]")
        mix_inputs.append("[music]")
        idx += 1
    else:
        graph.append("[voice_sc]anullsink")
    if ambience:
        inputs += ["-stream_loop", "-1", "-i", str(ambience)]
        graph.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{total:.3f},"
                     f"volume={ambience_db}dB,afade=t=in:d=2,afade=t=out:st={max(0.0, total - 2):.3f}:d=2[amb]")
        mix_inputs.append("[amb]")
        idx += 1
    for path, start in sfx:
        inputs += ["-i", str(path)]
        ms = int(round(start * 1000))
        graph.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-12dB,adelay={ms}|{ms}[sfx{idx}]")
        mix_inputs.append(f"[sfx{idx}]")
        idx += 1
    graph.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:normalize=0:dropout_transition=0,"
                 f"atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    await run(ff(*inputs, "-filter_complex", ";".join(graph), "-map", "[aout]", "-ar", "48000",
                 "-c:a", "pcm_s16le", str(dst)))


async def mux_final(video: Path, audio: Path, subtitles: Path | None, dst: Path,
                    fonts_dir: Path | None = None) -> None:
    vf = []
    if subtitles:
        sub = _escape_filter_path(subtitles)
        vf.append(f"ass=filename='{sub}'" + (f":fontsdir='{_escape_filter_path(fonts_dir)}'" if fonts_dir else ""))
    vf.append("format=yuv420p")
    await run(ff("-i", str(video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
                 "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                 "-profile:v", "high", "-level", "4.1",
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
                 "-shortest", str(dst)))


async def extract_frame(video: Path, at: float, dst: Path) -> None:
    await run(ff("-ss", f"{at:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(dst)))


def _escape_filter_path(p: Path) -> str:
    s = str(p.resolve())
    return s.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
