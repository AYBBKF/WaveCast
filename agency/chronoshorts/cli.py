"""Interface en ligne de commande.

  chronoshorts produce [--seed "thème"] [--resume DIR]
  chronoshorts bot            # bot Telegram (commandes /produce, /status…)
  chronoshorts schedule       # production quotidienne automatique
  chronoshorts check          # vérifie l'environnement (ffmpeg, clés, modèles)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
import sys
from pathlib import Path

from .config import get_settings


def _logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def _produce(args: argparse.Namespace) -> int:
    from .pipeline import Pipeline

    p = Pipeline()
    res = await p.produce(seed=args.seed, resume=Path(args.resume) if args.resume else None)
    print(f"\nVidéo : {res.video}\nLivrée : {res.delivered}\nCoût LLM ≈ {res.cost_usd:.3f} $")
    if res.decision:
        print(f"Directeur : {res.decision.verdict}")
    return 0 if res.video else 1


async def _check() -> int:
    s = get_settings()
    ok = True
    for tool in ("ffmpeg", "ffprobe"):
        print(f"{tool:10s} {'OK' if shutil.which(tool) else 'MANQUANT'}")
        ok &= bool(shutil.which(tool))
    print(f"Anthropic  {'clé présente' if s.anthropic_api_key else 'ANTHROPIC_API_KEY manquante'}")
    print(f"TTS        {s.tts_provider}" + ("" if s.tts_provider != "elevenlabs" or s.elevenlabs_api_key else "  (clé manquante)"))
    print(f"Images     {s.image_provider}" + ("" if s.image_provider != "replicate" or s.replicate_api_token else "  (token manquant)"))
    print(f"Vidéo      {s.video_provider} ({s.replicate_video_model})")
    print(f"Telegram   {'configuré' if s.telegram_bot_token and s.telegram_chat_id else 'non configuré'}")
    print(f"Langue     {s.language} · cible {s.target_duration_min:.0f}-{s.target_duration_max:.0f} s")
    if s.anthropic_api_key:
        from .llm import LLM
        llm = LLM(s)
        d, w = await llm.resolve_models()
        print(f"Modèles    directeur={d}  agents={w}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="chronoshorts", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("produce", help="produire un Short")
    p.add_argument("--seed", help="thème ou contrainte éditoriale (optionnel)")
    p.add_argument("--resume", help="reprendre une production (dossier)")
    sub.add_parser("bot", help="lancer le bot Telegram")
    sub.add_parser("schedule", help="lancer le planificateur quotidien")
    sub.add_parser("check", help="vérifier l'environnement")
    args = ap.parse_args(argv)
    _logging(args.verbose)

    if args.cmd == "produce":
        return asyncio.run(_produce(args))
    if args.cmd == "check":
        return asyncio.run(_check())
    if args.cmd == "bot":
        from .bot import run_bot
        return asyncio.run(run_bot())
    if args.cmd == "schedule":
        from .scheduler import run_scheduler
        return asyncio.run(run_scheduler())
    return 2


if __name__ == "__main__":
    sys.exit(main())
