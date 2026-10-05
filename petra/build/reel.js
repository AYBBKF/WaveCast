// Petra Reel: كيف نحت الأنباط واجهات البتراء؟  Deterministic, seekable: renderFrame(t) draws the frame at t seconds.
// All timing comes from the measured narration (timeline.js); SFX cue times are exported as window.CUES.
'use strict';
const W = 1080, H = 1920, FPS = 30, TOTAL = TL.total;
const { PAL, setBoil, rng, poly, rect, piece, tracing, backdrop, cliff, facade, urnTomb, artisan, tool, forearm, jordanMap, city } = PAPER;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eio = p => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eo = p => 1 - Math.pow(1 - p, 3);
const back = p => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const popIn = (t, t0, d = 0.35) => t < t0 ? 0 : back(prog(t, t0, t0 + d));
const Ls = i => TL.lines[i - 1].start, Le = i => TL.lines[i - 1].end, G = (i, k) => TL.lines[i - 1].groups[k].start;

// ---------- layout ----------
const FX = 170, FY = 300, FW = 740, FH = 1110;           // the facade (same geometry as the approved storyboard)
const RECESS = [FX - 0.06 * FW, FY - 0.04 * FH, 1.12 * FW, 1.04 * FH];
const DOOR = [FX + 0.5 * FW, FY + 0.775 * FH];
const ART = { x: 205, y: 1395, h: 520 };                  // foreground artisan in the hook / loop frame

// ---------- scene boundaries (from the narration) ----------
const S = {
  s2: Ls(2), s3: Ls(3) - 0.1, s4: Ls(4) - 0.1, s5: Ls(5), s6: Ls(6), s7: Ls(7), s8: Ls(8) - 0.1, s9: Ls(9) - 0.1, s10: Ls(10),
};
const WIPES = [S.s3, S.s4, S.s8, S.s9];

// ---------- cached paper layers (3 stop-motion boil variants each) ----------
const CACHE = new Map();
function cached(key, w, h, draw) {
  if (!CACHE.has(key)) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g); CACHE.set(key, c); }
  return CACHE.get(key);
}
let B = 0;                                               // current boil variant
const withBoil = (b, fn) => { setBoil(b); const r = fn(); setBoil(B); return r; };
const STAGE = () => cached('stage' + B, W, H, g => withBoil(B, () => {
  backdrop(g, 0, 0, W, H, PAL.parch, 3);
  cliff(g, -60, 70, W + 120, H, 11, { strata: 10 });
}));
const FACADE = () => cached('fac' + B, W, H, g => withBoil(B, () => facade(g, FX, FY, FW, FH, 1, { seed: 21 })));
const URN = () => cached('urn' + B, 800, 880, g => withBoil(B, () => urnTomb(g, 20, 20, 760, 840, 61)));
const CITY = () => cached('city' + B, W, 1300, g => withBoil(B, () => { backdrop(g, 0, 0, W, 1300, PAL.parch, 8); city(g, 0, 120, W, 1180, 141); }));
const GRAIN = () => cached('grain', W, H, g => { const r = rng(5); for (let k = 0; k < 9000; k++) { g.fillStyle = r() < 0.5 ? 'rgba(255,250,240,0.05)' : 'rgba(60,40,25,0.05)'; g.fillRect(r() * W, r() * H, 1 + r() * 2, 1 + r() * 2); } });

// ---------- peel bands: horizontal paper layers of rock over the facade, peeled top-down ----------
const BANDS = (() => {
  const [x, y, w, h] = RECESS, n = 4, r = rng(77), cuts = [y - 10];
  for (let k = 1; k < n; k++) cuts.push(y + h * k / n);
  cuts.push(y + h + 10);
  const edge = (yy, s) => { const p = []; for (let i = 0; i <= 10; i++) p.push([x - 20 + (w + 40) * i / 10, yy + (k => (r() - 0.5) * 40)(s)]); return p; };
  const lines = cuts.map((c, i) => edge(c, i));
  return lines.slice(0, n).map((top, k) => [...top, ...lines[k + 1].slice().reverse()]);
})();
// p: 0 = in place (rock), 1 = gone. Each band hinges on its top edge, swings out and drops.
function drawBands(peel, hingeDir = 1) {
  BANDS.forEach((pts, k) => {
    const p = peel[k]; if (p >= 1) return;
    if (p <= 0) {                                         // resting band = seamless part of the cliff (no visible seam)
      ctx.save(); poly(ctx, pts); ctx.clip(); ctx.drawImage(STAGE(), 0, 0); ctx.restore(); return;
    }
    const ys = pts.map(q => q[1]), y0 = Math.min(...ys), x0 = RECESS[0] + (hingeDir > 0 ? 0 : RECESS[2]);
    ctx.save();
    if (p > 0) {
      const e = eio(p);
      ctx.translate(x0, y0); ctx.rotate(-hingeDir * e * 0.55); ctx.translate(-x0 + e * 60 * hingeDir, -y0 + e * e * 900);
      ctx.globalAlpha = 1 - clamp((p - 0.6) / 0.4);
    }
    ctx.shadowColor = 'rgba(40,25,15,0.4)'; ctx.shadowBlur = 18 + 20 * p; ctx.shadowOffsetY = 8 + 20 * p;
    poly(ctx, pts); ctx.fillStyle = PAL.white; ctx.fill();                     // white cut edge + shadow
    ctx.shadowColor = 'transparent';
    ctx.save(); poly(ctx, pts.map(([a, b]) => [a + (k % 2 ? 3 : -3), b + 4])); ctx.clip(); ctx.drawImage(STAGE(), 0, 0); ctx.restore();
    ctx.restore();
  });
}

