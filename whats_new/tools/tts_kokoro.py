"""Offline voice track for "GPT asks Claude what's new" using Kokoro-82M (Apache-2.0) via kokoro-onnx.

Used because ElevenLabs (direct and through Higgsfield) had insufficient credits. Writes the 13 lines
to audio/vo/NN_speaker.mp3, the names build_audio.py expects; existing clips are kept (re-use).
  pip install kokoro-onnx soundfile
  model files: github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
  python3 whats_new/tools/tts_kokoro.py <dir with kokoro-v1.0.onnx + voices-v1.0.bin>
"""
import os, re, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = sys.argv[1] if len(sys.argv) > 1 else '.'

# Same voice for a character in every line.
VOICE = {'GPT': ('am_puck', 'en-us', 1.08), 'CLAUDE': ('bm_george', 'en-gb', 0.94)}

# Spoken text = PRODUCTION.md lines without eleven_v3 tags. Kokoro reads digits well enough, but the
# spelled-out forms keep "171" and "4.5" unambiguous.
src = open(os.path.join(ROOT, 'tools/build_audio.py')).read()
LINES = re.findall(r"\((\d+), '(GPT|CLAUDE)', '(\w+)', \"(.*?)\",", src)

k = Kokoro(os.path.join(MODEL_DIR, 'kokoro-v1.0.onnx'), os.path.join(MODEL_DIR, 'voices-v1.0.bin'))
os.makedirs(f'{ROOT}/audio/vo', exist_ok=True)
for lid, spk, fname, text in LINES:
    out = f'{ROOT}/audio/vo/{fname}.mp3'
    if os.path.exists(out):
        print('keep', fname); continue
    spoken = re.sub(r'\[[^\]]*\]\s*', '', text).strip()
    voice, lang, speed = VOICE[spk]
    samples, sr = k.create(spoken, voice=voice, speed=speed, lang=lang)
    tmp = out[:-4] + '.wav'
    sf.write(tmp, np.asarray(samples, np.float32), sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ar', '48000', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '160k', out], check=True)
    os.remove(tmp)
    print(f'L{lid} {spk:<6} {voice} {len(samples) / sr:5.2f}s  {spoken}')
