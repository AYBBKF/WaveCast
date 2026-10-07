"""Les 11 agents : 1 directeur (Opus) + 10 spécialistes (Haiku)."""

from .base import Agent
from .director import Director
from .workers import (
    AnimatorAgent,
    ArtDirectorAgent,
    EditorAgent,
    HistorianAgent,
    PromptEngineerAgent,
    ScreenwriterAgent,
    SeoQaAgent,
    StoryboardAgent,
    StrategistAgent,
    VoiceDirectorAgent,
)

__all__ = [
    "Agent", "Director", "HistorianAgent", "StrategistAgent", "ScreenwriterAgent",
    "StoryboardAgent", "ArtDirectorAgent", "PromptEngineerAgent", "AnimatorAgent",
    "VoiceDirectorAgent", "EditorAgent", "SeoQaAgent",
]
