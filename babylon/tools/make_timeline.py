"""Caption groups + SRT for the Babylon literary Reel.

Until the full George recording exists, word times are PROVISIONAL (estimated from character
length). After recording, pass measured word timings:  python3 make_timeline.py words.txt
where words.txt has one "start-end" pair per narration word, in order (as measured with faster-whisper).
"""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# Locked narration exactly as approved (captions show it without the pronunciation-only diacritics).
NARRATION = """أصبحت أغنى رجلٍ في بابل… لكنني خسرت أول مالٍ جمعته.
كنت ناسخاً أكتب على ألواح الطين. أعمل طويلاً، ثم يذهب أجري للطعام والملابس، ولا يبقى شيء.
سألت رجلاً ثرياً عن البداية، فتعلّمت أن أحتفظ بعُشر ما أكسب.
بدأت أدّخر. لكنني سلّمت مدخراتي لصانع طوب كي يشتري جواهر.
عندما عاد، كانت الجواهر مجرد زجاج!
خسرت المال، وتعلّمت أن الخبرة في الطوب لا تعني الخبرة في الجواهر.
بدأت من جديد، وموّلت صانع دروع يعرف عمله. ثم تعلّمت أن أعيد استثمار الأرباح، بدل إنفاقها كلها.
وبعد سنوات، اختارني معلّمي شريكاً لإدارة أملاكه، ثم نلت نصيباً من تركته.
هكذا بدأت ثروتي تكبر؛ بالتعلّم، والصبر، والفرص.
والآن… هل عرفت من أنا؟ اكتب اسمي في التعليقات."""

words = NARRATION.split()
END = re.compile(r'[.!؟…؛]$')
PAUSE = re.compile(r'[،,:]$')

TOTAL = float(sys.argv[2]) if len(sys.argv) > 2 else None   # final film length (narration + lead-in + inserted pauses + hold)
if len(sys.argv) > 1:
    times = [tuple(map(float, x.split('-'))) for x in open(sys.argv[1]).read().split()]
    assert len(times) == len(words), (len(times), len(words))
    provisional = False
else:  # rough estimate: ~0.068 s per letter + pauses; rescaled to 58 s
    t, times = 0.0, []
    for w in words:
        d = 0.18 + 0.068 * len(re.sub(r'[^ء-ي]', '', w))
        times.append((t, t + d)); t += d + (0.45 if END.search(w) else 0.18 if PAUSE.search(w) else 0.02)
    k = 58.0 / t; times = [(a * k, b * k) for a, b in times]; provisional = True

# caption groups: 2-5 whole words, split at punctuation, long phrases split evenly, single words joined forward
import math
phrases, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    if END.search(w) or PAUSE.search(w): phrases.append(cur); cur = []
if cur: phrases.append(cur)
chunks = []
for ph in phrases:
    k = math.ceil(len(ph) / 5); size = math.ceil(len(ph) / k)
    chunks += [ph[j:j + size] for j in range(0, len(ph), size)]
merged, buf = [], []
for ch in chunks:
    if buf and END.search(words[buf[-1]]) and merged and not END.search(words[merged[-1][-1]]) and len(merged[-1]) + len(buf) <= 5:
        merged[-1] += buf; buf = []          # a lone sentence-final word joins its own sentence, not the next one
    if buf and len(buf) + len(ch) > 5: merged.append(buf); buf = []
    buf = buf + ch
    if len(buf) >= 2: merged.append(buf); buf = []
if buf: merged[-1] += buf
out = []
for j, g in enumerate(merged):
    start = max(0.0, times[g[0]][0] - 0.06)
    nxt = times[merged[j + 1][0]][0] - 0.06 if j + 1 < len(merged) else None
    end = min(nxt, times[g[-1]][1] + 0.9) if nxt else times[g[-1]][1] + 1.8
    out.append({'text': ' '.join(words[k] for k in g), 'start': round(start, 2), 'end': round(end, 2), 'n': len(g)})

os.makedirs(f'{ROOT}/build', exist_ok=True)
DUR = round(TOTAL or times[-1][1] + 2.2, 2)
json.dump({'provisional': provisional, 'duration': DUR,
           'words': [{'w': w, 's': round(a, 2), 'e': round(b, 2)} for w, (a, b) in zip(words, times)], 'groups': out},
          open(f'{ROOT}/build/timeline.json', 'w'), ensure_ascii=False, indent=1)
open(f'{ROOT}/build/timeline.js', 'w').write('window.TIMELINE=' + json.dumps(
    {'provisional': provisional, 'duration': DUR, 'groups': out,
     'words': [{'w': w, 's': round(a, 2)} for w, (a, b) in zip(words, times)]}, ensure_ascii=False) + ';\n')

def ts(x):
    m, s = divmod(x, 60)
    return f'00:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}'
with open(f'{ROOT}/build/babylon_literary_ar.srt', 'w', encoding='utf-8') as f:
    for i, g in enumerate(out, 1):
        f.write(f"{i}\n{ts(g['start'])} --> {ts(g['end'])}\n{g['text']}\n\n")
print(f"{len(words)} words, {len(out)} groups ({'PROVISIONAL' if provisional else 'measured'}), "
      f"sizes {min(g['n'] for g in out)}-{max(g['n'] for g in out)}")
