// "One Million Checks vs Twenty Steps" — seekable, deterministic edit. renderFrame(t) draws frame at t seconds.
'use strict';
const W = 1080, H = 1920, FPS = 30, TOTAL = TL.total;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eio = p => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eo = p => 1 - Math.pow(1 - p, 3);
const back = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const LN = Object.fromEntries(TL.lines.map(l => [l.id, l]));
const cap = (id, k) => LN[id].captions[k].start;
const fmt = n => n.toLocaleString('en-US');
const FONT = w => `${w} Fredoka, sans-serif`;
const C = { bg: '#fbf6ec', ink: '#1d1b1a', yellow: '#ffd43b', dot: '#22a37c', opus: '#e07a55', grey: '#cfc8bb', panel: '#ffffff' };

// ---------- direction: per line, what each character does ----------
// arms: [left, right]; brows: [L, R] raise; tilt: + angry / - worried; eye: openness; look: pupils
const DIR = {
  1: { DOT: { arms: ['hip', 'up'], fR: 1, mood: 'grin', brows: [0.6, 0.6], hop: 1 },
       OPUS: { arms: ['cross', 'cross'], mood: 'flat', brows: [0, 0.5], eye: 0.7, look: [-0.8, 0] } },
  2: { OPUS: { arms: ['down', 'present'], mood: 'smug', brows: [0, 0.8], eye: 0.75, look: [-0.6, 0] },
       DOT: { arms: ['hip', 'hip'], mood: 'frown', brows: [-0.2, -0.2], tilt: 0.6, look: [0.7, 0] } },
  3: { DOT: { arms: ['shrug', 'shrug'], mood: 'flat', brows: [0.2, 0.2], tilt: 0.5, eye: 0.8, look: [0.7, 0] },
       OPUS: { arms: ['cross', 'cross'], mood: 'smug', brows: [0.3, 0.3], eye: 0.8, look: [-0.6, 0] } },
  4: { OPUS: { arms: ['down', 'raise'], fR: 1, mood: 'smile', brows: [0.4, 0.4], look: [-0.5, -0.6] },
       DOT: { arms: ['down', 'cheek'], mood: 'flat', brows: [0.7, 0.3], look: [0.4, -0.7] } },
  5: { DOT: { arms: ['shrug', 'shrug'], mood: 'smug', brows: [0.1, 0.5], eye: 0.55, look: [0.6, 0.1] },
       OPUS: { arms: ['cross', 'cross'], mood: 'flat', brows: [0, 0], eye: 0.6, look: [-0.7, 0] } },
  6: { OPUS: { arms: ['down', 'raise'], fR: 1, mood: 'smug', brows: [0.2, 0.7], look: [-0.5, 0] },
       DOT: { arms: ['down', 'down'], mood: 'flat', brows: [0.6, 0.6], look: [0.5, -0.3], eyeGrow: true } },
  7: { DOT: { arms: ['cheek', 'cheek'], mood: 'flat', brows: [1, 1], tilt: -0.6, eyeScale: 1.15, look: [0, 0], hop: 1.6, shake: true },
       OPUS: { arms: ['cross', 'cross'], mood: 'smug', brows: [0.2, 0.6], eye: 0.75, look: [-0.7, 0] } },
  8: { OPUS: { arms: ['down', 'raise'], fR: 1, mood: 'flat', brows: [0.5, 0.2], look: [-0.4, 0] },
       DOT: { arms: ['down', 'down'], mood: 'frown', brows: [0.4, 0.4], tilt: -0.5, look: [0.5, 0], lean: 0.05 } },
  9: { DOT: { arms: ['cross', 'cross'], mood: 'frown', brows: [-0.2, -0.2], tilt: 0.7, eye: 0.7, look: [0.7, 0] },
       OPUS: { arms: ['down', 'down'], mood: 'smile', brows: [0.4, 0.4], look: [-0.6, 0] } },
  10: { OPUS: { arms: ['down', 'down'], mood: 'smug', brows: [0, 0.9], eye: 0.5, look: [-0.9, 0] },
        DOT: { arms: ['cross', 'cross'], mood: 'frown', brows: [-0.3, -0.3], tilt: 0.8, eye: 0.7, look: [0.8, 0] } },
};
const LOOP_POSE = { DOT: { arms: ['hip', 'up'], fR: 1, mood: 'grin', brows: [0.6, 0.6] } };   // final beat == opening pose

