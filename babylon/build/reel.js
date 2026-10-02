// DEEP CURIOUS — literary Reel adapted from «أغنى رجل في بابل». The narrator's name is never shown.
// Every beat is keyed to a narration word (cue), so swapping in the measured recording re-times the film.
'use strict';

const NAMES = ['bg_interior', 'bg_street', 'p_rich_pouch', 'p_scribe', 'p_disappointed', 'p_facing',
  'sec_brickmaker', 'sec_armorer', 'sec_mentor', 'tablets', 'stylus', 'coin', 'jar', 'pouch_empty', 'coin_bag',
  'bread', 'jug', 'garment', 'jewels', 'glass', 'shield'];
Object.assign(PLACEHOLDER, {
  p_rich_pouch: 1.25, p_scribe: 1.0, p_disappointed: 1.25, p_facing: 1.25, sec_brickmaker: 1.6, sec_armorer: 1.6,
  sec_mentor: 1.6, tablets: 0.8, stylus: 1.2, coin: 1, jar: 1.1, pouch_empty: 1.0, coin_bag: 1.1, bread: 0.7,
  jug: 1.2, garment: 0.8, jewels: 0.8, glass: 0.8, shield: 1,
});
const DURATION = TIMELINE.duration;

// ---------- cues: start time of the n-th occurrence of a narration word ----------
function cue(word, n = 1) {
  let k = 0;
  for (const w of TIMELINE.words) if (w.w.replace(/[^ء-ي]/g, '') === word && ++k === n) return w.s;
  throw new Error('cue not found: ' + word + ' #' + n);
}
const Q = {
  open: 0, lost1: cue('لكنني', 1),
  scribe: cue('كنت'), wage: cue('يذهب'), nothing: cue('يبقى'),
  ask: cue('سألت'), learn1: cue('فتعلمت'), tenth: cue('بعشر'),
  save: cue('بدأت', 1), handed: cue('سلمت'), jewelsWord: cue('جواهر', 1),
  back: cue('عندما'), glass: cue('زجاج'),
  lost2: cue('خسرت', 2), lesson: cue('الخبرة', 1),
  restart: cue('بدأت', 2), funded: cue('ومولت'), reinvest: cue('أعيد'),
  years: cue('وبعد'), partner: cue('اختارني'), estate: cue('نلت'),
  grow: cue('هكذا'), learnW: cue('بالتعلم'), patience: cue('والصبر'), chance: cue('والفرص'),
  now: cue('والآن'), ask2: cue('هل'), write: cue('اكتب'),
};

