// DEEP CURIOUS — "What if World War III reached your life without a bomb?" (Arabic Reel)
// Seekable, deterministic canvas timeline. window.renderFrame(t) draws the frame at time t (seconds).
'use strict';

const W = 1080, H = 1920, FPS = 30, DURATION = 61.5;
const C = {
  cream: '#F3EAD3', paper: '#FBF6EA', kraft: '#C9A97A', mustard: '#D9A93A', coral: '#E07A5F',
  teal: '#2F7F86', navy: '#1E2B4A', violet: '#7B6B9E', charcoal: '#2A2A30', ink: '#1B2236',
};

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

// ---------- assets ----------
const IMG = {};
const NAMES = ['bgshop', 'bgmap', 'char_bread_side', 'char_thinking', 'char_lookup', 'char_bread_front',
  'ship', 'truck', 'fuel_pump', 'barrel', 'factory', 'food_crate', 'globe', 'waves', 'bread',
  'city_damaged', 'heat', 'radiation', 'calendar', 'dove', 'handshake'];
function loadAll() {
  return Promise.all(NAMES.map(n => new Promise((res, rej) => {
    const im = new Image(); im.onload = () => { IMG[n] = im; res(); }; im.onerror = rej;
    im.src = `../assets/layers/${n}.png`;
  })));
}

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