// ---------- shots: camera + character placement ----------
const SHOT_LAYOUT = {
  1: { DOT: [430, 1330, 1.05], OPUS: [930, 1330, 0.72], cam: [1.0, 1.06] },
  2: { DOT: [300, 1330, 0.9], OPUS: [785, 1330, 0.9], cam: [1.0, 1.04] },
  3: { DOT: [215, 1340, 0.72], OPUS: [760, 1330, 0.95], cam: [1.0, 1.03] },
  4: { DOT: [290, 1360, 0.78], OPUS: [790, 1360, 0.78], cam: [1.0, 1.02] },
  5: { DOT: [540, 1330, 1.3], OPUS: [1010, 1340, 0.7], cam: [1.0, 1.08] },
  6: { DOT: [300, 1330, 0.9], OPUS: [785, 1330, 0.9], cam: [1.0, 1.04] },
};
function lineAt(t) { let cur = TL.lines[0]; for (const l of TL.lines) if (t >= l.start - 0.12) cur = l; return cur; }
function shotAt(t) { return lineAt(t).shot; }
function shotStart(s) { return TL.lines.find(l => l.shot === s).start - 0.12; }

function blink(t, off) { const c = (t + off) % 3.7; return c < 0.13 ? 0.08 : 1; }
function mouthFor(spk, t) {
  const l = TL.lines.find(l => l.speaker === spk && t >= l.start && t < l.end);
  if (!l || l.pending || !l.env.length) return 0;
  return l.env[Math.min(l.env.length - 1, Math.floor((t - l.start) * FPS))] || 0;
}
function charState(kind, t) {
  const l = lineAt(t), prev = TL.lines[TL.lines.indexOf(l) - 1];
  let d = DIR[l.id][kind];
  const loop = l.id === 10 && t > l.end + 0.25 && kind === 'DOT';
  if (loop) d = Object.assign({}, d, LOOP_POSE.DOT);
  const pd = loop ? DIR[10].DOT : prev ? DIR[prev.id][kind] : d;
  const k = eo(prog(t, loop ? l.end + 0.25 : l.start - 0.12, (loop ? l.end + 0.25 : l.start - 0.12) + 0.28));
  const lay = SHOT_LAYOUT[l.shot][kind];
  const speaking = l.speaker === kind && t >= l.start && t < l.end;
  let hop = 0, squash = 0;
  if (d.hop) { const p = prog(t, (loop ? l.end + 0.25 : l.start) - 0.05, (loop ? l.end + 0.25 : l.start) + 0.45); hop = Math.sin(Math.PI * p) * 0.18 * d.hop; squash = p > 0.85 && p < 1 ? -0.5 * Math.sin((p - 0.85) / 0.15 * Math.PI) : 0; }
  if (speaking) hop += mouthFor(kind, t) * 0.018;                      // tiny talk bounce
  const eyeGrow = d.eyeGrow ? 1 + 0.18 * prog(t, cap(6, 2), cap(6, 2) + 0.4) : 1;
  return {
    kind, t, x: lay[0], y: lay[1], s: lay[2],
    armL: d.arms[0], armR: d.arms[1], armBlend: { fromL: pd.arms[0], fromR: pd.arms[1], k },
    fingerR: !!d.fR, mood: d.mood, browL: lerp(pd.brows[0], d.brows[0], k), browR: lerp(pd.brows[1], d.brows[1], k),
    browTilt: lerp(pd.tilt || 0, d.tilt || 0, k), eyeOpen: Math.min(blink(t, kind === 'DOT' ? 0 : 1.6), d.eye || 1),
    look: d.look, mouth: speaking ? mouthFor(kind, t) : 0, hop, squash, lean: d.lean || 0,
    eyeScale: (d.eyeScale || 1) * eyeGrow,
  };
}

