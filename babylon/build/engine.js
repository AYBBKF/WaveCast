// Shared paper-cut animation engine (deterministic, seekable). Extracted from the DEEP CURIOUS WW3 Reel.
'use strict';
const W = 1080, H = 1920, FPS = 30;
const C = {
  cream: '#F3EAD3', paper: '#FBF6EA', kraft: '#C9A97A', mustard: '#D9A93A', coral: '#E08A72',
  teal: '#3E8A8C', navy: '#1E2B4A', ink: '#1B2236', copper: '#B8733A', clay: '#B5653F',
};
const IMG = {};
// assets load if present; missing ones render as labelled paper placeholders until production art exists
function loadAll(names) {
  return Promise.all(names.map(n => new Promise(res => {
    const im = new Image(); im.onload = () => { IMG[n] = im; res(); }; im.onerror = () => res();
    im.src = `../assets/layers/${n}.png`;
  })));
}
const PLACEHOLDER = {};   // name -> aspect (h / w), set by the scene file
// ---------- deterministic helpers ----------
function hash(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return ((h >>> 0) % 100000) / 100000;
}
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, p) => a + (b - a) * p;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const easeInOut = p => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const easeOut = p => 1 - Math.pow(1 - p, 3);
const easeOutBack = p => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); };
const step12 = t => Math.floor(t * 12);          // stop-motion "on twos" clock
const stepT = t => Math.floor(t * 15) / 15;      // quantised time for pop-ins
const jit = (key, t, amp) => (hash(key + ':' + step12(t)) - 0.5) * 2 * amp;
const bump = (t, a, b) => Math.sin(Math.PI * prog(t, a, b));
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');

// ---------- paper grain (seeded, generated once) ----------
let GRAIN = null;
function makeGrain() {
  const g = document.createElement('canvas'); g.width = 540; g.height = 960;
  const gx = g.getContext('2d'); const id = gx.createImageData(540, 960); const r = mulberry32(7);
  for (let i = 0; i < id.data.length; i += 4) {
    const v = 128 + (r() - 0.5) * 70; id.data[i] = v; id.data[i + 1] = v * 0.98; id.data[i + 2] = v * 0.94; id.data[i + 3] = 255;
  }
  gx.putImageData(id, 0, 0);
  gx.globalAlpha = 0.18; gx.strokeStyle = '#6b5a40'; gx.lineWidth = 0.6;
  for (let i = 0; i < 260; i++) {           // paper fibres
    const x = r() * 540, y = r() * 960, a = r() * Math.PI * 2, l = 6 + r() * 18;
    gx.beginPath(); gx.moveTo(x, y); gx.quadraticCurveTo(x + Math.cos(a) * l * 0.5 + r() * 4, y + Math.sin(a) * l * 0.5, x + Math.cos(a) * l, y + Math.sin(a) * l); gx.stroke();
  }
  GRAIN = g;
}