// ---------- code-built props ----------
function coin(x, y, r, t, key, a = 1) {
  if (a <= 0) return;
  if (IMG.coin) return sticker('coin', x, y, r * 2.25, { t, alpha: a, still: !key });
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x + (key ? jit(key + 'x', t, 1) : 0), y + (key ? jit(key + 'y', t, 1) : 0));
  shadowOn(0.7); ctx.beginPath(); ctx.arc(0, 0, r + 6, 0, Math.PI * 2); ctx.fillStyle = '#FFFDF7'; ctx.fill(); shadowOff();
  const g = ctx.createRadialGradient(-r * 0.3, -r * 0.35, r * 0.1, 0, 0, r);
  g.addColorStop(0, '#E7A867'); g.addColorStop(1, C.copper);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
  ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(90,45,20,0.6)'; ctx.beginPath(); ctx.arc(0, 0, r * 0.72, 0, Math.PI * 2); ctx.stroke();
  ctx.strokeStyle = 'rgba(90,45,20,0.55)'; ctx.lineWidth = 2.5;            // small wedge marks
  for (let i = 0; i < 3; i++) { const yy = -r * 0.25 + i * r * 0.25; ctx.beginPath(); ctx.moveTo(-r * 0.3, yy); ctx.lineTo(r * 0.3, yy); ctx.stroke(); }
  ctx.restore();
}
const easeIn = p => p * p * p;
// exactly ten coins: nine stay together, one is saved into the open jar
function tenCoins(t, t0, tSplit, cx, cy, jar) {
  const r = 34, pos = [];
  for (let i = 0; i < 10; i++) pos.push([cx + (i % 5 - 2) * 84, cy + Math.floor(i / 5) * 84]);
  for (let i = 0; i < 10; i++) {
    const p = pop(t, t0 + i * 0.07, 0.3);
    if (i === 9 && t >= tSplit) {
      // arc to just above the OPEN jar mouth, then drop straight in; clipped at the front rim so it visibly goes inside
      const m = easeInOut(prog(stepT(t), tSplit, tSplit + 0.8)), d = easeIn(prog(stepT(t), tSplit + 0.8, tSplit + 1.15));
      const x = lerp(pos[i][0], jar.x, m), y = lerp(pos[i][1], jar.top - 46, m) - Math.sin(m * Math.PI) * 140 + d * 110;
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, jar.rim); ctx.clip();
      coin(x, y, r * lerp(1, 0.78, m), t, 'c9', 1);
      ctx.restore();
      if (d > 0.6) sparkle(jar.x + 26, jar.rim - 10, 22, t, 1 - prog(t, tSplit + 1.15, tSplit + 1.6));
    } else {
      const shift = t >= tSplit ? -18 * easeOut(prog(t, tSplit, tSplit + 0.5)) : 0;   // the nine close ranks
      coin(pos[i][0] + shift, pos[i][1], r * p.s, t, 'c' + i, p.a);
    }
  }
}
// glass: translucent cracked shards with cool reflections (drawn over / instead of the glass asset)
function glassShards(cx, cy, t, a) {
  if (a <= 0) return;
  const r = mulberry32(99); const all = [];
  ctx.save(); ctx.globalAlpha = a;
  for (let i = 0; i < 6; i++) {
    const x = cx + (r() - 0.5) * 260, y = cy + (r() - 0.5) * 120, s = 40 + r() * 34, n = 4 + Math.floor(r() * 3);
    const pts = []; for (let k = 0; k < n; k++) { const ang = k / n * Math.PI * 2 + r() * 0.6; pts.push([x + Math.cos(ang) * s * (0.6 + r() * 0.5), y + Math.sin(ang) * s * (0.5 + r() * 0.5)]); }
    all.push(pts);
    const tint = ['rgba(120,190,190,0.30)', 'rgba(220,140,120,0.28)', 'rgba(150,170,220,0.28)'][i % 3];
    ctx.beginPath(); pts.forEach(([px, py], k) => k ? ctx.lineTo(px, py) : ctx.moveTo(px, py)); ctx.closePath();
    ctx.fillStyle = tint; ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.stroke();           // thin bright edge
    ctx.lineWidth = 1.5; ctx.strokeStyle = 'rgba(40,60,70,0.45)';                          // crack line
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); ctx.lineTo((pts[2][0] + x) / 2, (pts[2][1] + y) / 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(pts[1][0] + 4, pts[1][1] + 4); ctx.lineTo(pts[1][0] + 18, pts[1][1] + 14);
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.stroke();            // glint
  }
  const sw = prog(t, Q.glass + 0.2, Q.glass + 1.0);                                       // one cold shine sweep
  if (sw > 0 && sw < 1) {
    const gx = cx - 200 + sw * 400; const g = ctx.createLinearGradient(gx - 60, 0, gx + 60, 0);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(235,250,255,0.55)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.beginPath(); all.forEach(pts => { pts.forEach(([px, py], k) => k ? ctx.lineTo(px, py) : ctx.moveTo(px, py)); ctx.closePath(); });
    ctx.clip(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(cx - 220, cy - 140, 440, 280);   // shine only on the shards
  }
  ctx.restore();
}
function sparkle(x, y, s, t, a) {
  const k = 0.6 + 0.4 * Math.sin(t * 9 + x);
  ctx.save(); ctx.globalAlpha = a * k; ctx.fillStyle = '#FFF6D8'; ctx.translate(x, y); ctx.beginPath();
  for (let i = 0; i < 8; i++) { const rr = i % 2 ? s * 0.25 : s; const ang = i * Math.PI / 4; ctx.lineTo(Math.cos(ang) * rr, Math.sin(ang) * rr); }
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function loopArrows(cx, cy, rad, t, a) {           // reinvestment loop: dotted arrows around the jar
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = C.teal; ctx.lineWidth = 9; ctx.setLineDash([2, 20]); ctx.lineCap = 'round';
  ctx.lineDashOffset = -t * 40; ctx.beginPath(); ctx.arc(cx, cy, rad, -Math.PI * 0.9, Math.PI * 0.75); ctx.stroke();
  ctx.setLineDash([]); const ang = Math.PI * 0.75, hx = cx + Math.cos(ang) * rad, hy = cy + Math.sin(ang) * rad;
  ctx.fillStyle = C.teal; ctx.translate(hx, hy); ctx.rotate(ang + Math.PI / 2); ctx.beginPath(); ctx.moveTo(0, -22); ctx.lineTo(18, 10); ctx.lineTo(-18, 10); ctx.closePath(); ctx.fill();
  ctx.restore();
}
// passing years: four lighting moods (dawn, noon, dusk, lamp-lit night) — palms stay leafy
const LIGHT = ['rgba(255,190,140,0.22)', 'rgba(255,245,215,0.06)', 'rgba(224,138,114,0.26)', 'rgba(30,43,74,0.42)'];
function yearLight(t, t0, t1) {
  const p = prog(t, t0, t1) * 4; const i = Math.min(3, Math.floor(p)); const f = p - i;
  ctx.fillStyle = LIGHT[i]; ctx.fillRect(0, 0, W, H);
  if (i < 3 && f > 0.8) { ctx.globalAlpha = (f - 0.8) / 0.2; ctx.fillStyle = LIGHT[i + 1]; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
}

// ---------- scenes ----------
function sOpening(t) {
  drawBg('bg_street', 1.06 + 0.02 * prog(t, 0, Q.scribe), 0.5, 0.5);
  const ch = sticker('p_rich_pouch', 520, 1400, 760, { t, anchor: 'bottom' });
  if (t > Q.lost1) {                                   // the empty pouch shakes: nothing falls out
    const sh = Math.sin(t * 22) * 8 * bump(t, Q.lost1 + 0.2, Q.lost1 + 1.4);
    sticker('pouch_empty', 760 + sh, ch.top + 120, 190, { t, rot: 0.2 });
  }
  card('حكاية أدبية', 540, 150, { t, alpha: prog(t, 0.2, 0.5) * (1 - prog(t, Q.scribe - 0.4, Q.scribe)), font: 'cairo', size: 46, fill: C.mustard, rot: -0.02 });
}
function sScribe(t) {
  drawBg('bg_interior', 1.12, 0.5, 0.55);
  sticker('tablets', 820, 1150, 260, { t });
  sticker('p_scribe', 460, 1330, 780, { t, anchor: 'bottom' });
  sticker('stylus', 610, 1080, 90, { t, rot: -0.5 });
  // wage arrives, then leaves for food and clothes
  const items = [['bread', 230, 620], ['garment', 540, 520], ['jug', 850, 620]];
  items.forEach(([n, x, y], i) => { const p = pop(t, Q.wage + 0.3 + i * 0.35); if (p.a) sticker(n, x, y, 200, { t, alpha: p.a * (1 - prog(t, Q.nothing + 0.6, Q.nothing + 1.0)), scale: p.s }); });
  for (let i = 0; i < 3; i++) {
    const t0 = Q.wage + i * 0.35, m = easeInOut(prog(stepT(t), t0, t0 + 0.8));
    if (t > t0 && m < 1) coin(lerp(520, items[i][1], m), lerp(1000, items[i][2] + 60, m) - Math.sin(m * Math.PI) * 120, 30, t, 'w' + i);
  }
  if (t > Q.nothing) card('لا يبقى شيء', 540, 1260, { t, alpha: pop(t, Q.nothing + 0.2).a, scale: pop(t, Q.nothing + 0.2).s, size: 50, edge: C.coral, rot: 0.02 });
}
function sTenth(t) {
  drawBg('bg_interior', 1.3, 0.35, 0.45);
  const m = pop(t, Q.ask + 0.1, 0.5); sticker('sec_mentor', 250, 1330, 520, { t, alpha: m.a, anchor: 'bottom' });
  const jw = 230, jh = jw * (IMG.jar ? IMG.jar.height / IMG.jar.width : PLACEHOLDER.jar);
  const jar = { x: 820, y: 1120, top: 1120 - jh / 2, rim: 1120 - jh / 2 + jh * 0.14 };   // rim = front lip of the open mouth
  if (t > Q.learn1 - 0.3) {
    const ja = pop(t, Q.learn1 - 0.3).a; sticker('jar', jar.x, jar.y, jw, { t, alpha: ja, still: true });
    if (!IMG.jar) { ctx.save(); ctx.globalAlpha = ja; ctx.fillStyle = '#3a2416'; ctx.beginPath(); ctx.ellipse(jar.x, jar.rim - 6, jw * 0.3, 14, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore(); }  // placeholder open mouth
  }
  if (t > Q.learn1) tenCoins(t, Q.learn1, Q.tenth + 0.15, 540, 620, jar);
  if (t > Q.tenth + 0.9) card('العُشر', 820, 1330, { t, alpha: pop(t, Q.tenth + 0.9).a, scale: pop(t, Q.tenth + 0.9).s, size: 48, fill: C.mustard });
}
function sJewels(t) {
  drawBg('bg_street', 1.25, 0.6, 0.55);
  sticker('sec_brickmaker', 760, 1400, 560, { t, anchor: 'bottom', alpha: pop(t, Q.save + 0.2).a });
  sticker('p_rich_pouch', 280, 1400, 600, { t, anchor: 'bottom' });
  const jarLevel = prog(t, Q.save, Q.handed);                       // saving takes time: coins drop one by one
  for (let i = 0; i < 4; i++) if (jarLevel > i / 4) coin(470 + (i % 2) * 30, 1180 - i * 20, 26, t, 'j' + i);
  if (t > Q.handed) {
    const m = easeInOut(prog(stepT(t), Q.handed + 0.2, Q.handed + 1.1));
    sticker('coin_bag', lerp(430, 700, m), lerp(1060, 1000, m) - Math.sin(m * Math.PI) * 80, 170, { t });
  }
  if (t > Q.jewelsWord) {
    const p = pop(t, Q.jewelsWord, 0.4); sticker('jewels', 700, 760, 300, { t, alpha: p.a, scale: p.s });
    for (let i = 0; i < 4; i++) sparkle(600 + i * 60, 700 + (i % 2) * 80, 26, t, p.a);
  }
}
function sGlass(t) {
  drawBg('bg_street', 1.6, 0.55, 0.62, `rgba(30,43,74,${0.25 * prog(t, Q.glass, Q.glass + 0.4)})`);
  const reveal = prog(stepT(t), Q.glass, Q.glass + 0.35);
  sticker(reveal < 1 ? 'p_rich_pouch' : 'p_disappointed', 540, 1420, 720, { t, anchor: 'bottom' });
  const jp = 1 - reveal;
  sticker('jewels', 540, 760, 360, { t, alpha: jp });
  for (let i = 0; i < 5; i++) sparkle(440 + i * 50, 700 + (i % 2) * 90, 30, t, jp);
  if (reveal > 0) { sticker('glass', 540, 760, 360, { t, alpha: reveal }); glassShards(540, 760, t, reveal); }
  if (t > Q.glass + 0.4) card('زجاج', 540, 560, { t, alpha: pop(t, Q.glass + 0.4).a, scale: pop(t, Q.glass + 0.4).s, font: 'cairo', size: 64, edge: C.coral, rot: -0.03 });
}
function sLesson(t) {
  drawBg('bg_interior', 1.5, 0.5, 0.2, 'rgba(30,43,74,0.30)');
  const a = pop(t, Q.lesson), b = pop(t, Q.lesson + 1.0);
  card('خبرة في الطوب', 540, 620, { t, alpha: a.a, scale: a.s, font: 'cairo', size: 58, rot: -0.03 });
  card('خبرة في الجواهر', 540, 1000, { t, alpha: b.a, scale: b.s, font: 'cairo', size: 58, rot: 0.02 });
  if (t > Q.lesson + 1.4) {
    // hand-drawn "not equal" sign (the Arabic font has no ≠ glyph)
    const p = pop(t, Q.lesson + 1.4); ctx.save(); ctx.globalAlpha = p.a; ctx.translate(540, 812); ctx.scale(p.s, p.s);
    ctx.strokeStyle = C.coral; ctx.lineCap = 'round'; ctx.lineWidth = 16;
    ctx.beginPath(); ctx.moveTo(-60, -22); ctx.lineTo(60, -22); ctx.moveTo(-60, 22); ctx.lineTo(60, 22); ctx.moveTo(26, -64); ctx.lineTo(-26, 64); ctx.stroke(); ctx.restore();
  }
}
function sWorkshop(t) {
  drawBg('bg_interior', 1.12, 0.6, 0.5, 'rgba(255,190,140,0.08)');
  [[250, 420], [520, 360], [790, 420]].forEach(([x, y], i) => sticker('shield', x, y, 210, { t, alpha: pop(t, Q.restart + 0.2 + i * 0.25).a }));
  sticker('sec_armorer', 300, 1400, 560, { t, anchor: 'bottom', alpha: pop(t, Q.restart + 0.3).a });
  sticker('p_scribe', 800, 1400, 520, { t, anchor: 'bottom', alpha: pop(t, Q.restart + 0.5).a });
  if (t > Q.funded) { const m = easeInOut(prog(stepT(t), Q.funded + 0.2, Q.funded + 1.0)); sticker('coin_bag', lerp(760, 380, m), 980 - Math.sin(m * Math.PI) * 90, 150, { t }); }
  if (t > Q.reinvest) {
    const a = pop(t, Q.reinvest).a; sticker('jar', 540, 1130, 200, { t, alpha: a });
    loopArrows(540, 1100, 190, t, a);
    for (let i = 0; i < 3; i++) { const t0 = Q.reinvest + 0.5 + i * 0.6; const m = prog(stepT(t), t0, t0 + 0.6); if (m > 0 && m < 1) coin(540 + Math.cos(-Math.PI * 0.9 + m * 2.6) * 190, 1100 + Math.sin(-Math.PI * 0.9 + m * 2.6) * 190, 26, t, 'r' + i); }
  }
}
function sYears(t) {
  drawBg('bg_interior', 1.08, 0.5, 0.5);
  sticker('sec_mentor', 330, 1420, 520, { t, anchor: 'bottom', alpha: 1 - 0.6 * prog(t, Q.estate + 0.3, Q.estate + 1.2) });
  sticker('p_rich_pouch', 760, 1420, 560, { t, anchor: 'bottom' });
  sticker('tablets', 540, 1180, 220, { t });
  const n = Math.floor(1 + 4 * prog(t, Q.years, Q.grow));             // jars added gradually, one per season of light
  for (let i = 0; i < n; i++) sticker('jar', 200 + i * 170, 1560 - i * 6, 130 + i * 14, { t, alpha: pop(t, Q.years + i * (Q.grow - Q.years) / 4).a });
  yearLight(t, Q.years, Q.grow);
  if (t > Q.estate) card('نصيب من التركة', 540, 520, { t, alpha: pop(t, Q.estate + 0.3).a, scale: pop(t, Q.estate + 0.3).s, size: 50, fill: C.cream });
}
function sGrow(t) {
  drawBg('bg_street', 1.1, 0.5, 0.45, 'rgba(255,220,160,0.10)');
  for (let i = 0; i < 5; i++) sticker('jar', 160 + i * 190, 1240, 150 + i * 10, { t });
  [['بالتعلّم', Q.learnW, 470], ['بالصبر', Q.patience, 690], ['بالفرص', Q.chance, 910]].forEach(([w, t0, y], i) => {
    const p = pop(t, t0); card(w, 540, y, { t, alpha: p.a, scale: p.s, font: 'cairo', size: 62, fill: [C.cream, C.mustard, C.paper][i], rot: (i - 1) * 0.03 });
  });
}
function sQuestion(t) {
  drawBg('bg_street', 1.06, 0.5, 0.5);
  sticker('p_facing', 540, 1400, 780, { t, anchor: 'bottom' });
  const q = pop(t, Q.ask2, 0.5);
  card('هل عرفت من أنا؟', 540, 300, { t, alpha: q.a, scale: q.s, font: 'cairo', size: 76, fill: C.mustard, rot: -0.02 });
  const c = prog(t, Q.write + 1.6, Q.write + 2.1);
  card('مستوحاة من كتاب «أغنى رجل في بابل»', 540, 1745, { t, alpha: c, font: 'cairo', size: 32, fill: C.paper });
}

// scene list (start cue, draw); each scene runs until the next one, joined by paper-page turns
const SCENES = [
  [0, sOpening], [Q.scribe - 0.2, sScribe], [Q.ask - 0.2, sTenth], [Q.save - 0.2, sJewels], [Q.back - 0.1, sGlass],
  [Q.lost2 - 0.1, sLesson], [Q.restart - 0.2, sWorkshop], [Q.years - 0.2, sYears], [Q.grow - 0.2, sGrow], [Q.now - 0.2, sQuestion],
];
const TURN = 0.45;
function pageTurn(t, A, B, t0) {                     // page-turn: the new page slides in from the right edge with a curl shadow
  const p = easeInOut(prog(t, t0, t0 + TURN)); A(t);
  const x = W * (1 - p);
  ctx.save(); ctx.beginPath(); ctx.rect(x, 0, W - x + 2, H); ctx.clip(); ctx.translate((1 - p) * 40, 0); B(t); ctx.restore();
  const g = ctx.createLinearGradient(x - 60, 0, x + 10, 0);
  g.addColorStop(0, 'rgba(30,20,8,0)'); g.addColorStop(1, 'rgba(30,20,8,0.35)'); ctx.fillStyle = g; ctx.fillRect(x - 60, 0, 70, H);
  ctx.fillStyle = '#FFFDF7'; ctx.fillRect(x - 4, 0, 8, H);
}
function renderFrame(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); shadowOff(); ctx.globalAlpha = 1;
  let i = 0; while (i + 1 < SCENES.length && t >= SCENES[i + 1][0]) i++;
  if (i > 0 && t < SCENES[i][0] + TURN) pageTurn(t, SCENES[i - 1][1], SCENES[i][1], SCENES[i][0]); else SCENES[i][1](t);
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.22; ctx.drawImage(GRAIN, 0, 0, W, H); ctx.restore();
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(10,8,6,0.36)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  captions(t);
  if (TIMELINE.provisional) { ctx.save(); ctx.font = '700 26px sans-serif'; ctx.fillStyle = 'rgba(180,40,40,0.8)'; ctx.fillText('PROVISIONAL TIMING / PLACEHOLDER ART', 24, 40); ctx.restore(); }
}

window.READY = (async () => {
  await loadAll(NAMES);
  await Promise.all([document.fonts.load('800 60px Cairo', 'عربي'), document.fonts.load('700 50px Ruqaa', 'عربي')]);
  makeGrain();
  window.renderFrame = renderFrame; window.DURATION = DURATION; window.FPS = FPS;
  const q = new URLSearchParams(location.search); renderFrame(parseFloat(q.get('t') || '0'));
  return true;
})();
