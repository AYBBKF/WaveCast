# "Hey Claude, anything new?": YouTube Short production package

English, vertical 9:16, 1080×1920, about 49.5 s. GPT casually asks Claude what's new. Claude brags; GPT roasts.
**This replaces the previous DOT vs OPUS concept completely.**

## 1. What is rendered and what is not

| Asset | Status | Notes |
|---|---|---|
| Timed animatic MP4 | **Rendered** | `deliverables/gpt_asks_claude_whats_new_ANIMATIC.mp4`, 1080×1920, 30 fps, 49.5 s. Vector animation, captions, highlights, synthesised sound effects and quiet music. |
| Captions (SRT) | **Rendered** | `deliverables/whats_new.en.srt`. Timing is provisional until the voices exist. |
| Character animation | **Rendered (code)** | `build/whats_new.js` drives both characters from `mascot/build/bean.js`. It covers blinks, brows, gestures, poses, hops, the speaking mouth, camera moves and reaction holds. |
| ElevenLabs voices (13 lines) | **NOT generated** | The test call for line 1 was refused: *"You have 22 credits remaining, while 34 credits are required."* The animatic is silent where dialogue goes and uses placeholder lip movement. |
| GPT Image 2.5 keyframes (7) | **NOT generated** | Higgsfield balance is 0.75 credits; one image costs 1 credit. |
| Higgsfield animation clips (7) | **NOT generated** | Kling 3.0 costs 7.5 credits per 5 s, or 15 per 10 s. |
| Music | Synthesised placeholder | A soft pluck loop about 24 dB under the dialogue. It stops on the punchline. |

The red **"ANIMATIC · voices pending"** tag on screen disappears automatically once all 13 voice clips exist.

## 2. Fact check (verified 2026-10-03)

