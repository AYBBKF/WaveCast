# DOT vs OPUS — "One Million Checks vs Twenty Steps"
YouTube Short · English · 9:16 · 1080×1920 · 30 fps · ~40 s

## 0. What was actually generated (status: 3 Oct 2026)

| Asset | Status | Notes |
|---|---|---|
| Voice lines 1, 2, 3, 5, 6, 9 | **Generated** (ElevenLabs `eleven_v3`) | `audio/vo/01_dot.mp3 … 09_dot.mp3`. All six transcribe correctly; no tags were read aloud. |
| Voice lines 4, 7, 8, 10 | **Not generated** | The ElevenLabs account ran out mid-batch: "quota of 10000 … 22 credits remaining" and "Free Tier access has been disabled … upgrade to a paid subscription". These four need ≈246 credits. |
| Six GPT Image 2.5 keyframes | **Not generated** | Higgsfield balance 1.75 credits (one image costs 2.75 at high, 1 at medium); ElevenLabs out of credits. Prompts are in §3. |
| Higgsfield image-to-video | **Not generated** | No credits. Prompts are in §4. |
| Character art used in the cut | Code-drawn vector stand-ins (`build/mascots.js`) | Drawn to the written character spec; the attached reference image did not reach the session. |
| Mouth animation | Generated from the real audio | Mouth open/close follows each recorded line's loudness. Pending lines keep the mouth closed. |
| SFX + background music | Synthesised in code (royalty-free) | Whooshes, pops, one tick per midpoint check, comedic "boing", quiet plucked-chord loop. |
| WIP video | **Rendered** | `deliverables/one_million_checks_vs_twenty_steps_WIP.mp4`: real audio for 6/10 lines and timed silent slots marked "VO PENDING". |
| SRT | **Generated** | Timed to the actual audio for the 6 recorded lines. The 4 pending lines are estimates and must be re-timed after recording, which happens automatically on rebuild. |

**To finish:** add credits, generate the 4 missing lines with the exact text in §5, then save them as `audio/vo/04_opus.mp3`, `07_dot.mp3`, `08_opus.mp3` and `10_opus.mp3`. Then run:

```
python3 tools/build_audio.py && node tools/render.cjs video build/short_silent.mp4
```

Then mux, as in the README. Shot timings, captions, mouths and the SRT re-time from the real recordings.

## 1. Final timed script & storyboard (timings from the recorded audio; * = estimated, pending VO)

| Time | Shot | Line | Picture | On-screen overlay |
|---|---|---|---|---|
| 0.00–4.16 | 1 | **DOT:** One million numbers. One target. I'll check every single one! | DOT front and centre, finger up, grinning; OPUS small at right, arms crossed, side-eye. | "1,000,000" pill pops; a haystack of number chips; one red target. |
| 4.38–9.45 | 2 | **OPUS:** That's up to a million checks. Are you searching… or taking a census? | Two-shot; OPUS presents with one hand, smug brow; DOT, hands on hips, scowls. | "LINEAR SEARCH: check every item": the cursor walks tile by tile, the counter races, "worst case: 1,000,000 checks". |
| 10.02–12.50 | 2 | **DOT:** Fine, professor. What's your genius plan? | DOT shrugs, half-lidded. | Scan keeps grinding. |
| 12.72–18.72* | 3 | **OPUS:** If the list is already sorted, binary search checks the middle… then eliminates half the possibilities. | OPUS raises a finger and points at the panel; DOT leans in. | Sorted row, "ALREADY SORTED ✓", target 70, pointer on middle 47, "70 > 47 → left half is out", left half greys out. |
| 18.94–21.50 | 4 | **DOT:** Half? That's my motivation after lunch. | DOT sarcastic shrug; OPUS unimpressed. | Halving bar starts: each check splits the range, one half fades, the kept half zooms back to full width. |
| 21.72–26.45 | 4 | **OPUS:** A million items. At most… twenty search steps. | OPUS finger raised; DOT's eyes grow. | "check #1 … #20", "items left: 500,000 → 250,000 → … → 1", 20 dots fill, "at most 20 checks". |
| 26.97–29.67* | 5 | **DOT:** Twenty?! I haven't even opened my code editor. | Whip-in close-up on DOT: hands on cheeks, huge eyes, hop + shake, "boing". | Recap card: LINEAR up to 1,000,000 checks vs BINARY* at most 20 checks ("*on an already-sorted list · counts of checks, not speed"). |
| 30.04–33.04* | 6 | **OPUS:** Sorted list, though. Sorting it first has a cost. | Two-shot; OPUS finger up; DOT deflates. | "unsorted? sort it first": tiles shuffle into order, "sorting = extra work". |
| 33.26–36.22 | 6 | **DOT:** So the winner is… whoever read the requirements. | DOT arms crossed, grumbling. | — |
| 36.44–38.54* | 6 | **OPUS:** Finally. A correct answer. | OPUS deadpan, one eyebrow up. | — |
| 38.8–39.66 | 6 | (button) | DOT snaps back to the opening pose (finger up, grin) for a seamless loop. | — |

