"""Build the dialogue track, timeline, captions, mouth envelopes, SFX and music for
"One Million Checks vs Twenty Steps".

Recorded lines live in audio/vo/NN_speaker.mp3. Lines that are not recorded yet are kept as
timed placeholders (silence + captions + a 'VO pending' flag) so the edit can be reviewed;
drop the missing clips into audio/vo/ with the listed names and re-run to get the final cut.
"""
import json, os, subprocess
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SR = 48000
FPS = 30

# id, speaker, file, spoken text (copy-ready for ElevenLabs), caption phrases as (word-range, text),
# measured word times (faster-whisper base.en on the generated clip) or None, placeholder seconds
LINES = [
 (1, 'DOT', '01_dot', "[excited] One million numbers. One target. I'll check every single one!",
  [((0, 2), "*1,000,000* numbers."), ((3, 4), "One target."), ((5, 9), "I'll check every single one!")],
  [(0.00,0.30),(0.30,0.66),(0.66,1.20),(1.68,1.76),(1.76,2.16),(2.76,2.90),(2.90,3.04),(3.04,3.38),(3.38,3.76),(3.76,4.00)], None),
 (2, 'OPUS', '02_opus', "[dryly] That's up to a million checks. Are you searching... or taking a census?",
  [((0, 5), "That's up to *1,000,000* checks."), ((6, 8), "Are you searching…"), ((9, 12), "…or taking a census?")],
  [(0.00,0.38),(0.38,0.48),(0.48,0.68),(0.68,0.78),(0.78,1.02),(1.02,1.50),(2.46,3.12),(3.12,3.28),(3.28,3.72),(3.72,4.84),(4.84,5.20),(5.20,5.46),(5.46,5.72)], None),
 (3, 'DOT', '03_dot', "[annoyed] Fine, professor. What's your genius plan?",
  [((0, 1), "Fine, professor."), ((2, 4), "What's your genius plan?")],
  [(0.00,0.30),(0.40,0.66),(1.06,1.24),(1.24,1.32),(1.32,1.58),(1.58,1.92)], None),
 (4, 'OPUS', '04_opus', "If the list is already sorted, binary search checks the middle... then eliminates half the possibilities.",
  [((0, 5), "If the list is *ALREADY SORTED*,"), ((6, 10), "binary search checks the middle…"), ((11, 15), "…then eliminates half the possibilities.")],
  None, 6.0),
 (5, 'DOT', '05_dot', "[sarcastic] Half? That's my motivation after lunch.",
  [((0, 0), "Half?"), ((1, 5), "That's my motivation after lunch.")],
  [(0.00,0.42),(0.78,1.10),(1.10,1.20),(1.20,1.50),(1.50,2.02),(2.02,2.32)], None),
 (6, 'OPUS', '06_opus', "A million items. At most... twenty search steps.",
  [((0, 2), "*1,000,000* items."), ((3, 4), "At most…"), ((5, 7), "*20* search steps.")],
  [(0.00,0.16),(0.16,0.52),(0.52,1.08),(1.74,2.62),(2.62,2.96),(3.60,4.78),(4.78,5.26),(5.26,5.68)], None),
 (7, 'DOT', '07_dot', "[shocked] Twenty?! I haven't even opened my code editor.",
  [((0, 0), "*20*?!"), ((1, 7), "I haven't even opened my code editor.")],
  None, 2.7),
 (8, 'OPUS', '08_opus', "Sorted list, though. Sorting it first has a cost.",
  [((0, 2), "Sorted list, though."), ((3, 8), "Sorting it first has a cost.")],
  None, 3.0),
 (9, 'DOT', '09_dot', "[grumbling] So the winner is... whoever read the requirements.",
  [((0, 3), "So the winner is…"), ((4, 7), "…whoever read the requirements.")],
  [(0.00,0.22),(0.22,0.32),(0.32,0.46),(0.46,0.94),(1.26,1.54),(1.54,2.00),(2.00,2.16),(2.16,2.44)], None),
 (10, 'OPUS', '10_opus', "[deadpan] Finally. A correct answer.",
  [((0, 0), "Finally."), ((1, 3), "A correct answer.")],
  None, 2.1),
]
GAP = 0.22
EXTRA_AFTER = {2: 0.35, 6: 0.30, 7: 0.15}     # reaction holds
END_HOLD = 0.9
SHOTS = {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 6, 10: 6}   # line -> shot


