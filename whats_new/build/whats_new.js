// "GPT asks Claude what's new": seekable, deterministic edit. renderFrame(t) draws the frame at t seconds.
// Every beat is keyed to the dialogue timeline (timeline.js), so re-recording a line re-times the whole cut.
'use strict';
const W = 1080, H = 1920, FPS = 30, TOTAL = TL.total;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eio = p => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eo = p => 1 - Math.pow(1 - p, 3);
const back = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const popIn = (t, t0, d = 0.35) => t < t0 ? 0 : back(prog(t, t0, t0 + d));
const L = Object.fromEntries(TL.lines.map(l => [l.id, l]));
const cap = (id, k) => L[id].captions[k].start;
const { PAL, SPECS, drawCharacter } = BEAN;
const C = { wall: '#F6EEE3', floor: '#EADCCB', ink: PAL.ink, gpt: '#3E9E78', claude: PAL.terra, yellow: '#FFD43B',
            ui: '#2C2C2E', uiHead: '#3B3B3E', uiGrid: '#4A4A4E', sel: '#F5A623' };

// ---------- key times ----------
const STUDIO = cap(2, 1) + 0.55;                 // "...whole studio" -> celebrity pose
const SIDE_EYE = L[2].end + 0.05;
const ICONS_T = cap(4, 0) + 0.5;
const PANEL_IN = cap(7, 1) + 0.25, PANEL_OUT = L[11].end + 0.35;
const PLUG_T = cap(8, 0) + 0.55, BUILD_T = cap(8, 1);
const ZERO_T = cap(9, 0) + 0.9;
const RENDER_T = L[10].start, TOKENS_T = cap(10, 1) + 0.25;
const GPU_T = L[11].start, STAR_T = cap(11, 1) + 0.35;
const BOSS_T = L[12].start, CLAP_T = cap(13, 0) + 0.1;

