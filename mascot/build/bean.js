// BEAN — vector model of the channel mascot (concept B: terracotta bean with a cream asterisk).
// Everything is drawn in a fixed 1000x1000 "body frame"; only face parts, arms and small
// extras change between poses, so the silhouette and facial placement never move.
//   drawBean(ctx, pose)        pose = POSES.neutral or any object with the same fields
//   renderSticker(name, size)  -> { cutout, diecut } canvases (transparent backgrounds)
(function (root) {
  const PAL = {
    terra: '#C96442', coral: '#EA8A6C', blush: '#E57B60', cream: '#F6E9D7',
    ink: '#2B1D17', tongue: '#EE9A7E', drop: '#BFE0EE', white: '#FFFFFF',
  };
  const LW = 10;                                   // master outline weight (body frame units)
  const EYE = { L: [468, 398], R: [578, 392], rx: 16, ry: 26 };
  const MOUTH = [528, 468];
  const MARK = [470, 262];                         // forehead asterisk
  const CHEEK = { L: [438, 455], R: [620, 448] };
  const SHOULDER = { L: [402, 545], R: [680, 545] };

  function bodyPath(ctx) {
    ctx.beginPath();
    ctx.moveTo(520, 165);
    ctx.bezierCurveTo(625, 160, 688, 235, 688, 355);
    ctx.bezierCurveTo(688, 470, 705, 560, 695, 650);
    ctx.bezierCurveTo(685, 760, 595, 805, 510, 800);
    ctx.bezierCurveTo(408, 795, 342, 730, 348, 640);
    ctx.bezierCurveTo(354, 560, 402, 522, 398, 452);
    ctx.bezierCurveTo(394, 385, 342, 335, 362, 255);
    ctx.bezierCurveTo(380, 190, 450, 168, 520, 165);
    ctx.closePath();
  }

  function stroke(ctx, w, col) {
    ctx.lineWidth = w; ctx.strokeStyle = col || PAL.ink;
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
  }
  function dot(ctx, x, y, r, col) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); }

  // Limb: [start, elbow, hand]; smooth quadratic through the elbow.
  function limb(ctx, pts, hand) {
    const [a, b, c] = pts;
    ctx.beginPath(); ctx.moveTo(a[0], a[1]);
    const mx = 2 * b[0] - (a[0] + c[0]) / 2, my = 2 * b[1] - (a[1] + c[1]) / 2;
    ctx.quadraticCurveTo(mx, my, c[0], c[1]);
    stroke(ctx, LW);
    if (hand !== false) dot(ctx, c[0], c[1], 11, PAL.ink);
  }

  function legs(ctx) {
    ctx.beginPath(); ctx.moveTo(478, 780); ctx.lineTo(474, 880); ctx.lineTo(452, 884); stroke(ctx, LW);
    ctx.beginPath(); ctx.moveTo(562, 782); ctx.lineTo(566, 880); ctx.lineTo(588, 884); stroke(ctx, LW);
  }

  function asterisk(ctx) {
    const [x, y] = MARK;
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 3;
      ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a) * 30, y + Math.sin(a) * 30);
    }
    stroke(ctx, 19, PAL.cream);
  }

  function eye(ctx, side, type, look) {
    const [cx0, cy0] = EYE[side];
    const [lx, ly] = look || [0, 0];
    const cx = cx0 + lx, cy = cy0 + ly, m = side === 'L' ? -1 : 1;
    const oval = (rx, ry) => { ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); ctx.fillStyle = PAL.ink; ctx.fill(); };
    const shine = (r) => dot(ctx, cx + 5, cy - 9, r, PAL.white);
    switch (type) {
      case 'open': oval(EYE.rx, EYE.ry); shine(4.5); break;
      case 'wide': oval(EYE.rx + 4, EYE.ry + 7); shine(6); break;
      case 'half': case 'flat': {
        const lid = type === 'half' ? cy0 - 3 : cy0 + 1;
        ctx.save(); ctx.beginPath(); ctx.rect(cx0 - 40, lid, 80, 80); ctx.clip();
        oval(EYE.rx, EYE.ry); ctx.restore();
        ctx.beginPath(); ctx.moveTo(cx0 - 21, lid + (type === 'half' ? m * 2 : 0)); ctx.lineTo(cx0 + 21, lid - (type === 'half' ? m * 2 : 0));
        stroke(ctx, 8);
        break;
      }
      case 'happy':
        ctx.beginPath(); ctx.moveTo(cx0 - 17, cy0 + 8); ctx.quadraticCurveTo(cx0, cy0 - 22, cx0 + 17, cy0 + 8);
        stroke(ctx, 9); break;
      case 'squeeze':
        ctx.beginPath(); ctx.moveTo(cx0 + m * 15, cy0 - 13); ctx.lineTo(cx0 - m * 12, cy0); ctx.lineTo(cx0 + m * 15, cy0 + 13);
        stroke(ctx, 9); break;
    }
  }

  // Brow: offsets (inner, outer) from the resting line; arch > 0 bows it upward.
  function brow(ctx, side, inner, outer, arch) {
    const [cx, cy] = EYE[side], m = side === 'L' ? 1 : -1, y = cy - 50;
    const xi = cx + m * 19, xo = cx - m * 19;
    ctx.beginPath(); ctx.moveTo(xo, y + outer);
    ctx.quadraticCurveTo(cx, y + (inner + outer) / 2 - (arch || 0), xi, y + inner);
    stroke(ctx, 9);
  }

  function mouth(ctx, type) {
    const [x, y] = MOUTH;
    const openShape = (path, tongueY, tongueR) => {
      path(); ctx.fillStyle = PAL.ink; ctx.fill();
      ctx.save(); path(); ctx.clip();
      ctx.beginPath(); ctx.ellipse(x + 4, tongueY, tongueR, tongueR * 0.7, 0, 0, Math.PI * 2); ctx.fillStyle = PAL.tongue; ctx.fill();
      ctx.restore(); path(); stroke(ctx, 8);
    };
    ctx.beginPath();
    switch (type) {
      case 'smile': ctx.moveTo(x - 24, y - 3); ctx.quadraticCurveTo(x, y + 16, x + 24, y - 5); stroke(ctx, 9); break;
      case 'smirk':
        ctx.moveTo(x - 22, y + 4); ctx.quadraticCurveTo(x + 6, y + 12, x + 30, y - 12); stroke(ctx, 9);
        ctx.beginPath(); ctx.moveTo(x + 26, y - 20); ctx.quadraticCurveTo(x + 36, y - 12, x + 33, y - 2); stroke(ctx, 6); break;
      case 'flat': ctx.moveTo(x - 22, y + 8); ctx.quadraticCurveTo(x, y + 1, x + 22, y + 9); stroke(ctx, 9); break;
      case 'pursed': ctx.moveTo(x - 2, y + 6); ctx.quadraticCurveTo(x + 12, y + 1, x + 24, y + 4); stroke(ctx, 9); break;
      case 'wobble':
        ctx.moveTo(x - 24, y + 4);
        ctx.quadraticCurveTo(x - 16, y - 4, x - 8, y + 4); ctx.quadraticCurveTo(x, y + 12, x + 8, y + 4);
        ctx.quadraticCurveTo(x + 16, y - 4, x + 24, y + 4); stroke(ctx, 8); break;
      case 'o':
        ctx.ellipse(x, y + 12, 14, 20, 0, 0, Math.PI * 2); ctx.fillStyle = PAL.ink; ctx.fill(); break;
      case 'laugh':
        openShape(() => { ctx.beginPath(); ctx.moveTo(x - 40, y - 6); ctx.quadraticCurveTo(x, y - 12, x + 40, y - 8);
          ctx.bezierCurveTo(x + 40, y + 40, x + 14, y + 58, x - 2, y + 58); ctx.bezierCurveTo(x - 22, y + 58, x - 42, y + 38, x - 40, y - 6); ctx.closePath(); }, y + 52, 26);
        break;
      case 'talk':
        openShape(() => { ctx.beginPath(); ctx.moveTo(x - 24, y - 2); ctx.quadraticCurveTo(x, y - 6, x + 24, y - 3);
          ctx.bezierCurveTo(x + 26, y + 26, x + 10, y + 36, x, y + 36); ctx.bezierCurveTo(x - 12, y + 36, x - 26, y + 24, x - 24, y - 2); ctx.closePath(); }, y + 34, 16);
        break;
    }
  }

  function cheeks(ctx, mode) {
    if (!mode) return;
    const big = mode === 'hot';
    for (const s of ['L', 'R']) {
      const [x, y] = CHEEK[s];
      ctx.beginPath(); ctx.ellipse(x, y, big ? 34 : 24, big ? 19 : 13, 0, 0, Math.PI * 2);
      ctx.fillStyle = big ? '#E46A55' : PAL.blush; ctx.fill();
      if (big) for (let i = -1; i <= 1; i++) {
        ctx.beginPath(); ctx.moveTo(x + i * 14 - 5, y + 8); ctx.lineTo(x + i * 14 + 5, y - 8); stroke(ctx, 5);
      }
    }
  }

  function drop(ctx, x, y, s) {
    ctx.beginPath(); ctx.moveTo(x, y - 30 * s);
    ctx.bezierCurveTo(x + 6 * s, y - 14 * s, x + 18 * s, y - 2 * s, x + 18 * s, y + 10 * s);
    ctx.arc(x, y + 10 * s, 18 * s, 0, Math.PI, false);
    ctx.bezierCurveTo(x - 18 * s, y - 2 * s, x - 6 * s, y - 14 * s, x, y - 30 * s);
    ctx.closePath(); ctx.fillStyle = PAL.drop; ctx.fill(); stroke(ctx, 7);
  }

  function extras(ctx, list) {
    for (const e of list || []) {
      if (e === 'laughLines') {
        for (const [x1, y1, x2, y2] of [[320, 330, 290, 312], [310, 380, 276, 380], [320, 430, 290, 448],
                                         [720, 300, 750, 282], [728, 350, 762, 350]]) {
          ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); stroke(ctx, 9);
        }
      } else if (e === 'shockLines') {
        for (const [x1, y1, x2, y2] of [[440, 140, 425, 98], [520, 128, 520, 82], [600, 140, 617, 98]]) {
          ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); stroke(ctx, 10);
        }
      } else if (e === 'sweat') drop(ctx, 712, 278, 1);
      else if (e === 'sweatSmall') drop(ctx, 368, 330, 0.8);
      else if (e === 'vein') {
        const [x, y] = [626, 262];
        for (let q = 0; q < 4; q++) {
          const a = q * Math.PI / 2 + Math.PI / 4, ox = Math.cos(a) * 15, oy = Math.sin(a) * 15;
          ctx.beginPath(); ctx.arc(x + ox * 1.6, y + oy * 1.6, 13, a + Math.PI * 0.72, a + Math.PI * 1.28); stroke(ctx, 8, '#9E3B22');
        }
      } else if (e === 'thinkDots') {
        for (const [x, y, r] of [[724, 262, 10], [762, 206, 15], [812, 138, 21]]) {
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = PAL.cream; ctx.fill(); stroke(ctx, 7);
        }
      }
    }
  }

  function drawBean(ctx, p) {
    ctx.save();
    for (const a of p.arms.filter(a => !a.front)) limb(ctx, a.pts, a.hand);
    legs(ctx);
    bodyPath(ctx); ctx.fillStyle = PAL.terra; ctx.fill(); stroke(ctx, LW);
    asterisk(ctx);
    cheeks(ctx, p.cheeks);
    eye(ctx, 'L', p.eyes, p.look); eye(ctx, 'R', p.eyesR || p.eyes, p.look);
    brow(ctx, 'L', ...p.browL); brow(ctx, 'R', ...p.browR);
    mouth(ctx, p.mouth);
    for (const a of p.arms.filter(a => a.front)) limb(ctx, a.pts, a.hand);
    extras(ctx, p.extras);
    ctx.restore();
  }

  const DOWN_L = { pts: [SHOULDER.L, [330, 625], [318, 702]] };
  const DOWN_R = { pts: [SHOULDER.R, [736, 625], [748, 702]] };
  const POSES = {
    neutral: { eyes: 'open', browL: [0, 2, 3], browR: [0, 2, 3], mouth: 'smile', cheeks: 'soft', arms: [DOWN_L, DOWN_R] },
    smug: { eyes: 'half', look: [5, 2], browL: [6, 6, 0], browR: [-14, -20, 6], mouth: 'smirk', cheeks: 'soft',
      arms: [{ pts: [SHOULDER.L, [312, 600], [356, 668]] }, DOWN_R] },
    laughing: { eyes: 'happy', browL: [-10, -4, 4], browR: [-10, -4, 4], mouth: 'laugh', cheeks: 'soft', extras: ['laughLines'],
      arms: [{ front: true, pts: [[384, 585], [430, 650], [500, 650]] }, { pts: [SHOULDER.R, [758, 478], [772, 396]] }] },
    shocked: { eyes: 'wide', browL: [-24, -20, 6], browR: [-24, -20, 6], mouth: 'o', extras: ['shockLines', 'sweat'],
      arms: [{ pts: [SHOULDER.L, [318, 478], [326, 388]] }, { pts: [SHOULDER.R, [764, 470], [752, 382]] }] },
    annoyed: { eyes: 'flat', look: [-3, 0], browL: [14, -4, 0], browR: [14, -4, 0], mouth: 'flat', extras: ['vein'],
      arms: [{ front: true, pts: [[384, 575], [470, 628], [615, 588]] }, { front: true, pts: [[696, 575], [598, 632], [452, 600]] }] },
    thinking: { eyes: 'open', look: [6, -7], browL: [4, 4, 0], browR: [-14, -22, 5], mouth: 'pursed', cheeks: 'soft', extras: ['thinkDots'],
      arms: [{ front: true, pts: [[384, 600], [470, 655], [622, 612]] }, { front: true, pts: [[697, 590], [650, 600], [566, 520]] }] },
    embarrassed: { eyes: 'squeeze', browL: [-10, 4, 0], browR: [-10, 4, 0], mouth: 'wobble', cheeks: 'hot', extras: ['sweat'],
      arms: [{ front: true, pts: [[384, 610], [432, 690], [514, 694]] }, { front: true, pts: [[697, 610], [636, 692], [544, 694]] }] },
    talking: { eyes: 'open', browL: [-6, -8, 4], browR: [-6, -8, 4], mouth: 'talk', cheeks: 'soft',
      arms: [DOWN_L, { pts: [SHOULDER.R, [784, 575], [806, 486]] }] },
  };
  const ORDER = ['neutral', 'smug', 'laughing', 'shocked', 'annoyed', 'thinking', 'embarrassed', 'talking'];

  // Same transform for every sticker: the bean always occupies the same pixels.
  function renderSticker(name, size, border) {
    const k = size / 1000 * 0.98;
    const cut = document.createElement('canvas'); cut.width = cut.height = size;
    const c = cut.getContext('2d');
    c.setTransform(k, 0, 0, k, size / 2 - 540 * k, size / 2 - 485 * k);   // bean + limbs centred in frame
    drawBean(c, POSES[name]);
    const die = document.createElement('canvas'); die.width = die.height = size;
    const d = die.getContext('2d'), R = border || size * 0.022;
    for (const rr of [R, R * 0.75, R * 0.5, R * 0.25])
      for (let i = 0; i < 64; i++) { const a = i / 64 * Math.PI * 2; d.drawImage(cut, Math.cos(a) * rr, Math.sin(a) * rr); }
    d.globalCompositeOperation = 'source-in'; d.fillStyle = PAL.white; d.fillRect(0, 0, size, size);
    d.globalCompositeOperation = 'destination-over';               // faint contact shadow behind the die-cut
    d.filter = `blur(${size * 0.006}px)`; d.globalAlpha = 0.18; d.drawImage(die, 0, size * 0.008);
    d.filter = 'none'; d.globalAlpha = 1; d.globalCompositeOperation = 'source-over';
    d.drawImage(cut, 0, 0);
    return { cutout: cut, diecut: die };
  }

  root.BEAN = { PAL, POSES, ORDER, drawBean, renderSticker };
})(typeof window !== 'undefined' ? window : globalThis);