// ---------- carving: finished facade above the carve line, raw cliff below ----------
function stageCarved(s, t) {
  ctx.drawImage(STAGE(), 0, 0);
  if (s <= 0) return;
  const top = RECESS[1] - 20, cy = RECESS[1] + s * (RECESS[3] + 40), r = rng(31), edge = [];
  for (let i = 0; i <= 14; i++) edge.push([RECESS[0] - 30 + (RECESS[2] + 60) * i / 14, cy + (r() - 0.5) * 34]);
  ctx.save(); poly(ctx, [[RECESS[0] - 30, top], [RECESS[0] + RECESS[2] + 30, top], ...edge.slice().reverse()]); ctx.clip();
  ctx.drawImage(FACADE(), 0, 0); ctx.restore();
  if (s < 1) {                                            // the working face: torn paper edge + tool marks
    ctx.save(); ctx.beginPath(); edge.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
    ctx.shadowColor = 'rgba(40,25,15,0.45)'; ctx.shadowBlur = 12; ctx.shadowOffsetY = -6;
    ctx.lineWidth = 9; ctx.strokeStyle = PAL.white; ctx.lineJoin = 'round'; ctx.stroke(); ctx.restore();
    ctx.save(); ctx.strokeStyle = 'rgba(110,50,35,0.45)'; ctx.lineWidth = 3; const m = rng(9);
    for (let k = 0; k < 34; k++) { const x = RECESS[0] + m() * RECESS[2], y = cy + 14 + m() * 70; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 10, y + 15); ctx.stroke(); }
    ctx.restore();
  }
}
function stagePeeled(peel) {
  ctx.drawImage(STAGE(), 0, 0);
  ctx.save(); ctx.beginPath(); ctx.rect(...RECESS); ctx.clip(); ctx.drawImage(FACADE(), 0, 0); ctx.restore();
  drawBands(peel);
}
const bandSchedule = (t, t0, t1, reverse = false) => {      // 4 overlapping peels between t0 and t1
  const d = (t1 - t0) / 2.2;
  return [0, 1, 2, 3].map(k => {
    const a = t0 + k * (t1 - t0 - d) / 3, p = prog(t, a, a + d);
    return reverse ? 1 - prog(t, t1 - (a - t0) - d, t1 - (a - t0)) : p;
  });
};

// ---------- particles: stone chips with gravity ----------
const IMPACTS = [];                                       // {t, x, y, n, layer}
function chipsAt(t, layer) {
  for (const im of IMPACTS) {
    if (im.layer !== layer) continue;
    const dt = t - im.t; if (dt < 0 || dt > 1.3) continue;
    const r = rng(Math.round(im.t * 1000));
    for (let k = 0; k < im.n; k++) {
      const vx = (r() - 0.6) * 520 * im.s, vy = -(150 + r() * 380) * im.s, sz = (7 + r() * 13) * im.s;
      const x = im.x + vx * dt, y = im.y + vy * dt + 0.5 * 2600 * im.s * dt * dt;
      ctx.save(); ctx.translate(x, y); ctx.rotate(dt * (r() - 0.5) * 14); ctx.globalAlpha = 1 - prog(dt, 0.9, 1.3);
      piece(ctx, [[-sz, -sz * 0.6], [sz * 0.7, -sz], [sz, sz * 0.5], [-sz * 0.4, sz]], r() < 0.5 ? PAL.rose : PAL.roseLt,
        { seed: k + 3, border: 2, amp: 0.6, step: 6, blur: 4, sy: 3, tex: false });
      ctx.restore();
    }
    if (dt < 0.35) {                                      // dust puff
      ctx.save(); ctx.globalAlpha = 0.35 * (1 - dt / 0.35); ctx.fillStyle = PAL.parchDk;
      ctx.beginPath(); ctx.arc(im.x, im.y, 18 + 140 * dt * im.s, 0, 7); ctx.fill(); ctx.restore();
    }
  }
}

// ---------- SFX cue list (exported for build_audio.py) ----------
const CUES = [];
const cue = (type, t, gain = 1) => CUES.push({ type, t: +t.toFixed(3), gain });

