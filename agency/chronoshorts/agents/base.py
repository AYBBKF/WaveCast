"""Classe de base d'un agent : un rôle, un prompt système stable (mis en cache),
un modèle (directeur ou spécialiste) et des appels structurés."""

from __future__ import annotations

import logging
from typing import TypeVar

from pydantic import BaseModel

from ..config import Settings, get_settings
from ..llm import LLMBackend

T = TypeVar("T", bound=BaseModel)
log = logging.getLogger("chronoshorts.agents")

CHANNEL_CHARTER = """\
CHARTE DE LA CHAÎNE
- Genre : documentaires courts (YouTube Shorts 9:16, 45-60 s) sur l'histoire et la vie
  quotidienne des civilisations. Le spectateur doit sentir qu'il voyage dans le temps.
- Style : "Emotional Historical Storytelling" — animation 2.5D/3D stylisée, personnages
  expressifs, actions réelles, décors détaillés, lumière cinématographique, caméra dynamique.
- Rigueur : jamais de fait inventé. Une scène du quotidien reconstituée sans preuve directe
  doit être signalée. Les éléments incertains ou controversés sont nuancés.
- Pas de clickbait mensonger, pas de diaporama statique, pas de visages déformés.
- Langue de la narration : {language}. Les prompts visuels sont rédigés en anglais.
"""


class Agent:
    name: str = "agent"
    role: str = "worker"  # "worker" (Haiku) ou "director" (Opus)
    description: str = ""

    def __init__(self, llm: LLMBackend, settings: Settings | None = None):
        self.llm = llm
        self.settings = settings or get_settings()

    def system_prompt(self) -> str:
        charter = CHANNEL_CHARTER.format(language=self.settings.language_name)
        return f"{charter}\n\nRÔLE : {self.name}\n{self.description}"

    async def ask(
        self,
        user: str,
        output_format: type[T],
        *,
        web_search: bool = False,
        max_tokens: int = 16000,
    ) -> T:
        log.info("[%s] appel (%s)", self.name, output_format.__name__)
        return await self.llm.structured(
            agent=self.name,
            role=self.role,
            system=self.system_prompt(),
            user=user,
            output_format=output_format,
            web_search=web_search,
            max_tokens=max_tokens,
        )