// ---------- drawing helpers ----------
function bg(t) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(30,25,20,0.05)';
  for (let y = 40; y < H; y += 60) for (let x = (y / 60) % 2 ? 30 : 0; x < W; x += 60) { ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fill(); }
  ctx.fillStyle = '#efe6d3'; ctx.fillRect(0, 1350, W, H - 1350);
  ctx.fillStyle = 'rgba(30,25,20,0.08)'; ctx.fillRect(0, 1350, W, 4);
}
function panel(x, y, w, h, a = 1) {
  ctx.save(); ctx.globalAlpha = a; ctx.shadowColor = 'rgba(40,30,20,0.18)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 34); ctx.fillStyle = C.panel; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke(); ctx.restore();
}
function text(s, x, y, size, color = C.ink, weight = 600, align = 'center', a = 1) {
  ctx.save(); ctx.globalAlpha = a; ctx.font = FONT(weight) .replace('Fredoka', `${size}px Fredoka`); ctx.font = `${weight} ${size}px Fredoka, sans-serif`;
  ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); ctx.restore();
}
function pill(s, x, y, size, fill, color = C.ink, a = 1, sc = 1) {
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(sc, sc); ctx.font = `700 ${size}px Fredoka, sans-serif`;
  const w = ctx.measureText(s).width + size * 0.9, h = size * 1.45;
  ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fillStyle = fill; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 2); ctx.restore();
}
function tile(x, y, w, h, label, fill, a = 1, outline = C.ink) {
  ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, 12); ctx.fillStyle = fill; ctx.fill();
  ctx.lineWidth = 4; ctx.strokeStyle = outline; ctx.stroke();
  if (label !== '') { ctx.font = `600 ${Math.round(h * 0.42)}px Fredoka, sans-serif`; ctx.fillStyle = C.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(label, x, y + 2); }
  ctx.restore();
}
const popIn = (t, t0, d = 0.35) => t < t0 ? 0 : back(prog(t, t0, t0 + d));

