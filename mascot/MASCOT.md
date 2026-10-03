# BEAN: channel mascot and sticker pack

A Claude-inspired comedy mascot: a terracotta bean with a small cream asterisk on its forehead.
It is calm, intelligent, slightly smug and unexpectedly funny.

## What was generated and how

| Deliverable | File | Made with |
|---|---|---|
| Three-concept comparison | `concepts/bean_concepts_comparison.png` (1024×680 preview) | **GPT Image 2.5 via Higgsfield**, medium quality, 2K, 1 credit. Job `2896ba18-28df-4cc2-9510-3b47089e984c`. The full 2K original is in the Higgsfield library; this workspace can't reach the Higgsfield CDN, so the local copy is the bridged preview. |
| 8 stickers with white die-cut border | `stickers/01_neutral.png` … `08_talking.png` (2048×2048 RGBA) | **Vector art drawn in code** (`build/bean.js`), traced from concept B. **Not GPT Image output.** The balance after the concept sheet was 0.75 credits, and one GPT Image 2.5 image costs at least 1 credit. |
| 8 borderless cutouts (for animation) | `cutouts/*.png` (2048×2048 RGBA) | Same vector model |
| Contact sheet | `bean_sticker_pack_contact_sheet.png` | Same vector model |

Re-render the pack with `node mascot/tools/render_stickers.cjs [size]`.
Every sticker uses the same transform, so the body occupies the exact same pixels in all eight. Only the face, arms and small extras change, which lets you swap them frame-to-frame in an edit without jitter.

## Why concept B

- **A, soft asterisk:** reads as a flower or cookie. The face is lost inside a busy outline, and the eight rays fight the arms.
- **B, bean (chosen):** a single convex silhouette, ideal for squash and stretch. It has the largest clear face area for mouth swaps and lip-sync. The forehead asterisk brands it without touching the outline, and it reads at 96 px.
- **C, cream blob:** defaults to "grumpy". The cream body vanishes on light backgrounds, and crossed arms merge into the mass.

## Character bible (locked)

- **Body:** upright kidney bean, about 1.9:1 height to width. Wider rounded bottom, slight inward curve on the left side at eye level. Flat terracotta `#C96442`, dark brown outline `#2B1D17` about 1% of body height.
- **Mark:** small 6-ray cream asterisk `#F6E9D7` with rounded ends. Upper-left forehead, about 1/8 of body width. Never on the belly, never another colour.
- **Eyes:** two small vertical oval ink eyes with one tiny white highlight, at about 37% from the top, slightly asymmetric (right eye a hair higher).
- **Brows:** short thick ink dashes, the main acting tool.
- **Mouth:** small, centred just below the eyes. A single ink line, or an open D-shape with a coral tongue `#EE9A7E`.
- **Cheeks:** soft coral blush ovals `#E57B60`.
- **Limbs:** thin ink stick arms with a dot hand, and two thin stick legs with tiny foot ticks. Nothing else.
- **Never:** gloves, shoes, clothing, armour, robot parts, sharp spikes, gradients, 3D, texture, text.
- **Allowed extras (small, outlined):** pale-blue sweat drop `#BFE0EE`, motion ticks, shock ticks, three thought dots, a dark-red anger mark.

## Sticker list

| # | Pose | Face | Gesture / extra |
|---|---|---|---|
| 1 | Neutral | open eyes, relaxed brows, small smile | arms relaxed |
| 2 | Smug grin | half-lidded eyes glancing right, right brow raised | lopsided smirk, hand on hip |
| 3 | Laughing | `^ ^` eyes, big open mouth | hand on belly, other arm up, laugh ticks |
| 4 | Shocked | tall eyes, brows high, small "o" mouth | hands up, shock ticks, sweat drop |
| 5 | Annoyed | flat lids, brows angled down, flat mouth | arms crossed, anger mark |
| 6 | Thinking | eyes up-right, one brow up, pursed mouth | hand on chin, thought dots |
| 7 | Embarrassed | `> <` eyes, hot blush with hatch, wobbly mouth | hands together, sweat drop |
| 8 | Talking | open eyes, brows lifted, open mouth | explaining hand raised |