// ---------- characters: placement, arm library, poses ----------
const GROUND = 1390, SCALE = 0.76;
const POS = { GPT: 292, CLAUDE: 800 };
const SPEC = { GPT: SPECS.GPT, CLAUDE: SPECS.BEAN };
const GS = SPECS.GPT.SHOULDER, BS = SPECS.BEAN.SHOULDER;
const ARM = {
  GPT: {
    down: [{ pts: [GS.L, [282, 720], [276, 792]] }, { pts: [GS.R, [760, 720], [766, 792]] }],
    wave: { pts: [GS.R, [790, 600], [792, 505]] },
    hipL: { pts: [GS.L, [256, 700], [306, 762]] }, hipR: { pts: [GS.R, [786, 700], [734, 762]] },
    point: { pts: [GS.R, [800, 640], [866, 596]] },
    shrug: [{ pts: [GS.L, [250, 640], [244, 568]] }, { pts: [GS.R, [792, 640], [798, 568]] }],
    cross: [{ front: true, pts: [[318, 690], [420, 738], [600, 702]] }, { front: true, pts: [[724, 690], [620, 744], [440, 710]] }],
    chinR: { front: true, pts: [[724, 690], [668, 712], [568, 668]] },
    clap: [{ front: true, pts: [[318, 700], [404, 762], [508, 724]] }, { front: true, pts: [[724, 700], [638, 762], [534, 724]] }],
  },
  CLAUDE: {
    down: [{ pts: [BS.L, [330, 625], [318, 702]] }, { pts: [BS.R, [736, 625], [748, 702]] }],
    present: { pts: [BS.R, [784, 575], [806, 486]] },
    presentL: { pts: [BS.L, [300, 560], [262, 488]] },
    celeb: [{ pts: [BS.L, [318, 430], [290, 330]] }, { pts: [BS.R, [766, 430], [794, 330]] }],
    hipL: { pts: [BS.L, [312, 600], [356, 668]] },
    finger: { pts: [BS.R, [772, 500], [788, 404]] },
    panel: { pts: [BS.R, [782, 470], [826, 378]] },
    cross: [{ front: true, pts: [[384, 575], [470, 628], [615, 588]] }, { front: true, pts: [[696, 575], [598, 632], [452, 600]] }],
    boss: [{ pts: [BS.L, [306, 410], [392, 262]] }, { pts: [BS.R, [776, 410], [690, 262]] }],
  },
};
const A = ARM.GPT, B = ARM.CLAUDE;
const POSE = {
  GPT: {
    hey:        { eyes: 'open', look: [8, 0], browL: [-6, -8, 4], browR: [-6, -8, 4], rest: 'smile', arms: [A.down[0], A.wave], cheeks: 'soft' },
    listen:     { eyes: 'open', look: [8, 0], browL: [0, 2, 3], browR: [0, 2, 3], rest: 'smile', arms: A.down, cheeks: 'soft' },
    curious:    { eyes: 'open', look: [8, -2], browL: [-4, -6, 3], browR: [-10, -14, 5], rest: 'smile', arms: A.down, cheeks: 'soft' },
    sideeye:    { eyes: 'half', look: [11, 0], browL: [10, 10, 0], browR: [-20, -28, 6], rest: 'line', arms: A.cross, cheeks: 'soft', lean: -0.07 },
    tease:      { eyes: 'half', look: [8, 0], browL: [2, 2, 0], browR: [-12, -18, 5], rest: 'smirk', arms: [A.hipL, A.point], cheeks: 'soft', lean: 0.04 },
    ponder:     { eyes: 'open', look: [8, -6], browL: [4, 4, 0], browR: [-12, -18, 4], rest: 'pursed', arms: [A.down[0], A.chinR], cheeks: 'soft' },
    sus:        { eyes: 'open', look: [9, 0], browL: [8, -2, 0], browR: [-14, -18, 5], rest: 'o', arms: A.shrug, cheeks: 'soft', lean: 0.05 },
    flat:       { eyes: 'flat', look: [9, 0], browL: [12, -2, 0], browR: [12, -2, 0], rest: 'line', arms: A.cross, extras: ['vein'] },
    sass:       { eyes: 'half', look: [8, 0], browL: [0, 0, 0], browR: [-12, -18, 5], rest: 'smirk', arms: [A.hipL, A.hipR], cheeks: 'soft' },
    impressed:  { eyes: 'open', look: [6, -8], browL: [-8, -10, 4], browR: [-8, -10, 4], rest: 'o', arms: A.down, cheeks: 'soft' },
    sly:        { eyes: 'half', look: [8, 0], browL: [4, 4, 0], browR: [-14, -20, 5], rest: 'smirk', arms: [A.down[0], A.chinR], cheeks: 'soft' },
    listen2:    { eyes: 'open', look: [8, 0], browL: [2, 0, 0], browR: [2, 0, 0], rest: 'flat', arms: A.cross, cheeks: 'soft' },
    accuse:     { eyes: 'half', look: [10, 0], browL: [12, -4, 0], browR: [12, -4, 0], rest: 'flat', arms: [A.hipL, A.point], lean: 0.06 },
    unimpressed:{ eyes: 'flat', look: [9, 0], browL: [10, 4, 0], browR: [10, 4, 0], rest: 'line', arms: A.cross },
    stare:      { eyes: 'open', look: [0, 0], browL: [6, 6, 0], browR: [6, 6, 0], rest: 'line', arms: A.clap, clap: true },
  },
  CLAUDE: {
    listen:     { eyes: 'open', look: [-8, 0], browL: [0, 2, 3], browR: [0, 2, 3], rest: 'smile', arms: B.down, cheeks: 'soft' },
    proud:      { eyes: 'half', look: [-6, 0], browL: [-12, -18, 6], browR: [6, 6, 0], rest: 'smirk', arms: [B.down[0], B.present], cheeks: 'soft' },
    celeb:      { eyes: 'happy', look: [0, 0], browL: [-10, -6, 4], browR: [-10, -6, 4], rest: 'grin', arms: B.celeb, cheeks: 'soft' },
    unbothered: { eyes: 'flat', look: [-8, 0], browL: [6, 6, 0], browR: [6, 6, 0], rest: 'line', arms: B.cross },
    lecture:    { eyes: 'open', look: [-6, 0], browL: [-8, -10, 4], browR: [-8, -10, 4], rest: 'smile', arms: [B.down[0], B.finger], cheeks: 'soft' },
    calm:       { eyes: 'open', look: [-8, 0], browL: [0, 0, 2], browR: [0, 0, 2], rest: 'smile', arms: [B.presentL, B.down[1]], cheeks: 'soft' },
    burn:       { eyes: 'half', look: [-8, 0], browL: [-14, -20, 6], browR: [6, 6, 0], rest: 'smirkL', arms: [B.hipL, B.down[1]], cheeks: 'soft' },
    explain3d:  { eyes: 'open', look: [3, -7], browL: [-6, -8, 4], browR: [-6, -8, 4], rest: 'smile', arms: [B.down[0], B.panel], cheeks: 'soft' },
    plain:      { eyes: 'open', look: [-8, 0], browL: [2, 2, 0], browR: [2, 2, 0], rest: 'flat', arms: B.down, cheeks: 'soft' },
    factual:    { eyes: 'open', look: [-6, 0], browL: [-4, -6, 3], browR: [-4, -6, 3], rest: 'smile', arms: [B.down[0], B.finger], cheeks: 'soft' },
    cool:       { eyes: 'half', look: [-8, 0], browL: [0, 0, 0], browR: [0, 0, 0], rest: 'line', arms: B.cross },
    boss:       { eyes: 'half', look: [-4, 0], browL: [-6, -10, 4], browR: [-6, -10, 4], rest: 'smirkL', arms: B.boss, cheeks: 'soft', lean: 0.05, shades: true },
  },
};
const SEG = {
  GPT: [[0, 'hey'], [L[1].end + 0.1, 'listen'], [cap(2, 1), 'curious'], [SIDE_EYE, 'sideeye'], [L[3].start + 0.15, 'tease'],
        [L[4].start, 'ponder'], [L[5].start - 0.1, 'sus'], [L[6].start + 0.2, 'listen'], [cap(6, 2) + 0.6, 'flat'],
        [L[7].start, 'sass'], [PANEL_IN + 0.05, 'impressed'], [L[9].start - 0.05, 'sly'], [L[10].start + 0.1, 'listen2'],
        [L[11].start - 0.05, 'accuse'], [L[12].start, 'unimpressed'], [L[13].start - 0.1, 'stare']],
  CLAUDE: [[0, 'listen'], [L[2].start - 0.05, 'proud'], [STUDIO, 'celeb'], [L[3].start + 0.3, 'unbothered'], [L[4].start - 0.05, 'lecture'],
           [L[5].start + 0.1, 'listen'], [L[6].start - 0.05, 'calm'], [cap(6, 2), 'burn'], [L[7].start + 0.3, 'listen'],
           [L[8].start - 0.05, 'explain3d'], [L[9].start, 'plain'], [L[10].start - 0.05, 'factual'], [L[11].start + 0.2, 'cool'], [BOSS_T, 'boss']],
};
const HOPS = { GPT: [[L[5].start - 0.1, 0.6], [L[11].start, 0.5]], CLAUDE: [[STUDIO, 1.0], [BOSS_T, 0.5]] };

