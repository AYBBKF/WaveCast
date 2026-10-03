// Vector stand-ins for DOT (GPT) and OPUS (Claude), drawn to the written character spec:
// DOT: green interwoven knot body; OPUS: coral radial starburst body. Both: large white eyes,
// expressive eyebrows, thin black limbs, white gloves, black shoes. Mouths are animated from audio.
'use strict';
const INK = '#1d1b1a';
const PAL = {
  DOT: { fill: '#22a37c', light: '#58c7a0', dark: '#11624a', lid: '#1f9670' },
  OPUS: { fill: '#e07a55', light: '#f2a07f', dark: '#9a4428', lid: '#d26d49' },
};

function knotBody(ctx, R, p) {          // three interlaced capsules -> "interwoven knot" rosette
  const L = R * 1.05, Wd = R * 0.36;
  const caps = [0, Math.PI / 3, 2 * Math.PI / 3];
  const capsule = a => { ctx.save(); ctx.rotate(a); ctx.beginPath(); ctx.roundRect(-L, -Wd, 2 * L, 2 * Wd, Wd); ctx.restore(); };
  ctx.lineJoin = 'round';
  caps.forEach(a => { capsule(a); ctx.fillStyle = p.fill; ctx.fill(); });
  // weave: each capsule's outline is drawn, then the next capsule's fill covers one crossing
  caps.forEach((a, i) => {
    capsule(a); ctx.lineWidth = R * 0.07; ctx.strokeStyle = INK; ctx.stroke();
    ctx.save(); ctx.rotate(caps[(i + 1) % 3]); ctx.beginPath(); ctx.roundRect(L * 0.15, -Wd + R * 0.035, L * 0.6, 2 * Wd - R * 0.07, Wd * 0.6);
    ctx.fillStyle = p.fill; ctx.fill(); ctx.restore();
  });
  caps.forEach(a => { ctx.save(); ctx.rotate(a); ctx.beginPath(); ctx.roundRect(-L * 0.92, -Wd * 0.55, L * 0.5, Wd * 0.28, Wd * 0.14); ctx.fillStyle = p.light; ctx.globalAlpha = 0.55; ctx.fill(); ctx.restore(); });
  // ribbon bands: two lines along each lobe, broken where another band passes over -> reads as an interlaced knot
  ctx.lineWidth = R * 0.035; ctx.strokeStyle = p.dark; ctx.lineCap = 'round';
  caps.forEach((a, i) => {
    ctx.save(); ctx.rotate(a);
    [-1, 1].forEach(e => {
      [-1, 1].forEach(sd => {
        const x0 = sd * R * 0.6, x1 = sd * (L - Wd * 0.9);
        ctx.beginPath(); ctx.moveTo(x0, e * Wd * 0.42); ctx.lineTo(x1, e * Wd * 0.42); ctx.stroke();
      });
    });
    ctx.restore();
  });
  ctx.beginPath(); ctx.arc(0, 0, R * 0.6, 0, Math.PI * 2); ctx.fillStyle = p.fill; ctx.fill();   // face plate
  ctx.beginPath(); ctx.arc(0, 0, R * 0.6, 0, Math.PI * 2); ctx.lineWidth = R * 0.035; ctx.strokeStyle = p.dark; ctx.globalAlpha = 0.55; ctx.stroke(); ctx.globalAlpha = 1;
}
function burstBody(ctx, R, p, t) {      // rounded radial starburst
  const n = 12, ri = R * 0.66;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const a0 = (i / n) * Math.PI * 2 - Math.PI / 2, a1 = ((i + 0.5) / n) * Math.PI * 2 - Math.PI / 2, a2 = ((i + 1) / n) * Math.PI * 2 - Math.PI / 2;
    const tipR = R * (1 + 0.015 * Math.sin(t * 3 + i));
    if (i === 0) ctx.moveTo(Math.cos(a0) * ri, Math.sin(a0) * ri);
    ctx.quadraticCurveTo(Math.cos(a1 - 0.09) * tipR * 1.02, Math.sin(a1 - 0.09) * tipR * 1.02, Math.cos(a1) * tipR, Math.sin(a1) * tipR);
    ctx.quadraticCurveTo(Math.cos(a1 + 0.09) * tipR * 1.02, Math.sin(a1 + 0.09) * tipR * 1.02, Math.cos(a2) * ri, Math.sin(a2) * ri);
  }
  ctx.closePath(); ctx.fillStyle = p.fill; ctx.fill(); ctx.lineWidth = R * 0.07; ctx.lineJoin = 'round'; ctx.strokeStyle = INK; ctx.stroke();
  ctx.beginPath(); ctx.arc(-R * 0.18, -R * 0.2, R * 0.5, Math.PI * 1.05, Math.PI * 1.45); ctx.lineWidth = R * 0.06; ctx.strokeStyle = p.light; ctx.globalAlpha = 0.7; ctx.stroke(); ctx.globalAlpha = 1;
}