## Reusable character description (paste into any episode prompt)

> BEAN, a minimal 2D cartoon mascot: an upright terracotta (#C96442) kidney-bean-shaped body with a clean dark-brown (#2B1D17) outline. A small cream (#F6E9D7) six-ray rounded asterisk on the upper-left forehead. Two small vertical oval black eyes with a tiny white highlight, short thick dark eyebrows, a small simple mouth, soft coral blush dots. Thin dark stick arms ending in small round dot hands, two thin stick legs with tiny foot ticks. Flat colours, no gradients, no texture, no 3D, no gloves, no shoes, no clothing, no spikes. Calm, intelligent, slightly smug, unexpectedly funny.

## Image prompts (GPT Image 2.5 on Higgsfield)

**Settings:** model `gpt_image_2_5`, `aspect_ratio 1:1`, `background transparent`, quality `high` for the hero sticker, `medium` for the rest. Attach the concept sheet job `2896ba18-…` or `stickers/01_neutral.png` as the image reference, so the silhouette is copied rather than reinvented.

**Live cost (checked 2026-10-03):**

| Quality | Cost per image | Full pack of 8 |
|---|---|---|
| medium 2K | 1 credit | 8 credits |
| high 2K | 2.75 credits | 22 credits |

**Base prompt** (append one expression line):

```
Single sticker of BEAN, the same character as the reference image: keep the exact same silhouette, proportions, colours, outline weight, asterisk position and eye/mouth placement. [CHARACTER DESCRIPTION]. Thick white die-cut sticker border around the whole character, fully transparent background, centred, full body, front view. No text, no speech bubbles, no scenery, no props.
Expression: <LINE>
```

| # | Expression line |
|---|---|
| 1 | Neutral: calm open eyes, relaxed brows, small gentle smile, arms relaxed at sides. |
| 2 | Smug grin: half-lidded eyes glancing sideways, right eyebrow raised, lopsided smirk, one hand on hip. |
| 3 | Laughing: eyes closed as happy upturned arcs, wide open mouth with coral tongue, one hand on belly, other arm raised, small motion ticks beside the head. |
| 4 | Shocked: eyes slightly taller, eyebrows raised high, tiny round "o" mouth, both hands up beside the head, three short shock ticks above, one small pale-blue sweat drop. |
| 5 | Annoyed: flat half-closed eyelids, eyebrows angled down toward the centre, flat slightly downturned mouth, arms crossed over the body, small dark-red anger mark on the forehead. |
| 6 | Thinking: eyes looking up and to the right, one eyebrow raised, small pursed mouth to one side, one hand on chin, three small rising thought dots (no bubble). |
| 7 | Embarrassed: eyes squeezed shut as > < shapes, strong blush with short hatch lines, small wobbly mouth, both hands together in front, one sweat drop. |
| 8 | Talking: open eyes, brows slightly lifted, mouth open mid-word in a small D-shape, one hand raised palm-up as if explaining. |

**Concept sheet prompt** (the one used for `concepts/bean_concepts_comparison.png`) is stored as Higgsfield job `2896ba18-28df-4cc2-9510-3b47089e984c`. Its outline:
- Three mascots side by side on flat cream.
- A: plump eight-ray rounded asterisk.
- B: terracotta bean with a cream forehead asterisk.
- C: cream blob with a terracotta belly asterisk and thick brows.
- Same palette and the same no-gloves/shoes/spikes/3D/text rules as above.

## Animation notes

- `build/bean.js` exposes `BEAN.drawBean(ctx, pose)` and `BEAN.POSES`. It plugs into the existing canvas pipelines (`short/build`, `reel/build`).
- For lip-sync, cycle the mouth between `smile`, `talk` and `o`, and keep everything else fixed.
- For blinks, set `eyes: 'flat'` for 2 frames.