function segAt(kind, t) {
  const s = SEG[kind]; let i = 0;
  for (let k = 0; k < s.length; k++) if (t >= s[k][0]) i = k;
  return { cur: POSE[kind][s[i][1]], prev: POSE[kind][s[Math.max(0, i - 1)][1]], t0: s[i][0] };
}
const lerpPt = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
function blendArms(pa, ca, k) {
  // keep the old draw layer until the arm has mostly left the body, so it never vanishes mid-move
  return ca.map((a, i) => ({ front: k < 0.7 ? pa[i].front : a.front, pts: a.pts.map((p, j) => lerpPt(pa[i].pts[j], p, k)) }));
}
function blink(t, off) { const c = (t + off) % 3.4; return c < 0.12 ? 0.05 : 1; }
function speaking(kind, t) { return TL.lines.find(l => l.speaker === kind && t >= l.start && t < l.end); }
function mouthAmt(l, t) {
  if (!l.pending && l.env.length) return l.env[Math.min(l.env.length - 1, Math.floor((t - l.start) * FPS))] || 0;
  // placeholder lip flap until the real clip exists: ~4.6 syllables/s, closed at phrase breaks
  const u = t - l.start;
  if (u < 0.05 || l.end - t < 0.1) return 0;
  if (l.captions.some((c, k) => k > 0 && Math.abs(t - c.start) < 0.09)) return 0;
  const ph = u * 4.6 + l.id * 0.37;
  return 0.15 + 0.8 * Math.pow(Math.abs(Math.sin(Math.PI * ph)), 0.8) * (0.7 + 0.3 * Math.sin(u * 7.3 + l.id));
}

function charState(kind, t) {
  const { cur, prev, t0 } = segAt(kind, t);
  const k = eo(prog(t, t0, t0 + 0.26));
  const pose = {
    eyes: cur.eyes, look: lerpPt(prev.look || [0, 0], cur.look || [0, 0], k), cheeks: cur.cheeks, extras: cur.extras,
    browL: cur.browL.map((v, i) => lerp(prev.browL[i], v, k)), browR: cur.browR.map((v, i) => lerp(prev.browR[i], v, k)),
    arms: blendArms(prev.arms, cur.arms, k), open: blink(t, kind === 'GPT' ? 0.4 : 2.1),
  };
  const l = speaking(kind, t);
  if (l) { pose.mouth = 'speak'; pose.mouthAmt = mouthAmt(l, t); pose.mouthRest = cur.rest; } else pose.mouth = cur.rest;
  if (cur.clap) {                                    // slow, deadpan clap: hands part and meet
    const c = t - CLAP_T, beat = c > 0 && c < 2.5 ? Math.abs(Math.sin(Math.PI * c / 0.62)) : 0;
    pose.arms = pose.arms.map((a, i) => ({ front: true, pts: a.pts.map((p, j) => j === 0 ? p : [p[0] + (i ? 1 : -1) * beat * (j === 2 ? 70 : 30), p[1] - beat * 10]) }));
  }
  let hop = 0, sq = 0;
  for (const [h0, amp] of HOPS[kind]) {
    const p = prog(t, h0 - 0.02, h0 + 0.42);
    if (p > 0 && p < 1) { hop += Math.sin(Math.PI * p) * 38 * amp; if (p > 0.82) sq -= 0.06 * amp * Math.sin((p - 0.82) / 0.18 * Math.PI); }
  }
  const breathe = 0.011 * Math.sin(t * 2.3 + (kind === 'GPT' ? 0 : 1.7)) + (l ? pose.mouthAmt * 0.018 : 0);
  return { pose, hop, sq, breathe, lean: lerp(prev.lean || 0, cur.lean || 0, k), shades: cur.shades };
}

function drawChar(kind, t) {
  const st = charState(kind, t), x = POS[kind];
  ctx.save();
  ctx.fillStyle = 'rgba(43,29,23,0.13)';             // contact shadow
  ctx.beginPath(); ctx.ellipse(x, GROUND + 4, 120 * (1 - st.hop / 200), 18, 0, 0, Math.PI * 2); ctx.fill();
  ctx.translate(x, GROUND - st.hop); ctx.rotate(st.lean);
  ctx.scale(SCALE * (1 - st.sq), SCALE * (1 + st.sq + st.breathe));
  ctx.translate(-520, -884);
  drawCharacter(ctx, SPEC[kind], st.pose);
  if (kind === 'CLAUDE') { shades(t); creditStar(t); }
  ctx.restore();
}