// arm poses: [elbow, hand] offsets from the shoulder in body radii (right arm; mirrored for left)
const ARM = {
  down: [[0.25, 0.45], [0.35, 0.95]], hip: [[0.55, 0.25], [0.25, 0.55]], up: [[0.2, -0.55], [0.35, -1.15]],
  point: [[0.6, -0.15], [1.2, -0.3]], shrug: [[0.55, 0.05], [0.95, -0.35]], cross: [[0.35, 0.4], [-0.35, 0.35]],
  present: [[0.6, 0.15], [1.15, -0.1]], raise: [[0.45, -0.45], [0.6, -1.0]], cheek: [[0.55, 0.2], [0.15, -0.05]],
  wave: [[0.6, -0.4], [0.95, -0.95]],
};
function glove(ctx, x, y, r, a, finger) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(a);
  ctx.lineWidth = r * 0.22; ctx.strokeStyle = INK; ctx.fillStyle = '#fff';
  if (finger) { ctx.beginPath(); ctx.roundRect(r * 0.55, -r * 0.28, r * 1.05, r * 0.56, r * 0.28); ctx.fill(); ctx.stroke(); }
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.arc(-r * 0.15, -r * 0.85, r * 0.38, 0, Math.PI * 2); ctx.fill(); ctx.stroke();   // thumb
  ctx.beginPath(); ctx.moveTo(-r * 0.6, r * 0.75); ctx.lineTo(r * 0.6, r * 0.75); ctx.lineWidth = r * 0.12; ctx.stroke();     // cuff line
  ctx.restore();
}
function lerpPose(a, b, k) { return a.map((p, i) => [p[0] + (b[i][0] - p[0]) * k, p[1] + (b[i][1] - p[1]) * k]); }

/* o: x, y (feet baseline), s (scale), kind, t, lean, squash, browL, browR (raise, -1..1), browTilt (+angry, -worried),
      eyeOpen (0..1), look [dx,dy], mouth (0..1 open), mood ('smile','flat','frown','grin','smug'),
      armL, armR (pose names), armBlend {fromL, fromR, k} optional, fingerL, fingerR, face (-1 left .. 1 right turn) */