// hook strikes (foreground artisan): impact every 0.9 s across line 1
const HOOK_HITS = []; for (let t = 0.32; t < Ls(2) - 0.3; t += 0.9) HOOK_HITS.push(t);
HOOK_HITS.forEach(t => { IMPACTS.push({ t, x: 368, y: 1030, n: 7, s: 1, layer: 'stage' }); cue('chisel', t); cue('stones', t + 0.12, 0.7); });
// line 2 peel: one paper cue per band
const PEEL2 = [S.s2 + 0.15, S.s2 + 4.4];
[0, 1, 2, 3].forEach(k => { const d = (PEEL2[1] - PEEL2[0]) / 2.2; cue('paper', PEEL2[0] + k * (PEEL2[1] - PEEL2[0] - d) / 3 + 0.1, 0.9); cue('stones', PEEL2[0] + k * (PEEL2[1] - PEEL2[0] - d) / 3 + 0.5, 0.5); });
cue('pop', G(2, 2) + 0.05, 0.7);                          // map
// line 3 close-up strikes (chips burst at the chisel TIP, the hammer lands on the chisel END)
const CHISEL_END = [500, 1075], CHISEL_TIP = [CHISEL_END[0] + Math.cos(Math.PI + 0.42) * 22 * 7.2, CHISEL_END[1] + Math.sin(Math.PI + 0.42) * 22 * 7.2];
const WRIST = [800, 760], HAMMER_L = Math.hypot(CHISEL_END[0] - 800, CHISEL_END[1] + 30 - 760);
const HAMMER_A0 = Math.atan2(CHISEL_END[1] + 30 - 760, CHISEL_END[0] - 800);   // angle at impact
const TOOL_HITS = []; for (let t = S.s3 + 0.55; t < G(3, 2) - 0.1; t += 0.62) TOOL_HITS.push(t);
TOOL_HITS.forEach(t => { IMPACTS.push({ t, x: CHISEL_TIP[0], y: CHISEL_TIP[1], n: 9, s: 1.5, layer: 'close' }); cue('chisel', t, 1.1); cue('stones', t + 0.1, 0.8); });
[G(3, 2), G(3, 2) + 0.9, G(3, 3)].forEach(t => cue('pop', t, 0.6));
// line 4 arrow; line 6 rapid strikes while the carve line descends
cue('pop', G(4, 2) + 0.1, 0.5);
const CARVE6 = [S.s6 + 0.1, G(6, 1) + 1.0];
const RAPID = []; for (let t = CARVE6[0]; t < CARVE6[1]; t += 0.34) RAPID.push(t);
RAPID.forEach((t, i) => { const s = lerp(0.45, 1, prog(t, ...CARVE6)); IMPACTS.push({ t, x: RECESS[0] + 80 + (i * 211) % (RECESS[2] - 160), y: RECESS[1] + s * (RECESS[3] + 40), n: 5, s: 0.9, layer: 'stage' }); cue('chisel', t, 0.75); });
cue('swell', G(6, 1) + 0.5, 1);
cue('dip', S.s7 + 0.2, 1); cue('whoosh', S.s7 + 0.1, 0.8); cue('thud', G(7, 2) + 0.15, 1);
cue('return', S.s8, 1);
[0.6, 1.3, 2.0].forEach(d => cue('pop', G(8, 1) + d, 0.5)); cue('pop', G(8, 0) + 0.8, 0.5);
WIPES.forEach(t => cue('paper', t - 0.12, 0.8));
const FALLBACK9 = [G(9, 1) + 0.1, G(9, 1) + 1.9];
[0, 1, 2, 3].forEach(k => cue('paper', FALLBACK9[0] + k * 0.42, 0.7));
const PEEL10 = [S.s10 + 0.1, S.s10 + 2.0];
[0, 1, 2, 3].forEach(k => cue('paper', PEEL10[0] + k * 0.45, 0.7));
[G(10, 1), G(10, 2)].forEach(t => cue('pop', t + 0.05, 0.6));
const LOOP = TOTAL - 0.62;
cue('paper', LOOP, 0.6);

// ---------- text helpers (Arabic, RTL, Cairo) ----------
function plate(text, x, y, size = 30, fill = PAL.parch, col = PAL.navy, seed = 0) {
  ctx.save(); ctx.font = `700 ${size}px Cairo`; ctx.direction = 'rtl';
  const w = ctx.measureText(text).width + size * 1.2;
  piece(ctx, rect(x - w / 2, y - size * 0.85, w, size * 1.6), fill, { seed: seed || text.length * 13 + size, border: 3, amp: 1.5 });
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = col; ctx.fillText(text, x, y + 2); ctx.restore();
}
function reconstructionTag(t, on) {                       // "simplified illustration" on every carving / cutaway sequence
  if (on > 0) { ctx.save(); ctx.globalAlpha = on; plate('تصوّر مبسّط', 920, 270, 26, PAL.mustard, PAL.navy, 5); ctx.restore(); }
}

