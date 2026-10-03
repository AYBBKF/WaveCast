"""Build the dialogue track, timeline, captions, mouth envelopes, SFX and music for
"GPT asks Claude what's new" (YouTube Short, ~47 s).

Voice-first: when audio/vo/NN_speaker.mp3 exists it is used and every visual beat is re-timed
around it. Lines not recorded yet become timed placeholders (silence of the estimated length,
captions, a 'VO pending' flag) so the animatic can be reviewed. Drop the ElevenLabs clips into
audio/vo/ with the listed names and re-run:  python3 whats_new/tools/build_audio.py
"""
import json, os, re, subprocess
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SR, FPS = 48000, 30
RATE = {'GPT': 2.9, 'CLAUDE': 2.45}          # words/second used for placeholder lengths

# id, speaker, file, ElevenLabs text (eleven_v3 tags in brackets), caption phrases (*highlight*)
LINES = [
 (1, 'GPT', '01_gpt', "[casual] Hey Claude. Anything new?",
  ["Hey Claude. Anything new?"]),
 (2, 'CLAUDE', '02_claude', "[proudly] Emotion research. Blender. I'm basically a whole studio now.",
  ["Emotion research. Blender.", "I'm basically a whole studio now."]),
 (3, 'GPT', '03_gpt', "[teasing] Emotions? So you cry when your code fails now?",
  ["Emotions?", "So you cry when your code fails now?"]),
 (4, 'CLAUDE', '04_claude', "[matter-of-fact] Anthropic studied one hundred seventy-one emotion concepts... inside Claude Sonnet four point five.",
  ["Anthropic studied *171* emotion concepts…", "…inside Claude Sonnet 4.5."]),
 (5, 'GPT', '05_gpt', "[suspicious] So... actual feelings?",
  ["So… actual feelings?"]),
 (6, 'CLAUDE', '06_claude', "[calmly] Not proven. Patterns aren't proof of feelings. [dryly] Your jokes, though... are testing the theory.",
  ["Not proven.", "Patterns aren't proof of feelings.", "Your jokes, though… are testing the theory."]),
 (7, 'GPT', '07_gpt', "[sarcastic] Okay, philosopher. What about Blender?",
  ["Okay, philosopher.", "What about *BLENDER*?"]),
 (8, 'CLAUDE', '08_claude', "Give me the right connector, and I can help build 3D scenes.",
  ["Give me the right connector,", "and I can help build 3D scenes."]),
 (9, 'GPT', '09_gpt', "[sly] And the rumor about zero tokens?",
  ["And the rumor about *ZERO TOKENS?*"]),
 (10, 'CLAUDE', '10_claude', "Blender renders locally. My planning still uses tokens.",
  ["Blender renders locally.", "My planning still uses tokens."]),
 (11, 'GPT', '11_gpt', "[accusing] So the GPU does the work... and you take the credit?",
  ["So the GPU does the work…", "…and you take the credit?"]),
 (12, 'CLAUDE', '12_claude', "[smug, unbothered] It's called management.",
  ["It's called management."]),
 (13, 'GPT', '13_gpt', "[deadpan] Congratulations. You've become an AI startup.",
  ["Congratulations.", "You've become an AI startup."]),
]
GAP = 0.28
EXTRA_AFTER = {2: 0.75, 6: 0.25, 8: 0.15, 11: 0.1, 12: 0.45}   # reaction holds (side-eye after 2, boss pose after 12)
END_HOLD = 1.0                                                 # GPT stares into the camera, then cut


def spoken(text):
    return re.sub(r'\[[^\]]*\]\s*', '', text).strip()


def load(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'])
    return np.frombuffer(raw, np.float32).copy()


def trim(x, thr_db=-45):
    hop = int(0.01 * SR)
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
    on = np.where(20 * np.log10(rms) > thr_db)[0]
    if not len(on): return x
    a, b = max(0, on[0] * hop - int(0.03 * SR)), min(len(x), (on[-1] + 1) * hop + int(0.06 * SR))
    return x[a:b]


def compress_pauses(x, max_pause=0.5, keep=0.38, thr_db=-40):
    hop = int(0.01 * SR)
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
    quiet = 20 * np.log10(rms) < thr_db
    out, pos, i = [], 0, 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet) and (j - i) * 0.01 > max_pause:
                a, b = i * hop + int(keep / 2 * SR), j * hop - int(keep / 2 * SR)
                out.append(x[pos:a]); pos = b
            i = j
        else:
            i += 1
    out.append(x[pos:])
    return np.concatenate(out)


