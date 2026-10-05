"""Music, SFX and final mix for the Petra Reel (all synthesised here; royalty-free).

Inputs : audio/narration_edit.wav (tools/make_timeline.py), build/cues.json (render.cjs cues)
Outputs: audio/music.wav, audio/sfx.wav, audio/mix_master.wav (-16 LUFS integrated, true peak <= -1 dBTP)

Music: restrained mystery and wonder - sparse oud-like plucks (Karplus-Strong) in D Hijaz, a warm drone,
a gentle low frame-drum pulse. It opens up at the facade reveal, dips at the tomb twist and returns warmer.
"""
import json, os, subprocess
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SR = 48000
rng = np.random.default_rng(11)

def load(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']), np.float32).copy()

narr = load(f'{ROOT}/audio/narration_edit.wav')
CUES = json.load(open(f'{ROOT}/build/cues.json'))
TOTAL = CUES['total']; N = int(TOTAL * SR)
narr = np.pad(narr, (0, max(0, N - len(narr))))[:N]
at = {c['type']: c['t'] for c in CUES['cues'] if c['type'] in ('swell', 'dip', 'return')}
tt = np.arange(N) / SR

def env_points(points):                                  # piecewise-linear automation [(t, value), ...]
    xs, ys = zip(*points); return np.interp(tt, xs, ys).astype(np.float32)

# ---------------- music ----------------
def ks_pluck(f, dur=1.6, bright=0.5, seed=0):            # Karplus-Strong plucked string (oud-like)
    r = np.random.default_rng(seed); n = int(dur * SR); p = max(2, int(SR / f))
    buf = r.uniform(-1, 1, p).astype(np.float32); out = np.empty(n, np.float32)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * (0.996 - 0.004 * (1 - bright))
    a = np.minimum(1, np.arange(n) / (0.004 * SR))
    return out * a
HZ = lambda m: 440 * 2 ** ((m - 69) / 12)
D_HIJAZ = [62, 63, 66, 67, 69, 70, 72, 74]              # D Eb F# G A Bb C D
D_MAJ = [62, 64, 66, 67, 69, 71, 74]

BEAT = 60 / 72
music = np.zeros((2, N), np.float32)
# drone: D2 + A2, slow breathing, filtered harmonics
drone = sum(np.sin(2 * np.pi * HZ(m) * tt + k) * a for k, (m, a) in enumerate([(38, 0.6), (45, 0.35), (50, 0.18), (57, 0.06)]))
drone *= (0.75 + 0.25 * np.sin(2 * np.pi * tt / 9.0))
music += np.stack([drone, drone]) * 0.22

# plucked phrases: sparse at first, more notes during the reveal, quiet at the tomb, warm major at the end
phr = [0, 2, 4, 3, 1, 2, 0, None, 4, 5, 4, 2, 3, 1, 0, None]
b = 0
while b * BEAT < TOTAL - 1.0:
    t0 = b * BEAT
    dense = 1 if (at['swell'] - 1.5 <= t0 < at['dip']) or (CUES['cues'][0]['t'] + 4 < t0 < 12) else 0
    if at['dip'] <= t0 < at['return']: b += 1; continue       # tomb twist: drone only
    if b % 2 == 0 or dense:
        deg = phr[b % len(phr)]
        if deg is not None:
            scale = D_MAJ if t0 >= at['return'] + 6 else D_HIJAZ
            m = scale[deg % len(scale)] + (12 if dense and b % 4 == 1 else 0) - 12
            s = ks_pluck(HZ(m), 1.8, 0.4 + 0.3 * dense, seed=b) * (0.5 if b % 2 else 0.75)
            i = int((t0 + rng.uniform(0, 0.02)) * SR); j = min(N, i + len(s)); pan = 0.35 * np.sin(b * 1.7)
            music[0, i:j] += s[:j - i] * (1 - pan) * 0.5; music[1, i:j] += s[:j - i] * (1 + pan) * 0.5
    b += 1

def frame_drum(gain=1.0):                                 # low soft thump + skin slap
    n = int(0.6 * SR); x = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 40 * np.exp(-x * 30)) * x) * np.exp(-x * 7)
    slap = rng.standard_normal(n) * np.exp(-x * 60) * 0.15
    return ((body + slap) * gain).astype(np.float32)
b = 0
while b * BEAT < TOTAL - 0.8:
    t0 = b * BEAT
    if not (at['dip'] <= t0 < at['return']) and t0 > 2.0 and b % 2 == 0:
        s = frame_drum(0.55 if b % 4 == 0 else 0.35); i = int(t0 * SR); j = min(N, i + len(s)); music[:, i:j] += s[:j - i] * 0.5
    b += 1

# level automation: open up at the reveal + light sweep, dip at the tomb, warm return, fade out
mus_gain = env_points([(0, 0.8), (at['swell'] - 1.0, 0.85), (at['swell'] + 0.3, 1.35), (at['dip'] - 0.4, 1.2),
                       (at['dip'] + 0.6, 0.38), (at['return'] - 0.3, 0.42), (at['return'] + 1.0, 1.0),
                       (TOTAL - 1.4, 1.0), (TOTAL, 0.0)])
music *= mus_gain