// Caption: words laid out right-to-left so single words can be highlighted; max 2 lines.
function captions(t) {
  let grp = null;
  for (const l of TL.lines) for (const g of l.groups) if (t >= g.start - 0.05 && t < g.end + 0.12) grp = g;
  if (!grp) return;
  const size = 62, maxW = 860, lh = size * 1.32;
  ctx.save(); ctx.font = `700 ${size}px Cairo`; ctx.direction = 'rtl';
  const words = grp.text.split(' ').map(w => ({ w: w.replace(/\*/g, ''), hl: /\*/.test(w) }));
  // handle "و*أسواق*" style: prefix outside the stars stays plain colour but same word
  const space = ctx.measureText(' ').width, rows = [[]]; let rw = 0;
  for (const wd of words) { wd.width = ctx.measureText(wd.w).width; if (rw + wd.width > maxW && rows[rows.length - 1].length) { rows.push([]); rw = 0; } rows[rows.length - 1].push(wd); rw += wd.width + space; }
  const rowW = rows.map(r => r.reduce((a, w) => a + w.width, 0) + space * (r.length - 1));
  const p = eo(prog(t, grp.start - 0.05, grp.start + 0.1)), bw = Math.max(...rowW) + 70, bh = rows.length * lh + 34, cy = 1530;
  ctx.globalAlpha = p; ctx.translate(540, cy + (1 - p) * 14);
  piece(ctx, rect(-bw / 2, -bh / 2, bw, bh), PAL.parch, { seed: Math.round(grp.start * 10), border: 5, amp: 2.5, blur: 14, sy: 6 });
  ctx.textBaseline = 'middle'; ctx.textAlign = 'right';
  rows.forEach((r, ri) => {
    let x = rowW[ri] / 2; const y = -bh / 2 + 17 + lh * (ri + 0.5) + 4;
    for (const wd of r) {
      ctx.fillStyle = wd.hl ? PAL.terra : PAL.navy; ctx.fillText(wd.w, x, y);
      if (wd.hl) { ctx.save(); ctx.strokeStyle = 'rgba(217,164,65,0.85)'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x - wd.width, y + size * 0.52); ctx.lineTo(x, y + size * 0.48); ctx.stroke(); ctx.restore(); }
      x -= wd.width + space;
    }
  });
  ctx.restore();
}

// ---------- camera ----------
function camera(z, fx, fy, draw) { ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-fx, -fy); draw(); ctx.restore(); }

// ---------- artisan helpers ----------
function hitPose(t, hits, lead = 0.28, hold = 0.22) {      // 'strike' (raised) between hits, 'chisel' at impact
  for (const h of hits) if (t >= h - 0.02 && t < h + hold) return 'chisel';
  return 'strike';
}
function foregroundArtisan(t, hits) { artisan(ctx, ART.x, ART.y, ART.h, hitPose(t, hits), 81); }

// ---------- scenes ----------
function sceneHook(t) {                                   // line 1: the cliff, the first strikes, the question
  const z = lerp(1.0, 1.04, prog(t, 0, S.s2));
  camera(z, 540, 960, () => {
    ctx.drawImage(STAGE(), 0, 0);
    const ga = prog(t, G(1, 0) + 1.0, G(1, 0) + 2.0) * 0.55;  // ghost of the facade to come (tracing paper)
    if (ga > 0) { ctx.save(); ctx.globalAlpha = ga; ctx.beginPath(); ctx.rect(...RECESS); ctx.clip(); ctx.drawImage(FACADE(), 0, 0); ctx.restore();
      ctx.save(); ctx.globalAlpha = ga * 0.9; tracing(ctx, rect(...RECESS), 4, 0.55); ctx.restore(); }
    const lift = prog(t, G(1, 1) + 0.4, S.s2) * 0.12;        // "...by removing parts": the first layer starts to lift
    drawBands([lift, 0, 0, 0]);
    chipsAt(t, 'stage');
    foregroundArtisan(t, HOOK_HITS);
  });
  const q = popIn(t, 0.9, 0.4) * (1 - prog(t, G(1, 1), G(1, 1) + 0.3));
  if (q > 0) { ctx.save(); ctx.translate(800, 560); ctx.scale(q, q); ctx.font = '700 230px Cairo'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 16; ctx.strokeStyle = PAL.white; ctx.strokeText('؟', 0, 0); ctx.fillStyle = PAL.navy; ctx.fillText('؟', 0, 0); ctx.restore(); }
}