def load(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'])
    return np.frombuffer(raw, np.float32).copy()


def compress_pauses(x, max_pause=0.55, keep=0.42, thr_db=-40):
    """Shorten internal pauses longer than max_pause to `keep` seconds; return audio + time map old->new."""
    hop = int(0.01 * SR)
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
    quiet = 20 * np.log10(rms) < thr_db
    runs, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet) and (j - i) * 0.01 > max_pause: runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    out, cuts, pos = [], [], 0.0
    for a, b in runs:
        mid_keep_a = a + keep / 2; mid_keep_b = b - keep / 2
        out.append(x[int(pos * SR):int(mid_keep_a * SR)]); cuts.append((mid_keep_a, mid_keep_b - mid_keep_a)); pos = mid_keep_b
    out.append(x[int(pos * SR):])
    def tmap(t):
        return t - sum(d for a, d in cuts if t >= a + d) - sum(min(max(t - a, 0), d) for a, d in cuts if a <= t < a + d)
    return np.concatenate(out), tmap


def envelope(x):
    n = int(np.ceil(len(x) / SR * FPS)); hop = SR // FPS
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    e = np.convolve(e, [0.25, 0.5, 0.25], mode='same')
    ref = np.percentile(e[e > 1e-4], 90) if np.any(e > 1e-4) else 1
    m = np.clip((20 * np.log10(e / ref + 1e-9) + 26) / 26, 0, 1)        # 0 = closed, 1 = wide open
    return [round(float(v), 2) for v in m]


# ---------------- dialogue ----------------
track, lines_out, t = [], [], 0.0
for lid, spk, fname, text, phrases, wt, ph_dur in LINES:
    path = f'{ROOT}/audio/vo/{fname}.mp3'
    if os.path.exists(path):
        x, tmap = compress_pauses(load(path))
        words = [(tmap(a), tmap(b)) for a, b in wt] if wt else None
        dur, pending = len(x) / SR, False
        env = envelope(x)
    else:
        x, words, dur, pending, env = np.zeros(int(ph_dur * SR), np.float32), None, ph_dur, True, []
    caps = []
    for k, ((w0, w1), cap) in enumerate(phrases):
        if words:
            s, e = words[w0][0], words[w1][1]
        else:                                           # placeholder: spread phrases evenly
            s, e = dur * k / len(phrases), dur * (k + 1) / len(phrases)
        caps.append({'text': cap, 'start': round(t + max(0, s - 0.05), 3), 'end': round(t + e + 0.12, 3)})
    for k in range(len(caps) - 1):                      # no gaps/overlaps between consecutive phrases
        caps[k]['end'] = max(caps[k]['end'], caps[k + 1]['start']) if caps[k + 1]['start'] - caps[k]['end'] < 0.4 else caps[k]['end']
        caps[k]['end'] = min(caps[k]['end'], caps[k + 1]['start'])
    lines_out.append({'id': lid, 'speaker': spk, 'start': round(t, 3), 'end': round(t + dur, 3), 'shot': SHOTS[lid],
                      'pending': pending, 'file': f'{fname}.mp3', 'text': text, 'captions': caps, 'env': env})
    track.append(x)
    t += dur
    pad = GAP + EXTRA_AFTER.get(lid, 0) + (END_HOLD if lid == 10 else 0)
    track.append(np.zeros(int(pad * SR), np.float32)); t += pad

dialog = np.concatenate(track); TOTAL = len(dialog) / SR

# ---------------- SFX + music (synthesised, royalty-free) ----------------
rng = np.random.default_rng(7)
def whoosh(d=0.45):
    n = int(d * SR); noise = rng.standard_normal(n).astype(np.float32)
    f = np.fft.rfft(noise); fr = np.fft.rfftfreq(n, 1 / SR)
    f *= np.exp(-((fr - 1800) / 1400) ** 2); w = np.fft.irfft(f, n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (w / (np.abs(w).max() + 1e-9) * env * 0.5).astype(np.float32)
def boing(d=0.55):
    tt = np.arange(int(d * SR)) / SR
    fr = 520 * np.exp(-tt * 2.2) + 140 + 25 * np.sin(2 * np.pi * 14 * tt)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    return (np.sin(ph) * np.exp(-tt * 3.0) * 0.55).astype(np.float32)
def pop(f=900, d=0.09):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * tt * (1 - tt * 3)) * np.exp(-tt * 45) * 0.45).astype(np.float32)
def tick():
    return pop(1600, 0.035) * 0.6

