#!/usr/bin/env bash
# Mix narration + suspense bed + paper/rumble SFX, then normalise to -16 LUFS / -1 dBTP.
set -euo pipefail
cd "$(dirname "$0")/../audio"
DUR=61.5
# music sits ~20 dB under the voice (voice -24 LUFS raw, music -21.6 LUFS raw -> -22.4 dB);
# extra dip before "لكن هناك فرق مهم" (the nuclear distinction) at 25.4–27.9 s; fade out at the end.
MUSIC_VOL="0.0759*(1-0.72*min(1,max(0,(t-25.3)/0.5))*min(1,max(0,(27.9-t)/0.7)))"
SW="volume=6dB"
ffmpeg -v error -y \
  -i narration_george.mp3 -i music_suspense.mp3 -i sfx_swish.wav -i sfx_rumble.wav \
  -filter_complex "
    [0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur=${DUR}[vo];
    [1:a]aresample=48000,volume=eval=frame:volume='${MUSIC_VOL}',afade=t=out:st=59.2:d=2.3,atrim=0:${DUR}[mu];
    [2:a]aresample=48000,${SW},asplit=6[s1][s2][s3][s4][s5][s6];
    [s1]adelay=1950|1950[d1];[s2]adelay=22200|22200[d2];[s3]adelay=25900|25900[d3];
    [s4]adelay=31050|31050[d4];[s5]adelay=42650|42650[d5];[s6]adelay=52100|52100[d6];
    [3:a]aresample=48000,volume=-12dB,asplit=2[r1][r2];
    [r1]adelay=31200|31200,volume=-6dB[q1];[r2]adelay=33050|33050[q2];
    [vo][mu][d1][d2][d3][d4][d5][d6][q1][q2]amix=inputs=10:normalize=0:duration=first,atrim=0:${DUR}[mix]" \
  -map "[mix]" -c:a pcm_s16le mix_raw.wav

# two-pass loudness normalisation
read -r I TP LRA TH OFF < <(ffmpeg -nostats -i mix_raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | python3 -c "import sys,json; t=sys.stdin.read(); j=json.loads(t[t.rindex('{'):]); print(j['input_i'],j['input_tp'],j['input_lra'],j['input_thresh'],j['target_offset'])")
ffmpeg -v error -y -i mix_raw.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true,aresample=48000" \
  -c:a pcm_s16le mix_final.wav
ffmpeg -nostats -i mix_final.wav -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary" | grep -E "I:|Peak:|LRA:"
