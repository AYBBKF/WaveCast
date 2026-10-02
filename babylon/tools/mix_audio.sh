#!/usr/bin/env bash
# Mix the edited George narration with the mystery score, dip the score at the glass reveal, normalise to -16 LUFS / -1.5 dBTP.
set -euo pipefail
cd "$(dirname "$0")/.."
DUR=$(cat build/duration.txt)
GLASS=$(python3 -c "
import json,re
W=json.load(open('build/timeline.json'))['words']
print([w['s'] for w in W if re.sub(r'[^ء-ي]','',w['w'])=='زجاج'][0])")
# voice -24.4 LUFS raw, score -19.2 LUFS raw -> -24.2 dB keeps the score ~19 dB under the voice;
# extra -10 dB dip from just before «زجاج» until the lesson begins, with short ramps
VOL="0.0617*(1-0.68*min(1,max(0,(t-(${GLASS}-0.35))/0.25))*min(1,max(0,((${GLASS}+1.7)-t)/0.6)))"
ffmpeg -v error -y -i audio/narration_edit.wav -i audio/music_mystery.mp3 -filter_complex "
  [0:a]aresample=48000,pan=stereo|c0=c0|c1=c0[vo];
  [1:a]aresample=48000,volume=eval=frame:volume='${VOL}',afade=t=in:d=0.8,afade=t=out:st=$(python3 -c "print(${DUR}-2.2)"):d=2.2,atrim=0:${DUR}[mu];
  [vo][mu]amix=inputs=2:normalize=0:duration=first,atrim=0:${DUR}[mix]" -map "[mix]" -c:a pcm_s16le audio/mix_raw.wav
read -r I TP LRA TH OFF < <(ffmpeg -nostats -i audio/mix_raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | python3 -c "import sys,json; t=sys.stdin.read(); j=json.loads(t[t.rindex('{'):]); print(j['input_i'],j['input_tp'],j['input_lra'],j['input_thresh'],j['target_offset'])")
ffmpeg -v error -y -i audio/mix_raw.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true,aresample=48000" -c:a pcm_s16le audio/mix_final.wav
echo "glass dip at ${GLASS}s; duration ${DUR}s"
ffmpeg -nostats -i audio/mix_final.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