// ---------- primitives ----------
let BG = { x0: 0, y0: 0, s: 1, iw: 1, ih: 1 };
function drawBg(name, zoom, cx, cy, tint) {
  const im = IMG[name]; const s = Math.max(W / im.width, H / im.height) * zoom;
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
  const im = IMG[name]; const h = w * im.height / im.width;
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
function hypoChip(t) {
  if (t < 0.25 || t > 8.4) return;
  const a = prog(t, 0.25, 0.5) * (1 - prog(t, 8.1, 8.4));
  const emph = 1 + 0.14 * bump(t, 4.7, 6.1);
  card('سيناريو افتراضي', 540, 150, { t, alpha: a, scale: emph, font: 'cairo', size: 44, fill: C.mustard, ink: C.ink, rot: -0.02 });
}

// ---------- scenes ----------
// S1: hook in the shop
function sceneHook(t) {
  drawBg('bgshop', 1.08 + 0.02 * t, 0.5, 0.5);
  // a dark paper shadow crosses the background
  const sx = lerp(1500, -420, easeInOut(prog(t, 0, 2.6)));
  blob(sx, 620, 520, 11, C.navy, 0.55); blob(sx + 260, 980, 380, 12, C.navy, 0.35);
  const ch = sticker('char_bread_side', 470, 1390, 720, { t, anchor: 'bottom' });
  const bread = [470 + 0.12 * 720 - 30, ch.top + 0.56 * ch.h];
  globeOnThread(t, bread, 0.85);
}
function globeOnThread(t, bread, t0) {
  const gp = pop(t, t0, 0.45); const gx = 820, gy = 560;
  if (gp.a > 0) {
    const tp = prog(t, t0 + 0.1, t0 + 0.6);
    ctx.save(); ctx.globalAlpha = gp.a; ctx.strokeStyle = C.ink; ctx.lineWidth = 3; ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(bread[0], bread[1]);
    const ex = lerp(bread[0], gx, tp), ey = lerp(bread[1], gy + 95, tp);
    ctx.quadraticCurveTo((bread[0] + ex) / 2 + 40, Math.max(bread[1], ey) + 60, ex, ey); ctx.stroke(); ctx.restore();
    sticker('globe', gx, gy + Math.sin(t * 1.6) * 6, 200, { t, scale: gp.s, alpha: gp.a });
  }
}

// S2–S4: world map → connected system → disruption
const OCEAN = { pac: [0.11, 0.55], atl: [0.36, 0.46], satl: [0.45, 0.61], ind: [0.70, 0.565], wpac: [0.94, 0.47] };
function sceneMap(t) {
  const z = lerp(1.26, 1.1, easeInOut(prog(t, 2.05, 4.6)));
  drawBg('bgmap', z, 0.5, 0.49);
  // ominous drifting shadows (symbolic, not tied to any country)
  blob(lerp(-200, 1250, prog(t, 2, 16)), 520, 460, 21, '#05070d', 0.32);
  blob(lerp(1300, -250, prog(t, 3, 18)), 1400, 520, 22, '#05070d', 0.28);
  const tp = pop(t, 2.6, 0.5);
  const titleA = tp.a * (1 - prog(t, 7.7, 8.1));
  card('الحرب العالمية الثالثة؟', 540, 470, { t, alpha: titleA, scale: tp.s, font: 'cairo', size: 86, rot: -0.03 });

  // illustrative supply network over open ocean (not real routes, not conflict locations)
  const P = k => bgPt(...OCEAN[k]);
  const netA = 1 - 0.55 * prog(t, 9.0, 9.6);
  const nodes = ['pac', 'atl', 'satl', 'ind', 'wpac'];
  nodes.forEach((k, i) => { const pp = pop(t, 8.05 + i * 0.12, 0.3); if (pp.a) dot(...P(k), 13 * pp.s, C.teal, pp.a * netA); });
  route([P('pac'), P('atl'), P('ind'), P('wpac')], prog(t, 8.1, 9.2), { color: C.cream, width: 7, dash: [18, 14], flow: t * 30, alpha: 0.9 * netA });
  route([P('atl'), P('satl'), P('ind')], prog(t, 8.4, 9.3), { color: C.cream, width: 7, dash: [18, 14], flow: t * 30, alpha: 0.9 * netA });
  card('مسارات توضيحية', 780, 1210, { t, alpha: pop(t, 8.4).a * (1 - prog(t, 9.0, 9.3)), size: 40, rot: 0.03 });

  // dim map for the object layout
  ctx.fillStyle = `rgba(16,22,40,${0.5 * prog(t, 9.0, 9.6)})`; ctx.fillRect(0, 0, W, H);

  // --- connected system (match cut: each object grows out of an ocean node) ---
  const slot = (k, x, y, t0) => { const p = easeOut(prog(stepT(t), t0, t0 + 0.5)); const [nx, ny] = P(k); return [lerp(nx, x, p), lerp(ny, y, p), p]; };
  const shipDrift = jit('drift', t, 0) + (t > 16.4 ? -Math.min(60, (t - 16.4) * 22) : 0);
  if (t >= 9.2) {
    const [x, y, p] = slot('atl', 450, 540, 9.2);
    sticker('waves', 450, y + 100, 760 * p, { t, alpha: p });
    sticker('ship', x + shipDrift + (t > 16.4 ? Math.sin(t * 3) * 4 : 0), y, 540 * p, { t, alpha: clamp(p * 2) });
    card('الشحن', 850, 430, { t, alpha: pop(t, 9.5).a, scale: pop(t, 9.5).s, size: 52, rot: 0.04 });
  }
  if (t >= 10.7) {
    const [x, y, p] = slot('ind', 330, 900, 10.7);
    const shake = t > 18.9 && t < 20.4 ? Math.sin(t * 40) * 3 : 0;
    sticker('fuel_pump', x + shake, y, 190 * p, { t, alpha: clamp(p * 2) });
    sticker('truck', x + 270, y + 30, 340 * p, { t, alpha: clamp(p * 2) });
    card('الطاقة', 860, 830, { t, alpha: pop(t, 11.0).a, scale: pop(t, 11.0).s, size: 52, rot: -0.03 });
  }
  if (t >= 12.3) {
    const [x, y, p] = slot('wpac', 380, 1255, 12.3);
    sticker('factory', x, y, 300 * p, { t, alpha: clamp(p * 2) });
    sticker('food_crate', x + 300, y + 15, 270 * p, { t, alpha: clamp(p * 2) });
    card('الإمدادات', 860, 1150, { t, alpha: pop(t, 12.7).a, scale: pop(t, 12.7).s, size: 52, rot: 0.03 });
  }
  // routes linking the chain
  const broken = t >= 15.84;
  const r1 = [[470, 640], [560, 720], [600, 790]];
  const r2 = [[620, 1000], [560, 1060], [660, 1120]];
  route(r1, prog(t, 12.9, 13.7), { color: broken ? C.coral : C.teal, width: 9, dash: [20, 14], flow: broken ? 0 : t * 40 });
  route(r2, prog(t, 13.5, 14.3), { color: C.teal, width: 9, dash: [20, 14], flow: t * 40 });
  if (t >= 16.3) {                       // break in the shipping route + possible delay
    const bp = pop(t, 16.3, 0.35); const bx = 555, by = 718;
    ctx.save(); ctx.globalAlpha = bp.a; ctx.translate(bx, by); ctx.scale(bp.s, bp.s);
    shadowOn(0.7); ctx.beginPath(); ctx.arc(0, 0, 40, 0, Math.PI * 2); ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
    ctx.strokeStyle = C.coral; ctx.lineWidth = 11; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-18, -18); ctx.lineTo(18, 18); ctx.moveTo(18, -18); ctx.lineTo(-18, 18); ctx.stroke(); ctx.restore();
    const cp = pop(t, 17.6, 0.4);
    if (cp.a) {
      card('تأخير محتمل', 835, 650, { t, alpha: cp.a, scale: cp.s, size: 44, edge: C.coral, rot: 0.04 });
      clock(690, 650, 26, t, cp.a);
    }
  }
  if (t >= 18.9) {                       // transport-cost indicator (no numbers)
    const mp = pop(t, 19.0, 0.4); const gx = 105, gy = 930, gh = 240;
    ctx.save(); ctx.globalAlpha = mp.a; ctx.translate(gx, gy); ctx.scale(mp.s, mp.s);
    shadowOn(0.8); paperPath(-46, -gh / 2, 92, gh, 0.42, 4); ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
    const lvl = lerp(0.22, 0.86, easeInOut(prog(t, 20.3, 22.2)));
    ctx.fillStyle = C.coral; ctx.fillRect(-30, gh / 2 - 16 - (gh - 32) * lvl, 60, (gh - 32) * lvl);
    ctx.strokeStyle = C.ink; ctx.lineWidth = 3; for (let i = 1; i < 5; i++) { const yy = gh / 2 - 16 - (gh - 32) * i / 5; ctx.beginPath(); ctx.moveTo(-30, yy); ctx.lineTo(-14, yy); ctx.stroke(); }
    ctx.restore();
    arrowUp(gx, gy - gh / 2 - 20, 70 + 30 * prog(t, 20.3, 22.2), C.coral, mp.a);
    card('كلفة النقل', gx + 20, gy + gh / 2 + 62, { t, alpha: mp.a, scale: mp.s, size: 40, rot: -0.03 });
    if (t >= 21.9) arrowUp(520, 1150, 80, C.coral, pop(t, 21.9).a, 13);   // production cost
  }
}
function clock(x, y, r, t, a) {
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fillStyle = '#FFFDF7'; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.coral; ctx.stroke();
  ctx.lineCap = 'round'; ctx.strokeStyle = C.ink; ctx.lineWidth = 4;
  const ang = step12(t) * 0.5; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(ang) * r * 0.7, Math.sin(ang) * r * 0.7); ctx.moveTo(0, 0); ctx.lineTo(0, -r * 0.5); ctx.stroke();
  ctx.restore();
}