// ---------- overlays per shot ----------
function ovHaystack(t) {                       // S1: one million numbers, one target
  const t0 = cap(1, 0);
  const s = popIn(t, t0);
  if (s > 0) pill('1,000,000', 540, 330, 92, C.yellow, C.ink, 1, s);
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 26; i++) {
    const x = 90 + rnd() * 900, y = 470 + rnd() * 360, n = Math.floor(rnd() * 999999);
    const a = prog(t, t0 + 0.1 + i * 0.02, t0 + 0.3 + i * 0.02);
    if (a > 0) tile(x, y + Math.sin(t * 2 + i) * 6, 128, 54, fmt(n), '#fffdf6', a * 0.9, '#b9ae9a');
  }
  const ta = popIn(t, cap(1, 1));
  if (ta > 0) {                                  // the one target
    ctx.save(); ctx.translate(760, 640); ctx.scale(ta, ta);
    [46, 32, 18].forEach((r, k) => { ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fillStyle = k % 2 ? '#fff' : '#e8584a'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = C.ink; ctx.stroke(); });
    ctx.restore(); text('target', 760, 712, 34, C.ink, 600, 'center', ta);
  }
}
function ovLinear(t) {                         // S2: checking one by one, up to a million checks
  const a = prog(t, LN[2].start - 0.1, LN[2].start + 0.2);
  if (a <= 0) return;
  panel(60, 250, 960, 470, a);
  text('LINEAR SEARCH: check every item', 540, 320, 44, C.ink, 700, 'center', a);
  const n = 8, x0 = 150;
  const run = prog(t, LN[2].start + 0.2, LN[3].end);           // the scan keeps going (and going)
  const idx = Math.floor(run * 60) % n;
  for (let i = 0; i < n; i++) tile(x0 + i * 112, 450, 96, 96, '', i < idx ? '#e9e3d6' : '#fffdf6', a);
  tile(x0 + idx * 112, 450, 104, 104, '?', C.yellow, a);
  const shown = Math.min(1000000, Math.floor(Math.pow(run, 2.2) * 1000000));
  text(`checks so far: ${fmt(Math.max(1, shown))}`, 540, 580, 46, C.ink, 600, 'center', a);
  if (t > cap(2, 0)) pill('worst case: 1,000,000 checks', 540, 665, 38, C.yellow, C.ink, a, popIn(t, cap(2, 0)));
}
const SORTED = [2, 5, 9, 14, 21, 30, 38, 47, 55, 61, 70, 76, 84, 91, 99];
function ovSorted(t) {                         // S3: sorted list, check the middle, drop half
  const a = prog(t, LN[4].start - 0.1, LN[4].start + 0.2);
  if (a <= 0) return;
  panel(50, 230, 980, 560, a);
  text('a sorted list (1,000,000 items)', 540, 300, 40, C.ink, 600, 'center', a);
  const sa = popIn(t, cap(4, 0));
  if (sa > 0) pill('ALREADY SORTED ✓', 540, 380, 44, C.yellow, C.ink, 1, sa);
  const n = SORTED.length, w = 58, x0 = 540 - (n - 1) * 31;
  const midT = cap(4, 1) + 0.3, cutT = cap(4, 2) + 0.2;
  const cutA = prog(t, cutT, cutT + 0.4);
  for (let i = 0; i < n; i++) {
    const gone = i <= 7 ? cutA : 0;
    tile(x0 + i * 62, 520, w, 80, String(SORTED[i]), i === 7 && t > midT ? C.yellow : '#fffdf6', a * (1 - 0.75 * gone), i === 7 && t > midT ? C.ink : '#8d826e');
  }
  text('target: 70', 220, 640, 38, C.ink, 700, 'center', a);
  if (t > midT) {
    const m = popIn(t, midT); ctx.save(); ctx.globalAlpha = a; ctx.translate(x0 + 7 * 62, 440); ctx.scale(m, m);
    ctx.beginPath(); ctx.moveTo(0, 18); ctx.lineTo(-22, -16); ctx.lineTo(22, -16); ctx.closePath(); ctx.fillStyle = C.opus; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = C.ink; ctx.stroke(); ctx.restore();
    text('middle: 47', x0 + 7 * 62, 640, 38, C.ink, 600, 'center', prog(t, midT, midT + 0.3));
  }
  if (cutA > 0) {
    text('70 > 47 → left half is out', 540, 720, 40, '#b23b2e', 700, 'center', cutA);
    ctx.save(); ctx.globalAlpha = cutA; ctx.strokeStyle = '#b23b2e'; ctx.lineWidth = 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x0 - 30, 520); ctx.lineTo(x0 + 7 * 62 + 30, 520); ctx.stroke(); ctx.restore();
  }
}
const LEFT = (() => { const a = [1000000]; for (let k = 1; k <= 19; k++) a.push(Math.floor(1000000 / Math.pow(2, k))); return a; })();
function ovHalving(t) {                        // S4: the range halves, check after check (max 20)
  const a = prog(t, LN[5].start - 0.1, LN[5].start + 0.2);
  if (a <= 0) return;
  panel(50, 220, 980, 640, a);
  text('BINARY SEARCH: each check halves the range', 540, 290, 40, C.ink, 700, 'center', a);
  const t0 = LN[5].start, t1 = cap(6, 2) + 0.3;
  const p = prog(t, t0, t1) * 20, k = Math.min(20, Math.floor(p)), f = p - Math.floor(p);
  // bar: the current range; it splits, one half fades, the kept half zooms back to full width
  const bx = 110, bw = 860, by = 420, bh = 90;
  const split = k < 20 ? eio(clamp(f * 2.2)) : 1;
  ctx.save(); ctx.globalAlpha = a;
  ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 18); ctx.fillStyle = '#fffdf6'; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke();
  if (k < 20) {
    const keepRight = k % 2 === 0, half = bw / 2, zoom = eio(clamp((f - 0.55) / 0.45));
    const gx = keepRight ? bx : bx + half;
    ctx.globalAlpha = a * (1 - zoom) * split; ctx.fillStyle = '#d9d2c4'; ctx.fillRect(gx + 4, by + 4, half - 8, bh - 8);
    ctx.globalAlpha = a; ctx.fillStyle = C.yellow;
    const kx = keepRight ? lerp(bx + half, bx, zoom) : bx, kw = lerp(half, bw, zoom);
    ctx.beginPath(); ctx.roundRect(kx + 4, by + 4, kw - 8, bh - 8, 14); ctx.fill();
    ctx.strokeStyle = C.opus; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(bx + half, by - 18); ctx.lineTo(bx + half, by + bh + 18); ctx.globalAlpha = a * split * (1 - zoom); ctx.stroke();
  } else { ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.roundRect(bx + bw / 2 - 30, by + 4, 60, bh - 8, 14); ctx.fill(); }
  ctx.restore();
  const shownK = Math.max(0, Math.min(20, k + (f > 0.1 ? 1 : 0)));
  text(`check #${shownK}`, 300, 600, 56, C.ink, 700, 'center', a);
  const leftTxt = shownK === 0 ? fmt(1000000) : shownK <= 19 ? fmt(LEFT[shownK]) : 'found it';
  text(shownK === 20 ? 'last item checked' : `items left: ${leftTxt}`, 760, 600, 44, C.ink, 600, 'center', a);
  // little history ticks: 20 dots fill as checks happen
  for (let i = 0; i < 20; i++) { ctx.beginPath(); ctx.arc(160 + i * 40, 700, 13, 0, Math.PI * 2); ctx.fillStyle = i < shownK ? C.opus : '#ece5d6'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = C.ink; ctx.stroke(); }
  if (t > cap(6, 2)) pill('at most 20 checks', 540, 790, 46, C.yellow, C.ink, a, popIn(t, cap(6, 2)));
}
function ovRecap(t) {                          // S5: the comparison — operation counts, not timings
  const a = prog(t, LN[7].start + 0.2, LN[7].start + 0.5);
  if (a <= 0) return;
  panel(60, 230, 960, 400, a);
  text('LINEAR SEARCH', 300, 320, 40, C.ink, 700, 'center', a);
  text('up to', 300, 385, 34, C.ink, 500, 'center', a);
  pill('1,000,000', 300, 455, 56, '#fffdf6', C.ink, a, 1);
  text('checks', 300, 530, 34, C.ink, 500, 'center', a);
  text('BINARY SEARCH*', 780, 320, 40, C.ink, 700, 'center', a);
  text('at most', 780, 385, 34, C.ink, 500, 'center', a);
  pill('20', 780, 455, 64, C.yellow, C.ink, a, popIn(t, LN[7].start + 0.5));
  text('checks', 780, 530, 34, C.ink, 500, 'center', a);
  text('*on an already-sorted list · counts of checks, not speed', 540, 595, 27, '#6b6152', 500, 'center', a);
}
function ovSortCost(t) {                       // S6: sorting first has a cost
  const a = prog(t, LN[8].start - 0.1, LN[8].start + 0.2) * (1 - prog(t, LN[9].end, LN[9].end + 0.4));
  if (a <= 0) return;
  panel(60, 250, 960, 420, a);
  text('unsorted? sort it first', 540, 320, 42, C.ink, 700, 'center', a);
  const vals = [61, 9, 84, 30, 2, 76, 47, 14, 99, 38], sorted = [...vals].sort((x, y) => x - y);
  const sp = eio(prog(t, cap(8, 1), cap(8, 1) + 1.2));
  vals.forEach((v, i) => {
    const j = sorted.indexOf(v), x = 540 + (lerp(i, j, sp) - 4.5) * 86, y = 450 - Math.sin(sp * Math.PI) * (i % 2 ? 40 : -40);
    tile(x, y, 74, 74, String(v), sp >= 1 ? '#fffdf6' : '#f5efe2', a);
  });
  if (t > cap(8, 1)) pill('sorting = extra work', 540, 590, 44, C.yellow, C.ink, a, popIn(t, cap(8, 1)));
}