// ---------- body-frame props (drawn in Claude's 1000-unit frame) ----------
function shades(t) {                                  // imaginary sunglasses: dashed outline only
  if (t < BOSS_T) return;
  const p = eo(prog(t, BOSS_T + 0.05, BOSS_T + 0.42)), y = lerp(150, 392, p);
  ctx.save(); ctx.globalAlpha = clamp(p * 2);
  ctx.setLineDash([12, 10]); ctx.lineWidth = 8; ctx.strokeStyle = '#FFFFFF'; ctx.lineCap = 'round';
  ctx.fillStyle = 'rgba(255,255,255,0.18)';
  for (const cx of [466, 580]) { ctx.beginPath(); ctx.roundRect(cx - 44, y - 26, 88, 54, [8, 8, 26, 26]); ctx.fill(); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(510, y - 14); ctx.quadraticCurveTo(523, y - 22, 536, y - 14); ctx.stroke();
  ctx.setLineDash([]);
  const g = prog(t, BOSS_T + 0.42, BOSS_T + 0.8);  // glint
  if (g > 0 && g < 1) sparkle(560 + g * 40, y - 30, 16 * Math.sin(Math.PI * g), '#FFFFFF');
  ctx.restore();
}
function creditStar(t) {                              // "...and you take the credit?" -> gold star slapped on
  if (t < STAR_T || t > BOSS_T + 1.2) return;
  const s = popIn(t, STAR_T, 0.3) * (1 - prog(t, BOSS_T + 0.8, BOSS_T + 1.2));
  ctx.save(); ctx.translate(600, 610); ctx.rotate(0.2); ctx.scale(s, s);
  star(0, 0, 46, 20, C.yellow); ctx.restore();
}

// ---------- drawing helpers ----------
function star(x, y, R, r, fill) {
  ctx.beginPath();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r : R; ctx[i ? 'lineTo' : 'moveTo'](x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.strokeStyle = C.ink; ctx.stroke();
}
function sparkle(x, y, r, col) {
  ctx.beginPath(); ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r);
  ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r); ctx.fillStyle = col; ctx.fill();
}
function text(s, x, y, size, color = C.ink, weight = 600, align = 'center', a = 1) {
  ctx.save(); ctx.globalAlpha *= a; ctx.font = `${weight} ${size}px Fredoka, sans-serif`;
  ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); ctx.restore();
}
function pill(s, x, y, size, fill, color = C.ink, a = 1, sc = 1) {
  if (sc <= 0 || a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(sc, sc); ctx.font = `700 ${size}px Fredoka, sans-serif`;
  const w = ctx.measureText(s).width + size * 0.9, h = size * 1.45;
  ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fillStyle = fill; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 2); ctx.restore();
}
function strokeInk(w = 6) { ctx.lineWidth = w; ctx.strokeStyle = C.ink; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); }

function background(t) {
  ctx.fillStyle = C.wall; ctx.fillRect(-200, -200, W + 400, H + 400);
  ctx.fillStyle = 'rgba(43,29,23,0.045)';
  for (let y = 40; y < 1400; y += 64) for (let x = (y / 64) % 2 ? 32 : 0; x < W; x += 64) { ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fill(); }
  ctx.globalAlpha = 0.13; ctx.fillStyle = '#57B58F'; ctx.beginPath(); ctx.arc(POS.GPT, 1130, 250, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = PAL.terra; ctx.beginPath(); ctx.arc(POS.CLAUDE, 1060, 290, 0, Math.PI * 2); ctx.fill(); ctx.globalAlpha = 1;
  ctx.fillStyle = C.floor; ctx.fillRect(-200, GROUND - 10, W + 400, H);
  ctx.fillStyle = 'rgba(43,29,23,0.10)'; ctx.fillRect(-200, GROUND - 10, W + 400, 5);
}

// ---------- overlays ----------
function celebrity(t) {                               // spotlight + camera flashes on "whole studio"
  const a = prog(t, STUDIO - 0.05, STUDIO + 0.15) * (1 - prog(t, L[3].start + 0.2, L[3].start + 0.5));
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a * 0.35; ctx.fillStyle = '#FFF6D8';
  ctx.beginPath(); ctx.moveTo(POS.CLAUDE - 70, -40); ctx.lineTo(POS.CLAUDE + 70, -40); ctx.lineTo(POS.CLAUDE + 260, GROUND + 20); ctx.lineTo(POS.CLAUDE - 260, GROUND + 20); ctx.fill();
  ctx.restore();
  for (let k = 0; k < 3; k++) {
    const f = prog(t, STUDIO + 0.05 + k * 0.17, STUDIO + 0.3 + k * 0.17);
    if (f > 0 && f < 1) {
      const [x, y] = [[620, 820], [960, 900], [700, 1240]][k];
      ctx.save(); ctx.globalAlpha = 1 - f; ctx.translate(x, y); ctx.rotate(k);
      sparkle(0, 0, 70 + 60 * f, '#FFFFFF'); ctx.restore();
    }
  }
  for (let k = 0; k < 5; k++) {                       // twinkles that linger while GPT side-eyes
    const ph = (t * 1.6 + k * 0.37) % 1, s = Math.sin(Math.PI * ph) * a;
    sparkle([600, 1000, 640, 990, 820][k], [780, 860, 1080, 1180, 700][k], 22 * s, C.yellow);
  }
}
function flashScreen(t) {
  let f = 0;
  for (let k = 0; k < 3; k++) { const p = prog(t, STUDIO + 0.05 + k * 0.17, STUDIO + 0.17 + k * 0.17); if (p > 0 && p < 1) f = Math.max(f, 1 - p); }
  if (f > 0) { ctx.fillStyle = `rgba(255,255,255,${0.32 * f})`; ctx.fillRect(0, 0, W, H); }
}

const ICONS = [
  { kind: 'happy', col: '#FFD43B', x: 690, y: 690 }, { kind: 'sad', col: '#9CCBEA', x: 900, y: 610 },
  { kind: 'angry', col: '#F07A62', x: 560, y: 520 }, { kind: 'heart', col: '#F49AB5', x: 1000, y: 800 },
  { kind: 'wow', col: '#C8B6F2', x: 780, y: 420 },
];
function emoji(kind, col, x, y, r) {
  ctx.save(); ctx.translate(x, y);
  if (kind === 'heart') {
    ctx.beginPath(); ctx.moveTo(0, r * 0.75);
    ctx.bezierCurveTo(-r * 1.3, -r * 0.1, -r * 0.6, -r * 1.05, 0, -r * 0.4);
    ctx.bezierCurveTo(r * 0.6, -r * 1.05, r * 1.3, -r * 0.1, 0, r * 0.75);
    ctx.fillStyle = col; ctx.fill(); strokeInk(6); ctx.restore(); return;
  }
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); strokeInk(6);
  ctx.fillStyle = C.ink; const e = r * 0.34;
  const eyes = () => { ctx.beginPath(); ctx.ellipse(-e, -r * 0.15, r * 0.09, r * 0.14, 0, 0, 7); ctx.ellipse(e, -r * 0.15, r * 0.09, r * 0.14, 0, 0, 7); ctx.fill(); };
  ctx.beginPath();
  if (kind === 'happy') { eyes(); ctx.beginPath(); ctx.arc(0, r * 0.08, r * 0.42, 0.15 * Math.PI, 0.85 * Math.PI); strokeInk(6); }
  if (kind === 'sad') { eyes(); ctx.beginPath(); ctx.arc(0, r * 0.62, r * 0.36, 1.2 * Math.PI, 1.8 * Math.PI); strokeInk(6); }
  if (kind === 'angry') { eyes(); ctx.beginPath(); ctx.moveTo(-e - 12, -r * 0.48); ctx.lineTo(-e + 12, -r * 0.34); ctx.moveTo(e + 12, -r * 0.48); ctx.lineTo(e - 12, -r * 0.34); ctx.moveTo(-r * 0.3, r * 0.4); ctx.lineTo(r * 0.3, r * 0.4); strokeInk(6); }
  if (kind === 'wow') { eyes(); ctx.beginPath(); ctx.ellipse(0, r * 0.38, r * 0.15, r * 0.2, 0, 0, 7); ctx.fill(); }
  if (kind === 'meh') { ctx.beginPath(); ctx.moveTo(-e - 12, -r * 0.12); ctx.lineTo(-e + 12, -r * 0.12); ctx.moveTo(e - 12, -r * 0.12); ctx.lineTo(e + 12, -r * 0.12); ctx.moveTo(-r * 0.3, r * 0.4); ctx.lineTo(r * 0.3, r * 0.4); strokeInk(6); }
  ctx.restore();
}
function emotions(t) {
  const out = prog(t, cap(6, 1), cap(6, 1) + 0.6);            // "patterns aren't proof" -> icons drift off
  ICONS.forEach((ic, k) => {
    const s = popIn(t, ICONS_T + k * 0.32, 0.4);
    if (s <= 0 || out >= 1) return;
    ctx.save(); ctx.globalAlpha = 1 - out;
    emoji(ic.kind, ic.col, ic.x + Math.sin(t * 1.3 + k) * 12, ic.y + Math.cos(t * 1.7 + k) * 10 - out * 160, 52 * s);
    ctx.restore();
  });
  const sa = prog(t, L[4].start, L[4].start + 0.3) * (1 - prog(t, L[6].end, L[6].end + 0.3));
  if (sa > 0) pill('Anthropic interpretability research · Claude Sonnet 4.5', 540, 250, 30, '#FFFFFF', C.ink, sa);
  const m = popIn(t, cap(6, 2) + 0.35, 0.4) * (1 - prog(t, L[7].start + 0.2, L[7].start + 0.5));
  if (m > 0) emoji('meh', '#FFD43B', POS.CLAUDE + 40, 770 + Math.sin(t * 2) * 6, 50 * m);   // the theory, under test
}