// S5: back to the shop shelf
function sceneShelf(t) {
  drawBg('bgshop', 1.5 + 0.03 * prog(t, 22.3, 26.5), 0.70, 0.52);
  const ex = lerp(-420, 330, easeOut(prog(stepT(t), 22.6, 23.3)));
  sticker('char_thinking', ex - 40, 1400, 620, { t, anchor: 'bottom' });
  const [gx, gy] = bgPt(0.935, 0.587);
  if (t >= 24.1) {                                      // highlight the gap on the shelf
    const p = prog(t, 24.1, 24.7); ctx.save(); ctx.strokeStyle = C.coral; ctx.lineWidth = 9; ctx.setLineDash([22, 14]); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.ellipse(Math.min(gx, 860), gy, 140, 100, -0.08, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * p); ctx.stroke(); ctx.restore();
  }
  const tp = pop(t, 24.95, 0.4);
  if (tp.a) priceTag(Math.min(gx, 860) - 230, gy + 210, t, tp);
  card('قد يتأثر السعر', 640, 470, { t, alpha: pop(t, 25.3).a, scale: pop(t, 25.3).s, size: 50, edge: C.coral, rot: 0.03 });
}
function priceTag(x, y, t, p) {
  ctx.save(); ctx.globalAlpha = p.a; ctx.translate(x, y); ctx.rotate(-0.12 + Math.sin(t * 2.2) * 0.04); ctx.scale(p.s, p.s);
  ctx.strokeStyle = C.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-70, -60); ctx.quadraticCurveTo(-110, -120, -60, -150); ctx.stroke();
  shadowOn(0.8); ctx.beginPath(); ctx.moveTo(-90, -45); ctx.lineTo(70, -45); ctx.lineTo(110, 0); ctx.lineTo(70, 45); ctx.lineTo(-90, 45); ctx.closePath();
  ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
  ctx.beginPath(); ctx.moveTo(-80, -36); ctx.lineTo(64, -36); ctx.lineTo(98, 0); ctx.lineTo(64, 36); ctx.lineTo(-80, 36); ctx.closePath(); ctx.fillStyle = C.coral; ctx.fill();
  ctx.beginPath(); ctx.arc(70, 0, 9, 0, Math.PI * 2); ctx.fillStyle = '#FFFDF7'; ctx.fill();
  ctx.fillStyle = '#FFF8E6'; ctx.font = '900 64px Cairo'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.direction = 'rtl'; ctx.fillText('؟', -30, 4);
  ctx.restore();
  arrowUp(x + 20, y - 70, 70, C.coral, p.a, 12);
}