function drawMascot(ctx, o) {
  const p = PAL[o.kind], s = o.s, R = 150 * s, t = o.t || 0;
  const breathe = 1 + 0.012 * Math.sin(t * 2.4 + (o.kind === 'DOT' ? 0 : 1.3));
  const sq = o.squash || 0;
  const bodyY = o.y - R - 175 * s;
  ctx.save(); ctx.translate(o.x, 0);
  // ground shadow
  ctx.beginPath(); ctx.ellipse(0, o.y + 6 * s, R * 0.95, R * 0.16, 0, 0, Math.PI * 2); ctx.fillStyle = 'rgba(60,45,30,0.13)'; ctx.fill();
  ctx.translate(0, bodyY); ctx.rotate(o.lean || 0);
  const lift = -(o.hop || 0) * R;
  ctx.translate(0, lift);
  // legs + shoes
  ctx.lineCap = 'round'; ctx.strokeStyle = INK; ctx.lineWidth = 8 * s;
  [-1, 1].forEach(d => {
    const hx = d * R * 0.32, hy = R * 0.75, fx = d * R * 0.45, fy = R + 175 * s - 18 * s - lift;
    ctx.beginPath(); ctx.moveTo(hx, hy); ctx.quadraticCurveTo(d * R * 0.42, (hy + fy) / 2, fx, fy); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(fx + d * 18 * s, fy + 6 * s, 40 * s, 19 * s, d * 0.08, 0, Math.PI * 2); ctx.fillStyle = INK; ctx.fill();
    ctx.beginPath(); ctx.ellipse(fx + d * 28 * s, fy - 2 * s, 12 * s, 5 * s, 0, 0, Math.PI * 2); ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fill();
  });
  // arms (behind body for 'down'/'hip', in front otherwise)
  const arms = [['L', -1], ['R', 1]].map(([k, d]) => {
    let pose = ARM[o['arm' + k] || 'down'];
    const bl = o.armBlend && o.armBlend['from' + k] ? lerpPose(ARM[o.armBlend['from' + k]], pose, o.armBlend.k) : pose;
    return { d, pose: bl, finger: o['finger' + k], front: !['down', 'hip'].includes(o['arm' + k] || 'down') };
  });
  const drawArm = a => {
    const sx = a.d * R * 0.78, sy = R * 0.12;
    const ex = sx + a.d * a.pose[0][0] * R, ey = sy + a.pose[0][1] * R, hx = sx + a.d * a.pose[1][0] * R, hy = sy + a.pose[1][1] * R;
    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(ex, ey, hx, hy); ctx.lineWidth = 8 * s; ctx.strokeStyle = INK; ctx.stroke();
    const ang = Math.atan2(hy - ey, hx - ex);
    glove(ctx, hx, hy, 24 * s, a.finger ? ang : ang + (a.d < 0 ? Math.PI : 0) * 0, a.finger);
  };
  arms.filter(a => !a.front).forEach(drawArm);
  // body
  ctx.save(); ctx.scale(breathe * (1 + sq * 0.12), breathe * (1 - sq * 0.12));
  if (o.kind === 'DOT') knotBody(ctx, R, p); else burstBody(ctx, R, p, t);
  ctx.restore();
  // face
  const fx = (o.face || 0) * R * 0.12, fyy = -R * 0.08;
  ctx.save(); ctx.translate(fx, fyy);
  const eo = Math.max(0.05, o.eyeOpen ?? 1), look = o.look || [0, 0];
  [-1, 1].forEach(d => {
    const ex = d * R * 0.3, ey = -R * 0.1, rx = R * 0.22, ry = R * 0.3 * (o.eyeScale || 1);
    ctx.beginPath(); ctx.ellipse(ex, ey, rx, ry, 0, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = R * 0.045; ctx.strokeStyle = INK; ctx.stroke();
    ctx.save(); ctx.beginPath(); ctx.ellipse(ex, ey, rx, ry, 0, 0, Math.PI * 2); ctx.clip();
    const px = ex + look[0] * rx * 0.45, py = ey + look[1] * ry * 0.4 + ry * 0.12;
    ctx.beginPath(); ctx.arc(px, py, R * 0.1, 0, Math.PI * 2); ctx.fillStyle = INK; ctx.fill();
    ctx.beginPath(); ctx.arc(px - R * 0.035, py - R * 0.04, R * 0.032, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill();
    // eyelid (blink / half-lidded)
    const lidH = 2 * ry * (1 - eo);
    if (lidH > 0.5) { ctx.fillStyle = p.lid; ctx.fillRect(ex - rx - 2, ey - ry - 2, 2 * rx + 4, lidH + 2); ctx.beginPath(); ctx.moveTo(ex - rx, ey - ry + lidH); ctx.lineTo(ex + rx, ey - ry + lidH); ctx.lineWidth = R * 0.04; ctx.strokeStyle = INK; ctx.stroke(); }
    ctx.restore();
    // eyebrow
    const raise = (d < 0 ? o.browL : o.browR) || 0, tilt = (o.browTilt || 0) * -d;
    const by = ey - ry - R * 0.12 - raise * R * 0.12;
    ctx.save(); ctx.translate(ex, by); ctx.rotate(tilt * 0.35);
    ctx.beginPath(); ctx.moveTo(-rx * 0.85, 0); ctx.quadraticCurveTo(0, -R * 0.06, rx * 0.85, 0); ctx.lineWidth = R * 0.075; ctx.lineCap = 'round'; ctx.strokeStyle = INK; ctx.stroke();
    ctx.restore();
  });
  // mouth
  const m = Math.max(0, Math.min(1, o.mouth || 0)), my = R * 0.33, mw = R * 0.24;
  if (m > 0.08) {
    const h = R * (0.05 + 0.24 * m), w = mw * (0.75 + 0.35 * m);
    ctx.beginPath(); ctx.ellipse(0, my + h * 0.35, w, h, 0, 0, Math.PI * 2); ctx.fillStyle = '#3a1712'; ctx.fill(); ctx.lineWidth = R * 0.04; ctx.strokeStyle = INK; ctx.stroke();
    ctx.save(); ctx.beginPath(); ctx.ellipse(0, my + h * 0.35, w, h, 0, 0, Math.PI * 2); ctx.clip();
    ctx.beginPath(); ctx.ellipse(0, my + h * 1.05, w * 0.7, h * 0.55, 0, 0, Math.PI * 2); ctx.fillStyle = '#e8737a'; ctx.fill(); ctx.restore();
  } else {
    const mood = o.mood || 'smile';
    const c = { smile: R * 0.09, grin: R * 0.14, flat: 0, frown: -R * 0.08, smug: R * 0.06 }[mood];
    ctx.beginPath(); ctx.moveTo(-mw, my); ctx.quadraticCurveTo(mood === 'smug' ? mw * 0.4 : 0, my + c, mw * (mood === 'smug' ? 0.9 : 1), my - (mood === 'smug' ? R * 0.05 : 0));
    ctx.lineWidth = R * 0.05; ctx.lineCap = 'round'; ctx.strokeStyle = INK; ctx.stroke();
  }
  ctx.restore();
  arms.filter(a => a.front).forEach(drawArm);
  ctx.restore();
}