// Blender-style viewport: generic dark 3D window (no logos)
function blenderPanel(t) {
  const a = popIn(t, PANEL_IN, 0.4), out = prog(t, PANEL_OUT, PANEL_OUT + 0.35);
  if (a <= 0 || out >= 1) return;
  const x0 = 80, y0 = 200, w = 920, h = 600;
  ctx.save(); ctx.globalAlpha = 1 - out;
  ctx.translate(540, y0 + h / 2); ctx.scale(a, a); ctx.translate(-540, -(y0 + h / 2));
  ctx.shadowColor = 'rgba(0,0,0,0.25)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
  ctx.beginPath(); ctx.roundRect(x0, y0, w, h, 26); ctx.fillStyle = C.ui; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.save(); ctx.beginPath(); ctx.roundRect(x0, y0, w, h, 26); ctx.clip();
  ctx.fillStyle = C.uiHead; ctx.fillRect(x0, y0, w, 64);
  ['#FF5F57', '#FEBC2E', '#28C840'].forEach((c, i) => { ctx.beginPath(); ctx.arc(x0 + 40 + i * 34, y0 + 32, 10, 0, 7); ctx.fillStyle = c; ctx.fill(); });
  text('3D viewport', x0 + 160, y0 + 33, 28, '#D8D8DC', 500, 'left');
  // render progress in the header (L10: "Blender renders locally")
  const rp = prog(t, RENDER_T + 0.2, cap(10, 1));
  if (t > RENDER_T) {
    text(rp < 1 ? 'Rendering… on your computer' : 'Rendered locally ✓', x0 + w - 330, y0 + 33, 26, rp < 1 ? '#FFD9A0' : '#9BE3B5', 600, 'center');
    ctx.fillStyle = '#55555A'; ctx.beginPath(); ctx.roundRect(x0 + w - 150, y0 + 24, 120, 18, 9); ctx.fill();
    ctx.fillStyle = C.sel; ctx.beginPath(); ctx.roundRect(x0 + w - 150, y0 + 24, 120 * rp, 18, 9); ctx.fill();
  }
  // perspective grid floor
  const vx = 540, vy = y0 + 230, gy = y0 + h;
  ctx.strokeStyle = C.uiGrid; ctx.lineWidth = 2;
  for (let i = -10; i <= 10; i++) { ctx.beginPath(); ctx.moveTo(vx + i * 26, vy + 40); ctx.lineTo(vx + i * 150, gy + 40); ctx.stroke(); }
  for (let j = 0; j < 9; j++) { const yy = vy + 40 + Math.pow(j / 8, 1.9) * (gy - vy); ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x0 + w, yy); ctx.stroke(); }
  ctx.lineWidth = 3; ctx.strokeStyle = '#C0504D'; ctx.beginPath(); ctx.moveTo(x0, vy + 150); ctx.lineTo(x0 + w, vy + 150); ctx.stroke();
  ctx.strokeStyle = '#7FA346'; ctx.beginPath(); ctx.moveTo(vx, vy + 40); ctx.lineTo(vx + 40, gy + 40); ctx.stroke();
  // nav gizmo
  [['#E0565B', 50, -10, 'X'], ['#7DBE4C', -18, -42, 'Y'], ['#4F8BE0', 0, 42, 'Z']].forEach(([c, dx, dy, l]) => {
    ctx.beginPath(); ctx.moveTo(x0 + w - 70, y0 + 140); ctx.lineTo(x0 + w - 70 + dx * 0.7, y0 + 140 - dy * 0.7); ctx.lineWidth = 4; ctx.strokeStyle = c; ctx.stroke();
    ctx.beginPath(); ctx.arc(x0 + w - 70 + dx * 0.7, y0 + 140 - dy * 0.7, 13, 0, 7); ctx.fillStyle = c; ctx.fill(); text(l, x0 + w - 70 + dx * 0.7, y0 + 141 - dy * 0.7, 16, '#1A1A1A', 700);
  });
  const rendered = rp;
  // objects pop in on "...help build 3D scenes"
  const o1 = popIn(t, BUILD_T + 0.1), o2 = popIn(t, BUILD_T + 0.45), o3 = popIn(t, BUILD_T + 0.8);
  if (o1 > 0) cube(360, y0 + 420, 70 * o1, rendered);
  if (o2 > 0) sphere(560, y0 + 440, 56 * o2, rendered);
  if (o3 > 0) beanStatue(740, y0 + 470, o3, rendered);
  // GPU card doing the actual work (L11)
  const g = popIn(t, GPU_T + 0.1, 0.35);
  if (g > 0) gpu(x0 + 150, y0 + h - 95, g, t);
  // zero-token rumour coin (L9)
  const z = popIn(t, ZERO_T, 0.35) * (1 - prog(t, RENDER_T, RENDER_T + 0.3));
  if (z > 0) { ctx.save(); ctx.translate(x0 + w - 130, y0 + 300); ctx.scale(z, z); ctx.rotate(Math.sin(t * 3) * 0.1);
    ctx.beginPath(); ctx.arc(0, 0, 64, 0, 7); ctx.fillStyle = C.yellow; ctx.fill(); strokeInk(6);
    ctx.beginPath(); ctx.arc(0, 0, 48, 0, 7); ctx.lineWidth = 4; ctx.strokeStyle = '#C9A21E'; ctx.stroke();
    text('0', -6, 4, 62, C.ink, 700); text('?', 34, -36, 44, '#E05A44', 700); ctx.restore(); }
  ctx.restore();
  // connector: requirement chip + plug cable from Claude into the window (L8)
  const ca = prog(t, L[8].start, L[8].start + 0.3);
  if (ca > 0) pill('needs Blender + the Blender connector (MCP)', 540, y0 + h - 34, 26, '#FFFFFF', C.ink, ca);
  ctx.restore();
}
function cube(x, y, s, r) {
  const top = r > 0.5 ? '#F2C7A6' : '#B9B9BE', left = r > 0.5 ? '#D9906A' : '#8E8E94', right = r > 0.5 ? '#B8704F' : '#77777D';
  const face = (pts, c) => { ctx.beginPath(); pts.forEach((p, i) => ctx[i ? 'lineTo' : 'moveTo'](x + p[0] * s, y + p[1] * s)); ctx.closePath(); ctx.fillStyle = c; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = r > 0.5 ? C.ink : C.sel; ctx.stroke(); };
  face([[0, -1], [0.95, -0.5], [0, 0], [-0.95, -0.5]], top);
  face([[-0.95, -0.5], [0, 0], [0, 1.05], [-0.95, 0.55]], left);
  face([[0.95, -0.5], [0, 0], [0, 1.05], [0.95, 0.55]], right);
}
function sphere(x, y, s, r) {
  ctx.beginPath(); ctx.arc(x, y, s, 0, 7); ctx.fillStyle = r > 0.5 ? '#9DD7BE' : '#A3A3A8'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = r > 0.5 ? C.ink : '#5A5A5F'; ctx.stroke();
  ctx.beginPath(); ctx.ellipse(x - s * 0.35, y - s * 0.38, s * 0.28, s * 0.18, -0.6, 0, 7); ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.fill();
}
function beanStatue(x, y, s, r) {                     // Claude modelled... itself. On a pedestal.
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = r > 0.5 ? '#E9DCCB' : '#9A9AA0'; ctx.beginPath(); ctx.roundRect(-70, 40, 140, 44, 8); ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.translate(0, 40); ctx.scale(0.28, 0.28); ctx.translate(-520, -800);
  SPECS.BEAN.body(ctx); ctx.fillStyle = r > 0.5 ? PAL.terra : '#B0B0B5'; ctx.fill(); ctx.lineWidth = 14; ctx.strokeStyle = r > 0.5 ? C.ink : C.sel; ctx.stroke();
  ctx.save(); SPECS.BEAN.body(ctx); ctx.clip(); ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillRect(330, 140, 150, 700); ctx.restore();
  SPECS.BEAN.mark(ctx);
  ctx.restore();
}
function gpu(x, y, s, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const shake = t < L[11].end ? Math.sin(t * 60) * 2 : 0; ctx.translate(shake, 0);
  ctx.beginPath(); ctx.roundRect(-110, -48, 220, 96, 12); ctx.fillStyle = '#5B5F66'; ctx.fill(); strokeInk(5);
  for (const fx of [-50, 50]) {
    ctx.beginPath(); ctx.arc(fx, 0, 34, 0, 7); ctx.fillStyle = '#2E3035'; ctx.fill(); strokeInk(4);
    for (let b = 0; b < 5; b++) { const a = t * 18 + b * Math.PI * 2 / 5; ctx.beginPath(); ctx.moveTo(fx, 0); ctx.lineTo(fx + Math.cos(a) * 28, Math.sin(a) * 28); ctx.lineWidth = 6; ctx.strokeStyle = '#A9ADB5'; ctx.stroke(); }
  }
  ctx.fillStyle = '#D8B45A'; for (let i = 0; i < 8; i++) ctx.fillRect(-90 + i * 22, 48, 12, 12);
  ctx.restore();
  const d = (t * 1.4) % 1;                              // it's sweating
  ctx.save(); ctx.globalAlpha = 1 - d; ctx.translate(x + 120, y - 40 + d * 30);
  ctx.beginPath(); ctx.moveTo(0, -16); ctx.quadraticCurveTo(12, 0, 0, 10); ctx.quadraticCurveTo(-12, 0, 0, -16); ctx.fillStyle = PAL.drop; ctx.fill(); strokeInk(3); ctx.restore();
}
function plugCable(t) {                               // Claude plugs into the viewport on "right connector"
  const a = prog(t, L[8].start + 0.1, PLUG_T), out = prog(t, PANEL_OUT, PANEL_OUT + 0.35);
  if (a <= 0 || out >= 1) return;
  const sx = POS.CLAUDE + 30, sy = 1250, ex = 985, ey = 830, p = eo(a);      // cable leaves from behind Claude's back
  const hx = lerp(sx + 190, ex, p), hy = lerp(sy, ey, p);
  ctx.save(); ctx.globalAlpha = 1 - out;
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.bezierCurveTo(sx + 330, sy + 40, hx + 40, lerp(sy, hy, 0.3), hx, hy); strokeInk(9);
  ctx.translate(hx, hy); ctx.rotate(-Math.PI / 2 - 0.3);
  ctx.beginPath(); ctx.roundRect(-22, -14, 44, 40, 8); ctx.fillStyle = '#F6E9D7'; ctx.fill(); strokeInk(5);
  ctx.fillStyle = C.ink; ctx.fillRect(-12, -30, 7, 18); ctx.fillRect(5, -30, 7, 18);
  ctx.restore();
  const s = prog(t, PLUG_T, PLUG_T + 0.3);
  if (s > 0 && s < 1) { ctx.save(); ctx.globalAlpha = 1 - s; sparkle(ex, ey - 20, 40 * s + 14, C.yellow); ctx.restore(); }
}
function planningTokens(t) {                          // L10: "my planning still uses tokens"
  const a = prog(t, TOKENS_T - 0.1, TOKENS_T + 0.2) * (1 - prog(t, L[11].start + 0.6, L[11].start + 1.0));
  if (a <= 0) return;
  const mx = 330, my = 900;                         // above GPT, clear of the viewport
  ctx.save(); ctx.globalAlpha = a;
  ctx.beginPath(); ctx.roundRect(mx - 190, my - 34, 380, 68, 34); ctx.fillStyle = '#FFFFFF'; ctx.fill(); strokeInk(5);
  text('planning tokens', mx - 50, my + 2, 28, C.ink, 700);
  const fill = clamp(prog(t, TOKENS_T, TOKENS_T + 1.4));
  ctx.beginPath(); ctx.roundRect(mx + 60, my - 14, 110, 28, 14); ctx.fillStyle = '#EFE6D8'; ctx.fill(); strokeInk(4);
  ctx.beginPath(); ctx.roundRect(mx + 62, my - 12, 106 * fill, 24, 12); ctx.fillStyle = C.yellow; ctx.fill();
  ctx.restore();
  for (let k = 0; k < 6; k++) {                       // coins hop from Claude's head into the meter
    const p = prog(t, TOKENS_T + 0.25 + k * 0.22 - 0.25, TOKENS_T + 0.25 + k * 0.22 + 0.3);
    if (p <= 0 || p >= 1) continue;
    const x = lerp(POS.CLAUDE + 10, mx + 110, p), y = lerp(960, my, p) - Math.sin(Math.PI * p) * 120;
    ctx.save(); ctx.translate(x, y); ctx.scale(Math.cos(p * 9), 1);
    ctx.beginPath(); ctx.arc(0, 0, 22, 0, 7); ctx.fillStyle = C.yellow; ctx.fill(); strokeInk(4); ctx.restore();
  }
}