// S6/S8: the fork — world war vs possible nuclear escalation
const FORK = { base: [540, 1250], split: [540, 960], main: [[540, 960], [600, 770], [760, 600]], side: [[540, 960], [430, 820], [300, 710]] };
function fork(t, o) {
  const trunkP = o.full ? 1 : prog(t, 26.4, 27.0);
  route([FORK.base, FORK.split], trunkP, { color: C.cream, width: 64 });
  route(FORK.main, o.full ? 1 : prog(t, 26.9, 27.8), { color: C.cream, width: 64 });
  const sideA = o.sideAlpha ?? 1;
  route(FORK.side, o.full ? 1 : prog(t, 28.9, 29.6), { color: C.coral, width: 14, dash: [2, 26], alpha: sideA });
  (o.extra || []).forEach((pts, i) => route(pts, prog(t, 43.0 + i * 0.25, 43.6 + i * 0.25), { color: C.cream, width: 10, dash: [2, 22], alpha: 0.75 }));
  const m = o.full ? { s: 1, a: 1 } : pop(t, 27.72);
  card('حرب عالمية', 760, 500, { t, alpha: m.a, scale: m.s, font: 'cairo', size: 58, rot: 0.03 });
  const s = o.full ? { s: 1, a: 1 } : pop(t, 29.35);
  card('تصعيد نووي\nمحتمل', 290, 600, { t, alpha: s.a * Math.max(0.55, sideA), scale: s.s, font: 'cairo', size: 50, edge: C.coral, rot: -0.04 });
}
function sceneFork(t) {
  drawBg('bgmap', 4.2, 0.5, 0.0, 'rgba(10,14,28,0.35)');
  fork(t, {});
  const st = pop(t, 29.2, 0.45);
  card('لا تعني تلقائياً\nحرباً نووية', 540, 1290, { t, alpha: st.a, scale: st.s, font: 'cairo', size: 60, fill: C.cream, rot: 0.01 });
}