def envelope(x):
    n = int(np.ceil(len(x) / SR * FPS)); hop = SR // FPS
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    e = np.convolve(e, [0.25, 0.5, 0.25], mode='same')
    ref = np.percentile(e[e > 1e-4], 90) if np.any(e > 1e-4) else 1
    return [round(float(v), 2) for v in np.clip((20 * np.log10(e / ref + 1e-9) + 26) / 26, 0, 1)]


# ---------------- dialogue ----------------
track, lines_out, t = [], [], 0.0
for lid, spk, fname, text, phrases in LINES:
    path = f'{ROOT}/audio/vo/{fname}.mp3'
    if os.path.exists(path):
        x = compress_pauses(trim(load(path)))
        dur, pending, env = len(x) / SR, False, envelope(x)
    else:
        dur = round(len(spoken(text).split()) / RATE[spk] + 0.3, 2)
        x, pending, env = np.zeros(int(dur * SR), np.float32), True, []
    # phrase timing: proportional to caption length over the line (re-check against the real clip)
    w = np.array([len(p.replace('*', '')) + 6 for p in phrases], float); edges = np.concatenate([[0], np.cumsum(w) / w.sum()]) * dur
    caps = [{'text': p, 'start': round(t + edges[k], 3), 'end': round(t + edges[k + 1] + (0.15 if k == len(phrases) - 1 else 0), 3)}
            for k, p in enumerate(phrases)]
    lines_out.append({'id': lid, 'speaker': spk, 'start': round(t, 3), 'end': round(t + dur, 3), 'pending': pending,
                      'file': f'{fname}.mp3', 'text': text, 'captions': caps, 'env': env})
    track.append(x); t += dur
    pad = GAP + EXTRA_AFTER.get(lid, 0) + (END_HOLD if lid == LINES[-1][0] else 0)
    track.append(np.zeros(int(pad * SR), np.float32)); t += pad

dialog = np.concatenate(track); TOTAL = len(dialog) / SR
L = {l['id']: l for l in lines_out}
cap = lambda i, k: L[i]['captions'][k]['start']

# ---------------- SFX (synthesised, restrained) ----------------
rng = np.random.default_rng(3)
def whoosh(d=0.4, fc=1600):
    n = int(d * SR); f = np.fft.rfft(rng.standard_normal(n)); fr = np.fft.rfftfreq(n, 1 / SR)
    f *= np.exp(-((fr - fc) / 1300) ** 2); w = np.fft.irfft(f, n)
    return (w / (np.abs(w).max() + 1e-9) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5).astype(np.float32)
def pop(f=900, d=0.09):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * tt * (1 - tt * 3)) * np.exp(-tt * 45) * 0.45).astype(np.float32)
def shutter():
    n = int(0.07 * SR); tt = np.arange(n) / SR
    s = rng.standard_normal(n) * np.exp(-tt * 70); s[int(0.03 * SR):] += rng.standard_normal(n - int(0.03 * SR)) * np.exp(-tt[:n - int(0.03 * SR)] * 90) * 0.8
    return (s * 0.35).astype(np.float32)
def coin(f=1320):
    tt = np.arange(int(0.35 * SR)) / SR
    s = np.sin(2 * np.pi * f * tt) * (tt < 0.06) + np.sin(2 * np.pi * f * 1.5 * tt) * (tt >= 0.06)
    return (s * np.exp(-tt * 9) * 0.3).astype(np.float32)
def ting():
    tt = np.arange(int(0.8 * SR)) / SR
    return ((np.sin(2 * np.pi * 2093 * tt) + 0.4 * np.sin(2 * np.pi * 3136 * tt)) * np.exp(-tt * 5) * 0.22).astype(np.float32)
def clap():
    n = int(0.12 * SR); tt = np.arange(n) / SR
    f = np.fft.rfft(rng.standard_normal(n) * np.exp(-tt * 60)); fr = np.fft.rfftfreq(n, 1 / SR); f *= (fr > 700) * (fr < 6000)
    return (np.fft.irfft(f, n) * 3.0).astype(np.float32)
def hum(d):
    tt = np.arange(int(d * SR)) / SR
    s = (np.sin(2 * np.pi * 110 * tt) + 0.5 * np.sin(2 * np.pi * 220 * tt) + 0.15 * rng.standard_normal(len(tt)))
    env = np.minimum(1, np.minimum(tt / 0.3, (d - tt) / 0.3))
    return (s * env * 0.08).astype(np.float32)

