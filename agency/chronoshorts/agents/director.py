"""Le directeur (Claude Opus) : stratégie, choix du sujet, supervision,
validation et autorisation de diffusion. Il n'intervient qu'aux points de
décision importants ; les spécialistes travaillent en parallèle entre deux."""

from __future__ import annotations

from .. import schemas as S
from .base import Agent
from .workers import _j


class Director(Agent):
    name = "directeur"
    role = "director"
    description = """\
Tu es directeur général, producteur exécutif et réalisateur artistique de la chaîne.
Tu définis la stratégie éditoriale, choisis les sujets les plus captivants, supervises
dix spécialistes, garantis la rigueur historique, décides de l'angle narratif, détectes
les passages ennuyeux, exiges des corrections précises et valides le montage final avant
d'autoriser la diffusion. Tu es exigeant : un Short doit accrocher en 2 secondes, ne
jamais relâcher la tension, et laisser une image mémorable. Tu n'inventes jamais de fait."""

    async def choose_topic(self, proposals: S.TopicProposals, history: list[str],
                           language: str, target_words: int) -> S.EditorialBrief:
        user = (
            f"Propositions du stratège :\n{_j(proposals)}\n\n"
            f"Sujets déjà produits : {history or 'aucun'}\n\n"
            f"Choisis le meilleur sujet (ou améliore-le), fixe l'angle narratif, les éléments "
            f"incontournables, les pièges à éviter. target_words = {target_words} "
            f"(narration en {language}, 45-60 s au débit naturel d'un narrateur)."
        )
        return await self.ask(user, S.EditorialBrief)

    async def review_script(self, script: S.Script, dossier: S.ResearchDossier,
                            fact_check: S.QAReport) -> S.DirectorReview:
        user = (
            f"Script :\n{_j(script)}\n\nFact-check de l'historien :\n{_j(fact_check)}\n\n"
            f"Points incertains du dossier :\n{_j(dossier.uncertain_or_controversial)}\n\n"
            "Évalue : hook en ≤ 2 s ? passages ennuyeux ? rigueur ? émotion ? conclusion "
            "mémorable ? Si une correction est nécessaire, donne des instructions précises et "
            "actionnables au scénariste (approved=false). Sinon approved=true."
        )
        return await self.ask(user, S.DirectorReview)

    async def review_visuals(self, storyboard: S.Storyboard, bible: S.ArtBible,
                             animation: S.AnimationPlan) -> S.DirectorReview:
        user = (
            f"Storyboard :\n{_j(storyboard)}\n\nArt bible (résumé) :\n"
            f"{bible.style_statement}\nPalette : {bible.palette}\nInterdits : {bible.negative_rules}\n\n"
            f"Plan d'animation :\n"
            f"{_j([{'scene': a.scene_index, 'expression': a.facial_expression, 'camera': a.camera_dynamics, 'pacing': a.pacing} for a in animation.scenes])}\n\n"
            "Vérifie : chaque scène a-t-elle une action visible et une émotion lisible ? "
            "Rythme (pas de scène > 6 s, variété des plans) ? Continuité des personnages ? "
            "Donne approved=true si c'est exploitable ; sinon instructions précises."
        )
        return await self.ask(user, S.DirectorReview)

    async def final_decision(self, qa: S.QAReport, technical_report: dict,
                             seo: S.SeoPackage) -> S.FinalDecision:
        user = (
            f"Rapport QA :\n{_j(qa)}\n\nRapport technique :\n{_j(technical_report)}\n\n"
            f"Titre proposé : {seo.title}\n\n"
            "Décide si la vidéo peut être envoyée sur Telegram. Refuse si un problème bloquant "
            "subsiste (durée hors 45-60 s, absence d'audio, erreur historique majeure, "
            "majorité de scènes en repli). Donne des pistes d'amélioration pour la prochaine."
        )
        return await self.ask(user, S.FinalDecision)
