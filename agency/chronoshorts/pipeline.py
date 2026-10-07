"""Orchestrateur : enchaîne les agents et les fournisseurs pour produire un Short.

Étapes (chacune persistée dans state.json, reprise possible) :
 1. strategy   — stratège (Haiku) → directeur (Opus) choisit le sujet et l'angle
 2. research   — historien (Haiku, recherche web)
 3. script     — scénariste ⇄ fact-check historien ⇄ revue du directeur (≤ 2 révisions)
 4. duration   — TTS de la narration complète, ajustement du script au débit réel
 5. storyboard — storyboard, puis en parallèle : art bible, voix, plan sonore, SEO
 6. visuals    — prompts → animation → revue du directeur (≤ 1 révision)
 7. media      — par scène, en parallèle : TTS, image clé, clip animé
 8. assemble   — FFmpeg : enchaînement, mixage, sous-titres, encodage
 9. qa         — rapport QA (Haiku) → décision finale (Opus) → Telegram
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import schemas as S
from .agents import (
    AnimatorAgent, ArtDirectorAgent, Director, EditorAgent, HistorianAgent,
    PromptEngineerAgent, ScreenwriterAgent, SeoQaAgent, StoryboardAgent,
    StrategistAgent, VoiceDirectorAgent,
)
from .config import Settings, get_settings
from .llm import LLM, LLMBackend
from .media import ffmpeg as F
from .media.subtitles import build_ass, build_srt
from .providers.image import ImageResult, get_image_provider
from .providers.music import MusicLibrary
from .providers.telegram import Telegram
from .providers.tts import DEFAULT_SECONDS_PER_WORD, TTSResult, WordTiming, get_tts, split_words
from .providers.video import MotionSpec, get_video_provider
from .storage import History, Production

log = logging.getLogger("chronoshorts.pipeline")

SCENE_TAIL = 0.35  # respiration visuelle après la fin de la phrase (s)
VOICE_LEAD = 0.12  # la voix démarre juste après l'entrée de la scène (s)


@dataclass
class ProductionResult:
    production: Production
    video: Path | None
    delivered: bool
    decision: S.FinalDecision | None
    cost_usd: float


class Pipeline:
    def __init__(self, settings: Settings | None = None, llm: LLMBackend | None = None,
                 telegram: Telegram | None = None):
        self.s = settings or get_settings()
        self.llm = llm or LLM(self.s)
        self.telegram = telegram or Telegram(self.s)
        self.director = Director(self.llm, self.s)
        self.historian = HistorianAgent(self.llm, self.s)
        self.strategist = StrategistAgent(self.llm, self.s)
        self.screenwriter = ScreenwriterAgent(self.llm, self.s)
        self.storyboard = StoryboardAgent(self.llm, self.s)
        self.art = ArtDirectorAgent(self.llm, self.s)
        self.prompter = PromptEngineerAgent(self.llm, self.s)
        self.animator = AnimatorAgent(self.llm, self.s)
        self.voice = VoiceDirectorAgent(self.llm, self.s)
        self.editor = EditorAgent(self.llm, self.s)
        self.seoqa = SeoQaAgent(self.llm, self.s)
        self.tts = get_tts(self.s)
        self.images = get_image_provider(self.s)
        self.videos = get_video_provider(self.s)
        self.music = MusicLibrary(self.s)
        self.history = History(self.s)

    # ------------------------------------------------------------------ API
    async def produce(self, seed: str | None = None, resume: Path | None = None,
                      notify_chat: str | None = None) -> ProductionResult:
        t0 = time.monotonic()
        prod = Production(resume) if resume else Production.new(self.s, seed or "short")
        prod.log(f"début (seed={seed!r}, resume={resume})")
        await self._notify(f"🎬 Production lancée{f' — thème : {seed}' if seed else ''}", notify_chat)
        try:
            brief = await self.stage_strategy(prod, seed)
            dossier = await self.stage_research(prod, brief)
            script = await self.stage_script(prod, brief, dossier)
            script, spw = await self.stage_duration(prod, script)
            board, bible, voice, sound, seo = await self.stage_storyboard(prod, brief, dossier, script, spw)
            prompts, anim = await self.stage_visuals(prod, board, bible)
            scenes = await self.stage_media(prod, board, prompts, anim, voice)
            tech = await self.stage_assemble(prod, board, scenes, sound, seo)
            decision, delivered = await self.stage_qa(prod, brief, script, board, tech, seo, dossier, notify_chat)
        except Exception as e:  # noqa: BLE001 — on journalise puis on relance
            prod.log(f"ÉCHEC : {e!r}")
            await self._notify(f"❌ Production échouée : {e}", notify_chat)
            raise
        finally:
            prod.put("costs", self.llm.costs.report())
        self.history.add(brief.chosen_title, brief.civilization, prod.root, delivered)
        prod.log(f"terminé en {time.monotonic() - t0:.0f} s, coût LLM ≈ {self.llm.costs.total_usd():.3f} $")
        return ProductionResult(prod, prod.final_video if prod.final_video.exists() else None,
                                delivered, decision, self.llm.costs.total_usd())

    async def _notify(self, text: str, chat: str | None) -> None:
        try:
            if self.telegram.enabled or chat:
                await self.telegram.send_message(text, chat)
        except Exception as e:  # noqa: BLE001
            log.warning("notification Telegram impossible : %s", e)

    # ------------------------------------------------------------ 1. stratégie
    async def stage_strategy(self, prod: Production, seed: str | None) -> S.EditorialBrief:
        if prod.has("brief"):
            return prod.get("brief", S.EditorialBrief)
        proposals = await self.strategist.propose(self.history.titles(), seed)
        prod.put("proposals", proposals)
        spw = DEFAULT_SECONDS_PER_WORD[self.s.language]
        target_words = int(((self.s.target_duration_min + self.s.target_duration_max) / 2 - 1.5) / spw)
        brief = await self.director.choose_topic(proposals, self.history.titles(), self.s.language_name, target_words)
        prod.put("brief", brief)
        prod.log(f"sujet : {brief.chosen_title}")
        return brief

    # ------------------------------------------------------------ 2. recherche
    async def stage_research(self, prod: Production, brief: S.EditorialBrief) -> S.ResearchDossier:
        if prod.has("dossier"):
            return prod.get("dossier", S.ResearchDossier)
        dossier = await self.historian.research(brief)
        prod.put("dossier", dossier)
        return dossier

    # ------------------------------------------------------------ 3. script
    async def stage_script(self, prod: Production, brief: S.EditorialBrief,
                           dossier: S.ResearchDossier) -> S.Script:
        if prod.has("script"):
            return prod.get("script", S.Script)
        script = await self.screenwriter.write(brief, dossier)
        for round_ in range(3):
            fact = await self.historian.fact_check(script, dossier)
            review = await self.director.review_script(script, dossier, fact)
            prod.put(f"script_review_{round_}", {"fact_check": fact.model_dump(), "director": review.model_dump()})
            if review.approved and fact.passed:
                break
            instructions = review.revision_instructions
            blocking = [i for i in fact.issues if i.severity == "bloquant"]
            if blocking:
                instructions += "\n\nProblèmes historiques bloquants :\n" + "\n".join(
                    f"- {i.description} → {i.suggested_fix}" for i in blocking)
            if round_ == 2:
                prod.log("script accepté avec réserves après 3 tours")
                break
            prod.log(f"script : révision demandée (tour {round_ + 1})")
            script = await self.screenwriter.write(brief, dossier, revision=instructions, previous=script)
        prod.put("fact_check", fact)
        prod.put("script", script)
        return script

    # ------------------------------------------------------------ 4. durée
    async def stage_duration(self, prod: Production, script: S.Script) -> tuple[S.Script, float]:
        """Mesure la durée réelle de la narration et adapte le script (jamais la vitesse)."""
        if prod.has("duration"):
            d = prod.get("duration")
            return prod.get("script", S.Script), d["seconds_per_word"]
        lo, hi = self.s.target_duration_min, self.s.target_duration_max
        # marge pour les respirations entre scènes
        for attempt in range(3):
            res = await self.tts.synthesize(script.full_narration, prod.root / "audio" / f"full_{attempt}.wav")
            words = max(1, len(split_words(script.full_narration)))
            spw = res.duration / words
            est_total = res.duration + SCENE_TAIL * max(8, round(res.duration / 4.5))
            prod.log(f"narration {res.duration:.1f} s ({words} mots, {spw:.3f} s/mot) → vidéo ≈ {est_total:.1f} s")
            if lo <= est_total <= hi or attempt == 2:
                break
            script = await self.screenwriter.fit_duration(script, est_total, lo, hi)
            prod.put("script", script)
        prod.put("duration", {"narration_seconds": res.duration, "estimated_total": est_total,
                              "seconds_per_word": spw})
        return script, spw

    # ------------------------------------------------------------ 5. storyboard
    async def stage_storyboard(self, prod: Production, brief: S.EditorialBrief, dossier: S.ResearchDossier,
                               script: S.Script, spw: float):
        if prod.has("storyboard") and prod.has("seo"):
            return (prod.get("storyboard", S.Storyboard), prod.get("art_bible", S.ArtBible),
                    prod.get("voice_script", S.VoiceScript), prod.get("sound_plan", S.SoundPlan),
                    prod.get("seo", S.SeoPackage))
        board_task = asyncio.create_task(self.storyboard.breakdown(script, spw))
        seo_task = asyncio.create_task(self.seoqa.seo(brief, script, dossier))
        board = await board_task
        board = _repair_storyboard(board, script, spw, self.s)
        prod.put("storyboard", board)
        bible, voice, sound, seo = await asyncio.gather(
            self.art.art_bible(brief, dossier, board),
            self.voice.prepare(board),
            self.editor.sound_plan(board, brief),
            seo_task,
        )
        voice = _repair_voice_script(voice, board)
        prod.put("art_bible", bible)
        prod.put("voice_script", voice)
        prod.put("sound_plan", sound)
        prod.put("seo", seo)
        return board, bible, voice, sound, seo

    # ------------------------------------------------------------ 6. visuels
    async def stage_visuals(self, prod: Production, board: S.Storyboard, bible: S.ArtBible):
        if prod.has("animation"):
            return prod.get("prompts", S.PromptPack), prod.get("animation", S.AnimationPlan)
        prompts = await self.prompter.prompts(board, bible)
        prompts = _align_by_scene(prompts, board, "scenes", "scene_index")
        anim = await self.animator.animate(board, prompts, bible)
        anim = _align_by_scene(anim, board, "scenes", "scene_index")
        review = await self.director.review_visuals(board, bible, anim)
        prod.put("visual_review", review)
        if not review.approved and review.revision_instructions:
            prod.log("visuels : révision demandée par le directeur")
            # Une passe de correction : l'animateur réapplique les consignes.
            self.animator.description += f"\n\nCONSIGNES DU DIRECTEUR À APPLIQUER :\n{review.revision_instructions}"
            anim = await self.animator.animate(board, prompts, bible)
            anim = _align_by_scene(anim, board, "scenes", "scene_index")
        prod.put("prompts", prompts)
        prod.put("animation", anim)
        return prompts, anim

    # ------------------------------------------------------------ 7. médias
    async def stage_media(self, prod: Production, board: S.Storyboard, prompts: S.PromptPack,
                          anim: S.AnimationPlan, voice: S.VoiceScript) -> list[dict[str, Any]]:
        if prod.has("scenes_media"):
            return prod.get("scenes_media")
        sem = asyncio.Semaphore(self.s.max_concurrency)
        prompt_by = {p.scene_index: p for p in prompts.scenes}
        anim_by = {a.scene_index: a for a in anim.scenes}
        voice_by = {v.scene_index: v for v in voice.segments}
        seed = abs(hash(board.scenes[0].setting)) % 2_000_000

        async def one(scene: S.Scene) -> dict[str, Any]:
            async with sem:
                i = scene.index
                p, a, v = prompt_by[i], anim_by[i], voice_by[i]
                sdir = prod.root / "scenes"
                tts = await self.tts.synthesize(v.text, prod.root / "audio" / f"scene_{i:02d}.wav")
                seconds = max(self.s.scene_min_seconds - 1.0, tts.duration + SCENE_TAIL + VOICE_LEAD)
                image = await self._with_retry(lambda: self.images.generate(
                    p.image_prompt, p.negative_prompt, sdir / f"scene_{i:02d}.png", seed=seed + i))
                spec = MotionSpec(prompt=a.enriched_video_prompt or p.video_prompt, negative=p.negative_prompt,
                                  seconds=seconds, zoom=a.kenburns_zoom, pan=a.kenburns_pan)
                clip = await self.videos.animate(image, spec, sdir / f"scene_{i:02d}_raw.mp4")
                norm = sdir / f"scene_{i:02d}.mp4"
                real = await F.normalize_clip(clip.path, norm, seconds, self.s.width, self.s.height, self.s.fps)
                prod.log(f"scène {i}: voix {tts.duration:.2f}s, clip {real:.2f}s ({clip.method})")
                return {"index": i, "clip": str(norm), "seconds": real, "method": clip.method,
                        "transition": scene.transition_out, "tts": tts.to_json(), "image": str(image.path)}

        results = await asyncio.gather(*(one(sc) for sc in board.scenes))
        results.sort(key=lambda r: r["index"])
        prod.put("scenes_media", results)
        return results

    async def _with_retry(self, fn, attempts: int = 3):
        last: Exception | None = None
        for k in range(attempts):
            try:
                return await fn()
            except Exception as e:  # noqa: BLE001
                last = e
                log.warning("tentative %d échouée : %s", k + 1, e)
                await asyncio.sleep(2 * (k + 1))
        raise RuntimeError(f"échec après {attempts} tentatives : {last}")

    # ------------------------------------------------------------ 8. montage
    async def stage_assemble(self, prod: Production, board: S.Storyboard, scenes: list[dict[str, Any]],
                             sound: S.SoundPlan, seo: S.SeoPackage) -> dict[str, Any]:
        if prod.has("technical_report") and prod.final_video.exists():
            return prod.get("technical_report")
        entries = [F.TimelineEntry(Path(sc["clip"]), sc["seconds"], sc["transition"]) for sc in scenes]
        video_path = prod.root / "video_silent.mp4"
        offsets, total = await F.concat_with_transitions(entries, video_path, self.s.fps)

        segments: list[tuple[Path, float]] = []
        words: list[WordTiming] = []
        for sc, off in zip(scenes, offsets):
            tts = TTSResult.from_json(sc["tts"])
            start = off + VOICE_LEAD
            segments.append((tts.audio_path, start))
            words += [WordTiming(w.word, w.start + start, w.end + start) for w in tts.words]

        music_path, music_src = await self.music.music_for(sound.music_mood, total, prod.root / "audio")
        ambience = self.music.ambience_for(sound.ambience_tags)
        sfx: list[tuple[Path, float]] = []
        for cue in sound.sfx_cues:
            # format libre "scène 3 : cloche" → on cherche un tag présent en bibliothèque
            for tag in cue.replace(":", " ").split():
                p = self.music.sfx_for(tag.lower())
                if p:
                    num = next((int(t) for t in cue.split() if t.isdigit()), 1)
                    idx = max(0, min(len(offsets) - 1, num - 1))
                    sfx.append((p, offsets[idx]))
                    break
        mix_path = prod.root / "audio" / "mix.wav"
        await F.mix_audio(segments, music_path, ambience, sfx, mix_path, total)

        font = self.s.font_arabic if self.s.is_rtl else self.s.font_latin
        ass = build_ass(words, prod.root / "subtitles.ass", width=self.s.width, height=self.s.height,
                        font=font, style=sound.subtitle_style, rtl=self.s.is_rtl)
        build_srt(words, prod.root / "subtitles.srt")
        await F.mux_final(video_path, mix_path, ass, prod.final_video)
        await F.extract_frame(prod.final_video, min(1.0, total / 2), prod.root / "thumbnail_frame.jpg")

        info = await F.video_info(prod.final_video)
        lufs = await F.measure_loudness(prod.final_video)
        fallback = sum(1 for sc in scenes if sc["method"] == "kenburns")
        report = {
            "duration": round(info.duration, 2), "width": info.width, "height": info.height,
            "fps": round(info.fps, 2), "video_codec": info.video_codec, "audio_codec": info.audio_codec,
            "audio_channels": info.audio_channels, "loudness_lufs": lufs,
            "ratio_ok": abs(info.width / info.height - 9 / 16) < 0.01,
            "duration_in_target": self.s.target_duration_min <= info.duration <= self.s.target_duration_max,
            "scenes_planned": len(board.scenes), "scenes_rendered": len(scenes),
            "scenes_fallback_kenburns": fallback, "scenes_ai_video": len(scenes) - fallback,
            "subtitles": "ass (mot à mot) + srt", "subtitle_words": len(words),
            "music": music_src, "ambience": str(ambience) if ambience else "aucune", "sfx": len(sfx),
            "file_size_mb": round(prod.final_video.stat().st_size / 1e6, 2),
        }
        prod.put("technical_report", report)
        self._write_metadata(prod, seo, report)
        return report

    def _write_metadata(self, prod: Production, seo: S.SeoPackage, report: dict[str, Any]) -> None:
        script = prod.get("script", S.Script)
        dossier = prod.get("dossier", S.ResearchDossier)
        meta = {
            "title": seo.title, "description": seo.description, "hashtags": seo.hashtags, "tags": seo.tags,
            "sources": seo.sources_block, "editorial_disclaimer": seo.editorial_disclaimer,
            "thumbnail_concept": seo.thumbnail_concept,
            "reconstructed_without_direct_evidence": [b.narration for b in script.beats
                                                     if b.reconstructed_without_direct_evidence],
            "uncertain_or_controversial": dossier.uncertain_or_controversial,
            "historical_notes": script.historical_notes, "bibliography": dossier.bibliography,
            "technical": report, "language": self.s.language,
        }
        (prod.root / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------ 9. QA + livraison
    async def stage_qa(self, prod: Production, brief: S.EditorialBrief, script: S.Script, board: S.Storyboard,
                       tech: dict[str, Any], seo: S.SeoPackage, dossier: S.ResearchDossier,
                       notify_chat: str | None) -> tuple[S.FinalDecision, bool]:
        fact = prod.get("fact_check", S.QAReport) or S.QAReport(passed=True, score=100, issues=[], summary="n/a")
        qa = await self.seoqa.qa(tech, script, board, fact)
        prod.put("qa_report", qa)
        decision = await self.director.final_decision(qa, tech, seo)
        prod.put("final_decision", decision)
        authorized = decision.authorize_telegram if self.s.require_director_approval else qa.passed
        delivered = False
        if authorized and (self.telegram.enabled or notify_chat):
            caption = f"{seo.title}\n\n{brief.civilization} — {brief.period}\n{' '.join(seo.hashtags[:6])}"
            await self.telegram.send_video(prod.final_video, caption, tech["width"], tech["height"],
                                           tech["duration"], notify_chat)
            details = (f"📝 Description :\n{seo.description}\n\n{seo.sources_block}\n\n"
                       f"⚠️ {seo.editorial_disclaimer}\n\n🎯 QA {qa.score}/100 — {qa.summary}\n"
                       f"🎬 Directeur : {decision.verdict}\n"
                       f"⏱ {tech['duration']} s · {tech['scenes_ai_video']} scènes IA / "
                       f"{tech['scenes_fallback_kenburns']} composition animée · coût LLM ≈ "
                       f"{self.llm.costs.total_usd():.2f} $")
            await self.telegram.send_message(details, notify_chat)
            await self.telegram.send_document(prod.root / "metadata.json", "metadata.json", notify_chat)
            delivered = True
            prod.log("livré sur Telegram")
        elif authorized:
            prod.log("autorisé mais Telegram non configuré")
        else:
            prod.log(f"diffusion refusée par le directeur : {decision.verdict}")
            await self._notify(f"⛔ Vidéo non diffusée — {decision.verdict}\nDossier : {prod.root}", notify_chat)
        prod.put("delivered", delivered)
        return decision, delivered


# ---------------------------------------------------------------------------
# Réparations déterministes des sorties d'agents (robustesse)
# ---------------------------------------------------------------------------
def _repair_storyboard(board: S.Storyboard, script: S.Script, spw: float, s: Settings) -> S.Storyboard:
    """Ré-indexe, recale les durées sur le débit mesuré, découpe les scènes trop longues."""
    scenes: list[S.Scene] = []
    for sc in board.scenes:
        n_words = len(split_words(sc.narration))
        est = n_words * spw
        if est > s.scene_max_seconds + 1.5 and n_words >= 10:
            # découpe en deux moitiés de mots
            w = split_words(sc.narration)
            half = len(w) // 2
            for part in (w[:half], w[half:]):
                c = sc.model_copy(update={"narration": " ".join(part),
                                          "target_seconds": min(8.0, max(2.0, len(part) * spw))})
                scenes.append(c)
        else:
            scenes.append(sc.model_copy(update={"target_seconds": min(8.0, max(2.0, est or sc.target_seconds))}))
    for k, sc in enumerate(scenes):
        sc.index = k
    scenes[-1].transition_out = "fondu noir"
    return S.Storyboard(scenes=scenes, rhythm_notes=board.rhythm_notes)


def _repair_voice_script(voice: S.VoiceScript, board: S.Storyboard) -> S.VoiceScript:
    by = {v.scene_index: v for v in voice.segments}
    segs = []
    for sc in board.scenes:
        v = by.get(sc.index)
        if v is None or not v.text.strip():
            v = S.VoiceSegment(scene_index=sc.index, text=sc.narration, emotion=sc.emotion, pace="normal")
        segs.append(v)
    return S.VoiceScript(narrator_persona=voice.narrator_persona, segments=segs,
                         pronunciation_notes=voice.pronunciation_notes)


def _align_by_scene(pack, board: S.Storyboard, list_attr: str, key: str):
    """Garantit une entrée par scène (index exact), en dupliquant la plus proche si besoin."""
    items = getattr(pack, list_attr)
    by = {getattr(it, key): it for it in items}
    out = []
    for sc in board.scenes:
        it = by.get(sc.index)
        if it is None:
            nearest = min(items, key=lambda x: abs(getattr(x, key) - sc.index))
            it = nearest.model_copy(update={key: sc.index})
        out.append(it)
    return pack.model_copy(update={list_attr: out})