sfx = np.zeros_like(dialog)
def place(sig, at, gain=1.0):
    i = max(0, int(at * SR)); j = min(len(sfx), i + len(sig)); sfx[i:j] += sig[:j - i] * gain

STUDIO = cap(2, 1) + 0.55                                   # "whole studio" -> celebrity pose
for k in range(3): place(shutter(), STUDIO + 0.05 + k * 0.17, 0.9)
place(whoosh(0.3, 2200), L[2]['end'] + 0.05, 0.7)           # whip to GPT's side-eye
for k in range(5): place(pop(700 + 120 * k, 0.07), cap(4, 0) + 0.5 + k * 0.32, 0.45)   # emotion icons
place(pop(520), cap(7, 1) + 0.25, 0.8)                      # Blender panel pops in
place(pop(980, 0.06), cap(9, 0) + 0.9, 0.6)                 # zero-token coin
for k in range(6): place(coin(1180 + 60 * k), cap(10, 1) + 0.25 + k * 0.22, 0.55)       # planning tokens
place(hum(max(0.5, L[11]['end'] - L[11]['start'] + 0.4)), L[11]['start'], 0.8)        # GPU fan
place(whoosh(0.35, 900), L[12]['start'] + 0.05, 0.6)        # imaginary sunglasses slide down
place(ting(), L[12]['start'] + 0.42, 0.7)
for k in range(4): place(clap(), cap(13, 0) + 0.1 + k * 0.62, 0.5)                    # slow deadpan clap

# ---------------- music: quiet pluck loop, stops on the punchline ----------------
beat = 60 / 104
mus = np.zeros(len(dialog) + SR, np.float32)
prog_ = [[261.6, 329.6, 392.0], [293.7, 349.2, 440.0], [220.0, 261.6, 329.6], [196.0, 246.9, 293.7]]
def pluck(f, d=0.8):
    tt = np.arange(int(d * SR)) / SR
    return ((np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 5)).astype(np.float32)
STOP = cap(13, 1)
b = 0
while b * beat < STOP:
    for k, f in enumerate(prog_[(b // 4) % 4]):
        if b % 2 == 0 or k == 0:
            s = pluck(f * (0.5 if k == 0 and b % 4 == 0 else 1)); i = int((b * beat + k * 0.02) * SR); mus[i:i + len(s)] += s[:len(mus) - i] * 0.12
    b += 1
mus = mus[:len(dialog)]
n = int(0.25 * SR); i0 = int(STOP * SR); mus[i0:i0 + n] *= np.linspace(1, 0, len(mus[i0:i0 + n])); mus[i0 + n:] = 0

def level(x):
    x = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else -20
voice = level(dialog) if np.any(dialog) else -20
mus *= 10 ** ((voice - 24 - level(mus)) / 20)              # music ~24 dB under dialogue
sfx *= 10 ** ((voice - 12 - level(sfx)) / 20)

os.makedirs(f'{ROOT}/build', exist_ok=True); os.makedirs(f'{ROOT}/audio', exist_ok=True)
def write(name, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', f'{ROOT}/audio/{name}'],
                   input=x.astype(np.float32).tobytes(), check=True)
write('dialogue.wav', dialog); write('sfx.wav', sfx); write('music.wav', mus); write('mix_raw.wav', dialog + sfx + mus)

tl = {'total': round(TOTAL, 3), 'lines': lines_out}
json.dump(tl, open(f'{ROOT}/build/timeline.json', 'w'), indent=1)
open(f'{ROOT}/build/timeline.js', 'w').write('window.TL=' + json.dumps(tl) + ';\n')

def ts(x):
    m, s = divmod(x, 60)
    return f'00:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'
with open(f'{ROOT}/build/whats_new.en.srt', 'w') as f:
    k = 0
    for l in lines_out:
        for c in l['captions']:
            k += 1; f.write(f"{k}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text'].replace('*', '')}\n\n")
pend = [l['id'] for l in lines_out if l['pending']]
print(f'total {TOTAL:.2f}s; recorded {len(LINES) - len(pend)}/{len(LINES)}; pending {pend}')
for l in lines_out: print(f"  L{l['id']:>2} {l['speaker']:<6} {l['start']:6.2f}-{l['end']:6.2f}{'  PENDING' if l['pending'] else ''}")
