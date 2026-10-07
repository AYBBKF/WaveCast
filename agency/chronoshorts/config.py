"""Configuration centrale (variables d'environnement / fichier .env).

Tout est surchargeable par variable d'environnement préfixée `CHRONO_`
(ex. `CHRONO_LANGUAGE=ar`). Les clés API des fournisseurs gardent leurs noms
standards (`ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `REPLICATE_API_TOKEN`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Language = Literal["fr", "en", "ar"]

LANGUAGE_NAMES: dict[str, str] = {
    "fr": "français",
    "en": "English",
    "ar": "العربية الفصحى الحديثة (arabe standard moderne)",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHRONO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Modèles Claude -----------------------------------------------------
    # Identifiants réels (API Anthropic, 2026). Si l'un n'est pas disponible sur
    # le compte, `llm.resolve_models()` bascule sur la chaîne de repli ci-dessous
    # sans jamais inventer d'identifiant.
    director_model: str = "claude-opus-5-5"
    director_fallback_models: list[str] = ["claude-opus-5", "claude-opus-4-8", "claude-opus-4-7"]
    worker_model: str = "claude-haiku-5-5"
    worker_fallback_models: list[str] = ["claude-haiku-4-5", "claude-sonnet-5-5"]
    director_effort: Literal["low", "medium", "high", "xhigh", "max"] = "high"
    worker_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"
    # Repli serveur en cas de refus des classificateurs de sécurité (Opus 5.5).
    server_side_fallbacks: bool = True
    # Recherche web côté serveur pour l'agent historien.
    web_search: bool = True
    web_search_max_uses: int = 6
    # Vérifie les modèles via GET /v1/models au démarrage.
    verify_models: bool = True
    max_concurrency: int = 4

    # --- Chaîne ---------------------------------------------------------------
    channel_name: str = "ChronoShorts"
    language: Language = "fr"
    target_duration_min: float = 45.0
    target_duration_max: float = 60.0
    scene_min_seconds: float = 3.0
    scene_max_seconds: float = 6.0
    width: int = 1080
    height: int = 1920
    fps: int = 30

    # --- Fournisseurs ---------------------------------------------------------
    # TTS : elevenlabs | edge | silent (silent = tests hors ligne)
    tts_provider: Literal["elevenlabs", "edge", "silent"] = "elevenlabs"
    elevenlabs_api_key: str = Field(default="", alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = ""  # une seule voix pour toute la chaîne
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    edge_voice_fr: str = "fr-FR-HenriNeural"
    edge_voice_en: str = "en-US-GuyNeural"
    edge_voice_ar: str = "ar-SA-HamedNeural"

    # Images : replicate | placeholder
    image_provider: Literal["replicate", "placeholder"] = "replicate"
    replicate_api_token: str = Field(default="", alias="REPLICATE_API_TOKEN")
    replicate_image_model: str = "black-forest-labs/flux-1.1-pro"
    replicate_edit_model: str = "black-forest-labs/flux-kontext-pro"

    # Vidéo : replicate (image→vidéo) | kenburns (composition animée locale)
    video_provider: Literal["replicate", "kenburns"] = "replicate"
    # Modèles image→vidéo testés : bytedance/seedance-1-pro, kwaivgi/kling-v2.1,
    # minimax/hailuo-02. Le provider adapte les paramètres à chacun.
    replicate_video_model: str = "bytedance/seedance-1-pro"
    video_resolution: str = "1080p"
    # Si la génération vidéo échoue pour une scène, repli local (kenburns).
    video_fallback_kenburns: bool = True

    # Telegram
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    # Si True, le directeur doit autoriser l'envoi ; si False, envoi après QA.
    require_director_approval: bool = True

    # --- Chemins --------------------------------------------------------------
    workdir: Path = Path("./productions")
    assets_dir: Path = Path("./assets")
    font_latin: str = "DejaVu Sans"
    font_arabic: str = "Noto Naskh Arabic"

    # --- Planificateur --------------------------------------------------------
    daily_videos: int = 1
    schedule_hours: list[int] = [9]

    # --- Clé Anthropic (lue aussi par le SDK) ---------------------------------
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    @property
    def language_name(self) -> str:
        return LANGUAGE_NAMES[self.language]

    @property
    def is_rtl(self) -> bool:
        return self.language == "ar"

    def edge_voice(self) -> str:
        return {"fr": self.edge_voice_fr, "en": self.edge_voice_en, "ar": self.edge_voice_ar}[
            self.language
        ]


_settings: Settings | None = None


def get_settings(reload: bool = False) -> Settings:
    global _settings
    if _settings is None or reload:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings) -> None:
    """Utilisé par les tests pour injecter une configuration."""
    global _settings
    _settings = settings
