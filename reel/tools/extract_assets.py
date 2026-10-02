"""Stitch bridged tiles back into full sheets and cut transparent sheets into clean cutouts."""
import os, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAW = os.path.join(os.path.dirname(__file__), '..', 'assets', 'raw')
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'cut')
os.makedirs(OUT, exist_ok=True)

def stitch(name):
    l = Image.open(f'{RAW}/{name}_L.webp'); r = Image.open(f'{RAW}/{name}_R.webp')
    mode = 'RGBA' if 'A' in l.mode else 'RGB'
    im = Image.new(mode, (l.width + r.width, l.height))
    im.paste(l.convert(mode), (0, 0)); im.paste(r.convert(mode), (l.width, 0))
    im.save(f'{RAW}/{name}_full.png'); return im

def cut(im, prefix, min_frac=0.004):
    a = np.array(im)[..., 3]
    mask = a > 60
    grown = ndimage.binary_dilation(mask, iterations=14)
    lab, n = ndimage.label(grown)
    total = mask.size; parts = []
    for i in range(1, n + 1):
        comp = (lab == i) & mask
        if comp.sum() < total * min_frac: continue
        ys, xs = np.where(comp)
        parts.append((ys.min(), xs.min(), ys.max(), xs.max(), i))
    parts.sort(key=lambda p: (round(p[0] / 300), p[1]))  # reading order: rows then columns
    arr = np.array(im)
    for k, (y0, x0, y1, x1, i) in enumerate(parts):
        keep = ndimage.binary_dilation(lab == i, iterations=2)
        sub = arr.copy(); sub[..., 3] = np.where(keep, sub[..., 3], 0)
        a_ = sub[..., 3].astype(float)
        a_[a_ < 25] = 0                                   # kill faint specks
        sub[..., 3] = a_.astype(np.uint8)
        pad = 6
        crop = Image.fromarray(sub).crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
        crop.save(f'{OUT}/{prefix}_{k+1:02d}.png')
        print(prefix, k + 1, crop.size)
    return len(parts)

# character poses sit in a 2x2 grid; cut per quadrant so stacked poses never merge
s1 = stitch('s1'); q = s1.width // 2
for k, (x, y) in enumerate([(0, 0), (q, 0), (0, q), (q, q)]):
    cut(s1.crop((x, y, x + q, y + q)), f's1_{k+1}')
for s in ['s2', 's3']:
    cut(stitch(s), s)
for b in ['bgshop', 'bgmap']:
    stitch(b).convert('RGB').save(f'{OUT}/{b}.png')

# contact sheet for inspection
files = sorted(f for f in os.listdir(OUT) if f.startswith('s'))
th = 260; cols = 6; rows = (len(files) + cols - 1) // cols
cs = Image.new('RGB', (cols * th, rows * (th + 24)), (176, 176, 176)); d = ImageDraw.Draw(cs)
for i, f in enumerate(files):
    im = Image.open(f'{OUT}/{f}'); im.thumbnail((th - 10, th - 10))
    x, y = (i % cols) * th, (i // cols) * (th + 24)
    cs.paste(im, (x + 5, y + 5), im); d.text((x + 6, y + th + 4), f, fill=(0, 0, 0))
cs.save(f'{OUT}/../contact_sheet.png')
