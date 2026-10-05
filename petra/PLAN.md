# كيف نحت الأنباط واجهات البتراء؟: Petra Reel plan (storyboard stage)

DEEP CURIOUS · Arabic educational Reel · 9:16, 1080×1920, 30 fps · target 55–65 s (set by the real narration)

**Status: storyboard approved; Reel rendered with free fallbacks.** Both paid routes were still unfunded on 2026-10-05 (Higgsfield 0 credits; ElevenLabs refused the 38-credit preview with 22 credits left). See §7 for exactly what made what.

## 1. Tools, balances and live prices (checked 2026-10-05)

| Service | Balance | Live price | Notes |
|---|---|---|---|
| Higgsfield | **0 credits** | GPT Image 2.5: 1 credit (medium 2K), 2.75 credits (high 2K) | The 0.75 seen on 3 Oct is gone. The transaction log shows no spending after the mascot sheet (3 Oct, −1 credit), so the cause can't be determined from here. |
| ElevenLabs | ~22 credits at the last refusal (3 Oct); can't be queried directly | Pronunciation preview: **38**. Full narration (George, `eleven_multilingual_v2`): **673**. GPT Image 2.5 storyboard via ElevenLabs: **≈190** | Music is roughly 15 credits per second (Babylon: 877.5 for 58.5 s), so about **900** for 60 s. |

Because both image routes are unfunded, the storyboard is a **code-drawn paper-cut planning sketch** (`storyboard/`), **not GPT Image 2.5 output**. It is labelled that way on the sheet.

## 2. Sources and what they support

- **AMNH, "A Walk Through the Ruins of Petra"** (amnh.org/explore/ology/archaeology/a-walk-through-the-ruins-of-petra):
  - Petra is in "modern-day Jordan" and thrived "more than 2,000 years ago".
  - Monuments were cut "with hammers, chisels, and other tools".
  - "The entranceways to a few tombs and temples have been found unfinished. These discoveries show that builders usually carved from the top down."
  - The Royal Tombs are the Palace, Corinthian, Silk and **Urn** Tombs; "archaeologists still don't know who was buried in each tomb".
  - "Petra might seem like a city of tombs… The rest of the city was filled with buildings that have collapsed." The page also covers houses (Ez-Zantur), markets on the Colonnaded Street, and temples (Great Temple, Qasr al-Bint, Temple of the Winged Lions).
  - The Treasury's purpose is uncertain (a king's monument, possibly also a temple), so the Reel never calls it a tomb.
- **UNESCO World Heritage List no. 326** (whc.unesco.org/en/list/326):
  - "Petra is half-built, half-carved into the rock."
  - It describes "rock-cut tombs" as well as "freestanding temples", city walls and water systems.
  - The "royal tombs" include the Khasneh, the **Urn Tomb**, the Palace Tomb and the Corinthian Tomb, dating to the "first centuries BC to AD".
