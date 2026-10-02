# Babylon literary Reel: production prompts and pronunciation notes

Status: prepared, not generated. Waiting for storyboard approval and a confirmed Higgsfield top-up.
Storyboard (composition draft): `storyboard/babylon_storyboard.jpg`.
Higgsfield job: 2f0afe40-1d4d-4bde-b4da-73b7a61a68e0.

## Locked rules
- The protagonist stays anonymous: no name in narration, captions, labels, cover, title, description, tags or file names.
- The narration is locked. The ElevenLabs `text` field gets only the approved narration.
- Show «حكاية أدبية» clearly in the opening. Present the story as a book adaptation, not a biography.
- Never suggest that saving one tenth guarantees wealth.
- Use the paper-cut look:
  - white cut-out edges
  - visible paper fibers
  - layered soft shadows
- Build the saving scene in code with exactly 10 coins: 9 stay together and 1 is saved.
- Make the imitation jewels clearly glass:
  - translucent edges
  - reflections
  - code highlights added on top
- Keep secondary characters large and on their own sheet. Small objects go on separate sheets.
- Workflow:
  1. Generate the main character sheet first.
  2. Inspect its style.
  3. Only then generate the remaining sheets.

## Live prices (checked before any paid call; re-check right before generating)
- `gpt_image_2_5`, high, 2k: 2.75 credits (1:1 transparent or 9:16 opaque)
- `gpt_image_2_5`, medium, 2k: 1 credit
- Balance at last check: **1.75 credits**. That is not enough for any high-quality sheet.

## Shared style block (prepended to every prompt)
> Handmade paper-cut collage illustration for a stop-motion animation: watercolor, gouache and crayon details on visible textured paper with fibers, slightly irregular hand-cut edges, a clean bright WHITE paper border around every cut-out, soft warm layered drop shadows, flat layered paper depth (not painterly realism). Palette: cream, kraft beige, mustard, muted teal, soft coral, navy. Ancient Mesopotamia-inspired storybook setting. No text, no letters, no numbers, no names, no logos.

## Protagonist block (sheets 1 and 5)
> The SAME adult man, clearly aged 30–40: brown hair, light brown stubble, mature face, adult hands, simple illustrated eyes with expressive eyebrows, ancient-inspired long mustard robe with a muted teal sash and teal trim. Never a child or teenager. Match the reference storyboard face.

## Sheets
| # | Sheet | Aspect | Cost (high) | Order |
|---|-------|--------|-------------|-------|
| 1 | Protagonist poses (transparent) | 1:1 | 2.75 | **first, inspect before the rest** |
| 2 | Props A: saving and scribe objects (transparent) | 1:1 | 2.75 | after #1 is approved |
| 3 | Props B: expenses, jewels, glass, workshop (transparent) | 1:1 | 2.75 | after #1 |
| 4 | Secondary characters (transparent) | 3:2 | 2.75 | after #1 |
| 5 | Background A: mud-brick interior | 9:16 | 2.75 | after #1 |
| 6 | Background B: mud-brick street and market | 9:16 | 2.75 | after #1 |

- Total: 16.5 credits, plus a 2.75 correction reserve, so **19.25 are needed**.
- With the current 1.75, that means a top-up of at least **17.5**.

### 1. Protagonist poses
Settings: transparent background, reference image = storyboard job.
> [style] [protagonist] Character pose sheet on a fully TRANSPARENT background: FOUR large, clearly separated waist-up cut-outs of the same man in a 2×2 layout with wide empty space between them, nothing overlapping, no scenery. (1) prosperous, richer teal-and-mustard robe, holding up an EMPTY flat crumpled leather pouch and looking at it thoughtfully; (2) seated in profile as a humble scribe, both hands forward pressing a reed stylus downward (table and tablet will be separate layers); (3) looking down at his own open empty palm, disappointed but calm; (4) facing the viewer directly, calm half-smile, holding a reed stylus.

### 2. Props A: saving and scribe objects
Settings: transparent background, 6 items, 2 columns × 3 rows.
> [style] Prop sheet on a fully TRANSPARENT background: SIX large separate objects, each centred in its own cell with wide empty space, nothing touching: (1) a stack of four cuneiform clay tablets; (2) one reed stylus, long and thin, diagonal; (3) ONE single round copper coin, large, front view; (4) a small round clay jar with a cloth-tied lid; (5) an empty, flat, crumpled leather pouch with a loose drawstring; (6) a small full cloth bag of coins tied with string.

### 3. Props B: expenses, jewels, glass, workshop
Settings: transparent background, 6 items, 2 columns × 3 rows.
> [style] Prop sheet on a fully TRANSPARENT background: SIX large separate objects, each in its own cell with wide empty space, nothing touching: (1) a round flatbread loaf; (2) a clay water jug; (3) a folded simple linen garment; (4) a small cluster of five sparkling cut gems in coral, teal and violet, with bright star sparkles; (5) the SAME five pieces revealed as cheap broken colored GLASS: clearly translucent shards with thin see-through edges, cracked surfaces, white reflective glints, light passing through them, dull and worthless (not stones); (6) a round hammered bronze shield with a raised centre boss.

Code adds the dimmed see-through overlay, refraction glints and a short shine sweep on the glass.

### 4. Secondary characters
Settings: transparent background, 3:2, large figures only.
> [style] Character sheet on a fully TRANSPARENT background: THREE large, clearly separated waist-up adult figures side by side with wide gaps, no props except what they hold, no scenery: (1) a brickmaker about 40, clay-dusted hands, simple head cloth, earth-brown tunic, open friendly face; (2) an armorer about 45 in a leather apron, holding a smith's hammer; (3) an elderly wealthy mentor about 65, long grey beard, deep navy robe with mustard trim, wise calm expression.

