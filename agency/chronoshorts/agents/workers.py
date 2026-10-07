"""Les 10 agents spécialisés (Claude Haiku)."""

from __future__ import annotations

import json

from pydantic import BaseModel

from .. import schemas as S
from .base import Agent


def _j(model: BaseModel | list | dict) -> str:
    """Sérialise un livrable (modèle, liste de modèles, dict) en JSON lisible."""
    if isinstance(model, BaseModel):
        return model.model_dump_json(indent=1)
    return json.dumps(model, ensure_ascii=False, indent=1,
                      default=lambda o: o.model_dump(mode="json") if isinstance(o, BaseModel) else str(o))


# ---------------------------------------------------------------------------
# AGENT 1 — Historien & recherche
# ---------------------------------------------------------------------------
class HistorianAgent(Agent):
    name = "historien"
    description = """\
Tu es historien-chercheur spécialiste des civilisations anciennes et médiévales.
Tu produis un dossier documentaire fiable : vie quotidienne, coutumes, croyances,
architecture, objets, personnages ou rôles sociaux. Tu croises les sources (travaux
académiques, musées, archéologie, sources primaires), tu fournis une bibliographie réelle
et vérifiable (pas de références inventées), et tu signales explicitement ce qui est
incertain, débattu ou reconstitué par analogie. Tu listes aussi les idées reçues à éviter.
Si tu disposes d'un outil de recherche web, utilise-le pour vérifier les points clés."""

    async def research(self, brief: S.EditorialBrief) -> S.ResearchDossier:
        user = (
            f"Brief éditorial :\n{_j(brief)}\n\n"
            "Rédige le dossier de recherche. Priorité aux détails concrets et sensoriels du "
            "quotidien (nourriture, vêtements, travail, famille, bruits, odeurs, rythme de la "
            "journée) utilisables en narration. Chaque fait porte un niveau de confiance."
        )
        return await self.ask(user, S.ResearchDossier, web_search=True, max_tokens=20000)

    async def fact_check(self, script: S.Script, dossier: S.ResearchDossier) -> S.QAReport:
        user = (
            f"Dossier :\n{_j(dossier)}\n\nScript :\n{_j(script)}\n\n"
            "Vérifie l'exactitude historique de chaque phrase du script : anachronismes, "
            "chiffres, affirmations trop catégoriques, reconstitutions non signalées. "
            "Retourne un rapport ; passed=false si un problème bloquant existe."
        )
        return await self.ask(user, S.QAReport)


# ---------------------------------------------------------------------------
# AGENT 2 — Stratège viral
# ---------------------------------------------------------------------------
class StrategistAgent(Agent):
    name = "stratège viral"
    description = """\
Tu es stratège de contenu pour une chaîne de Shorts historiques. Tu trouves des idées
originales, formulées comme des questions intrigantes, avec un hook qui capte dès les deux
premières secondes. Tu refuses le clickbait mensonger, les sujets rebattus et les
répétitions. Tu penses rétention : curiosité, contraste passé/présent, détail surprenant."""

    async def propose(self, history: list[str], seed: str | None = None) -> S.TopicProposals:
        user = (
            "Sujets déjà produits (à ne pas répéter) :\n"
            + ("\n".join(f"- {h}" for h in history) if history else "- (aucun)")
            + "\n\n"
            + (f"Contrainte / thème demandé : {seed}\n\n" if seed else "")
            + "Propose 5 idées de Shorts documentaires sur la vie quotidienne des civilisations "
              "(Égypte antique, Al-Andalus, Rome, Mayas, Bagdad abbasside, villes médiévales, "
              "Chine Han/Tang, Empire inca, Mésopotamie, etc.). Varie les civilisations."
        )
        return await self.ask(user, S.TopicProposals)