## 2. Character bible (stand-ins drawn to this spec; use the same text in every image prompt)
- **DOT (GPT):** green interwoven-knot body, like interlaced rounded bands forming a rosette. Large white eyes with black pupils and expressive thick black eyebrows. Thin black arms and legs, white cartoon gloves, black shoes. Energetic, cheeky, competitive.
- **OPUS (Claude):** coral-orange radial starburst body with rounded spikes. Same eye, eyebrow, limb, glove and shoe construction as DOT. Calm, precise, slightly smug, dry.
- **Style:** clean 2D cartoon, bold even black outlines, flat colours with one soft highlight. Simple light cream background, no text, no numbers.

## 3. Six image prompts (GPT Image 2.5, Sunburst variant, 9:16; attach the character reference image to every call)
Shared suffix for every prompt:
> Clean expressive 2D cartoon, bold uniform black outlines, flat colours with soft single highlight, simple light cream background with a faint dot pattern, characters full-body in the middle third, empty upper area and lower fifth kept clear for captions and graphics. Keep both characters exactly as in the reference image: same silhouettes, colours, proportions, eyes, eyebrows, limbs, gloves, shoes. No text, no numbers, no logos, no speech bubbles. Only these two characters.

1. **Challenge:** DOT (green interwoven-knot mascot) front and centre, chest out, one gloved finger pointing straight up, big confident grin, eyebrows high; OPUS (coral starburst mascot) smaller at the right edge, arms crossed, sceptical side-eye toward DOT.
2. **Census joke:** two-shot, OPUS on the right, one hand presenting toward DOT, one eyebrow raised, smug closed-mouth smile; DOT on the left, hands on hips, eyebrows angled down in offended disbelief.
3. **Check the middle:** OPUS on the right, index finger raised toward the empty upper-left area as if pointing at a floating list, calm teacher expression; DOT smaller on the left, chin on glove, leaning in curiously.
4. **Halving:** both characters smaller at the bottom, looking up at the empty upper half of the frame (graphics will be added there); OPUS composed, finger raised; DOT shrugging with half-lidded sarcastic eyes.
5. **Twenty?!:** close-up of DOT, both gloves on its cheeks, eyes huge, eyebrows shooting up, mouth wide open in comic shock, small motion lines; OPUS peeking in from the right edge, unimpressed.
6. **Caveat + punchline:** two-shot, OPUS finger raised, deadpan half-lidded eyes, one eyebrow up; DOT arms crossed, grumpy frown, eyebrows down.

## 4. Animation prompts (Higgsfield image-to-video, silent, 2D-preserving; one per keyframe)
Shared rules:
> Keep the exact 2D illustration style, outlines, colours and character geometry; no 3D, no morphing, no new characters; camera static or a slow gentle push-in; subtle cartoon timing; silent; mouths closed unless noted (lip-sync is added in the edit).

1. DOT bounces once on the spot and pumps the raised finger; eyebrows lift; blinks once. OPUS stays still except one slow blink and a tiny eyebrow raise. Slow push-in.
2. OPUS's presenting hand makes a small "obviously" flick; one eyebrow rises. DOT taps a foot and narrows its eyes. Both blink once.
3. OPUS raises its finger slightly higher and holds; small nod. DOT leans forward and blinks twice. Gentle push-in toward OPUS.
4. DOT does a slow, exaggerated shrug and drops its shoulders; OPUS holds still, then a single slow blink. Camera static.
5. DOT jolts upward in a quick hop, lands with a squash, and holds the shocked pose with trembling eyebrows; tiny camera shake for 0.3 s. OPUS blinks once.
6. OPUS gives one small deadpan nod with a held eyebrow raise. DOT folds its arms tighter and huffs (shoulders up and down). Final 0.5 s: DOT perks up into the opening "finger up" pose for the loop.