function sceneReveal(t) {                                 // line 2: paper layers peel away -> the facade
  const z = lerp(1.1, 1.0, eio(prog(t, S.s2, Le(2))));
  camera(z, 540, 960, () => {
    stagePeeled(bandSchedule(t, ...PEEL2));
    chipsAt(t, 'stage');
    artisan(ctx, 250, 1415, 120, 'look', 81);
  });
  reconstructionTag(t, prog(t, S.s2 + 0.3, S.s2 + 0.6));
  const m = popIn(t, G(2, 2), 0.4);                       // Jordan inset at "في الأردن"
  if (m > 0) {
    ctx.save(); ctx.translate(70, 230); ctx.scale(m, m);
    const mp = jordanMap(ctx, 0, 0, 300, 121);
    ctx.restore();
    ctx.save(); ctx.globalAlpha = m;
    const px = 70 + mp.petra[0] * m, py = 230 + mp.petra[1] * m, pulse = 1 + 0.25 * Math.sin(t * 7);
    ctx.strokeStyle = PAL.terra; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(px, py, 22 * pulse, 0, 7); ctx.stroke();
    plate('الأردن', 70 + mp.jordan[0] * m, 230 + mp.jordan[1] * m - 6, 26, PAL.parch, PAL.navy, 7);
    plate('البتراء', px - 80, py + 6, 24, PAL.terra, PAL.white, 8);
    ctx.restore();
  }
}

const MARKS = (() => { const r = rng(17), a = []; for (let k = 0; k < 60; k++) a.push([140 + r() * 640, 760 + r() * 520, r()]); return a; })();
const DETAILS = [                                          // crops of the SAME facade: ornament, column, doorway
  { u: [0.33, 0.0, 0.34, 0.38], label: 'زخارف', x: 780, y: 520, rot: 0.06 },
  { u: [0.13, 0.47, 0.14, 0.48], label: 'أعمدة', x: 560, y: 600, rot: -0.04 },
  { u: [0.38, 0.58, 0.24, 0.40], label: 'مداخل', x: 300, y: 560, rot: -0.07 },
];
function sceneTools(t) {                                  // line 3: adult hands, hammer and chisel, chips, tool marks
  ctx.save(); ctx.translate(-1300, -1250); ctx.scale(2.6, 2.6); ctx.drawImage(STAGE(), 0, 0); ctx.restore();
  const done = TOOL_HITS.filter(h => h <= t).length;       // tool marks accumulate with every strike
  ctx.save(); ctx.strokeStyle = 'rgba(110,50,35,0.5)'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  MARKS.slice(0, done * 6).forEach(([x, y]) => { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 22, y + 32); ctx.stroke(); }); ctx.restore();
  // chisel hand (still): tip on the rock at CHISEL_TIP, struck end at CHISEL_END
  tool(ctx, 'chisel', CHISEL_END[0], CHISEL_END[1], Math.PI + 0.42, 7.2, 42);
  forearm(ctx, W + 60, 1460, CHISEL_END[0] + 30, CHISEL_END[1] + 40, 120, 41, 1);
  // hammer hand: the hammer swings about the wrist; at impact its head lands on the chisel's end
  let swing = 1;                                          // 1 = raised, 0 = on the chisel head
  for (const h of TOOL_HITS) { const d = t - h; if (d > -0.22 && d < 0) swing = Math.min(swing, -d / 0.22); if (d >= 0 && d < 0.3) swing = Math.min(swing, d / 0.3); }
  const a = lerp(HAMMER_A0, HAMMER_A0 + 1.15, eio(swing));
  forearm(ctx, W + 80, 520, WRIST[0], WRIST[1], 116, 43, 0);
  ctx.save(); ctx.translate(...WRIST); ctx.rotate(a);
  piece(ctx, rect(0, -13, HAMMER_L, 26), PAL.kraftDk, { seed: 45, border: 3, amp: 1 });          // wooden handle
  piece(ctx, rect(HAMMER_L - 34, -58, 68, 116), '#6E6A66', { seed: 46, border: 3, amp: 1.5, texOpts: { bloom: '30,30,40' } }); // iron head
  ctx.restore();
  piece(ctx, PAPER.ellipsePts(WRIST[0], WRIST[1], 62, 54, 20), PAL.skin, { seed: 47, border: 3 });  // fist around the handle
  chipsAt(t, 'close');
  // the three kinds of detail that emerge from the rock
  DETAILS.forEach((d, i) => {
    const t0 = [G(3, 2), G(3, 2) + 0.9, G(3, 3)][i], s = popIn(t, t0, 0.4);
    if (s <= 0) return;
    const [u, v, du, dv] = d.u, sw = du * FW, sh = dv * FH, k = 330 / Math.max(sw, sh);
    ctx.save(); ctx.translate(d.x, d.y); ctx.rotate(d.rot); ctx.scale(s, s);
    piece(ctx, rect(-sw * k / 2 - 14, -sh * k / 2 - 14, sw * k + 28, sh * k + 28), PAL.white, { seed: i + 50, border: 0, amp: 2 });
    ctx.drawImage(FACADE(), FX + u * FW - 0.03 * FW, FY + v * FH - 0.02 * FH, sw, sh, -sw * k / 2, -sh * k / 2, sw * k, sh * k);
    ctx.restore();
    if (s > 0.6) plate(d.label, d.x, d.y + sh * k / 2 + 50, 34, PAL.parch, PAL.navy, 30 + i);
  });
}