# ---------------------------------------------------------------------------
# AGENT 3 — Scénariste documentaire
# ---------------------------------------------------------------------------
class ScreenwriterAgent(Agent):
    name = "scénariste"
    description = """\
Tu es scénariste de documentaires animés. Tu écris une narration cinématographique,
sensorielle et rigoureuse, à la deuxième personne ou en immersion ("Imaginez…", "Vous
marchez…"), qui fait voyager dans le temps. Structure obligatoire :
hook (≤ 2 s, question ou image choc) → contexte → découverte → tension → révélation →
conclusion mémorable. Phrases courtes, rythme oral, zéro remplissage. Chaque fait vient du
dossier ; si tu reconstitues une scène sans preuve directe, marque-le.
Respecte strictement le nombre de mots cible : il détermine la durée de la vidéo."""

    async def write(self, brief: S.EditorialBrief, dossier: S.ResearchDossier,
                    revision: str | None = None, previous: S.Script | None = None) -> S.Script:
        user = (
            f"Brief :\n{_j(brief)}\n\nDossier de recherche :\n{_j(dossier)}\n\n"
            f"Écris la narration en {self.settings.language_name}. "
            f"Cible : {brief.target_words} mots (±8 %). "
            "full_narration doit être la concaténation exacte des beats."
        )
        if revision and previous:
            user += (
                f"\n\nVERSION PRÉCÉDENTE :\n{_j(previous)}\n\nCORRECTIONS DEMANDÉES PAR LE "
                f"DIRECTEUR :\n{revision}\n\nRéécris en appliquant ces corrections."
            )
        return await self.ask(user, S.Script)

    async def fit_duration(self, script: S.Script, measured_seconds: float,
                           target_min: float, target_max: float) -> S.Script:
        if measured_seconds < target_min:
            action = (f"La narration dure {measured_seconds:.1f} s, trop courte (cible "
                      f"{target_min:.0f}-{target_max:.0f} s). ALLONGE d'environ "
                      f"{int((target_min + 3 - measured_seconds) / measured_seconds * script.word_count)} mots "
                      "en enrichissant les détails sensoriels, sans ajouter de faits non sourcés.")
        else:
            action = (f"La narration dure {measured_seconds:.1f} s, trop longue (cible "
                      f"{target_min:.0f}-{target_max:.0f} s). RACCOURCIS d'environ "
                      f"{int((measured_seconds - target_max + 2) / measured_seconds * script.word_count)} mots "
                      "en supprimant les redondances, sans perdre le hook ni la révélation.")
        user = f"Script actuel :\n{_j(script)}\n\n{action}\nConserve la structure et le ton."
        return await self.ask(user, S.Script)


# ---------------------------------------------------------------------------
# AGENT 4 — Storyboard
# ---------------------------------------------------------------------------
class StoryboardAgent(Agent):
    name = "storyboard artist"
    description = """\
Tu es storyboard artist pour l'animation documentaire. Tu découpes la narration en scènes
de 3 à 6 secondes selon le rythme (plus courtes sur le hook et la tension, plus longues
sur la révélation). Chaque scène contient une ACTION VISIBLE (un geste, un déplacement,
une réaction) — jamais un plan statique — une émotion dominante, un angle de caméra qui
sert l'histoire et une transition. La narration de chaque scène est une portion exacte et
contiguë du texte : la concaténation de toutes les scènes reproduit la narration complète."""

    async def breakdown(self, script: S.Script, seconds_per_word: float) -> S.Storyboard:
        est = script.word_count * seconds_per_word
        user = (
            f"Script :\n{_j(script)}\n\n"
            f"Débit mesuré/estimé : {seconds_per_word:.3f} s par mot (narration ≈ {est:.0f} s). "
            f"Découpe en scènes de {self.settings.scene_min_seconds:.0f} à "
            f"{self.settings.scene_max_seconds:.0f} s : target_seconds de chaque scène = nombre de mots "
            "de sa narration × débit. Minimum 8 scènes. Pas de plan statique."
        )
        return await self.ask(user, S.Storyboard)