// ---------- captions ----------
function captions(t) {
  const l = TL.lines.find(l => l.captions.some(c => t >= c.start && t < c.end));
  if (!l) return;
  const c = l.captions.find(c => t >= c.start && t < c.end);
  const p = eo(prog(t, c.start, c.start + 0.12));
  const parts = c.text.split('*'); const size = 62;
  ctx.save(); ctx.font = `600 ${size}px Fredoka, sans-serif`;
  const widths = parts.map((s, i) => ctx.measureText(s).width + (i % 2 ? size * 0.5 : 0));
  let tw = widths.reduce((a, b) => a + b, 0);
  const maxW = 900, lines = tw > maxW ? 2 : 1;
  // two-line wrap: split at the space closest to the middle (plain parts only)
  let rows = [parts];
  if (lines === 2) {
    const full = c.text; const mid = full.length / 2; let cut = -1, best = 1e9, inHl = false;
    for (let i = 0; i < full.length; i++) { if (full[i] === '*') inHl = !inHl; if (full[i] === ' ' && !inHl && Math.abs(i - mid) < best) { best = Math.abs(i - mid); cut = i; } }
    rows = [full.slice(0, cut).split('*'), full.slice(cut + 1).split('*')];
    // keep highlight parity on the second row
    const opens = (full.slice(0, cut).match(/\*/g) || []).length; if (opens % 2) rows[1] = ['', ...rows[1]];
  }
  const lh = size * 1.3, by = 1478 - (rows.length - 1) * lh / 2;
  const accent = l.speaker === 'DOT' ? C.dot : C.opus;
  const mw = (s, hl) => { if (!hl) return ctx.measureText(s).width; ctx.font = `700 ${size}px Fredoka, sans-serif`; const w = ctx.measureText(s).width; ctx.font = `600 ${size}px Fredoka, sans-serif`; return w; };
  const rowW = rows.map(r => r.reduce((a, s, i) => a + (s ? mw(s, i % 2) + (i % 2 ? size * 0.5 + 6 : 0) : 0), 0));
  const boxW = Math.max(...rowW) + 60, boxH = rows.length * lh + 26;
  ctx.globalAlpha = p; ctx.translate(540 - 20, by + (1 - p) * 12);
  ctx.beginPath(); ctx.roundRect(-boxW / 2, -lh / 2 - 13, boxW, boxH, 26); ctx.fillStyle = 'rgba(29,27,26,0.9)'; ctx.fill();
  ctx.fillStyle = accent; ctx.beginPath(); ctx.roundRect(-boxW / 2, -lh / 2 - 13, 14, boxH, 7); ctx.fill();
  ctx.textBaseline = 'middle';
  rows.forEach((r, ri) => {
    let x = -rowW[ri] / 2; const y = ri * lh;
    r.forEach((s, i) => {
      if (!s) return;
      const w = mw(s, i % 2);
      if (i % 2) {
        ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.roundRect(x, y - size * 0.62, w + size * 0.5, size * 1.24, 14); ctx.fill();
        ctx.fillStyle = C.ink; ctx.font = `700 ${size}px Fredoka, sans-serif`; ctx.fillText(s, x + size * 0.25, y + 3); ctx.font = `600 ${size}px Fredoka, sans-serif`;
        x += w + size * 0.5 + 6;
      } else { ctx.fillStyle = '#fff'; ctx.fillText(s, x, y + 3); x += w; }
    });
  });
  ctx.restore();
}