# ---------------- SFX ----------------
def bandnoise(n, lo, hi, seed):
    r = np.random.default_rng(seed); f = np.fft.rfft(r.standard_normal(n)); fr = np.fft.rfftfreq(n, 1 / SR)
    f *= (fr > lo) & (fr < hi); return np.fft.irfft(f, n).astype(np.float32) / 30
def chisel(seed):                                        # iron-on-iron clink + stone bite
    n = int(0.35 * SR); x = np.arange(n) / SR
    ring = sum(np.sin(2 * np.pi * f * x) * a * np.exp(-x * d) for f, a, d in [(2150, 0.5, 38), (3420, 0.35, 45), (5230, 0.2, 60), (1180, 0.25, 30)])
    bite = bandnoise(n, 900, 7000, seed) * np.exp(-x * 90) * 6
    return (ring + bite).astype(np.float32)
def stones(seed):                                        # a few small fragments rattling down
    n = int(0.6 * SR); out = np.zeros(n, np.float32); r = np.random.default_rng(seed)
    for _ in range(7):
        i = int(r.uniform(0, 0.45) * SR); g = bandnoise(int(0.04 * SR), 500, 5000, int(r.integers(1e6))) * np.exp(-np.arange(int(0.04 * SR)) / SR * 120) * r.uniform(2, 6)
        out[i:i + len(g)] += g[:n - i]
    return out
def paper(seed):                                         # paper rustle / peel
    n = int(0.45 * SR); x = np.arange(n) / SR; r = np.random.default_rng(seed)
    crackle = (r.random(n) < 0.004) * r.uniform(-1, 1, n) * 0.6
    return (bandnoise(n, 1500, 9000, seed) * 5 * np.sin(np.pi * x / x[-1]) ** 1.5 + crackle * np.exp(-x * 4)).astype(np.float32)
def pop(seed):
    n = int(0.12 * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * 330 * x * (1 - x * 2)) * np.exp(-x * 40) * 0.5 + bandnoise(n, 2000, 6000, seed) * np.exp(-x * 120) * 3).astype(np.float32)
def whoosh(seed):
    n = int(0.9 * SR); x = np.arange(n) / SR
    return (bandnoise(n, 200, 2500, seed) * 6 * np.sin(np.pi * x / x[-1]) ** 2).astype(np.float32)
def thud(seed):
    n = int(0.9 * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * (55 + 30 * np.exp(-x * 20)) * x) * np.exp(-x * 5) * 0.9 + bandnoise(n, 80, 600, seed) * np.exp(-x * 12) * 4).astype(np.float32)
GEN = {'chisel': chisel, 'stones': stones, 'paper': paper, 'pop': pop, 'whoosh': whoosh, 'thud': thud}
LEVEL = {'chisel': 0.55, 'stones': 0.35, 'paper': 0.30, 'pop': 0.35, 'whoosh': 0.35, 'thud': 0.6}
sfx = np.zeros(N, np.float32)
for k, c in enumerate(CUES['cues']):
    if c['type'] not in GEN: continue
    s = GEN[c['type']](k + 1) * LEVEL[c['type']] * c['gain']; i = int(c['t'] * SR); j = min(N, i + len(s))
    if 0 <= i < N: sfx[i:j] += s[:j - i]
# canyon ambience: soft low wind, quieter inside the tomb
wind = bandnoise(N, 60, 900, 99) * (0.6 + 0.4 * np.sin(2 * np.pi * tt / 7.3)) * 2.2
wind *= env_points([(0, 1), (at['dip'], 1), (at['dip'] + 0.5, 0.35), (at['return'], 0.35), (at['return'] + 0.8, 0.8), (TOTAL - 1, 0.8), (TOTAL, 0)])
sfx += wind

# ---------------- mix: narration clearly dominant ----------------
def rms_db(x):
    x = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else -60
v = rms_db(narr)
music *= 10 ** ((v - 19 - rms_db(music.mean(0))) / 20)   # music ~19 dB under speech on average
sfx *= 10 ** ((v - 13 - rms_db(sfx)) / 20)
# duck music a further 4 dB while the narrator speaks
speech = np.convolve((np.abs(narr) > 0.02).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.37 * np.clip(speech * 3, 0, 1)
mix = np.stack([narr, narr]) * 0.95 + music * duck + np.stack([sfx, sfx])

def write(name, x, ch):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', '-', f'{ROOT}/audio/{name}'],
                   input=np.ascontiguousarray(x.T if ch == 2 else x).astype(np.float32).tobytes(), check=True)
write('music.wav', music, 2); write('sfx.wav', sfx, 1); write('mix_raw.wav', mix, 2)

# two-pass loudnorm to -16 LUFS / -1 dBTP (target -1.5 for codec headroom)
probe = subprocess.run(['ffmpeg', '-v', 'info', '-i', f'{ROOT}/audio/mix_raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
m = json.loads(probe[probe.rindex('{'):probe.rindex('}') + 1])
af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/audio/mix_raw.wav', '-af', af, '-ar', str(SR), f'{ROOT}/audio/mix_master.wav'], check=True)
print('mix_master.wav written; pre-norm', m['input_i'], 'LUFS')