### 5. Background A: mud-brick interior
Settings: 9:16, opaque.
> [style] Full-bleed vertical background, NO people: warm mud-brick room in layered paper: a small high window (top right), a wooden shelf with clay jars and tablets on the left, a low wooden worktable along the bottom third, an empty clear wall area in the centre for character cut-outs, soft lamp light. Reused for the scribe room, the shield workshop (shields added as layers) and the partnership scene.

### 6. Background B: mud-brick street and market
Settings: 9:16, opaque.
> [style] Full-bleed vertical background, NO people: a Babylon-inspired street of layered paper mud-brick houses, a coral cloth market awning, a tall date palm on one side, open sky at the top, a calm empty centre for characters. Seasons are tinted in code: green, gold, dry, bare.

## Built in code (not generated)
- **Saving scene:** exactly 10 coin instances from the single-coin asset. Nine stay grouped. One slides apart and drops into the jar, with the counter implied visually and no numbers shown.
- **Expenses:** coins flowing out to the bread, jug and garment.
- **Jewels to glass:** a match cut with the music dip.
- **Reinvestment:** a loop of dotted arrows from the shields back into the jar.
- **Growth:** jars grow gradually across paper-page and season transitions, with no magical multiplication.
- **Text:**
  - All Arabic captions.
  - The «حكاية أدبية» label.
  - The final question card «هل عرفت من أنا؟».
  - A small closing credit «مستوحاة من كتاب «أغنى رجل في بابل»».
  - No answer is ever shown.

## Pronunciation notes (George, `eleven_multilingual_v2`)
- **Preview text:** two exact excerpts of the locked narration. No added diacritics, no extra words.
  1. `سألت رجلاً ثرياً عن البداية، فتعلّمت أن أحتفظ بعُشر ما أكسب.`
  2. `وبعد سنوات، اختارني معلّمي شريكاً لإدارة أملاكه، ثم نلت نصيباً من تركته.`
- **Check by transcription and listening for:**

| Word | Expected reading | Risk to watch |
|------|------------------|---------------|
| بعُشر | bi-ʿushri | "one tenth" must not become «عَشر» / «عشرة» (ten) |
| تركته | tarikatihi (his estate) | must not be read «تَرَكتُه» (I left him) |
| نلت | niltu | — |
| معلّمي | muʿallimī | — |
| ناسخاً | nāsikhan | — |
| أجري | ajrī (my wage) | — |
| مدخراتي / أدّخر | muddakharātī / addakhiru | — |
| موّلت | mawwaltu | — |
| مالٍ / رجلٍ | mālin / rajulin | — |
| زجاج | zujāj | — |
| الخبرة | al-khibra | — |

- **Pauses:**
  - The two «…» should give short pauses: after «بابل» and after «والآن».
  - The «!» after «زجاج» marks the reveal.
- **If a word is misread:** report it and propose the smallest fix (one diacritic mark) for approval. Never change the locked text silently. If George cannot read Arabic clearly, propose an Arabic-native voice before switching.
- **Timing:** measure the real recording (duration, pauses, word timings) before setting scene cuts. Expected length is about 55–60 s.

## Music (ElevenLabs Music `eleven_music_v2_5`, 64 s, instrumental) — priced, NOT generated
Flow node `vClfFdeQ8SeoYfm9BeK8` (flow NB0jfUA3VonagF6Qnhcr). Estimate: **960 ElevenLabs credits ($0.096)**.
> About 64 seconds of restrained mystery underscore for an ancient-world storybook narration. Soft plucked strings in the spirit of a lyre or oud played sparsely, a low soft pulse like a slow heartbeat, warm low drone, gentle tension that slowly grows, light hand-frame-drum taps very quietly in the second half. Calm, curious, intimate; never epic or bombastic. Leave lots of space for spoken narration: no busy melody in the mid range. Instrumental only, no vocals, no choir. Gradually warmer and slightly more hopeful toward the end, then finish on a suspended, unresolved plucked note that rings out like an open question.

The music dip at the glass reveal is done in the mix (keyed to the measured «زجاج» time), not baked into the generated track.

## Voice — preview done, full recording PENDING the listening check
- Preview: `audio/preview_george.mp3` (11.6 s, 140 ElevenLabs credits).
- Full narration estimate: **640 ElevenLabs credits ($0.064)**, George `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`,
  locked text + the two approved pronunciation-only diacritics («بعُشْرِ ما أكسب», «نصيباً من تَرِكَتِهِ»).
- The ElevenLabs connector exposes no balance tool, so the available ElevenLabs credits must be confirmed in the ElevenLabs app.

## Panel 8 (approved note)
Passing years are shown through four lighting moods (dawn, noon, dusk, lamp-lit night) plus page-turn transitions; date palms stay leafy in every mood.

## Animation project (`build/`)
- `engine.js` shared paper-cut primitives; `reel.js` scenes keyed to narration words (`cue()`), so the measured recording re-times everything.
- Missing art renders as labelled paper placeholders; a "PROVISIONAL" stamp shows until measured timings replace the estimates.
- Code-built: exactly ten coins (nine stay, one saved), translucent glass shards with a clipped cold shine, reinvestment loop, gradual jar growth, page turns, «حكاية أدبية», «هل عرفت من أنا؟», closing credit.
- `tools/make_timeline.py` (captions + SRT; pass measured word times after recording), `tools/render.cjs` (stills / video).