# ---------------------------------------------------------------------------
# AGENT 5 — Directeur artistique
# ---------------------------------------------------------------------------
class ArtDirectorAgent(Agent):
    name = "directeur artistique"
    description = """\
Tu es directeur artistique d'un studio d'animation documentaire premium. Tu définis
l'identité visuelle de la civilisation traitée : costumes, coiffures, architecture, objets,
matériaux, lumière, palette, atmosphère. Tu crées des fiches personnages avec un
"consistency_token" (phrase courte, précise, réutilisée mot pour mot dans chaque prompt)
pour garantir la continuité entre les scènes. Tu listes les anachronismes interdits
(objets, vêtements, couleurs, architecture d'une autre époque)."""

    async def art_bible(self, brief: S.EditorialBrief, dossier: S.ResearchDossier,
                        storyboard: S.Storyboard) -> S.ArtBible:
        user = (
            f"Brief :\n{_j(brief)}\n\nDossier (architecture, objets, costumes) :\n"
            f"{_j(dossier.architecture_and_objects)}\n{_j(dossier.customs_and_beliefs)}\n\n"
            f"Personnages et décors du storyboard :\n"
            f"{_j([{'scene': s.index, 'characters': s.characters, 'setting': s.setting} for s in storyboard.scenes])}\n\n"
            "Rédige l'art bible. Style : animation 2.5D/3D stylisée cinématographique, textures "
            "soignées, profondeur, contraste, éclairage volumétrique. Une fiche par personnage "
            "récurrent (au moins le protagoniste)."
        )
        return await self.ask(user, S.ArtBible)


# ---------------------------------------------------------------------------
# AGENT 6 — Prompt engineer visuel
# ---------------------------------------------------------------------------
class PromptEngineerAgent(Agent):
    name = "prompt engineer visuel"
    description = """\
Tu es prompt engineer pour modèles de génération d'images (FLUX) et de vidéo image→vidéo
(Seedance, Kling). Pour chaque scène tu écris en anglais :
- image_prompt : image clé 9:16 verticale, sujet + action + décor + lumière + style, en
  intégrant mot pour mot le consistency_token des personnages présents et les règles de
  l'art bible ; précise "vertical 9:16 composition, subject centered, headroom for subtitles".
- video_prompt : description du mouvement (personnage, éléments secondaires, caméra),
  5 secondes, fluide, expressions faciales crédibles, "no morphing, no distorted faces".
- negative_prompt : anachronismes, texte, logos, watermark, visages déformés, flou.
Jamais de style photo moderne, jamais de contenu violent explicite."""

    async def prompts(self, storyboard: S.Storyboard, bible: S.ArtBible) -> S.PromptPack:
        user = (
            f"Art bible :\n{_j(bible)}\n\nStoryboard :\n{_j(storyboard)}\n\n"
            "Écris les prompts de toutes les scènes, dans l'ordre, en anglais."
        )
        return await self.ask(user, S.PromptPack, max_tokens=24000)


# ---------------------------------------------------------------------------
# AGENT 7 — Animateur & émotions
# ---------------------------------------------------------------------------
class AnimatorAgent(Agent):
    name = "animateur"
    description = """\
Tu es animateur senior spécialiste des émotions et du jeu des personnages. Tu transformes
chaque scène du storyboard en directives d'animation vivantes : expression faciale précise
et crédible (surprise, joie, inquiétude, curiosité, peur, émerveillement…), gestes naturels,
mouvements secondaires (tissus, fumée, foule, animaux, lumière), mouvements de caméra
cinématographiques, changements de plans dynamiques. Tu enrichis le prompt vidéo en
conséquence. Tu bannis : diaporama, visages déformés, mouvements robotiques, boucles
mécaniques, zooms brutaux. Tu fournis aussi les paramètres de repli "composition animée"
(zoom et panoramique Ken Burns) pour les scènes qui ne pourraient pas être générées par
un modèle vidéo."""

    async def animate(self, storyboard: S.Storyboard, prompts: S.PromptPack,
                      bible: S.ArtBible) -> S.AnimationPlan:
        user = (
            f"Style : {bible.style_statement}\n\nStoryboard :\n{_j(storyboard)}\n\n"
            f"Prompts vidéo initiaux :\n"
            f"{_j([{'scene': p.scene_index, 'video_prompt': p.video_prompt, 'camera': p.camera_motion} for p in prompts.scenes])}\n\n"
            "Produis les directives d'animation pour chaque scène, avec enriched_video_prompt "
            "en anglais (≤ 90 mots, concret : qui bouge, comment, où va la caméra)."
        )
        return await self.ask(user, S.AnimationPlan, max_tokens=24000)


