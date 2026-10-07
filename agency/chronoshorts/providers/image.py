"""Génération d'images clés (une par scène), 9:16.

- `replicate`   : FLUX 1.1 pro (ou tout modèle acceptant prompt + aspect_ratio).
- `placeholder` : image stylisée générée localement (tests, mode dégradé).
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import Settings, get_settings
from .replicate import ReplicateClient, first_url

log = logging.getLogger("chronoshorts.image")


@dataclass
class ImageResult:
    path: Path
    source_url: str | None  # URL distante réutilisable par le modèle vidéo


class ImageProvider:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def generate(self, prompt: str, negative: str, out_path: Path, seed: int | None = None) -> ImageResult:
        raise NotImplementedError


class ReplicateImage(ImageProvider):
    async def generate(self, prompt: str, negative: str, out_path: Path, seed: int | None = None) -> ImageResult:
        client = ReplicateClient(self.settings.replicate_api_token)
        inputs = {
            "prompt": prompt + ". Vertical 9:16 composition.",
            "aspect_ratio": "9:16",
            "output_format": "png",
            "safety_tolerance": 2,
            "prompt_upsampling": False,
        }
        if seed is not None:
            inputs["seed"] = seed
        out = await client.run(self.settings.replicate_image_model, inputs)
        url = first_url(out)
        await client.download(url, out_path)
        _ensure_portrait(out_path, self.settings.width, self.settings.height)
        return ImageResult(out_path, url)


class PlaceholderImage(ImageProvider):
    """Image 'concept art' procédurale : dégradé chaud, silhouettes, titre de la scène."""

    async def generate(self, prompt: str, negative: str, out_path: Path, seed: int | None = None) -> ImageResult:
        w, h = self.settings.width, self.settings.height
        hsh = int(hashlib.sha1(prompt.encode()).hexdigest()[:8], 16)
        hue = (hsh % 360)
        img = Image.new("RGB", (w, h))
        px = img.load()
        c1 = _hsv(hue, 0.55, 0.35)
        c2 = _hsv((hue + 40) % 360, 0.65, 0.12)
        for y in range(h):
            t = y / h
            col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
            for x in range(w):
                px[x, y] = col
        draw = ImageDraw.Draw(img)
        # "soleil" / source lumineuse
        cx, cy, r = w // 2 + (hsh % 300) - 150, h // 3, 220
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_hsv((hue + 20) % 360, 0.35, 0.95))
        # silhouettes d'architecture
        for i in range(12):
            bw = 90 + (hsh >> (i % 8)) % 160
            bh = 250 + ((hsh * (i + 3)) % 700)
            x0 = (i * 180 + hsh % 97) % (w + 200) - 100
            draw.rectangle((x0, h - bh, x0 + bw, h), fill=_hsv(hue, 0.5, 0.08))
        img = img.filter(ImageFilter.GaussianBlur(1.2))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        except OSError:  # pragma: no cover
            font = ImageFont.load_default()
        words = prompt.split()
        lines, cur = [], ""
        for wd in words:
            if len(cur) + len(wd) > 34:
                lines.append(cur)
                cur = wd
            else:
                cur = f"{cur} {wd}".strip()
            if len(lines) >= 4:
                break
        lines.append(cur)
        for k, line in enumerate(lines[:5]):
            draw.text((60, 160 + k * 56), line, fill=(240, 230, 210), font=font)
        img.save(out_path, "PNG")
        return ImageResult(out_path, None)


def _hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    r, g, b = {0: (c, x, 0), 1: (x, c, 0), 2: (0, c, x), 3: (0, x, c), 4: (x, 0, c), 5: (c, 0, x)}[
        int(h // 60) % 6
    ]
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def _ensure_portrait(path: Path, w: int, h: int) -> None:
    """Recadre/redimensionne en 9:16 exact si le modèle a renvoyé autre chose."""
    img = Image.open(path).convert("RGB")
    if img.size == (w, h):
        return
    ratio = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * ratio), math.ceil(img.height * ratio)), Image.LANCZOS)
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    img.crop((left, top, left + w, top + h)).save(path, "PNG")


def get_image_provider(settings: Settings | None = None) -> ImageProvider:
    s = settings or get_settings()
    return {"replicate": ReplicateImage, "placeholder": PlaceholderImage}[s.image_provider](s)