// ---------- frame ----------
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
  const s = shotAt(t), s0 = shotStart(s), lay = SHOT_LAYOUT[s];
  const nextStart = s < 6 ? shotStart(s + 1) : TOTAL;
  const z = lerp(lay.cam[0], lay.cam[1], eio(prog(t, s0, nextStart)));
  let shake = 0; if (s === 5) shake = Math.sin(t * 70) * 10 * (1 - prog(t, LN[7].start, LN[7].start + 0.5));
  const whip = s > 1 ? (1 - eo(prog(t, s0, s0 + 0.22))) * 120 : 0;       // quick whip-in on each cut
  // loop: settle the final frame back to the opening framing
  ctx.translate(540 + shake + whip, 1000); ctx.scale(z, z); ctx.translate(-540, -1000);
  bg(t);
  ({ 1: ovHaystack, 2: ovLinear, 3: ovSorted, 4: ovHalving, 5: ovRecap, 6: ovSortCost })[s](t);
  ['OPUS', 'DOT'].forEach(k => drawMascot(ctx, charState(k, t)));
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  captions(t);
  const l = lineAt(t);
  if (l.pending && t >= l.start - 0.1 && t < l.end + 0.2) pill('VO PENDING · WIP', 210, 90, 30, '#e8584a', '#fff');
}

window.READY = (async () => {
  await document.fonts.load('600 60px Fredoka');
  window.renderFrame = renderFrame; window.DURATION = TOTAL; window.FPS = FPS;
  const q = new URLSearchParams(location.search); renderFrame(parseFloat(q.get('t') || '0'));
  return true;
})();
