"""Schémas Pydantic des livrables de chaque agent.

Ces modèles servent de `output_format` (sorties structurées) pour les appels
Claude : chaque agent est contraint de renvoyer un JSON valide conforme.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Emotion = Literal[
    "émerveillement", "curiosité", "surprise", "joie", "inquiétude", "peur",
    "tension", "sérénité", "fierté", "mélancolie", "mystère",
]
CameraMove = Literal[
    "travelling avant", "travelling latéral", "zoom lent", "panoramique",
    "contre-plongée", "plongée", "plan fixe respirant", "orbite lente",
    "changement de perspective",
]
Transition = Literal["cut", "fondu enchaîné", "fondu noir", "volet", "zoom", "raccord mouvement"]


# ---------------------------------------------------------------------------
# Direction / stratégie
# ---------------------------------------------------------------------------

class TopicIdea(BaseModel):
    title: str = Field(description="Question ou titre intrigant, sans clickbait mensonger")
    civilization: str
    period: str = Field(description="Période ou siècle, ex. 'Nouvel Empire, v. 1300 av. J.-C.'")
    hook: str = Field(description="Accroche parlée des 2 premières secondes")
    why_it_works: str
    daily_life_angle: str = Field(description="Angle 'vie quotidienne / voyage dans le temps'")
    risk_of_repetition: Literal["faible", "moyen", "élevé"]


class TopicProposals(BaseModel):
    ideas: list[TopicIdea] = Field(min_length=3, max_length=8)


class EditorialBrief(BaseModel):
    """Décision du directeur : sujet retenu + ligne éditoriale."""
    chosen_title: str
    civilization: str
    period: str
    narrative_angle: str = Field(description="Angle narratif et promesse émotionnelle")
    hook: str
    must_include: list[str] = Field(description="Éléments factuels incontournables")
    must_avoid: list[str] = Field(description="Pièges, anachronismes, clichés à éviter")
    target_words: int = Field(description="Nombre de mots cible pour la narration")
    rationale: str


# ---------------------------------------------------------------------------
# Agent 1 — Historien
# ---------------------------------------------------------------------------

class Fact(BaseModel):
    statement: str
    confidence: Literal["établi", "probable", "incertain", "controversé"]
    sources: list[str] = Field(description="Références (auteur, ouvrage/site, année)")
    note: str = Field(default="", description="Nuance, débat historiographique ou limite des preuves")


class ResearchDossier(BaseModel):
    summary: str
    daily_life: list[Fact] = Field(description="Habitudes quotidiennes, nourriture, travail, famille")
    customs_and_beliefs: list[Fact]
    architecture_and_objects: list[Fact]
    key_figures_or_roles: list[Fact]
    common_misconceptions: list[str]
    uncertain_or_controversial: list[str] = Field(
        description="Points à signaler dans les métadonnées éditoriales"
    )
    bibliography: list[str] = Field(min_length=3)


# ---------------------------------------------------------------------------
# Agent 3 — Scénariste
# ---------------------------------------------------------------------------

class ScriptBeat(BaseModel):
    role: Literal["hook", "contexte", "découverte", "tension", "révélation", "conclusion"]
    narration: str = Field(description="Texte parlé exact de ce temps narratif")
    reconstructed_without_direct_evidence: bool = Field(
        default=False,
        description="True si la scène du quotidien est reconstituée sans preuve directe",
    )
    facts_used: list[str] = Field(default_factory=list)


class Script(BaseModel):
    title: str
    beats: list[ScriptBeat] = Field(min_length=5)
    full_narration: str = Field(description="Narration complète, concaténée, telle que lue")
    word_count: int
    historical_notes: list[str] = Field(
        default_factory=list, description="Précisions et réserves pour les métadonnées"
    )


# ---------------------------------------------------------------------------
# Agent 4 — Storyboard
# ---------------------------------------------------------------------------

class Scene(BaseModel):
    index: int
    narration: str = Field(description="Portion exacte de la narration couverte par cette scène")
    target_seconds: float = Field(ge=2.0, le=8.0)
    narrative_goal: str
    characters: list[str]
    setting: str
    visible_action: str = Field(description="Action concrète visible à l'écran (pas de plan statique)")
    emotion: Emotion
    camera: CameraMove
    transition_out: Transition
    time_of_day: str = Field(default="jour")


class Storyboard(BaseModel):
    scenes: list[Scene] = Field(min_length=8)
    rhythm_notes: str


# ---------------------------------------------------------------------------
# Agent 5 — Direction artistique
# ---------------------------------------------------------------------------

class CharacterSheet(BaseModel):
    name: str
    role: str
    age_and_build: str
    face_and_hair: str
    costume: str
    distinctive_props: list[str]
    consistency_token: str = Field(
        description="Phrase courte réutilisée mot pour mot dans chaque prompt pour garantir la continuité"
    )


class ArtBible(BaseModel):
    style_statement: str = Field(description="Identité artistique premium (2.5D/3D stylisé, cinéma documentaire)")
    palette: list[str] = Field(description="Couleurs dominantes avec intention")
    lighting: str
    textures_and_materials: str
    architecture_rules: str
    costume_rules: str
    characters: list[CharacterSheet] = Field(min_length=1)
    recurring_sets: list[str]
    negative_rules: list[str] = Field(description="Anachronismes et erreurs visuelles interdits")


# ---------------------------------------------------------------------------
# Agent 6 — Prompt engineer
# ---------------------------------------------------------------------------

class ScenePrompts(BaseModel):
    scene_index: int
    image_prompt: str = Field(description="Prompt image clé, anglais, 9:16, cohérent avec l'art bible")
    video_prompt: str = Field(description="Prompt de mouvement pour le modèle image→vidéo (anglais)")
    negative_prompt: str
    camera_motion: str = Field(description="Mouvement de caméra en termes techniques (dolly in, pan left...)")


class PromptPack(BaseModel):
    scenes: list[ScenePrompts]


# ---------------------------------------------------------------------------
# Agent 7 — Animateur / émotions
# ---------------------------------------------------------------------------

class AnimationDirective(BaseModel):
    scene_index: int
    facial_expression: str = Field(description="Expression crédible, détaillée")
    gestures: str
    secondary_motion: str = Field(description="Vent, tissus, fumée, foule, animaux…")
    camera_dynamics: str
    pacing: Literal["lent", "modéré", "rapide"]
    kenburns_zoom: float = Field(ge=1.02, le=1.25, description="Facteur de zoom pour le repli composition animée")
    kenburns_pan: Literal["gauche", "droite", "haut", "bas", "centre"]
    enriched_video_prompt: str = Field(description="Prompt vidéo final enrichi des émotions et mouvements")


class AnimationPlan(BaseModel):
    scenes: list[AnimationDirective]
    anti_patterns_checked: list[str] = Field(
        description="Ce qui a été évité : visages déformés, diaporama, mouvements artificiels…"
    )


# ---------------------------------------------------------------------------
# Agent 8 — Voix
# ---------------------------------------------------------------------------

class VoiceSegment(BaseModel):
    scene_index: int
    text: str = Field(description="Texte prêt pour le TTS, ponctué pour les pauses")
    emotion: str
    pace: Literal["lent", "normal", "soutenu"]
    emphasis_words: list[str] = Field(default_factory=list)


class VoiceScript(BaseModel):
    narrator_persona: str
    segments: list[VoiceSegment]
    pronunciation_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent 9 — Montage / son
# ---------------------------------------------------------------------------

class SoundPlan(BaseModel):
    music_mood: Literal["épique", "mystérieux", "contemplatif", "tendu", "chaleureux", "mélancolique"]
    music_energy_curve: str = Field(description="Comment l'intensité évolue du hook à la conclusion")
    ambience_tags: list[str] = Field(description="Ex: marché, vent désert, fleuve, forge, temple")
    sfx_cues: list[str] = Field(description="Ex: 'scène 3 : cloche lointaine', 'scène 7 : marteau'")
    subtitle_style: Literal["moderne", "classique", "documentaire"]
    transitions_summary: str


# ---------------------------------------------------------------------------
# Agent 10 — SEO & QA
# ---------------------------------------------------------------------------

class SeoPackage(BaseModel):
    title: str = Field(description="Titre YouTube Short (< 100 caractères)")
    description: str
    hashtags: list[str] = Field(min_length=5, max_length=15)
    tags: list[str]
    sources_block: str = Field(description="Bloc 'Sources' à coller dans la description")
    editorial_disclaimer: str = Field(description="Mention des reconstitutions sans preuves directes")
    thumbnail_concept: str
    thumbnail_prompt: str


class QAIssue(BaseModel):
    severity: Literal["bloquant", "majeur", "mineur"]
    area: Literal["historique", "visuel", "sous-titres", "audio", "ratio_durée", "narration", "seo"]
    description: str
    suggested_fix: str


class QAReport(BaseModel):
    passed: bool
    score: int = Field(ge=0, le=100)
    issues: list[QAIssue]
    summary: str


# ---------------------------------------------------------------------------
# Décisions du directeur
# ---------------------------------------------------------------------------

class DirectorReview(BaseModel):
    approved: bool
    score: int = Field(ge=0, le=100)
    boring_passages: list[str] = Field(default_factory=list)
    historical_concerns: list[str] = Field(default_factory=list)
    revision_instructions: str = Field(
        default="", description="Instructions précises pour l'agent si non approuvé"
    )
    notes: str = ""


class FinalDecision(BaseModel):
    authorize_telegram: bool
    verdict: str
    improvements_for_next_time: list[str]