// ---------- camera ----------
// keys: [time, zoom, focusX, focusY, transition seconds]
const CAM = [
  [0, 1.0, 540, 1080, 0],
  [STUDIO - 0.1, 1.22, POS.CLAUDE - 40, 1080, 0.25],
  [SIDE_EYE, 1.5, POS.GPT + 30, 1150, 0.18],
  [L[3].start + 0.75, 1.0, 540, 1080, 0.35],
  [BOSS_T, 1.16, POS.CLAUDE - 60, 1120, 0.4],
  [L[13].start - 0.1, 1.0, 540, 1080, 0.3],
  [cap(13, 1), 1.24, 450, 1130, 2.2],               // push toward GPT's stare, Claude's boss pose still in frame
];
function camAt(t) {
  let i = 0; for (let k = 0; k < CAM.length; k++) if (t >= CAM[k][0]) i = k;
  const c = CAM[i], p = i ? CAM[i - 1] : c, k = c[4] ? eio(prog(t, c[0], c[0] + c[4])) : 1;
  return [lerp(p[1], c[1], k), lerp(p[2], c[2], k), lerp(p[3], c[3], k)];
}

// ---------- captions ----------
function captions(t) {
  const l = TL.lines.find(l => l.captions.some(c => t >= c.start && t < c.end));
  if (!l) return;
  const c = l.captions.find(c => t >= c.start && t < c.end);
  const p = eo(prog(t, c.start, c.start + 0.12)), size = 60;
  ctx.save(); ctx.font = `600 ${size}px Fredoka, sans-serif`;
  const full = c.text; let rows = [full];
  const plain = full.replace(/\*/g, '');
  if (ctx.measureText(plain).width > 880) {          // two-line wrap at the space nearest the middle (outside highlights)
    let cut = -1, best = 1e9, inHl = false;
    for (let i = 0; i < full.length; i++) { if (full[i] === '*') inHl = !inHl; if (full[i] === ' ' && !inHl && Math.abs(i - full.length / 2) < best) { best = Math.abs(i - full.length / 2); cut = i; } }
    rows = [full.slice(0, cut), full.slice(cut + 1)];
  }
  const parts = rows.map(r => r.split('*'));
  const mw = (s, hl) => { ctx.font = `${hl ? 700 : 600} ${size}px Fredoka, sans-serif`; const w = ctx.measureText(s).width; ctx.font = `600 ${size}px Fredoka, sans-serif`; return w; };
  const rowW = parts.map(r => r.reduce((a, s, i) => a + (s ? mw(s, i % 2) + (i % 2 ? size * 0.5 + 6 : 0) : 0), 0));
  const lh = size * 1.3, boxW = Math.max(...rowW) + 64, boxH = rows.length * lh + 28, by = 1545 - (rows.length - 1) * lh / 2;
  const accent = l.speaker === 'GPT' ? C.gpt : C.claude;
  ctx.globalAlpha = p; ctx.translate(540, by + (1 - p) * 12);
  ctx.beginPath(); ctx.roundRect(-boxW / 2, -lh / 2 - 14, boxW, boxH, 26); ctx.fillStyle = 'rgba(43,29,23,0.92)'; ctx.fill();
  ctx.fillStyle = accent; ctx.beginPath(); ctx.roundRect(-boxW / 2, -lh / 2 - 14, 14, boxH, 7); ctx.fill();
  // speaker tag
  ctx.font = `700 30px Fredoka, sans-serif`; const nm = l.speaker === 'GPT' ? 'GPT' : 'CLAUDE', nw = ctx.measureText(nm).width + 34;
  ctx.beginPath(); ctx.roundRect(-boxW / 2 + 18, -lh / 2 - 14 - 30, nw, 46, 23); ctx.fillStyle = accent; ctx.fill();
  ctx.fillStyle = '#FFFFFF'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(nm, -boxW / 2 + 18 + nw / 2, -lh / 2 - 14 - 6);
  ctx.textAlign = 'left'; ctx.font = `600 ${size}px Fredoka, sans-serif`;
  parts.forEach((r, ri) => {
    let x = -rowW[ri] / 2; const y = ri * lh;
    r.forEach((s, i) => {
      if (!s) return;
      const w = mw(s, i % 2);
      if (i % 2) {                                    // highlighted keyword pops in
        const hp = back(prog(t, c.start + 0.05, c.start + 0.35));
        ctx.save(); ctx.translate(x + (w + size * 0.5) / 2, y); ctx.scale(hp, hp);
        ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.roundRect(-(w + size * 0.5) / 2, -size * 0.62, w + size * 0.5, size * 1.24, 14); ctx.fill();
        ctx.fillStyle = C.ink; ctx.font = `700 ${size}px Fredoka, sans-serif`; ctx.fillText(s, -w / 2, 3); ctx.restore();
        ctx.font = `600 ${size}px Fredoka, sans-serif`;
        x += w + size * 0.5 + 6;
      } else { ctx.fillStyle = '#FFFFFF'; ctx.fillText(s, x, y + 3); x += w; }
    });
  });
  ctx.restore();
}

