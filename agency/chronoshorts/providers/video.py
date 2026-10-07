"""Animation des scènes : image clé → clip vidéo.

- `replicate` : modèle image→vidéo (Seedance 1 Pro, Kling 2.1, Hailuo 02…).
- `kenburns`  : composition animée locale (zoom + panoramique + respiration de
  lumière) — repli garanti, jamais un simple diaporama.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ..config import Settings, get_settings
from ..media.ffmpeg import probe_duration
from ..media.kenburns import render_kenburns
from .image import ImageResult
from .replicate import ReplicateClient, ReplicateError, file_to_data_uri, first_url

log = logging.getLogger("chronoshorts.video")


@dataclass
class ClipResult:
    path: Path
    duration: float
    method: str  # "replicate:<model>" | "kenburns"


@dataclass
class MotionSpec:
    prompt: str
    negative: str
    seconds: float
    zoom: float = 1.12
    pan: str = "centre"


class VideoProvider:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def animate(self, image: ImageResult, spec: MotionSpec, out_path: Path) -> ClipResult:
        raise NotImplementedError


class KenBurnsVideo(VideoProvider):
    async def animate(self, image: ImageResult, spec: MotionSpec, out_path: Path) -> ClipResult:
        s = self.settings
        await render_kenburns(image.path, out_path, spec.seconds, s.width, s.height, s.fps,
                              zoom=spec.zoom, pan=spec.pan)
        return ClipResult(out_path, await probe_duration(out_path), "kenburns")


class ReplicateVideo(VideoProvider):
    def _inputs(self, model: str, image_ref: str, spec: MotionSpec) -> dict:
        name = model.split("/")[-1]
        # Durées acceptées par les modèles : Seedance 2-12 s (entier), Kling 5|10, Hailuo 6|10.
        if name.startswith("seedance"):
            dur = int(max(3, min(12, round(spec.seconds + 0.5))))
            return {"image": image_ref, "prompt": spec.prompt, "duration": dur,
                    "resolution": self.settings.video_resolution, "aspect_ratio": "9:16",
                    "fps": 24, "camera_fixed": False}
        if name.startswith("kling"):
            return {"start_image": image_ref, "prompt": spec.prompt,
                    "negative_prompt": spec.negative, "duration": 10 if spec.seconds > 5.2 else 5,
                    "mode": "standard"}
        if name.startswith("hailuo") or name.startswith("video-01"):
            return {"first_frame_image": image_ref, "prompt": spec.prompt,
                    "duration": 10 if spec.seconds > 6.2 else 6, "resolution": "1080p",
                    "prompt_optimizer": True}
        # Modèle inconnu : convention la plus répandue.
        return {"image": image_ref, "prompt": spec.prompt, "aspect_ratio": "9:16"}

    async def animate(self, image: ImageResult, spec: MotionSpec, out_path: Path) -> ClipResult:
        s = self.settings
        client = ReplicateClient(s.replicate_api_token)
        image_ref = image.source_url or file_to_data_uri(image.path)
        try:
            out = await client.run(s.replicate_video_model, self._inputs(s.replicate_video_model, image_ref, spec))
            await client.download(first_url(out), out_path)
            return ClipResult(out_path, await probe_duration(out_path), f"replicate:{s.replicate_video_model}")
        except (ReplicateError, OSError) as e:
            if not s.video_fallback_kenburns:
                raise
            log.warning("Vidéo IA échouée (%s) → repli composition animée", e)
            return await KenBurnsVideo(s).animate(image, spec, out_path)


def get_video_provider(settings: Settings | None = None) -> VideoProvider:
    s = settings or get_settings()
    return {"replicate": ReplicateVideo, "kenburns": KenBurnsVideo}[s.video_provider](s)
