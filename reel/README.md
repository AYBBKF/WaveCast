# DEEP CURIOUS — «ماذا لو اندلعت الحرب العالمية الثالثة؟» (Arabic Reel)

Vertical 1080×1920, 30 fps, 61.5 s. Hypothetical educational explainer, paper-cut style.

## Deliverables (`deliverables/`)
- `deep_curious_ww3_ar_1080x1920.mp4` — final video with burned-in Arabic captions (−16 LUFS, −1.5 dBTP)
- `deep_curious_ww3_ar.srt` — Arabic subtitles
- `cover_bila_qasf.png` — vertical cover «بلا قصف؟» + «سيناريو افتراضي»
- `publishing_ar.md` — title, description, tags, sources, credits

## Project
- `assets/layers/` — reusable transparent cutouts (4 character poses, ship, truck, fuel pump, barrel, factory, food crate, globe, waves, bread, damaged city, heat, radiation, calendar, dove, handshake) + 2 backgrounds (shop, paper world map). Generated with Higgsfield GPT Image 2.5.
- `audio/` — George narration (ElevenLabs eleven_multilingual_v2), suspense bed (ElevenLabs Music), synthesised paper swish / rumble.
- `build/reel.js` — seekable, seeded canvas timeline (`renderFrame(t)`); `build/timeline.js` — caption groups timed to the measured narration.
- `tools/make_timeline.py` → captions + SRT; `tools/mix_audio.sh` → mix + loudness; `tools/render.cjs` → stills / video / cover via headless Chromium; `tools/extract_assets.py` → cutouts from generated sheets.

Rebuild:
```
python3 tools/make_timeline.py
tools/mix_audio.sh
node tools/render.cjs video build/video_silent.mp4
ffmpeg -i build/video_silent.mp4 -i audio/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart deliverables/deep_curious_ww3_ar_1080x1920.mp4
node tools/render.cjs cover deliverables/cover_bila_qasf.png
```
Scrub in a browser: serve the `reel/` folder and open `build/index.html?t=30`.