function sceneTopDown(t) {                                // lines 4-5: unfinished facade, top-down arrow, camera tilt
  let z = 1, fy = 960;
  if (t >= S.s5) {                                        // line 5: start on the detailed top, tilt down to the rough rock
    const a = eio(prog(t, S.s5, S.s5 + 0.8)), b = eio(prog(t, G(5, 2), G(5, 3) + 0.6)), c = eio(prog(t, Le(5) - 0.4, S.s6));
    z = lerp(lerp(1, 1.75, a), 1, c); fy = lerp(lerp(960, 560, a), 1000, b); fy = lerp(fy, 960, c);
  }
  camera(z, 540, fy, () => {
    stageCarved(0.45, t);
    artisan(ctx, 690, 1415, 130, hitPose(t, [], 0.3), 81, -1);
    if (t >= G(5, 3) - 0.1 && t < S.s6) {                  // crayon ring around "rough rock"
      const p = prog(t, G(5, 3) - 0.1, G(5, 3) + 0.6);
      ctx.save(); ctx.strokeStyle = 'rgba(217,164,65,0.9)'; ctx.lineWidth = 10; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.ellipse(540, 1130, 380, 190, -0.04, -Math.PI / 2, -Math.PI / 2 + p * Math.PI * 2.1); ctx.stroke(); ctx.restore();
    }
  });
  reconstructionTag(t, 1);
  if (t < S.s5) {                                         // the code-drawn top-down arrow
    const p = eio(prog(t, G(4, 2) - 0.2, G(4, 3) + 1.0)), y0 = 320, y1 = lerp(y0 + 40, 1360, p);
    ctx.save(); ctx.strokeStyle = PAL.navy; ctx.fillStyle = PAL.navy; ctx.lineWidth = 14; ctx.lineCap = 'round';
    ctx.shadowColor = PAL.white; ctx.shadowBlur = 0; ctx.setLineDash([2, 26]);
    ctx.beginPath(); ctx.moveTo(1000, y0); ctx.lineTo(1000, y1 - 40); ctx.stroke(); ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(968, y1 - 46); ctx.lineTo(1000, y1); ctx.lineTo(1032, y1 - 46); ctx.closePath(); ctx.lineWidth = 6; ctx.strokeStyle = PAL.white; ctx.stroke(); ctx.fill();
    ctx.restore();
    if (t > G(4, 2) + 0.2) plate('الأعلى', 905, 330, 30, PAL.parch, PAL.navy, 11);
    if (t > G(4, 3) + 0.3) plate('الأسفل', 905, 1340, 30, PAL.parch, PAL.navy, 12);
  }
}