// S7: the additional danger (symbolic, restrained)
function sceneNuclear(t) {
  drawBg('bgmap', 4.2, 0.3, 0.0, 'rgba(26,26,32,0.66)');
  const a1 = pop(t, 31.3); const swap = t >= 39.3;
  if (!swap) card('إذا حدث تصعيد نووي', 540, 330, { t, alpha: a1.a, scale: a1.s, font: 'cairo', size: 60, edge: C.coral, rot: -0.02 });
  else { const b = pop(t, 39.3); card('إمكانية خطيرة…\nوليست مرحلة محتومة', 540, 330, { t, alpha: b.a, scale: b.s, font: 'cairo', size: 54, edge: C.coral, rot: -0.02 }); }
  const cy = lerp(1650, 1170, easeOut(prog(stepT(t), 33.1, 33.8)));
  if (t >= 33.1) { sticker('city_damaged', 540, cy, 1020, { t, shadowStrength: 1.4 }); card('دمار', 540, 1000, { t, alpha: pop(t, 33.7).a, scale: pop(t, 33.7).s, size: 44 }); }
  const items = [['heat', 250, 34.85, 'حرارة'], ['radiation', 540, 36.25, 'إشعاع'], ['calendar', 820, 37.15, 'آثار طويلة الأمد']];
  for (const [n, x, t0, lab] of items) {
    const p = pop(t, t0, 0.45); if (!p.a) continue;
    const rot = n === 'calendar' ? jit('cal', t, 0.05) : 0;
    sticker(n, x, 690, n === 'calendar' ? 220 : 210, { t, alpha: p.a, scale: p.s, rot });
    card(lab, x, 850, { t, alpha: p.a, scale: p.s, size: 38, rot: (hash(lab) - 0.5) * 0.08 });
  }
}

// S8: decisions and opportunities to prevent escalation
function sceneDecisions(t) {
  drawBg('bgmap', 4.2, 0.6, 0.0, 'rgba(70,58,110,0.42)');
  const blockP = easeOut(prog(stepT(t), 49.7, 50.3));
  fork(t, { full: true, sideAlpha: 1 - 0.55 * blockP, extra: [[[540, 960], [690, 900], [880, 870]], [[540, 1080], [420, 1050], [190, 1020]]] });
  const n1 = pop(t, 43.0); card('لا مسار واحداً مؤكداً', 540, 1300, { t, alpha: n1.a * (1 - prog(t, 49.3, 49.7)), scale: n1.s, font: 'cairo', size: 50, rot: 0.02 });
  const cal = pop(t, 45.75);
  if (cal.a) {
    const ca = cal.a * (1 - prog(t, 49.3, 49.7));
    sticker('calendar', 830, 1080, 170, { t, alpha: ca, scale: cal.s });
    ctx.save(); ctx.globalAlpha = ca; ctx.font = '900 110px Cairo'; ctx.fillStyle = C.coral; ctx.textAlign = 'center'; ctx.direction = 'rtl'; ctx.fillText('؟', 830, 1120); ctx.restore();
  }
  if (t >= 49.7) {          // a decision card slides onto the escalation branch
    card('قرارات', lerp(-200, 420, blockP), 800, { t, alpha: clamp(blockP * 2), size: 54, fill: C.teal, ink: '#FFF8E6', rot: -0.1 });
  }
  const d = pop(t, 50.6); if (d.a) sticker('dove', 230, 1150, 240, { t, alpha: d.a, scale: d.s });
  const hs = pop(t, 51.35);
  if (hs.a) { sticker('handshake', 820, 1150, 230, { t, alpha: hs.a, scale: hs.s }); card('منع التصعيد', 540, 1320, { t, alpha: hs.a, scale: hs.s, size: 46, fill: C.cream }); }
}

// S9: payoff and loop back to the opening
function scenePayoff(t) {
  drawBg('bgshop', 1.08 + 0.02 * prog(t, 52.2, 61.5), 0.5, 0.5);
  // the wider network, behind tracing paper
  const net = [['ship', 230, 430, 270, 52.55], ['factory', 540, 330, 200, 53.1], ['truck', 860, 430, 250, 53.65]];
  const pts = [];
  net.forEach(([n, x, y, w, t0]) => { const p = pop(t, t0, 0.4); if (p.a) sticker(n, x, y, w, { t, alpha: 0.9 * p.a, scale: p.s }); pts.push([x, y + 60]); });
  route([pts[0], [380, 520], pts[1]], prog(t, 53.0, 53.8), { color: C.teal, width: 7, dash: [16, 12], flow: t * 30, alpha: 0.9 });
  route([pts[1], [700, 520], pts[2]], prog(t, 53.6, 54.4), { color: C.teal, width: 7, dash: [16, 12], flow: t * 30, alpha: 0.9 });
  const veil = 0.32 * prog(t, 54.4, 55.4);
  ctx.save(); ctx.globalAlpha = veil; paperPath(40, 250, 1000, 520, 0.77, 10); ctx.fillStyle = '#FBF6EA'; ctx.fill(); ctx.restore();
  const ch = sticker('char_bread_front', 470, 1390, 720, { t, anchor: 'bottom' });
  globeOnThread(t, [470 + 0.14 * 720, ch.top + 0.66 * ch.h], 54.6);
  const f = pop(t, 56.9, 0.5);
  card('قد تصل آثارها إلى حياتك', 540, 165, { t, alpha: f.a, scale: f.s, font: 'cairo', size: 58, fill: C.mustard, rot: -0.02 });
}