| Claim in the script | Source | Notes |
|---|---|---|
| Anthropic studied **171** emotion concepts in **Claude Sonnet 4.5** | Anthropic, ["Emotion concepts and their function in a large language model"](https://www.anthropic.com/research/emotion-concepts-function), published 2 Apr 2026. Paper: [transformer-circuits.pub/2026/emotions](https://transformer-circuits.pub/2026/emotions/index.html) | "We compiled a list of 171 words for emotion concepts… and asked Claude Sonnet 4.5 to write short stories." The script attributes it to Sonnet 4.5, not to a new feature in another model. |
| Emotion representations are **not proof of feelings** | Same article | "None of this tells us whether language models actually feel anything or have subjective experiences." The line reads: "Not proven. Patterns aren't proof of feelings." |
| Working with Blender needs **suitable connected tools** | [Claude Academy: Using the Blender Connector](https://academy.claude.com/tutorials/using-the-blender-connector-in-claude) and [Blender MCP server](https://www.blender.org/lab/mcp-server/) | The connector reaches *your open Blender scene* through Blender's Python API. It needs Blender 4.2+, the Blender add-on running its MCP server, and the connector added in Claude Desktop. On screen: "needs Blender + the Blender connector (MCP)". |
| Local rendering doesn't make Claude free | General behaviour of tool use | Blender renders on your computer, but Claude's planning, messages and tool calls still use tokens. The line reads: "Blender renders locally. My planning still uses tokens." |

**Deliberately absent:** launch dates, benchmark numbers, token counts, and any "launched today" claim.

## 3. Characters (locked)

- **CLAUDE (BEAN):** the new sticker design from `mascot/MASCOT.md`.
  - Terracotta `#C96442` kidney bean with a cream six-ray asterisk on the upper-left forehead.
  - Small oval eyes, thick short brows, stick arms and legs, flat colours, dark-brown outline.
  - Confident, theatrical, dry.
- **GPT (PEBBLE):** new, built in the same flat language so the pair reads as one cast.
  - Round mint-green `#57B58F` pebble with a small cream rounded-hexagon ring on the upper-right forehead and one cheeky hair curl on top.
  - Same eyes, brows, limbs and outline as BEAN. **No OpenAI logo.**
  - Curious, cheeky, quick.
- **Silhouette rule:** GPT is short and round, Claude is tall and curved. They stay distinguishable at thumbnail size.

**Reusable description for image prompts:**

> Two flat 2D cartoon mascots on a warm cream studio set, clean dark-brown (#2B1D17) outlines, flat colours, no gradients, no texture, no 3D. LEFT: "GPT", a short round mint-green (#57B58F) pebble-shaped character with a small cream hexagon-ring mark on its upper-right forehead and a single curly hair on top. RIGHT: "Claude", a taller upright terracotta (#C96442) kidney-bean-shaped character with a small cream six-ray rounded asterisk on its upper-left forehead. Both: two small vertical oval black eyes with a tiny white highlight, short thick dark eyebrows, small simple mouth, soft blush dots, thin dark stick arms with round dot hands, thin stick legs with tiny foot ticks. No gloves, shoes, clothing, logos, spikes, text, letters, captions or speech bubbles.

## 4. Timed storyboard (provisional timing, re-timed automatically from the real voice clips)

| Time | Shot / camera | Dialogue | Visual comedy and gestures |
|---|---|---|---|
| 0.0–1.7 | Two-shot, static | **GPT:** "Hey Claude. Anything new?" | GPT waves; Claude listens and blinks. |
| 2.0–5.9 | Push in to Claude at "whole studio" | **CLAUDE:** "Emotion research. Blender. I'm basically a whole studio now." | Smug presenting hand, then **celebrity pose**: arms up, eyes closed in bliss, spotlight cone, three camera flashes with shutter clicks, twinkles. |
| 5.9–7.0 | Whip-zoom to GPT, vignette | (reaction hold) | **Exaggerated side-eye**: half-lids, eyes hard right, one brow sky-high, arms crossed, leaning away. Claude keeps posing off-frame. |
| 7.0–10.4 | Back to two-shot | **GPT:** "Emotions? So you cry when your code fails now?" | GPT smirks, hand on hip, points at Claude. Claude goes flat-eyed, arms crossed. |
| 10.6–16.3 | Two-shot | **CLAUDE:** "Anthropic studied **171** emotion concepts… inside Claude Sonnet 4.5." | Lecturing finger. **Floating emotion icons** pop in one by one (happy, sad, angry, heart, wow). Source chip at top. GPT ponders, hand on chin. |
| 16.5–17.9 | Two-shot | **GPT:** "So… actual feelings?" | GPT hops, palms up, suspicious brows. |
| 18.1–24.2 | Two-shot | **CLAUDE:** "Not proven. Patterns aren't proof of feelings. Your jokes, though… are testing the theory." | Icons drift away on "aren't proof". On the burn: Claude smirks, hand on hip; a tired face icon pops above Claude; GPT goes flat with an anger mark. |
| 24.7–26.7 | Two-shot | **GPT:** "Okay, philosopher. What about **BLENDER**?" | **3D viewport window** pops in above them: grid, axes, gizmo. No logos. |
| 27.0–32.2 | Two-shot | **CLAUDE:** "Give me the right connector, and I can help build 3D scenes." | Claude raises a plug into the viewport; requirement chip appears. A cube, a sphere, then a **statue of Claude itself** pop into the scene. GPT is impressed despite itself. |
| 32.6–35.0 | Two-shot | **GPT:** "And the rumor about **ZERO TOKENS?**" | A big "0?" coin wobbles in the viewport. GPT has a sly chin rub. |
| 35.3–38.8 | Two-shot | **CLAUDE:** "Blender renders locally. My planning still uses tokens." | Header bar: *Rendering… on your computer* fills to *Rendered locally ✓*, and the scene switches to rendered colours. Then token coins hop from Claude's head into a "planning tokens" meter (no numbers). |
| 39.1–43.2 | Two-shot | **GPT:** "So the GPU does the work… and you take the credit?" | A sweating GPU card with spinning fans appears in the viewport, humming. GPT points accusingly. A gold star slaps onto Claude's chest on "credit". |
| 43.6–45.1 | Push in to Claude | **CLAUDE:** "It's called management." | **Boss pose**: hands behind head, leaning back, smirk. Dashed "imaginary" sunglasses slide down with a ting. |
| 45.8–49.5 | Slow push toward GPT; Claude stays in frame | **GPT:** "Congratulations. You've become an AI startup." | GPT turns to **stare into the camera**, deadpan slow clap, vignette. Music cuts on the punchline. Hold 1 s, then end. |

## 5. ElevenLabs voices and dialogue (copy-ready)

- **Model:** `eleven_v3`, so the bracketed audio tags are performed and not read aloud.
- **Format:** one clip per line, saved as `whats_new/audio/vo/NN_speaker.mp3`.
- **GPT:** "Nolan – Nerdy, Energetic, Comedy" (`R9EZoy8pXSL8Yh4yxiew`). Lively, quick, sarcastic.
- **CLAUDE:** "Steve – Mellow Deep Male British" (`jr4BEb8zU7Zqyvq3fU4R`). Composed, low, slightly smug.
- Keep both voices for every line. Both IDs came from this workspace's voice library.

| # | File | Voice | Text (paste exactly) |
|---|---|---|---|
| 1 | `01_gpt.mp3` | GPT | `[casual] Hey Claude. Anything new?` |
| 2 | `02_claude.mp3` | CLAUDE | `[proudly] Emotion research. Blender. I'm basically a whole studio now.` |
| 3 | `03_gpt.mp3` | GPT | `[teasing] Emotions? So you cry when your code fails now?` |
| 4 | `04_claude.mp3` | CLAUDE | `[matter-of-fact] Anthropic studied one hundred seventy-one emotion concepts... inside Claude Sonnet four point five.` |
| 5 | `05_gpt.mp3` | GPT | `[suspicious] So... actual feelings?` |
| 6 | `06_claude.mp3` | CLAUDE | `[calmly] Not proven. Patterns aren't proof of feelings. [dryly] Your jokes, though... are testing the theory.` |
| 7 | `07_gpt.mp3` | GPT | `[sarcastic] Okay, philosopher. What about Blender?` |
| 8 | `08_claude.mp3` | CLAUDE | `Give me the right connector, and I can help build 3D scenes.` |
| 9 | `09_gpt.mp3` | GPT | `[sly] And the rumor about zero tokens?` |
| 10 | `10_claude.mp3` | CLAUDE | `Blender renders locally. My planning still uses tokens.` |
| 11 | `11_gpt.mp3` | GPT | `[accusing] So the GPU does the work... and you take the credit?` |
| 12 | `12_claude.mp3` | CLAUDE | `[smug, unbothered] It's called management.` |
| 13 | `13_gpt.mp3` | GPT | `[deadpan] Congratulations. You've become an AI startup.` |

**Cost:** 783 characters, about 783 credits for one take of every line. The live rate is about 1 credit per character (34 credits for line 1). Budget about 1,200 credits to allow retakes on the punchlines (lines 6, 12 and 13).

**Script changes from the brief:**
- "I'm *basically* a whole studio *now*."
- "*So* you cry…"
- "Anthropic studied 171 emotion concepts *inside Claude* Sonnet 4.5."
- Added "Patterns aren't proof of feelings" so the disclaimer is explicit.
- "*Give me the right connector*, and I can help build 3D scenes" replaces "With connected tools", which is more natural to say and the same meaning.
- "Blender renders locally. My planning still uses tokens."

Every fact keeps its meaning.

## 6. GPT Image 2.5 keyframe prompts (Higgsfield)

**Settings:**
- `model: gpt_image_2_5`, `aspect_ratio: 9:16`, `quality: medium`, `resolution: 2k`. Live price: 1 credit each.
- Image references: upload `mascot/stickers/01_neutral.png` (Claude) and one GPT pose render. Use **media_upload_widget** in the Higgsfield app; this workspace can't reach Higgsfield's upload host.
- Every prompt starts with the **reusable description** from §3, then the scene.
- The upper 40% of the frame stays empty wall, so captions and the viewport window can be added in the edit. **No text in any image.**

| Key | Covers | Scene prompt (append to the description) |
|---|---|---|
| K1 | 0–4.6 s | Wide two-shot, both standing on the floor line in the lower half. GPT waves with one hand, friendly raised brows, looking at Claude. Claude stands relaxed, arms down, small smile, looking at GPT. Mouths closed. |
| K2 | 4.6–7.0 s | Claude strikes a celebrity pose: both arms up in a V, eyes closed in bliss, wide grin, under a soft cream spotlight cone with three white camera-flash starbursts and small yellow twinkles. GPT beside it gives an exaggerated skeptical side-eye: half-closed eyelids, pupils hard toward Claude, one eyebrow raised very high, arms crossed, leaning away. |
| K3 | 7.0–10.4 s | GPT smirks with one hand on its hip and points at Claude with the other. Claude stands flat-eyed and unimpressed with arms crossed. Mouths closed. |
| K4 | 10.4–24.2 s | Claude lectures with one finger raised, eyebrows lifted. Five small flat round emotion icons float in the empty wall above (happy yellow, sad blue, angry red, pink heart, surprised lilac), no text. GPT ponders with one hand on its chin. Mouths closed. |
| K5 | 24.7–35.0 s | A floating dark-grey 3D-software viewport window (no logos, no text) fills the upper half: perspective grid floor, red and green axis lines, an orange-outlined grey cube, a grey sphere and a small terracotta bean-shaped statue on a pedestal. Claude raises a cable plug up toward the window. GPT looks up at it, impressed, mouth closed. |
| K6 | 35.0–43.5 s | The same viewport window, now rendered in warm colours, with a small grey GPU card with two fans and a sweat drop in its lower-left corner. GPT points accusingly at Claude, brows angled down. Claude has arms crossed, calm half-lidded eyes, and a small gold star sticker on its chest. |
| K7 | 43.5–49.5 s | Claude leans back with both hands behind its head, smug smirk, wearing dashed-outline white "imaginary" sunglasses (outline only, see-through). GPT faces the camera directly, deadpan, eyes looking straight at the viewer, hands together mid-clap. Mouths closed. |

## 7. Higgsfield motion prompts (image to video)

**Settings:**
- `model: kling3_0`, `mode: std`, `sound: off`, `aspect_ratio: 9:16`, `medias: [{role: start_image, value: <keyframe job id>}]`.
- Live prices: 5 s costs 7.5 credits; 10 s costs 15.
- **Prefix every prompt with:** "Keep the exact flat 2D cartoon style, outlines, colours and character shapes; no morphing, no new characters, no 3D, no text. Locked-off static camera. Both mouths stay closed. Subtle cartoon timing."
- The static camera and closed mouths let the edit composite the lip-sync mouth onto whoever is speaking. Only that character's mouth moves.

| Clip | Len | Motion prompt |
|---|---|---|
| K1 | 5 s | GPT waves twice and gives a small bounce, then lowers its arm; both blink once. Claude gives a slow blink and a tiny nod. |
| K2 | 5 s | Claude bounces once in the pose and holds; the flashes pop and fade one after another. GPT's raised eyebrow twitches higher; it leans further away and holds the side-eye. |
| K3 | 5 s | GPT's pointing hand jabs twice; small smug head tilt. Claude blinks slowly once, otherwise still. |
| K4 | 10 s | The emotion icons bob gently and drift upward. Claude's finger wags once. GPT taps its chin twice and blinks; at the end GPT's arms cross. |
| K5 | 10 s | The cube, sphere and statue rotate slowly in the viewport. Claude lifts the plug a little higher and holds. GPT's eyebrows rise slowly; one blink each. |
| K6 | 10 s | The GPU fans spin and the card trembles; the sweat drop slides down. GPT's pointing arm shakes with emphasis twice. Claude stays still with one slow, unbothered blink. |
| K7 | 5 s | Claude leans back a little further and settles. GPT does two slow, deadpan claps while keeping its stare locked on the camera; no other movement. |

**Higgsfield budget:**

| Item | Credits |
|---|---|
| 7 keyframes | 7 |
| 4 clips at 5 s | 30 |
| 3 clips at 10 s | 45 |
| Reserve for one re-roll | 7.5 |
| **Total** | **≈ 90** (balance now 0.75) |

**Leaner option (≈ 30 credits):**
- Generate only K2, K5 and K7, the three hero moments, and keep the vector rig everywhere else.
- Cost: 3 keyframes + 2 × 7.5 + 10 s × 1 + 7.5 reserve.

## 8. Editing instructions

1. **Voices first.**
   - Save the 13 clips to `whats_new/audio/vo/` using the names in §5.
   - Run `python3 whats_new/tools/build_audio.py`. It trims and tightens pauses, re-times every line, caption and visual beat, builds mouth envelopes, re-places the sound effects, and writes the SRT.
2. **Render.**
   - `node whats_new/tools/render.cjs video whats_new/build/video_silent.mp4`
   - Mux with `audio/mix_raw.wav`, then loudnorm to −14 LUFS integrated / −1 dBTP for Shorts.
3. **Lip-sync.** In the code rig, only the speaking character's mouth opens, driven by the real audio envelope. If you use the Kling clips, composite the rig's mouth layer over the speaker in each static shot.
4. **Captions.**
   - Added in the edit only, never inside generated images.
   - Dark box at y ≈ 1545, above the Shorts UI zone, with a speaker tag (mint for GPT, terracotta for CLAUDE).
   - Highlights pop in yellow: **171** (line 4), **BLENDER** (line 7), **ZERO TOKENS?** (line 9).
5. **Sound.**
   - Music about 24 dB under the voices, cut dead on "AI startup".
   - Restrained sound effects only: three shutter clicks, one whoosh on the side-eye whip, soft pops for the icons and viewport, coin blips for tokens, a low GPU hum, a slide-and-ting for the sunglasses, four slow claps.
6. **Ending.** Cut 1 s after the last word, on GPT's stare. No outro card, so it ends on the punchline.

**Title idea:** "I asked Claude what's new. It became a startup."