sfx = np.zeros_like(dialog)
def place(sig, at, gain=1.0):
    i = int(at * SR); j = min(len(sfx), i + len(sig)); sfx[i:j] += sig[:j - i] * gain

shot_starts = {}
for L in lines_out:
    shot_starts.setdefault(L['shot'], L['start'])
for s, at in shot_starts.items():
    if s > 1: place(whoosh(), max(0, at - 0.3), 0.8)
L = {l['id']: l for l in lines_out}
place(pop(700), L[1]['captions'][0]['start'] + 0.05, 0.9)          # 1,000,000 counter pops in
place(pop(1100), L[4]['captions'][1]['start'] + 0.2, 0.8)          # middle marker
half_t0, half_t1 = L[5]['start'], L[6]['captions'][2]['start'] + 0.3
for k in range(20):                                                # one tick per midpoint check
    place(tick(), half_t0 + (half_t1 - half_t0) * (k + 1) / 20, 0.7)
place(boing(), L[7]['start'] - 0.12, 0.9)                          # comedic reaction on "Twenty?!"
place(pop(500), L[10]['captions'][1]['start'], 0.7)

# quiet, light background music: soft plucked chord loop + brushed hats (100 BPM)
bpm, beat = 100, 60 / 100
mus = np.zeros(int((TOTAL + 1) * SR), np.float32)
prog = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
def pluck(f, d=0.9):
    tt = np.arange(int(d * SR)) / SR
    return ((np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 4.5)).astype(np.float32)
b = 0
while b * beat < TOTAL + 0.5:
    chord = prog[(b // 4) % 4]
    for k, f in enumerate(chord):
        if b % 2 == 0 or k == 0:
            s = pluck(f * (0.5 if k == 0 and b % 4 == 0 else 1)); i = int((b * beat + k * 0.02) * SR); mus[i:i + len(s)] += s[:len(mus) - i] * 0.12
    hn = rng.standard_normal(int(0.05 * SR)).astype(np.float32) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80)
    i = int((b * beat + beat / 2) * SR); mus[i:i + len(hn)] += np.diff(np.concatenate([[0], hn]))[:len(mus) - i] * 0.05
    b += 1
mus = mus[:len(dialog)]
fade = np.ones_like(mus); n = int(0.6 * SR); fade[-n:] = np.linspace(1, 0, n); mus *= fade

def lufs_like(x):                                     # rough loudness proxy for level matching
    return 20 * np.log10(np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2)) + 1e-9)
voice_level = lufs_like(dialog[dialog != 0]) if np.any(dialog) else -20
mus *= 10 ** ((voice_level - 22 - lufs_like(mus)) / 20)            # music ~22 dB under the dialogue
sfx *= 10 ** ((voice_level - 12 - lufs_like(sfx)) / 20)

os.makedirs(f'{ROOT}/build', exist_ok=True)
def write(name, x):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', f'{ROOT}/audio/{name}'], input=x.astype(np.float32).tobytes())
write('dialogue.wav', dialog); write('sfx.wav', sfx); write('music.wav', mus)
mix = dialog + sfx + mus
write('mix_raw.wav', mix)

json.dump({'total': round(TOTAL, 3), 'fps': FPS, 'lines': lines_out}, open(f'{ROOT}/build/timeline.json', 'w'), indent=1)
open(f'{ROOT}/build/timeline.js', 'w').write('window.TL=' + json.dumps({'total': round(TOTAL, 3), 'lines': lines_out}) + ';\n')

def ts(x):
    m, s = divmod(x, 60)
    return f'00:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'
with open(f'{ROOT}/build/one_million_checks_vs_twenty_steps.en.srt', 'w') as f:
    k = 0
    for l in lines_out:
        for c in l['captions']:
            k += 1; f.write(f"{k}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text'].replace('*', '')}\n\n")
pend = [l['id'] for l in lines_out if l['pending']]
print(f'total {TOTAL:.2f}s; recorded {10 - len(pend)}/10; pending lines {pend}')
for l in lines_out: print(f"  L{l['id']:>2} {l['speaker']:<4} {l['start']:6.2f}-{l['end']:6.2f} shot {l['shot']}{'  PENDING' if l['pending'] else ''}")
