# DOT vs OPUS — "One Million Checks vs Twenty Steps" (YouTube Short)

See `PRODUCTION.md` for the script, storyboard, prompts, voices, fact check, title and description, and the asset status.

- `deliverables/one_million_checks_vs_twenty_steps_WIP.mp4`: 1080×1920, 30 fps, 39.7 s, −14 LUFS. Six of ten lines have real voices; the four "VO PENDING" lines are timed silent slots.
- `deliverables/one_million_checks_vs_twenty_steps_WIP.en.srt`: captions timed to the recorded audio; the pending lines are estimates.

Finish (after adding the four missing clips to `audio/vo/` as `04_opus.mp3`, `07_dot.mp3`, `08_opus.mp3`, `10_opus.mp3`):

```
python3 tools/build_audio.py          # dialogue, captions, mouth envelopes, SFX, music, SRT
# normalise: see the loudnorm step in PRODUCTION.md / build history (-14 LUFS, -1.5 dBTP)
node tools/render.cjs video build/short_silent.mp4
ffmpeg -i build/short_silent.mp4 -i audio/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart deliverables/final.mp4
```