// ---------- frame ----------
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
  const [z, fx, fy] = camAt(t);
  ctx.save(); ctx.translate(540, 1080); ctx.scale(z, z); ctx.translate(-fx, -fy);   // camera layer: set + characters
  background(t);
  celebrity(t);
  plugCable(t);
  drawChar('GPT', t); drawChar('CLAUDE', t);
  ctx.restore();
  emotions(t); blenderPanel(t); planningTokens(t);    // graphics layer: not zoomed
  // side-eye vignette
  const v = prog(t, SIDE_EYE, SIDE_EYE + 0.15) * (1 - prog(t, L[3].start + 0.5, L[3].start + 0.8))
          + prog(t, cap(13, 1), cap(13, 1) + 1.2) * 0.7;
  if (v > 0) {
    const g = ctx.createRadialGradient(540, 1000, 300, 540, 1000, 1150);
    g.addColorStop(0, 'rgba(43,29,23,0)'); g.addColorStop(1, `rgba(43,29,23,${0.38 * clamp(v)})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  flashScreen(t);
  captions(t);
  if (TL.lines.some(l => l.pending)) pill('ANIMATIC · voices pending', 220, 96, 28, '#E8584A', '#FFFFFF', 0.92);
}

window.READY = (async () => {
  await document.fonts.load('600 60px Fredoka'); await document.fonts.load('700 60px Fredoka');
  window.renderFrame = renderFrame; window.DURATION = TOTAL; window.FPS = FPS;
  const q = new URLSearchParams(location.search); renderFrame(parseFloat(q.get('t') || '0'));
  return true;
})();