// ---------- placeholders (only used while production art is missing) ----------
const PH = {};
function placeholderImg(name, w, h) {
  if (PH[name]) return PH[name];
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  const bg = w > 1000;
  g.fillStyle = bg ? '#E9DCC0' : '#FFFDF7'; g.fillRect(0, 0, w, h);
  if (!bg) { g.fillStyle = '#F1E6CC'; g.fillRect(12, 12, w - 24, h - 24); }
  g.strokeStyle = '#B9A27A'; g.setLineDash([18, 12]); g.lineWidth = 6; g.strokeRect(16, 16, w - 32, h - 32);
  g.fillStyle = '#7A6545'; g.font = `700 ${Math.round(Math.min(w, h) / 9)}px sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(name, w / 2, h / 2);
  return (PH[name] = c);
}

// ---------- primitives ----------
let BG = { x0: 0, y0: 0, s: 1, iw: 1, ih: 1 };
function drawBg(name, zoom, cx, cy, tint) {
  const im = IMG[name] || placeholderImg(name, 1520, 2688); const s = Math.max(W / im.width, H / im.height) * zoom;
  let x0 = W / 2 - cx * im.width * s, y0 = H / 2 - cy * im.height * s;
  x0 = Math.min(0, Math.max(W - im.width * s, x0)); y0 = Math.min(0, Math.max(H - im.height * s, y0));
  ctx.drawImage(im, x0, y0, im.width * s, im.height * s);
  BG = { x0, y0, s, iw: im.width, ih: im.height };
  if (tint) { ctx.fillStyle = tint; ctx.fillRect(0, 0, W, H); }
}
const bgPt = (u, v) => [BG.x0 + u * BG.iw * BG.s, BG.y0 + v * BG.ih * BG.s];

function shadowOn(strength = 1) {
  ctx.shadowColor = `rgba(45,28,12,${0.34 * strength})`; ctx.shadowBlur = 26; ctx.shadowOffsetX = 6; ctx.shadowOffsetY = 12;
}
function shadowOff() { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0; }

// sticker: draws a cut-out centred at (x, y) [or bottom-anchored], width w
function sticker(name, x, y, w, o = {}) {
  const im = IMG[name] || placeholderImg(name, 600, Math.round(600 * (PLACEHOLDER[name] || 1))); const h = w * im.height / im.width;
  const t = o.t ?? 0; const a = o.alpha ?? 1; const sc = o.scale ?? 1;
  if (a <= 0 || sc <= 0) return { x, y, w, h };
  const jx = o.still ? 0 : jit(name + 'x', t, 1.4), jy = o.still ? 0 : jit(name + 'y', t, 1.4);
  const jr = o.still ? 0 : jit(name + 'r', t, 0.004);
  ctx.save(); ctx.globalAlpha = a;
  const ay = o.anchor === 'bottom' ? -h : -h / 2;
  ctx.translate(x + jx, y + jy); ctx.rotate((o.rot || 0) + jr); ctx.scale(sc, sc);
  if (o.shadow !== false) shadowOn(o.shadowStrength ?? 1);
  ctx.drawImage(im, -w / 2, ay, w, h);
  ctx.restore(); shadowOff();
  return { x, y, w, h, top: o.anchor === 'bottom' ? y - h : y - h / 2 };
}

function pop(t, t0, dur = 0.42) {
  if (t < t0) return { s: 0, a: 0 };
  const p = prog(stepT(t), t0, t0 + dur);
  return { s: lerp(0.55, 1, easeOutBack(p)), a: clamp(p * 3) };
}

// jagged paper polygon around a rect
function paperPath(x, y, w, h, seed, amp = 4) {
  const r = mulberry32(Math.floor(seed * 1e6)); const pts = [];
  const n = Math.max(6, Math.round(w / 40)), m = Math.max(3, Math.round(h / 40));
  for (let i = 0; i <= n; i++) pts.push([x + w * i / n, y + (r() - 0.5) * amp]);
  for (let i = 1; i <= m; i++) pts.push([x + w + (r() - 0.5) * amp, y + h * i / m]);
  for (let i = n - 1; i >= 0; i--) pts.push([x + w * i / n, y + h + (r() - 0.5) * amp]);
  for (let i = m - 1; i >= 1; i--) pts.push([x + (r() - 0.5) * amp, y + h * i / m]);
  ctx.beginPath(); pts.forEach(([px, py], i) => i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)); ctx.closePath();
}

// handwritten-style label card (Arabic text shaped by the browser, never split into letters)
function card(text, x, y, o = {}) {
  const t = o.t ?? 0; const a = o.alpha ?? 1; const sc = o.scale ?? 1;
  if (a <= 0 || sc <= 0) return;
  const size = o.size || 54; const font = o.font === 'cairo' ? `800 ${size}px Cairo` : `700 ${size}px Ruqaa`;
  ctx.save(); ctx.font = font; ctx.direction = 'rtl';
  const lines = String(text).split('\n');
  const tw = Math.max(...lines.map(l => ctx.measureText(l).width));
  const lh = size * (o.font === 'cairo' ? 1.45 : 1.55);
  const pw = tw + (o.padX ?? size * 0.9), ph = lines.length * lh + (o.padY ?? size * 0.35);
  ctx.globalAlpha = a;
  ctx.translate(x + jit(text + 'cx', t, 1), y + jit(text + 'cy', t, 1));
  ctx.rotate((o.rot || 0) + jit(text + 'cr', t, 0.003)); ctx.scale(sc, sc);
  shadowOn(0.9); paperPath(-pw / 2 - 8, -ph / 2 - 8, pw + 16, ph + 16, hash(text + 'b'), 5);
  ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();                      // white paper border
  paperPath(-pw / 2, -ph / 2, pw, ph, hash(text), 4);
  ctx.fillStyle = o.fill || C.paper; ctx.fill();
  if (o.edge) { ctx.lineWidth = 7; ctx.strokeStyle = o.edge; ctx.stroke(); }
  ctx.fillStyle = o.ink || C.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((l, i) => ctx.fillText(l, 0, (i - (lines.length - 1) / 2) * lh + size * 0.04));
  ctx.restore();
}

// smooth path through points; returns dense samples
function samplePath(pts, seg = 24) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let k = 0; k < seg; k++) {
      const u = k / seg, u2 = u * u, u3 = u2 * u;
      out.push([0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3),
        0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)]);
    }
  }
  out.push(pts[pts.length - 1]); return out;
}
function route(pts, p, o = {}) {
  if (p <= 0) return null;
  const s = samplePath(pts); let L = 0; const acc = [0];
  for (let i = 1; i < s.length; i++) { L += Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]); acc.push(L); }
  const target = L * clamp(p); let end = s[0];
  ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.globalAlpha = o.alpha ?? 1;
  const strokeIt = (color, width, dash) => {
    ctx.beginPath(); ctx.moveTo(s[0][0], s[0][1]);
    for (let i = 1; i < s.length && acc[i] <= target; i++) { ctx.lineTo(s[i][0], s[i][1]); end = s[i]; }
    ctx.setLineDash(dash || []); ctx.lineDashOffset = -(o.flow || 0);
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke();
  };
  if (o.border !== false) strokeIt('rgba(255,253,247,0.95)', (o.width || 10) + 8, o.dash);
  strokeIt(o.color || C.cream, o.width || 10, o.dash);
  ctx.restore();
  return { end, len: L };
}
function dot(x, y, r, color, a = 1) {
  ctx.save(); ctx.globalAlpha = a; shadowOn(0.6);
  ctx.beginPath(); ctx.arc(x, y, r + 5, 0, Math.PI * 2); ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); ctx.restore();
}
// irregular paper blob (used for drifting shadows)
function blob(x, y, r, seed, color, a) {
  const rnd = mulberry32(seed); ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = color; ctx.beginPath();
  const n = 28; for (let i = 0; i <= n; i++) { const ang = i / n * Math.PI * 2, rr = r * (0.82 + rnd() * 0.3); const px = x + Math.cos(ang) * rr, py = y + Math.sin(ang) * rr * 0.8; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
  ctx.closePath(); ctx.filter = 'blur(6px)'; ctx.fill(); ctx.filter = 'none'; ctx.restore();
}
function arrowUp(x, y, h, color, a = 1, wdt = 16) {
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = wdt; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - h + 18); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - 26, y - h + 30); ctx.lineTo(x, y - h - 6); ctx.lineTo(x + 26, y - h + 30); ctx.closePath(); ctx.fill(); ctx.restore();
}

// ---------- caption + chip overlays ----------
function captions(t) {
  const g = TIMELINE.groups.find(g => t >= g.start && t < g.end);
  if (!g) return;
  const p = prog(t, g.start, g.start + 0.14);
  const size = 66; ctx.save(); ctx.font = `800 ${size}px Cairo`; ctx.direction = 'rtl';
  const maxW = 860; const words = g.text.split(' '); const lines = [''];
  for (const wd of words) {                                  // wrap by whole words only (max 2 lines)
    const trial = lines[lines.length - 1] ? lines[lines.length - 1] + ' ' + wd : wd;
    if (ctx.measureText(trial).width > maxW && lines[lines.length - 1]) lines.push(wd); else lines[lines.length - 1] = trial;
  }
  const lh = size * 1.32; const tw = Math.max(...lines.map(l => ctx.measureText(l).width));
  const cx = 520, cy = 1510 - (lines.length - 1) * lh / 2;      // clear of right-edge UI and bottom 300px
  ctx.globalAlpha = p; ctx.translate(cx, cy + (1 - p) * 14);
  paperPath(-tw / 2 - 34, -lh / 2 - 6, tw + 68, lines.length * lh + 12, hash(g.text), 5);
  ctx.fillStyle = 'rgba(22,30,52,0.86)'; ctx.fill();
  ctx.fillStyle = '#FFF8E6'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((l, i) => ctx.fillText(l, 0, i * lh + 2));
  ctx.restore();
}
