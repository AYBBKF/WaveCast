"""LLM factice : renvoie des livrables plausibles pour chaque schéma, sans réseau.
Permet de tester toute la chaîne de production (agents → FFmpeg → fichier MP4)."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from chronoshorts import schemas as S
from chronoshorts.llm import CostTracker, UsageRecord

T = TypeVar("T", bound=BaseModel)

NARRATION = [
    "Imaginez Cordoue en l'an mille.",
    "La nuit tombe sur le Guadalquivir et des milliers de lampes s'allument.",
    "Vous marchez dans une rue pavée, éclairée, alors que Paris dort dans la boue.",
    "Ici, les bibliothèques comptent des centaines de milliers de volumes.",
    "Un marchand pèse des épices venues d'Inde, un copiste trempe sa plume.",
    "Dans les bains publics, on discute de poésie et d'astronomie.",
    "Mais derrière la splendeur, la cité se fissure.",
    "Les rivalités politiques menacent le califat tout entier.",
    "Quelques décennies plus tard, Cordoue sera pillée.",
    "Pourtant, son savoir traversera les siècles jusqu'à nous.",
    "Alors, la prochaine fois que vous ouvrez un livre, pensez à Cordoue.",
]
FULL = " ".join(NARRATION)
WORDS = len(FULL.split())


class FakeLLM:
    director_model = "fake-opus"
    worker_model = "fake-haiku"

    def __init__(self, approve_script_after: int = 0, approve_visuals: bool = True,
                 authorize: bool = True, fact_ok: bool = True):
        self.costs = CostTracker()
        self.calls: list[tuple[str, str]] = []
        self.script_reviews = 0
        self.approve_script_after = approve_script_after
        self.approve_visuals = approve_visuals
        self.authorize = authorize
        self.fact_ok = fact_ok

    async def structured(self, *, agent: str, role: str, system: str, user: str,
                         output_format: type[T], web_search: bool = False, max_tokens: int = 16000) -> T:
        self.calls.append((agent, output_format.__name__))
        self.costs.add(UsageRecord(agent, self.director_model if role == "director" else self.worker_model,
                                   1000, 300, 0, 0, 0.1))
        return self._build(agent, output_format, user)

    # ------------------------------------------------------------------
    def _build(self, agent: str, fmt: type[T], user: str) -> T:
        if fmt is S.TopicProposals:
            return S.TopicProposals(ideas=[S.TopicIdea(
                title=f"Sujet {i}", civilization="Al-Andalus", period="Xe siècle", hook="Et si…",
                why_it_works="contraste", daily_life_angle="une nuit", risk_of_repetition="faible")
                for i in range(3)])
        if fmt is S.EditorialBrief:
            return S.EditorialBrief(chosen_title="À quoi ressemblait une nuit à Cordoue en l'an mille ?",
                                    civilization="Al-Andalus", period="Califat de Cordoue, v. 1000",
                                    narrative_angle="voyage nocturne", hook=NARRATION[0],
                                    must_include=["éclairage public", "bibliothèques"], must_avoid=["clichés"],
                                    target_words=WORDS, rationale="fort contraste passé/présent")
        if fmt is S.ResearchDossier:
            f = lambda s: S.Fact(statement=s, confidence="probable", sources=["Lévi-Provençal, 1950"])  # noqa: E731
            return S.ResearchDossier(summary="Cordoue califale", daily_life=[f("rues éclairées")],
                                     customs_and_beliefs=[f("bains publics")], architecture_and_objects=[f("mosquée")],
                                     key_figures_or_roles=[f("copistes")], common_misconceptions=["tout le monde lisait"],
                                     uncertain_or_controversial=["nombre exact de volumes de la bibliothèque"],
                                     bibliography=["A", "B", "C"])
        if fmt is S.Script:
            beats = [S.ScriptBeat(role=r, narration=n) for r, n in zip(
                ["hook", "contexte", "découverte", "tension", "révélation", "conclusion"] + ["conclusion"] * 5,
                NARRATION)]
            beats[4].reconstructed_without_direct_evidence = True
            return S.Script(title="Nuit à Cordoue", beats=beats, full_narration=FULL, word_count=WORDS)
        if fmt is S.QAReport:
            if agent == "historien":
                return S.QAReport(passed=self.fact_ok, score=90 if self.fact_ok else 40,
                                  issues=[] if self.fact_ok else [S.QAIssue(severity="bloquant", area="historique",
                                                                             description="date fausse", suggested_fix="corriger")],
                                  summary="ok" if self.fact_ok else "problème")
            return S.QAReport(passed=True, score=88, issues=[S.QAIssue(severity="mineur", area="audio",
                                                                      description="musique un peu forte", suggested_fix="-2 dB")],
                              summary="conforme")
        if fmt is S.DirectorReview:
            if agent == "directeur" and "Fact-check" in user:
                self.script_reviews += 1
                ok = self.script_reviews > self.approve_script_after
                return S.DirectorReview(approved=ok, score=85 if ok else 55,
                                        revision_instructions="" if ok else "Renforce le hook.")
            return S.DirectorReview(approved=self.approve_visuals, score=80,
                                    revision_instructions="" if self.approve_visuals else "Plus de mouvement scène 3.")
        if fmt is S.Storyboard:
            scenes = [S.Scene(index=i, narration=n, target_seconds=4.0, narrative_goal="g",
                              characters=["Yahya"], setting="ruelle", visible_action="marche",
                              emotion="curiosité", camera="travelling avant",
                              transition_out=["cut", "fondu enchaîné", "volet"][i % 3])
                      for i, n in enumerate(NARRATION)]
            return S.Storyboard(scenes=scenes, rhythm_notes="crescendo")
        if fmt is S.ArtBible:
            return S.ArtBible(style_statement="2.5D cinéma", palette=["ambre"], lighting="lampes",
                              textures_and_materials="pierre", architecture_rules="arcs", costume_rules="tuniques",
                              characters=[S.CharacterSheet(name="Yahya", role="copiste", age_and_build="30 ans",
                                                           face_and_hair="barbe courte", costume="tunique",
                                                           distinctive_props=["plume"], consistency_token="Yahya, bearded copyist")],
                              recurring_sets=["ruelle"], negative_rules=["pas de lunettes"])
        if fmt is S.PromptPack:
            # volontairement incomplet (scène 5 absente) pour tester l'alignement
            return S.PromptPack(scenes=[S.ScenePrompts(scene_index=i, image_prompt=f"scene {i} cordoba night",
                                                       video_prompt="slow dolly in", negative_prompt="text",
                                                       camera_motion="dolly in") for i in range(len(NARRATION)) if i != 5])
        if fmt is S.AnimationPlan:
            return S.AnimationPlan(scenes=[S.AnimationDirective(
                scene_index=i, facial_expression="curieux", gestures="regarde", secondary_motion="flammes",
                camera_dynamics="dolly", pacing="modéré", kenburns_zoom=1.1 + 0.01 * i,
                kenburns_pan=["gauche", "droite", "haut", "bas", "centre"][i % 5],
                enriched_video_prompt="he looks up, lamps flicker, slow dolly in") for i in range(len(NARRATION))],
                anti_patterns_checked=["pas de diaporama"])
        if fmt is S.VoiceScript:
            return S.VoiceScript(narrator_persona="chaud", segments=[
                S.VoiceSegment(scene_index=i, text=n, emotion="curiosité", pace="normal")
                for i, n in enumerate(NARRATION) if i != 2])  # scène 2 manquante → réparée
        if fmt is S.SoundPlan:
            return S.SoundPlan(music_mood="mystérieux", music_energy_curve="montée", ambience_tags=["marché"],
                               sfx_cues=["scène 3 : cloche"], subtitle_style="moderne", transitions_summary="douces")
        if fmt is S.SeoPackage:
            return S.SeoPackage(title="Une nuit à Cordoue en l'an 1000", description="desc",
                                hashtags=["#histoire", "#cordoue", "#alandalus", "#shorts", "#documentaire"],
                                tags=["histoire"], sources_block="Sources : A, B, C",
                                editorial_disclaimer="Scène du marchand reconstituée.",
                                thumbnail_concept="ruelle éclairée", thumbnail_prompt="lit alley")
        if fmt is S.FinalDecision:
            return S.FinalDecision(authorize_telegram=self.authorize, verdict="prêt", improvements_for_next_time=["plus de rythme"])
        raise AssertionError(f"schéma non géré : {fmt}")