- **Visit Petra, the official site of the Petra Development & Tourism Region Authority** ([visitpetra.jo/en/Location/119](https://www.visitpetra.jo/en/Location/119)):
  - The Urn Tomb is "a Nabataean tomb", "most likely dated to the first half of the first century AD".
  - Its tall facade has engaged columns between pilasters and three niches. Two doorways open onto a large interior hall (18.95 × 17.15 m).
  - A Byzantine inscription records its conversion into a church in AD 447.

## 3. Narration review (no factual corrections required)

Every claim is supported by the sources above:
- **Jordan and "about 2,000 years ago":** AMNH and UNESCO.
- **Hammers and chisels:** AMNH.
- **"Often" top-down, inferred from unfinished facades:** AMNH; the narration's wording is suitably hedged.
- **"Many" facades were tombs:** UNESCO and AMNH; it says "many", not "all".
- **Houses, markets and temples:** AMNH and UNESCO.

**Optional, not required:**
- Line 3 could add «وأدواتٍ أخرى» to mirror AMNH's "and other tools". As written it is still accurate.
- «المفاجأة» appears twice (lines 4 and 7). Line 7 says «المفاجأة الأكبر», so the repetition reads as an escalation. I'd keep it.

**Pronunciation preview text** (ElevenLabs text field only): `البتراء، الأنباط، الأزاميل، النحّاتون.`
If George misreads a word, I'll propose the smallest fix (one diacritic, e.g. «البَتْراء», «الأَنْباط») before recording. I won't change the text silently.

**Locked narration text** (paste as-is; 116 words, 673 characters):

```
تخيّل أن تصنع واجهة كاملة… بإزالة أجزاء من الجبل!
هذا ما فعله الأنباط في واجهات البتراء، في الأردن، قبل نحو ألفي عام.
بالمطارق والأزاميل، أزال النحّاتون الحجر تدريجياً، حتى ظهرت الزخارف والأعمدة والمداخل من الصخر نفسه.
والمفاجأة؟ تشير واجهات لم يكتمل نحتها إلى أنهم غالباً بدأوا من الأعلى، ثم نزلوا إلى الأسفل.
تخيّل الجزء العلوي وقد ظهرت تفاصيله، بينما لا يزال ما تحته صخرة خشنة!
ضربة بعد ضربة، يتحوّل الجبل إلى واجهة مدهشة.
لكن المفاجأة الأكبر خلف المدخل: كثير من هذه الواجهات الفخمة كانت لمقابر!
ومع ذلك، كانت البتراء مدينة فيها بيوت وأسواق ومعابد أيضاً.
والآن انظر إلى هذه التفاصيل… وتخيّل الصخرة قبل أول ضربة.
أيّهما أصعب في رأيك: بناء واجهة بالحجارة، أم نحتها من جبل؟
```

**Expected length:** about 55–60 s. Babylon's 110 words came to 58.2 s with George. If it runs short, I'll add silence only inside existing pauses; no words change.

## 4. Storyboard v1

Files:
- `storyboard/petra_storyboard_v1.png`: full resolution, 1396×2748.
- `storyboard/petra_storyboard_v1_preview.jpg`.
- `storyboard/sb.js`: the editable source.

Shared drawing kit: `build/paper.js` (paper grain, fibres, torn white borders, watercolour blooms, crayon hatching, drop shadows, tracing-paper overlays).

| # | Time (provisional) | Panel | Accuracy guard on screen |
|---|---|---|---|
| 1 | 0–3 s | Rough rose-sandstone cliff; the artisan strikes; a chip falls; a ghosted facade outline and a "؟" pose the question | — |
| 2 | 3–10 s | Paper rock layers peel away; the facade emerges, still joined to the cliff | — |
| 3 | 10–16 s | Adult forearms in mustard sleeves: hammer on chisel, chips, tool marks; inset map of Jordan marking Petra | Map is a simplified outline |
| 4 | 16–23 s | Unfinished facade: carved top, rough bottom; code-drawn downward arrow | Small label «تصوّر مبسّط» (simplified illustration) |
| 5 | 23–31 s | Close-up column freed from the stone, then pull back: the artisan is tiny beside the facade | — |
| 6 | 31–39 s | Warm light sweeps the finished facade; push in toward the doorway | Not called a tomb (the Treasury-like facade's purpose is debated) |
| 7 | 39–47 s | **Urn Tomb** (documented), then a schematic cutaway: facade, doorway, carved hall. «مقابر» appears. No bodies. | «قبر الجرّة» + «تصوّر مبسّط» |
| 8 | 47–55 s | Living city: small rock-cut tombs on the cliff; a freestanding temple, houses and market stalls on the valley floor | Built city ≠ all carved |
| 9 | 55–65 s | The rough cliff wipes back over half the facade and then reveals it again; final question; the last frame matches panel 1 for the loop | — |

**Consistency:**
- **Facade:** one geometry (`PAPER.facade(stage)`), so panels 2, 4, 6 and 9 share the same viewpoint, scale and layout.
- **Carving stages:** the carving line moves top-down, and rough rock with chisel marks covers what is not yet carved.
- **Artisan:** fictional, about 35, brown hair, light stubble, mustard tunic with a muted-teal sash, adult proportions (about 7.5 heads tall).

## 5. Production asset plan after approval (Higgsfield GPT Image 2.5)

**Rules:**
- **Viewpoint:** front elevation, same lens.
- **Backgrounds:** plain flat parchment or transparent.
- **No text** in any image.
- **Style lock** in every prompt: *"handmade paper-cut collage, watercolour, gouache and crayon textures, visible paper fibres, irregular white cutout borders, layered paper, soft shadows; palette parchment cream, kraft beige, rose sandstone, terracotta, mustard, muted teal, midnight navy"*.
- **Transparency:** request a transparent background where supported, then check the alpha in the downloaded files. If the alpha is fake, cut out by flood fill (as in earlier projects).

| # | Asset | Quality | Credits |
|---|---|---|---|
| A1 | **Artisan character sheet**: 6 poses with generous spacing (strike, chisel, standing, looking up, walking, pointing); same face, clothes, proportions | high | 2.75 |
| A2 | **Completed facade master**: front elevation, isolated, full detail | high | 2.75 |
| A3 | Rough sandstone cliff and rock-layer plates (3–4 tearable layers, aligned to A2's footprint) | medium | 1 |
| A4 | Tools and fragments sheet: hammer, chisel, stone chips, dust puffs, column capital, cornice pieces | medium | 1 |
| A5 | Close-up forearms and hands holding hammer and chisel (mustard sleeves) | medium | 1 |
| A6 | Siq/canyon background (layered, for parallax) | medium | 1 |
| A7 | Urn Tomb exterior (documented features: urn on pediment, three niches, engaged columns, vaulted substructure) | medium | 1 |
| A8 | Simplified city background (tombs on the cliff; houses, market and temple on the valley floor) | medium | 1 |
| | **Subtotal** | | **11.5** |
| | Correction reserve (one high re-roll + one medium) | | **3.75** |
| | **Higgsfield total to approve** | | **15.25** |

**Built in code, at no cost:**
- The partially carved stages: A2 masked from the top down with A3 rock layers. This guarantees the same layout in every stage, which separate generations can't.
- The Urn Tomb cutaway schematic, the Jordan map, the arrows, all Arabic captions and on-screen words, and the light sweeps.

**ElevenLabs** (credits must cover this; the last seen balance was ~22):

| Item | Credits |
|---|---|
| Pronunciation preview | 38 |
| Full narration | 673 |
| One retake allowance | 673 |
| Music (~60 s) | ≈ 900 |
| **Total** | **≈ 2,284** (minimum without a retake ≈ 1,611) |

Sound effects (chisel taps, falling fragments, canyon ambience, paper transitions) will be synthesised in code or taken from royalty-free stock. The mix target is −16 LUFS integrated with true peak ≤ −1 dBTP, with narration dominant.

## 6. After approval

1. Pronunciation preview (38 credits). Report what can and can't be verified.
2. Full narration. Measure duration, pauses and word timings, and set cuts to the measured audio.
3. Generate assets A1, then A2, inspecting each before continuing, then A3–A8.
4. Build the animation: parallax, masks, controlled stone removal, falling fragments. Captions in 2–6-word groups, at most two lines, right-to-left, inside mobile-safe areas.
5. Music and sound effects; mix and master.
6. Deliver the MP4, Arabic SRT, vertical cover, Arabic title, description, tags, sources and project files.

## 7. Production record (what was actually used)

| Element | Made with | Notes |
|---|---|---|
| Narration | **Piper TTS, voice `ar_JO-kareem` (medium), offline open-source**, run in the Higgsfield sandbox (no credits) | Not George/ElevenLabs. Input was a fully diacritized copy of the locked narration; a script verified the letters are identical to the locked text (only vowel marks added). Length scale 0.68, so 116 words come to about 64 s. |
| Narration check | faster-whisper `small` (Arabic) in the sandbox | Every line was recovered in order. Small-model slips are on hard words such as تدريجياً, خشنة and the ي of ألفي. There was no listening check (I can't hear audio). |
| Artwork and animation | **Code-drawn paper-cut collage** (`build/paper.js`, `build/reel.js`) | Not GPT Image 2.5. One facade geometry drives every carving stage. Stop-motion "boil" on the cut edges at 8 fps. |
| Music | Synthesised in `tools/build_audio.py`: Karplus-Strong oud-like plucks in D Hijaz, a drone, a frame-drum pulse | Not ElevenLabs Music. Opens up at the reveal, dips at the tomb twist, returns warmer (D major) at the end. |
| Sound effects | Synthesised: chisel clinks, stone fragments, paper peels, pops, whoosh, thud, canyon wind | Cue times are exported from the animation (`build/cues.json`). |
| Captions and SRT | Drawn in code (Cairo, right-to-left, per-word highlights); `deliverables/petra_ar.srt` | 30 groups of 2–6 words, timed to the measured audio. |

**Rebuild:**
1. `python3 tools/make_timeline.py`
2. `node tools/render.cjs cues build/cues.json`
3. `python3 tools/build_audio.py`
4. `node tools/render.cjs video build/video_silent.mp4`, then mux with `audio/mix_master.wav`
5. `node tools/render.cjs cover deliverables/petra_cover_1080x1920.png`

**Upgrade path:** with credits, swap in George for `audio/narration_kareem.mp3` and re-run from step 1 (all cuts follow the new timing). Generated art can replace the code layers one at a time.