## 5. ElevenLabs voices and copy-ready dialogue
- **DOT:** "Nolan – Nerdy, Energetic, Comedy" (`R9EZoy8pXSL8Yh4yxiew`). Bright, quick, playful American adult male; cheeky confidence. Model `eleven_v3`.
- **OPUS:** "Steve – Mellow Deep Male British" (`jr4BEb8zU7Zqyvq3fU4R`). Composed, low, dry British adult male; understated sarcasm. Model `eleven_v3`.

Text field only: one line per clip, bracketed v3 audio tags only, no other directions.

| # | Voice | Text (paste exactly) | Status |
|---|---|---|---|
| 1 | DOT | `[excited] One million numbers. One target. I'll check every single one!` | generated |
| 2 | OPUS | `[dryly] That's up to a million checks. Are you searching... or taking a census?` | generated |
| 3 | DOT | `[annoyed] Fine, professor. What's your genius plan?` | generated |
| 4 | OPUS | `If the list is already sorted, binary search checks the middle... then eliminates half the possibilities.` | **pending** |
| 5 | DOT | `[sarcastic] Half? That's my motivation after lunch.` | generated |
| 6 | OPUS | `A million items. At most... twenty search steps.` | generated |
| 7 | DOT | `[shocked] Twenty?! I haven't even opened my code editor.` | **pending** |
| 8 | OPUS | `Sorted list, though. Sorting it first has a cost.` | **pending** |
| 9 | DOT | `[grumbling] So the winner is... whoever read the requirements.` | generated |
| 10 | OPUS | `[deadpan] Finally. A correct answer.` | **pending** |

Script tightening vs. the brief:
- Line 8 adds "it" ("Sorting it first…") for natural rhythm.
- Line 2 says "up to a million", keeping the worst-case wording.
- The sorted-list requirement is spoken twice: in lines 4 and 8.

## 6. Fact check (algorithms, not measured GPT/Claude performance)
- **Linear search** checks items one at a time; with 1,000,000 items, the worst case inspects all 1,000,000 (target last or absent). The NIST DADS definition: "Search an array or list by checking items one at a time."
- **Binary search** requires a **sorted** array and repeatedly halves the search interval (NIST DADS).
  - Its worst-case number of midpoint comparisons for n items is ⌊log₂ n⌋ + 1.
  - Since 2¹⁹ = 524,288 < 1,000,000 < 2²⁰ = 1,048,576, the worst case for 1,000,000 items is **20 checks**.
  - The on-screen "items left" sequence after each check is ⌊1,000,000 / 2ᵏ⌋: 500,000; 250,000; … 3; 1. Check #20 inspects the last candidate.
- **No runtime claims:** the video shows counts of checks only ("counts of checks, not speed"). It does not say "X times faster".
- **Sorting cost:** sorting the list first is extra work. The video says so without quantifying it, to avoid unsupported numbers.

Sources:
- NIST Dictionary of Algorithms and Data Structures, "binary search": https://xlinux.nist.gov/dads/HTML/binarySearch.html
- NIST Dictionary of Algorithms and Data Structures, "linear search": https://xlinux.nist.gov/dads/HTML/linearSearch.html
- D. E. Knuth, *The Art of Computer Programming*, Vol. 3 (Sorting and Searching), §6.2.1, binary search analysis (book).

## 7. YouTube title and description
**Title:** One Million Checks vs Twenty Steps 🔍 (Binary Search, Explained by Two Mascots)

**Description:**
DOT wants to check one million numbers, one by one. OPUS needs at most twenty checks… as long as the list is already sorted.

Linear search may inspect every item: up to 1,000,000 checks for a million items. Binary search on a sorted list checks the middle and throws away half each time, so a million items take at most 20 checks (2^20 = 1,048,576). These are counts of checks, not a speed benchmark, and sorting the list first has its own cost.

Sources:
• NIST DADS, binary search: https://xlinux.nist.gov/dads/HTML/binarySearch.html
• NIST DADS, linear search: https://xlinux.nist.gov/dads/HTML/linearSearch.html
• Knuth, The Art of Computer Programming, Vol. 3, §6.2.1

DOT and OPUS are cartoon mascots; the numbers describe algorithms, not the performance of any AI model.
#Shorts #binarysearch #coding #algorithms #computerscience
