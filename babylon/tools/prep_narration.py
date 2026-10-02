"""Lengthen the George narration only with silence (no words changed) and shift the measured word times.

Measured with faster-whisper (medium, word timestamps) on audio/narration_george.mp3: 110 words, 1:1 with the locked script.
Silences inserted inside existing pauses (found with ffmpeg silencedetect, -38 dB):
  lead-in 0.4 s; before «عندما عاد» 0.3 s; after «زجاج!» 0.6 s; after «تركته.» 0.4 s; after «والفرص» 0.5 s; after «والآن…» 0.3 s.
"""
import os, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = f'{ROOT}/audio'
LEAD, HOLD = 0.4, 3.0
INSERTS = [(21.15, 0.3), (24.17, 0.6), (43.27, 0.4), (48.07, 0.5), (49.20, 0.3)]   # (source time inside a pause, seconds added)

MEASURED = """0.00-0.46 0.46-0.82 0.82-1.14 1.14-1.36 1.36-2.00 2.00-2.52 2.52-2.90 2.90-3.22 3.22-3.50 3.50-4.52
4.52-4.78 4.78-5.32 5.32-5.62 5.62-5.92 5.92-6.28 6.28-6.96 6.96-7.28 7.28-7.98 7.98-8.20 8.20-8.56
8.56-8.90 8.90-9.42 9.42-10.20 10.20-10.40 10.40-10.78 10.78-11.50 11.60-11.90 11.90-12.32 12.32-12.74 12.74-12.86
12.86-13.56 13.56-14.12 14.12-14.24 14.24-14.74 14.74-15.12 15.12-15.30 15.30-16.18 16.18-16.52 16.52-17.32 17.32-17.80
17.80-18.20 18.20-18.90 18.90-19.34 19.34-19.78 19.78-20.08 20.08-20.48 20.48-21.08 21.32-21.78 21.78-22.26 22.26-22.50
22.50-22.96 22.96-23.42 23.42-24.44 24.44-24.86 24.86-25.40 25.40-25.90 25.90-26.06 26.06-26.50 26.50-26.62 26.62-26.94
26.94-27.14 27.14-27.40 27.40-27.80 27.80-27.94 27.94-28.88 28.88-29.38 29.38-29.52 29.52-30.26 30.26-30.70 30.70-31.04
31.04-31.38 31.38-31.72 31.72-32.84 32.84-33.02 33.02-33.50 33.50-33.64 33.64-33.94 33.94-34.44 34.44-35.14 35.14-35.50
35.50-36.12 36.12-36.98 37.24-37.48 37.48-38.26 38.26-38.74 38.74-39.18 39.18-39.68 39.68-40.34 40.34-41.30 41.30-41.46
41.46-41.78 41.78-42.38 42.38-42.48 42.48-43.06 43.66-44.06 44.06-44.38 44.38-44.86 44.86-45.82 45.82-46.52 46.52-47.22
47.22-48.44 48.44-49.58 49.58-49.72 49.72-50.04 50.04-50.14 50.14-51.04 51.04-51.36 51.36-51.64 51.64-51.72 51.72-52.46"""
# whisper stretches a word's end over a following pause; cap ends at the detected pause starts so captions don't linger
SIL = [(1.690, 2.016), (4.020, 4.521), (6.573, 6.916), (10.966, 11.501), (15.670, 16.112), (16.981, 17.302), (19.618, 19.880),
       (20.989, 21.322), (23.912, 24.421), (28.414, 28.984), (29.861, 30.184), (32.125, 32.794), (34.935, 35.187), (36.509, 37.151),
       (40.831, 41.210), (42.959, 43.578), (45.302, 45.748), (46.412, 46.678), (47.756, 48.383), (48.872, 49.520), (50.385, 50.994), (52.358, 52.709)]

def shift(x):
    return x + LEAD + sum(d for at, d in INSERTS if x >= at)

times = []
for pair in MEASURED.split():
    s, e = map(float, pair.split('-'))
    for a, b in SIL:
        if s < a < e: e = a; break
    times.append((round(shift(s), 3), round(shift(e), 3)))
assert len(times) == 110

src = f'{A}/narration_george.mp3'
cuts = [0.0] + [at for at, _ in INSERTS] + [None]
parts, fc = [], []
fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{LEAD}[s0]"); parts.append('[s0]')
for i in range(len(cuts) - 1):
    a, b = cuts[i], cuts[i + 1]
    fc.append(f"[0:a]atrim={a}" + (f":{b}" if b else "") + f",asetpts=PTS-STARTPTS[p{i}]"); parts.append(f'[p{i}]')
    if i < len(INSERTS):
        fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{INSERTS[i][1]}[s{i+1}]"); parts.append(f'[s{i+1}]')
fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{HOLD}[tail]"); parts.append('[tail]')
fc.append(''.join(parts) + f"concat=n={len(parts)}:v=0:a=1[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', ';'.join(fc), '-map', '[out]', '-ar', '44100', '-ac', '1',
                f'{A}/narration_edit.wav'], check=True)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{A}/narration_edit.wav']))
open(f'{ROOT}/build/word_times.txt', 'w').write('\n'.join(f'{s}-{e}' for s, e in times) + '\n')
open(f'{ROOT}/build/duration.txt', 'w').write(f'{dur:.3f}\n')
print(f'narration_edit.wav {dur:.2f}s; last word ends {times[-1][1]:.2f}s')