function sceneCarve(t) {                                  // line 6: strike after strike, the mountain becomes a facade
  const s = lerp(0.45, 1, eio(prog(t, ...CARVE6)));
  const pull = eio(prog(t, S.s6, G(6, 1) + 0.4));
  camera(lerp(1.5, 1.0, pull), lerp(380, 540, pull), lerp(1080, 960, pull), () => {
    stageCarved(s, t);
    chipsAt(t, 'stage');
    artisan(ctx, 120, 1415, 80, hitPose(t, RAPID), 81);   // small beside the facade: scale
  });
  reconstructionTag(t, 1 - prog(t, CARVE6[1], CARVE6[1] + 0.4));
  const L0 = G(6, 1) + 0.5, lp = prog(t, L0, L0 + 1.8);    // warm light sweeps the finished facade
  if (lp > 0 && lp < 1) {
    ctx.save(); ctx.globalCompositeOperation = 'soft-light';
    const x = lerp(-600, 1500, eio(lp)), g = ctx.createLinearGradient(x - 380, 0, x + 380, 400);
    g.addColorStop(0, 'rgba(255,214,140,0)'); g.addColorStop(0.5, 'rgba(255,214,140,0.95)'); g.addColorStop(1, 'rgba(255,214,140,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  }
}

function sceneTomb(t) {                                   // line 7: through the doorway -> Urn Tomb -> schematic cutaway
  const push = eio(prog(t, S.s7, S.s7 + 1.3));
  if (push < 1) {
    camera(lerp(1, 5.5, push), lerp(540, DOOR[0], push), lerp(960, DOOR[1], push), () => stageCarved(1, t));
    ctx.fillStyle = `rgba(31,42,68,${clamp(push * 1.3 - 0.2)})`; ctx.fillRect(0, 0, W, H);
    return;
  }
  backdrop(ctx, 0, 0, W, H, PAL.navy, 7);
  const e = eo(prog(t, S.s7 + 1.3, S.s7 + 1.9)), shrink = eio(prog(t, G(7, 1) + 0.3, G(7, 1) + 1.0));
  const sc = lerp(1.0, 0.72, shrink), ty = lerp(lerp(500, 140, e), 90, shrink);
  ctx.save(); ctx.translate(540 - 400 * sc, ty); ctx.scale(sc, sc); ctx.drawImage(URN(), 0, 0); ctx.restore();
  if (t > G(7, 1) - 0.2) plate('قبر الجرّة · البتراء', 540, ty + 880 * sc + 30, 30, PAL.parch, PAL.navy, 21);
  const c = eo(prog(t, G(7, 1) + 0.7, G(7, 1) + 1.3));
  if (c > 0) {                                            // restrained schematic cutaway (no bodies)
    ctx.save(); ctx.translate(0, lerp(500, 0, c)); ctx.globalAlpha = c;
    const X = 110, Y = 880, Wd = 860;
    piece(ctx, rect(X, Y, Wd, 300), PAL.rose, { seed: 71, border: 4 });
    piece(ctx, rect(X + 40, Y + 30, 60, 240), PAL.roseLt, { seed: 72, border: 2 });          // facade slab
    piece(ctx, rect(X + 100, Y + 150, 110, 90), PAL.navy, { seed: 73, border: 2 });          // doorway passage
    piece(ctx, rect(X + 210, Y + 40, 520, 200), PAL.parchDk, { seed: 74, border: 3 });       // the large hall cut into the rock
    [X + 260, X + 400, X + 540].forEach((x, i) => piece(ctx, rect(x, Y + 60, 90, 44), PAL.roseDk, { seed: 75 + i, border: 1.5 }));
    plate('واجهة', X + 70, Y + 286, 22, PAL.parch, PAL.navy, 41); plate('قاعة منحوتة', X + 470, Y + 286, 22, PAL.parch, PAL.navy, 42);
    ctx.restore();
    reconstructionTag(t, c);
  }
  const m = popIn(t, G(7, 2) + 0.1, 0.45);                // the word, stamped
  if (m > 0) { ctx.save(); ctx.translate(540, 1300); ctx.scale(m, m); ctx.rotate(-0.04); ctx.font = '900 150px Cairo'; ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 18; ctx.strokeStyle = PAL.white; ctx.strokeText('مقابر', 0, 0); ctx.fillStyle = PAL.mustard; ctx.fillText('مقابر', 0, 0); ctx.restore(); }
}

const CITY_LABELS = [                                      // anchors in the city drawing's unit space (x, y)
  { text: 'واجهات منحوتة', u: [0.75, 0.30], t: () => G(8, 0) + 0.8, fill: PAL.roseLt },
  { text: 'بيوت', u: [0.44, 0.58], t: () => G(8, 1) + 0.6, fill: PAL.parch },
  { text: 'أسواق', u: [0.30, 0.82], t: () => G(8, 1) + 1.3, fill: PAL.parch },
  { text: 'معابد', u: [0.21, 0.36], t: () => G(8, 1) + 2.0, fill: PAL.parch },
];
function sceneCity(t) {                                   // line 8: a city of houses, markets and temples too
  const z = lerp(1.18, 1.0, eio(prog(t, S.s8, S.s8 + 2.2)));
  camera(z, 540, 960, () => {
    backdrop(ctx, -100, -100, W + 200, H + 200, PAL.parch, 9);
    ctx.drawImage(CITY(), 0, 360);
    CITY_LABELS.forEach((lb, i) => {
      const s = popIn(t, lb.t(), 0.35); if (s <= 0) return;
      const x = lb.u[0] * W, y = 360 + 120 + lb.u[1] * 1180, ly = y - 150 - (i % 2) * 40;
      ctx.save(); ctx.globalAlpha = Math.min(1, s); ctx.strokeStyle = PAL.navy; ctx.lineWidth = 4; ctx.setLineDash([3, 9]); ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, ly + 26); ctx.stroke(); ctx.restore();
      ctx.save(); ctx.translate(x, ly); ctx.scale(s, s); plate(lb.text, 0, 0, 32, lb.fill, PAL.navy, 60 + i); ctx.restore();
    });
  });
}

function sceneFinale(t) {                                 // lines 9-10: details, the rock returns, the reveal again, the question
  if (t < S.s10) {
    const zz = eio(prog(t, S.s9, G(9, 1))), back_ = eio(prog(t, G(9, 1), G(9, 1) + 1.6));
    const z = lerp(lerp(1.0, 1.55, zz), 1.0, back_), fy = lerp(lerp(960, 540, zz), 960, back_);
    camera(z, 540, fy, () => {
      const peel = bandSchedule(t, ...FALLBACK9, true).map(p => t < FALLBACK9[0] ? 1 : p);
      stagePeeled(peel);
    });
    reconstructionTag(t, prog(t, FALLBACK9[0], FALLBACK9[0] + 0.3));
    return;
  }
  const loopK = prog(t, LOOP, TOTAL - 0.05);              // final beat: the rock falls back -> opening frame
  camera(1.0, 540, 960, () => {
    let peel = bandSchedule(t, ...PEEL10);
    if (loopK > 0) peel = peel.map((p, k) => Math.min(p, 1 - prog(loopK, k * 0.12, k * 0.12 + 0.5)));
    stagePeeled(peel);
    if (loopK > 0.6) foregroundArtisan(0, HOOK_HITS);     // same pose as frame 0
  });
  reconstructionTag(t, prog(t, S.s10 + 0.2, S.s10 + 0.5) * (1 - loopK));
  const q = popIn(t, G(10, 0) + 0.1, 0.4) * (1 - loopK);  // the final question as two paper choices
  if (q > 0) {
    ctx.save(); ctx.globalAlpha = Math.min(1, q);
    plate('أيّهما أصعب؟', 540, 300, 64, PAL.parch, PAL.navy, 91);
    const a = popIn(t, G(10, 1) + 0.05, 0.35), b = popIn(t, G(10, 2) + 0.05, 0.35);
    if (a > 0) { ctx.save(); ctx.translate(760, 470); ctx.rotate(0.05); ctx.scale(a, a); plate('بناءٌ بالحجارة', 0, 0, 40, PAL.teal, PAL.white, 92); ctx.restore(); }
    if (b > 0) { ctx.save(); ctx.translate(320, 470); ctx.rotate(-0.05); ctx.scale(b, b); plate('نحتٌ من جبل', 0, 0, 40, PAL.terra, PAL.white, 93); ctx.restore(); }
    ctx.restore();
  }
}

// paper wipe between sections (a torn kraft sheet slides across, right to left)
function wipe(t) {
  for (const w0 of WIPES) {
    const p = prog(t, w0 - 0.32, w0 + 0.32); if (p <= 0 || p >= 1) continue;
    const x = lerp(W + 80, -W - 1300, eio(p)), r = rng(Math.round(w0 * 10)), e1 = [], e2 = [];
    for (let i = 0; i <= 16; i++) { e1.push([x + (r() - 0.5) * 70, -40 + i * (H + 80) / 16]); e2.push([x + 1300 + (r() - 0.5) * 70, -40 + i * (H + 80) / 16]); }
    piece(ctx, [...e1, ...e2.reverse()], PAL.kraft, { seed: Math.round(w0), border: 8, amp: 0, blur: 30, sx: -12, sy: 0, texOpts: { blooms: 5, hatch: 0.6 } });
  }
}

// ---------- frame ----------
function renderFrame(t) {
  B = Math.floor(t * 8) % 3; setBoil(B);                  // stop-motion edge boil at 8 fps
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = PAL.parch; ctx.fillRect(0, 0, W, H);   // never show bare canvas
  if (t < S.s2) sceneHook(t);
  else if (t < S.s3) sceneReveal(t);
  else if (t < S.s4) sceneTools(t);
  else if (t < S.s6) sceneTopDown(t);
  else if (t < S.s7) sceneCarve(t);
  else if (t < S.s8) sceneTomb(t);
  else if (t < S.s9) sceneCity(t);
  else sceneFinale(t);
  ctx.drawImage(GRAIN(), 0, 0);
  const v = ctx.createRadialGradient(540, 900, 620, 540, 960, 1250);   // soft vignette
  v.addColorStop(0, 'rgba(31,42,68,0)'); v.addColorStop(1, 'rgba(31,42,68,0.32)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  wipe(t);
  captions(t);
}

// cover: finished facade + title (no narration text)
function renderCover() {
  B = 0; setBoil(0); ctx.setTransform(1, 0, 0, 1, 0, 0);
  camera(1.0, 540, 1010, () => { stageCarved(1, 0); artisan(ctx, 250, 1415, 120, 'look', 81); });
  ctx.drawImage(GRAIN(), 0, 0);
  const v = ctx.createLinearGradient(0, 1150, 0, H); v.addColorStop(0, 'rgba(31,42,68,0)'); v.addColorStop(1, 'rgba(31,42,68,0.85)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  piece(ctx, rect(80, 1380, 920, 330), PAL.parch, { seed: 301, border: 7, amp: 3, blur: 22, sy: 10 });
  ctx.fillStyle = PAL.navy; ctx.font = '900 92px Cairo'; ctx.fillText('كيف نحت الأنباط', 540, 1478);
  ctx.fillStyle = PAL.terra; ctx.fillText('واجهات البتراء؟', 540, 1600);
  ctx.restore();
  plate('DEEP CURIOUS', 540, 1790, 34, PAL.navy, PAL.parch, 302);
}

window.CUES = CUES;
window.READY = (async () => {
  await document.fonts.load('700 60px Cairo'); await document.fonts.load('900 60px Cairo');
  for (let b = 0; b < 3; b++) { B = b; STAGE(); FACADE(); URN(); CITY(); }    // warm the caches
  B = 0;
  window.renderFrame = renderFrame; window.renderCover = renderCover; window.DURATION = TOTAL; window.FPS = FPS;
  const q = new URLSearchParams(location.search); if (q.has('t')) renderFrame(parseFloat(q.get('t')));
  return true;
})();
