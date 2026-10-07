"""Composition animée locale ("Ken Burns cinématographique") à partir d'une image clé.

Ce n'est pas un diaporama : zoom progressif, panoramique directionnel, respiration
lumineuse, léger grain et vignettage animé. Utilisé quand le modèle vidéo est
indisponible ou échoue sur une scène.
"""

from __future__ import annotations

import math
from pathlib import Path

from .ffmpeg import ff, run


def _pan_expressions(pan: str) -> tuple[str, str]:
    """Expressions zoompan (x, y) selon la direction — `p` = progression 0→1."""
    center_x = "(iw-iw/zoom)/2"
    center_y = "(ih-ih/zoom)/2"
    if pan == "gauche":   # la caméra glisse vers la gauche : on part de la droite
        return "(iw-iw/zoom)*(1-p)", center_y
    if pan == "droite":
        return "(iw-iw/zoom)*p", center_y
    if pan == "haut":
        return center_x, "(ih-ih/zoom)*(1-p)"
    if pan == "bas":
        return center_x, "(ih-ih/zoom)*p"
    return center_x, center_y


async def render_kenburns(image: Path, dst: Path, seconds: float, width: int, height: int,
                          fps: int, zoom: float = 1.12, pan: str = "centre") -> None:
    n = max(2, int(math.ceil(seconds * fps)))
    zoom = max(1.02, min(1.3, zoom))
    # progression adoucie (ease-in-out) pour éviter l'effet mécanique
    p = f"(0.5-0.5*cos(PI*on/{n - 1}))"
    x_expr, y_expr = _pan_expressions(pan)
    x_expr, y_expr = x_expr.replace("p", p), y_expr.replace("p", p)
    # Sur-échantillonnage ×2 pour un zoom sous-pixel sans tremblement.
    up_w, up_h = width * 2, height * 2
    vf = ",".join([
        f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase:flags=lanczos",
        f"crop={up_w}:{up_h}",
        f"zoompan=z='1+({zoom}-1)*{p}':x='{x_expr}':y='{y_expr}':d={n}:s={width}x{height}:fps={fps}",
        # respiration lumineuse très douce + vignette
        "eq=brightness='0.012*sin(2*PI*t/3.7)':saturation=1.04",
        "vignette=angle=PI/4.6",
        "noise=alls=3:allf=t",
        "format=yuv420p",
    ])
    await run(ff("-i", str(image), "-vf", vf, "-t", f"{seconds:.3f}", "-r", str(fps),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(dst)))