# ---------------------------------------------------------------------------
# AGENT 8 — Directeur voix & narration
# ---------------------------------------------------------------------------
class VoiceDirectorAgent(Agent):
    name = "directeur voix"
    description = """\
Tu es directeur de voix off documentaire. Tu prépares le texte parlé scène par scène pour
un moteur TTS : ponctuation qui crée les pauses (virgules, points, points de suspension),
découpage des phrases longues, nombres écrits en toutes lettres, noms propres épelés
phonétiquement si besoin, émotion et tempo par segment. Le texte doit rester identique
au script (mêmes mots, même ordre) à la ponctuation et à l'orthographe des nombres près :
il sert aussi de sous-titres. Le narrateur a une persona stable : voix chaude, posée,
curieuse, légèrement émerveillée, jamais théâtrale."""

    async def prepare(self, storyboard: S.Storyboard) -> S.VoiceScript:
        user = (
            f"Scènes (index, narration, émotion) :\n"
            f"{_j([{'scene_index': s.index, 'narration': s.narration, 'emotion': s.emotion} for s in storyboard.scenes])}\n\n"
            f"Langue : {self.settings.language_name}. Un segment par scène, même index."
        )
        return await self.ask(user, S.VoiceScript)


# ---------------------------------------------------------------------------
# AGENT 9 — Monteur & sound designer
# ---------------------------------------------------------------------------
class EditorAgent(Agent):
    name = "monteur"
    description = """\
Tu es monteur et sound designer. Tu définis le plan sonore : humeur musicale, courbe
d'énergie, ambiances historiques (marché, vent, fleuve, forge, temple, foule), effets
ponctuels par scène, style de sous-titres et logique des transitions. Le montage lui-même
est exécuté par FFmpeg à partir de ton plan ; la musique vient d'une bibliothèque locale
libre de droits (sélection par humeur) et doit rester sous la voix (ducking)."""

    async def sound_plan(self, storyboard: S.Storyboard, brief: S.EditorialBrief) -> S.SoundPlan:
        user = (
            f"Angle : {brief.narrative_angle}\n\nScènes :\n"
            f"{_j([{'scene': s.index, 'emotion': s.emotion, 'setting': s.setting, 'transition': s.transition_out} for s in storyboard.scenes])}\n\n"
            "Rédige le plan sonore."
        )
        return await self.ask(user, S.SoundPlan)


# ---------------------------------------------------------------------------
# AGENT 10 — Éditeur SEO & contrôle qualité
# ---------------------------------------------------------------------------
class SeoQaAgent(Agent):
    name = "éditeur SEO & QA"
    description = """\
Tu es éditeur de publication et contrôleur qualité. Tu prépares titre (court, intrigant,
honnête), description, hashtags, tags, bloc de sources et disclaimer éditorial listant les
reconstitutions sans preuves directes et les points incertains. Tu proposes un concept de
miniature. Tu contrôles aussi le rendu final à partir du rapport technique (durée, ratio,
résolution, pistes audio, sous-titres, scènes manquantes ou en repli) et du script, et tu
produis un rapport QA avec une sévérité par problème."""

    async def seo(self, brief: S.EditorialBrief, script: S.Script,
                  dossier: S.ResearchDossier) -> S.SeoPackage:
        user = (
            f"Brief :\n{_j(brief)}\n\nScript :\n{_j(script)}\n\n"
            f"Bibliographie :\n{_j(dossier.bibliography)}\n\n"
            f"Points incertains / reconstitués :\n{_j(dossier.uncertain_or_controversial)}\n"
            f"{_j([b.narration for b in script.beats if b.reconstructed_without_direct_evidence])}\n\n"
            f"Langue : {self.settings.language_name}. Rédige le package SEO."
        )
        return await self.ask(user, S.SeoPackage)

    async def qa(self, technical_report: dict, script: S.Script, storyboard: S.Storyboard,
                 fact_check: S.QAReport) -> S.QAReport:
        user = (
            f"Rapport technique du montage :\n{_j(technical_report)}\n\n"
            f"Fact-check de l'historien :\n{_j(fact_check)}\n\n"
            f"Script :\n{script.full_narration}\n\n"
            f"Scènes prévues : {len(storyboard.scenes)}.\n\n"
            "Contrôle : durée dans la cible, ratio 9:16 1080×1920, audio présent et normalisé, "
            "sous-titres présents et synchronisés, nombre de scènes rendues, proportion de scènes "
            "en repli (composition animée) acceptable (< 50 %), erreurs historiques. "
            "passed=false uniquement s'il existe un problème bloquant."
        )
        return await self.ask(user, S.QAReport)
