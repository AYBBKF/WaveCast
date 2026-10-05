"""Build the measured timeline for the Petra Reel from the real narration recording.

- Tightens only the silences BETWEEN lines (no words or in-line pauses touched) -> audio/narration_edit.wav
- Places each caption group (2-6 words, *highlight*) inside its line, proportional to text length and
  snapped to the nearest real pause detected in the audio
- Writes build/timeline.js (window.TL) + deliverables/petra_ar.srt
"""
import json, os, subprocess
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SR = 48000
LEAD = 0.12          # narration starts almost immediately
GAP = 0.30           # silence between lines after tightening (recorded: 0.38)
TAIL = 0.85          # hold after the last word: final question + loop back to the opening frame

# line times as synthesised (Piper ar_JO-kareem, length_scale 0.68, 0.38 s gaps)
LINE_TIMES = [(0.00, 4.42), (4.80, 10.88), (11.26, 20.34), (20.72, 28.44), (28.82, 35.34),
              (35.72, 40.25), (40.63, 47.25), (47.63, 53.12), (53.50, 58.60), (58.98, 64.70)]
GROUPS = [
    ["تخيّل أن تصنع واجهة كاملة…", "بإزالة أجزاء من *الجبل!*"],
    ["هذا ما فعله *الأنباط*", "في واجهات *البتراء،*", "في *الأردن،*", "قبل نحو ألفي عام."],
    ["*بالمطارق* *والأزاميل،*", "أزال النحّاتون الحجر تدريجياً،", "حتى ظهرت الزخارف والأعمدة", "والمداخل من الصخر نفسه."],
    ["والمفاجأة؟ تشير واجهات", "لم يكتمل نحتها", "إلى أنهم غالباً بدأوا من *الأعلى،*", "ثم نزلوا إلى *الأسفل.*"],
    ["تخيّل الجزء العلوي", "وقد ظهرت تفاصيله،", "بينما لا يزال ما تحته", "صخرة *خشنة!*"],
    ["ضربة بعد ضربة،", "يتحوّل الجبل إلى واجهة *مدهشة.*"],
    ["لكن المفاجأة الأكبر خلف المدخل:", "كثير من هذه الواجهات الفخمة", "كانت *لمقابر!*"],
    ["ومع ذلك، كانت البتراء مدينة", "فيها *بيوت* و*أسواق* و*معابد* أيضاً."],
    ["والآن انظر إلى هذه التفاصيل…", "وتخيّل الصخرة قبل أول ضربة."],
    ["أيّهما أصعب في رأيك:", "بناء واجهة بالحجارة،", "أم نحتها من جبل؟"],
]


def load(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']), np.float32).copy()


def pauses(x, thr_db=-40, min_gap=0.10):
    hop = SR // 100
    r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
    q, out, i = 20 * np.log10(r) < thr_db, [], 0
    while i < len(q):
        if q[i]:
            j = i
            while j < len(q) and q[j]: j += 1
            if i > 0 and j < len(q) and (j - i) * 0.01 >= min_gap: out.append((i + j) / 2 * 0.01)
            i = j
        else:
            i += 1
    return out


x = load(f'{ROOT}/audio/narration_kareem.mp3')
# locate each line precisely around its synthesis time (mp3 encoder delay ~ tens of ms)
hop = SR // 100
r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
loud = 20 * np.log10(r) > -42
def snap(t, direction):
    i = int(t * 100)
    if direction > 0:                                   # first loud frame at/after t-0.1
        i = max(0, i - 10)
        while i < len(loud) and not loud[i]: i += 1
        return i * 0.01
    i = min(len(loud) - 1, i + 10)                      # last loud frame at/before t+0.1
    while i > 0 and not loud[i]: i -= 1
    return (i + 1) * 0.01

pieces, lines, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for k, (a, b) in enumerate(LINE_TIMES):
    a, b = snap(a, 1), snap(b, -1)
    a0, b0 = max(0, a - 0.03), min(len(x) / SR, b + 0.06)
    seg = x[int(a0 * SR):int(b0 * SR)]
    dur = len(seg) / SR
    # caption groups: proportional split, boundaries snapped to real in-line pauses
    w = np.array([len(g.replace('*', '')) + 4 for g in GROUPS[k]], float)
    edges = list(np.concatenate([[0], np.cumsum(w) / w.sum()]) * dur)
    ps = pauses(seg)
    for j in range(1, len(edges) - 1):
        near = [p for p in ps if abs(p - edges[j]) < 0.9]
        if near: edges[j] = min(near, key=lambda p: abs(p - edges[j]))
    groups = [{'text': g, 'start': round(t + edges[j], 3), 'end': round(t + edges[j + 1], 3)} for j, g in enumerate(GROUPS[k])]
    lines.append({'id': k + 1, 'start': round(t, 3), 'end': round(t + dur, 3), 'groups': groups})
    pieces.append(seg); t += dur
    if k < len(LINE_TIMES) - 1:
        pieces.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
pieces.append(np.zeros(int(TAIL * SR), np.float32)); t += TAIL
narr = np.concatenate(pieces)
TOTAL = round(len(narr) / SR, 3)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', f'{ROOT}/audio/narration_edit.wav'],
               input=narr.tobytes(), check=True)

os.makedirs(f'{ROOT}/build', exist_ok=True); os.makedirs(f'{ROOT}/deliverables', exist_ok=True)
tl = {'total': TOTAL, 'lines': lines}
open(f'{ROOT}/build/timeline.js', 'w').write('window.TL=' + json.dumps(tl, ensure_ascii=False) + ';\n')
json.dump(tl, open(f'{ROOT}/build/timeline.json', 'w'), ensure_ascii=False, indent=1)

def ts(v):
    h, rem = divmod(v, 3600); m, s = divmod(rem, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}'
with open(f'{ROOT}/deliverables/petra_ar.srt', 'w', encoding='utf-8') as f:
    n = 0
    for l in lines:
        for g in l['groups']:
            n += 1; f.write(f"{n}\n{ts(g['start'])} --> {ts(g['end'])}\n‫{g['text'].replace('*', '')}‬\n\n")
print(f'total {TOTAL}s, narration ends {lines[-1]["end"]}s, {n} caption groups')
for l in lines: print(f"L{l['id']:>2} {l['start']:6.2f}-{l['end']:6.2f}  " + ' | '.join(f"{g['start']:.2f}" for g in l['groups']))