// ---------- scene graph + paper-sheet transitions ----------
const SCENES = [
  { from: 0, to: 2.55, draw: sceneHook },
  { from: 2.05, to: 22.8, draw: sceneMap },
  { from: 22.3, to: 26.5, draw: sceneShelf },
  { from: 26.0, to: 31.6, draw: sceneFork },
  { from: 31.15, to: 43.25, draw: sceneNuclear },
  { from: 42.75, to: 52.7, draw: sceneDecisions },
  { from: 52.2, to: DURATION + 1, draw: scenePayoff },
];
const TRANS = [[2.05, 0.5], [22.3, 0.5], [26.0, 0.5], [31.15, 0.45], [42.75, 0.5], [52.2, 0.5]];

function tornEdge(y, seed) {
  const r = mulberry32(seed); const pts = []; for (let x = -20; x <= W + 20; x += 36) pts.push([x, y + (r() - 0.5) * 34]); return pts;
}
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); shadowOff(); ctx.globalAlpha = 1;
  const tr = TRANS.find(([a, d]) => t >= a && t < a + d);
  const active = SCENES.filter(s => t >= s.from && t < s.to);
  if (tr && active.length >= 2) {
    const [A, B] = [active[0], active[active.length - 1]];
    A.draw(t);
    const p = easeInOut(prog(t, tr[0], tr[0] + tr[1]));
    const edge = tornEdge(H * (1 - p) - 40 * (1 - p), Math.floor(tr[0] * 100));
    ctx.save(); ctx.beginPath(); ctx.moveTo(edge[0][0], edge[0][1]); edge.forEach(([x, y]) => ctx.lineTo(x, y)); ctx.lineTo(W + 20, H + 20); ctx.lineTo(-20, H + 20); ctx.closePath();
    ctx.shadowColor = 'rgba(20,12,4,0.5)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = -14; ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
    ctx.clip(); ctx.translate(0, 10 * (1 - p)); B.draw(t); ctx.restore();
    ctx.save(); ctx.strokeStyle = '#FFFDF7'; ctx.lineWidth = 10; ctx.beginPath(); edge.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke(); ctx.restore();
  } else {
    (active[active.length - 1] || SCENES[SCENES.length - 1]).draw(t);
  }
  // global paper texture + vignette
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.22; ctx.drawImage(GRAIN, 0, 0, W, H); ctx.restore();
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(10,8,6,0.38)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  hypoChip(t);
  captions(t);
}

// vertical cover: «بلا قصف؟» + small «سيناريو افتراضي» label, built from the opening frame
function renderCover() {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); shadowOff();
  sceneHook(1.9);
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.22; ctx.drawImage(GRAIN, 0, 0, W, H); ctx.restore();
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(10,8,6,0.45)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  card('بلا قصف؟', 540, 1560, { font: 'cairo', size: 150, fill: C.mustard, ink: C.ink, rot: -0.03 });
  card('سيناريو افتراضي', 540, 1740, { font: 'cairo', size: 46, fill: C.paper, ink: C.ink, edge: C.coral, rot: 0.02 });
}
window.READY = (async () => {
  await loadAll();
  await Promise.all([document.fonts.load('800 60px Cairo', 'عربي'), document.fonts.load('700 50px Ruqaa', 'عربي')]);
  makeGrain();
  window.renderFrame = renderFrame; window.renderCover = renderCover; window.DURATION = DURATION; window.FPS = FPS;
  const q = new URLSearchParams(location.search); renderFrame(parseFloat(q.get('t') || '0'));
  return true;
})();
