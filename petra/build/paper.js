// Paper-cut collage kit for the Petra Reel (DEEP CURIOUS).
// Handmade look in code: irregular cut edges, white cutout borders, soft drop shadows, paper grain,
// fibres, watercolour blooms and crayon hatching. Every scene element is drawn from ONE geometry,
// so carving stages share viewpoint, scale and layout (the facade never redesigns itself).
(function (root) {
  const PAL = {
    parch: '#F3E7CF', parchDk: '#E6D3B0', kraft: '#C9A77C', kraftDk: '#A88459',
    rose: '#D99A82', roseLt: '#EBC0AA', roseDk: '#B8735F', roseXd: '#8E5444',
    terra: '#B85B3E', mustard: '#D9A441', mustardDk: '#B7832A', teal: '#5E8C88', tealDk: '#45706C',
    navy: '#1F2A44', ink: '#2A2320', white: '#FFFDF7', skin: '#C98E6B', skinDk: '#A9714F', hair: '#5A3A26',
  };

  let BOIL = 0;                                         // stop-motion edge variant (0 for stills)
  const setBoil = b => { BOIL = b | 0; };

  // ---------- deterministic randomness ----------
  function rng(seed) {
    let a = (seed * 2654435761) >>> 0 || 1;
    return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }

  // Hand-cut edge: subdivide each edge and jitter it sideways.
  function wobble(pts, seed, amp = 3, step = 14) {
    const r = rng(seed), out = [];
    for (let i = 0; i < pts.length; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length];
      const L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(1, Math.round(L / step));
      const nx = -(y1 - y0) / (L || 1), ny = (x1 - x0) / (L || 1);
      for (let k = 0; k < n; k++) {
        const t = k / n, j = k === 0 ? 0 : (r() - 0.5) * 2 * amp;
        out.push([x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j]);
      }
    }
    return out;
  }
  const poly = (ctx, pts) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); };
  const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
  const PAPER_ELL = (cx, cy, rx, ry) => { const p = []; for (let i = 0; i < 22; i++) { const a = i / 22 * Math.PI * 2; p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); } return p; };
  const ellipsePts = (cx, cy, rx, ry, n = 28, a0 = 0, a1 = Math.PI * 2) => { const p = []; for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); } return p; };

  // ---------- textures ----------
  let GRAIN = null;
  function grain() {
    if (GRAIN) return GRAIN;
    const c = document.createElement('canvas'); c.width = c.height = 360;
    const g = c.getContext('2d'), r = rng(7), img = g.createImageData(360, 360);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 200 + r() * 55; img.data[i] = v; img.data[i + 1] = v * 0.97; img.data[i + 2] = v * 0.92; img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    for (let k = 0; k < 160; k++) {                      // paper fibres
      g.beginPath(); let x = r() * 360, y = r() * 360; g.moveTo(x, y);
      for (let s = 0; s < 4; s++) { x += (r() - 0.5) * 26; y += (r() - 0.5) * 26; g.lineTo(x, y); }
      g.strokeStyle = r() < 0.5 ? 'rgba(255,255,255,0.55)' : 'rgba(120,95,70,0.25)'; g.lineWidth = 0.6 + r(); g.stroke();
    }
    GRAIN = c; return c;
  }
  function texture(ctx, x, y, w, h, seed, opts = {}) {
    const r = rng(seed);
    ctx.save();
    ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = opts.grain ?? 0.33;
    ctx.fillStyle = ctx.createPattern(grain(), 'repeat'); ctx.fillRect(x - 10, y - 10, w + 20, h + 20);
    ctx.globalAlpha = 1;
    for (let k = 0; k < (opts.blooms ?? 3); k++) {        // watercolour / gouache blooms
      const bx = x + r() * w, by = y + r() * h, br = Math.max(w, h) * (0.25 + r() * 0.4);
      const gr = ctx.createRadialGradient(bx, by, 0, bx, by, br);
      gr.addColorStop(0, `rgba(${opts.bloom || '120,60,40'},${0.08 + r() * 0.08})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = gr; ctx.fillRect(x, y, w, h);
    }
    ctx.globalCompositeOperation = 'source-over';
    const hatch = opts.hatch ?? 1;                       // crayon strokes
    ctx.lineCap = 'round';
    for (let k = 0; k < (w * h / 900) * hatch; k++) {
      const hx = x + r() * w, hy = y + r() * h, L = 6 + r() * 16;
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx + L * 0.8, hy - L * 0.6);
      ctx.strokeStyle = r() < 0.6 ? 'rgba(90,40,25,0.07)' : 'rgba(255,240,220,0.10)'; ctx.lineWidth = 1 + r() * 1.6; ctx.stroke();
    }
    ctx.restore();
  }

  // A cut-paper piece: soft shadow + irregular white border + fill + texture.
  function piece(ctx, pts, fill, o = {}) {
    // BOIL shifts only the cut edges (stop-motion jitter); texture seeds stay fixed so nothing flickers
    const seed = o.seed ?? 1, w = wobble(pts, seed + BOIL * 7919, o.amp ?? 2.4, o.step ?? 14);
    const xs = w.map(p => p[0]), ys = w.map(p => p[1]);
    const bx = Math.min(...xs), by = Math.min(...ys), bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
    ctx.save();
    if (o.shadow !== false) { ctx.shadowColor = 'rgba(40,25,15,' + (o.shadowA ?? 0.28) + ')'; ctx.shadowBlur = o.blur ?? 10; ctx.shadowOffsetX = o.sx ?? 3; ctx.shadowOffsetY = o.sy ?? 5; }
    if (o.border !== 0) {                               // irregular white cutout border
      const wb = wobble(pts, seed + 99 + BOIL * 7919, (o.amp ?? 2.4) + 1.2, o.step ?? 14);
      poly(ctx, wb); ctx.lineJoin = 'round'; ctx.lineWidth = 2 * (o.border ?? 4); ctx.strokeStyle = o.borderColor || PAL.white; ctx.stroke();
      ctx.fillStyle = o.borderColor || PAL.white; ctx.fill();
    }
    ctx.shadowColor = 'transparent';
    poly(ctx, w); ctx.fillStyle = fill; ctx.globalAlpha = o.alpha ?? 1; ctx.fill();
    if (o.tex !== false) { ctx.clip(); texture(ctx, bx, by, bw, bh, seed + 5, o.texOpts || {}); }
    ctx.restore();
    return w;
  }
  // Translucent tracing-paper overlay.
  function tracing(ctx, pts, seed, a = 0.45) {
    const w = wobble(pts, seed, 2, 18);
    ctx.save(); poly(ctx, w); ctx.fillStyle = `rgba(250,246,236,${a})`; ctx.fill();
    ctx.lineWidth = 1.5; ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.stroke(); ctx.restore();
  }

  // ---------- background paper ----------
  function backdrop(ctx, x, y, w, h, color = PAL.parch, seed = 3) {
    ctx.save(); ctx.fillStyle = color; ctx.fillRect(x, y, w, h);
    ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); texture(ctx, x, y, w, h, seed, { grain: 0.4, blooms: 4, bloom: '150,110,70', hatch: 0.3 }); ctx.restore();
  }

  // ---------- cliff (rough sandstone with strata) ----------
  function cliff(ctx, x, y, w, h, seed = 11, o = {}) {
    const r = rng(seed);
    const top = [], n = 9;
    for (let i = 0; i <= n; i++) top.push([x + w * i / n, y + (r() * 0.08 + (i % 3 === 1 ? 0.03 : 0)) * h]);
    const pts = [...top, [x + w, y + h], [x, y + h]];
    piece(ctx, pts, o.fill || PAL.rose, { seed, amp: 5, step: 22, border: o.border ?? 0, texOpts: { blooms: 6, bloom: '150,60,40', hatch: 1.4 } });
    ctx.save(); poly(ctx, pts); ctx.clip();
    const bands = [PAL.roseLt, PAL.terra, PAL.roseDk, PAL.mustard, PAL.roseXd];
    for (let k = 0; k < (o.strata ?? 7); k++) {          // wavy coloured sandstone strata
      const by = y + h * (0.1 + k * 0.13 + r() * 0.04), amp = 6 + r() * 10, th = 6 + r() * 16;
      ctx.beginPath(); ctx.moveTo(x - 10, by);
      for (let sx = 0; sx <= w + 20; sx += 30) ctx.lineTo(x + sx, by + Math.sin(sx / 70 + k) * amp);
      for (let sx = w + 20; sx >= 0; sx -= 30) ctx.lineTo(x + sx, by + th + Math.sin(sx / 60 + k * 2) * amp);
      ctx.closePath(); ctx.globalAlpha = 0.22 + r() * 0.15; ctx.fillStyle = bands[k % bands.length]; ctx.fill();
    }
    ctx.restore();
    return pts;
  }

  // ---------- the facade (generic Petra-style, Khazneh-like two-storey rock-cut facade) ----------
  // Geometry in a unit box (0..1 x 0..1); stage = fraction carved from the TOP down (0 = rough rock, 1 = finished).
  function facade(ctx, X, Y, W, H, stage = 1, o = {}) {
    const P = (u, v) => [X + u * W, Y + v * H];
    const R = (u, v, du, dv) => rect(X + u * W, Y + v * H, du * W, dv * H);
    const seed = o.seed ?? 21;
    // recess cut back into the cliff
    piece(ctx, [P(-0.06, -0.04), P(1.06, -0.04), P(1.06, 1.0), P(-0.06, 1.0)], PAL.roseXd, { seed, border: 0, shadow: false, amp: 4, texOpts: { blooms: 2, bloom: '60,20,10' } });
    const carved = () => {
      const L = PAL.roseLt, M = PAL.rose, D = PAL.roseDk, S = { border: 2.5, amp: 1.2, step: 10, blur: 6, sy: 3, sx: 2, shadowA: 0.3 };
      // --- upper storey (0.00 .. 0.46)
      piece(ctx, R(0.02, 0.36, 0.96, 0.06), M, { ...S, seed: seed + 1 });                 // upper base band
      // side broken pediments
      for (const [u, flip] of [[0.02, 1], [0.70, -1]]) {
        const a = flip > 0 ? P(u, 0.14) : P(u + 0.28, 0.14), b = flip > 0 ? P(u + 0.28, 0.07) : P(u, 0.07), c = flip > 0 ? P(u + 0.28, 0.14) : P(u, 0.14);
        piece(ctx, [a, b, c], L, { ...S, seed: seed + 2 + u * 10 });
        piece(ctx, R(u, 0.14, 0.28, 0.03), M, { ...S, seed: seed + 3 + u * 10 });
        for (const cu of [0.03, 0.2]) piece(ctx, R(u + cu, 0.17, 0.05, 0.19), L, { ...S, seed: seed + 4 + cu * 50 + u * 10 });
      }
      // central tholos with conical roof and urn finial
      piece(ctx, R(0.37, 0.15, 0.26, 0.21), L, { ...S, seed: seed + 8 });
      for (const cu of [0.39, 0.475, 0.56]) piece(ctx, R(cu, 0.17, 0.04, 0.19), M, { ...S, seed: seed + 9 + cu * 40, border: 1.5 });
      piece(ctx, [P(0.36, 0.15), P(0.50, 0.05), P(0.64, 0.15)], M, { ...S, seed: seed + 12 });
      piece(ctx, ellipsePts(X + 0.5 * W, Y + 0.035 * H, 0.03 * W, 0.022 * H, 14), L, { ...S, seed: seed + 13 });
      // --- lower storey (0.46 .. 1.0)
      piece(ctx, R(0.0, 0.42, 1.0, 0.05), L, { ...S, seed: seed + 14 });                    // entablature
      piece(ctx, [P(0.22, 0.47), P(0.5, 0.40), P(0.78, 0.47)], L, { ...S, seed: seed + 15 }); // central pediment
      for (const cu of [0.03, 0.18, 0.33, 0.62, 0.77, 0.92]) piece(ctx, R(cu - 0.025, 0.49, 0.055, 0.44), cu > 0.2 && cu < 0.8 ? L : M, { ...S, seed: seed + 16 + cu * 30 });
      piece(ctx, R(0.42, 0.62, 0.16, 0.31), PAL.navy, { ...S, seed: seed + 22, texOpts: { blooms: 1, bloom: '10,10,30' } }); // doorway
      piece(ctx, R(0.0, 0.93, 1.0, 0.035), L, { ...S, seed: seed + 23 });                   // steps
      piece(ctx, R(0.04, 0.965, 0.92, 0.035), M, { ...S, seed: seed + 24 });
    };
    if (stage > 0) {
      ctx.save(); ctx.beginPath(); ctx.rect(X - 0.1 * W, Y - 0.1 * H, 1.2 * W, (stage * 1.1) * H); ctx.clip(); carved(); ctx.restore();
    }
    if (stage < 1) {                                     // rough uncarved rock below the carving line
      const cy = Y + stage * H * 1.05 - 0.05 * H, r = rng(seed + 40), edge = [];
      for (let i = 0; i <= 12; i++) edge.push([X - 0.06 * W + 1.12 * W * i / 12, cy + (r() - 0.5) * 0.03 * H]);
      const rough = [...edge, [X + 1.06 * W, Y + 1.0 * H], [X - 0.06 * W, Y + 1.0 * H]];
      piece(ctx, rough, PAL.rose, { seed: seed + 41, amp: 4, step: 16, border: 3, texOpts: { blooms: 4, bloom: '140,60,40', hatch: 1.8 } });
      ctx.save(); poly(ctx, rough); ctx.clip();          // chisel tool marks on the working face
      ctx.strokeStyle = 'rgba(110,50,35,0.35)'; ctx.lineWidth = 2;
      for (let k = 0; k < 26; k++) { const tx = X + r() * W, ty = cy + 10 + r() * 0.12 * H; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(tx + 6, ty + 9); ctx.stroke(); }
      ctx.restore();
    }
  }

  // ---------- Urn Tomb (documented; simplified paper version) ----------
  function urnTomb(ctx, X, Y, W, H, seed = 61) {
    const P = (u, v) => [X + u * W, Y + v * H], R = (u, v, du, dv) => rect(X + u * W, Y + v * H, du * W, dv * H);
    const S = { border: 2.5, amp: 1.2, step: 10, blur: 6, sy: 3, sx: 2 };
    piece(ctx, R(-0.05, 0.0, 1.1, 1.0), PAL.roseXd, { seed, border: 0, shadow: false });
    piece(ctx, [P(0.12, 0.12), P(0.5, 0.03), P(0.88, 0.12)], PAL.roseLt, { ...S, seed: seed + 1 });   // pediment
    piece(ctx, ellipsePts(X + 0.5 * W, Y + 0.02 * H, 0.04 * W, 0.03 * H, 14), PAL.rose, { ...S, seed: seed + 2 }); // the urn
    piece(ctx, R(0.08, 0.12, 0.84, 0.10), PAL.rose, { ...S, seed: seed + 3 });                         // attic
    for (const u of [0.25, 0.45, 0.65]) piece(ctx, R(u, 0.14, 0.1, 0.06), PAL.roseDk, { ...S, seed: seed + 4 + u * 10, border: 1.5 }); // three niches
    piece(ctx, R(0.06, 0.22, 0.88, 0.40), PAL.rose, { ...S, seed: seed + 8 });
    for (const u of [0.08, 0.27, 0.66, 0.85]) piece(ctx, R(u, 0.23, 0.07, 0.38), PAL.roseLt, { ...S, seed: seed + 9 + u * 10 }); // engaged columns / pilasters
    piece(ctx, R(0.40, 0.40, 0.2, 0.22), PAL.navy, { ...S, seed: seed + 13 });                           // doorway
    piece(ctx, R(0.0, 0.62, 1.0, 0.06), PAL.roseLt, { ...S, seed: seed + 14 });                          // terrace
    for (const u of [0.05, 0.37, 0.69]) {                                                                // vaulted substructure
      piece(ctx, R(u, 0.70, 0.26, 0.30), PAL.roseDk, { ...S, seed: seed + 15 + u * 10 });
      piece(ctx, [...ellipsePts(X + (u + 0.13) * W, Y + 0.80 * H, 0.09 * W, 0.07 * H, 12, Math.PI, Math.PI * 2), P(u + 0.22, 1.0), P(u + 0.04, 1.0)], PAL.navy, { ...S, seed: seed + 18 + u * 10, border: 1.5 });
    }
  }

  // ---------- artisan (fictional Nabataean craftsman, ~35, adult proportions) ----------
  // pose: 'strike' (hammer raised), 'chisel' (both hands at the rock), 'stand', 'look' (looking up)
  // (x, y) = point between the feet; h = full height in px.
  function artisan(ctx, x, y, h, pose = 'stand', seed = 81, flip = 1) {
    const s = h / 100;                                    // 100 units tall; head ~13 units (adult ~7.5 heads)
    ctx.save(); ctx.translate(x, y - h); ctx.scale(s * flip, s);
    const S = { border: 1.6, amp: 0.6, step: 6, blur: 4, sy: 2, sx: 1 };
    // legs + sandals
    piece(ctx, rect(-7, 58, 6, 40), PAL.skinDk, { ...S, seed: seed + 1 });
    piece(ctx, rect(2, 58, 6, 40), PAL.skin, { ...S, seed: seed + 2 });
    piece(ctx, rect(-9, 96, 10, 4), PAL.kraftDk, { ...S, seed: seed + 3 }); piece(ctx, rect(1, 96, 10, 4), PAL.kraftDk, { ...S, seed: seed + 4 });
    // back arm
    const backArm = pose === 'strike' ? [[-9, 26], [-20, 16], [-16, 4], [-12, 6], [-15, 15], [-6, 22]] : [[-9, 26], [-14, 44], [-10, 46], [-5, 30]];
    piece(ctx, backArm, PAL.skinDk, { ...S, seed: seed + 5 });
    // tunic (mustard) + sash (muted teal)
    piece(ctx, [[-11, 22], [11, 22], [15, 62], [-15, 62]], PAL.mustard, { ...S, seed: seed + 6, texOpts: { bloom: '150,100,20', hatch: 1.5 } });
    piece(ctx, [[-13, 40], [13, 36], [14, 42], [-12, 46]], PAL.teal, { ...S, seed: seed + 7, texOpts: { bloom: '20,60,60' } });
    piece(ctx, [[6, 42], [11, 41], [9, 56], [5, 55]], PAL.tealDk, { ...S, seed: seed + 8 });
    // head: neck, face, brown hair, light stubble, beard line
    piece(ctx, rect(-3, 16, 6, 7), PAL.skinDk, { ...S, seed: seed + 9, border: 0 });
    const face = pose === 'look' ? ellipsePts(1, 8, 6.2, 7.6, 20) : ellipsePts(1, 9, 6.2, 7.8, 20);
    piece(ctx, face, PAL.skin, { ...S, seed: seed + 10 });
    piece(ctx, [[-6, 6], [-4, 1], [2, -0.5], [7, 2], [7.5, 6], [3, 4], [-2, 5], [-5, 9]], PAL.hair, { ...S, seed: seed + 11, border: 1 });
    ctx.save(); ctx.fillStyle = 'rgba(70,45,30,0.35)'; const r = rng(seed + 12);
    for (let k = 0; k < 40; k++) { ctx.beginPath(); ctx.arc(-2 + r() * 8, 11 + r() * 5, 0.35, 0, 7); ctx.fill(); } ctx.restore();   // stubble
    ctx.fillStyle = PAL.ink; ctx.beginPath(); ctx.ellipse(4, pose === 'look' ? 6.5 : 8, 0.8, 1.0, 0, 0, 7); ctx.fill();               // eye (profile-ish)
    ctx.strokeStyle = PAL.ink; ctx.lineWidth = 0.7; ctx.beginPath(); ctx.moveTo(3, 6); ctx.lineTo(6, 5.6); ctx.stroke();             // brow
    ctx.beginPath(); ctx.moveTo(4.5, 13.5); ctx.lineTo(6.5, 13.3); ctx.stroke();                                                      // mouth
    // front arm + tools
    if (pose === 'strike') {
      piece(ctx, [[8, 26], [20, 14], [24, 6], [27, 8], [24, 17], [12, 30]], PAL.skin, { ...S, seed: seed + 13 });
      tool(ctx, 'hammer', 26, 6, -0.6, 1);
    } else if (pose === 'chisel') {
      piece(ctx, [[8, 26], [22, 32], [26, 30], [27, 34], [20, 37], [8, 32]], PAL.skin, { ...S, seed: seed + 13 });
      tool(ctx, 'chisel', 28, 33, 0.15, 0.8);
    } else {
      piece(ctx, [[8, 26], [12, 44], [8, 46], [5, 30]], PAL.skin, { ...S, seed: seed + 13 });
    }
    ctx.restore();
  }

  function tool(ctx, kind, x, y, rot = 0, sc = 1, seed = 91) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc);
    const S = { border: 1.4, amp: 0.4, step: 5, blur: 3, sy: 2, sx: 1 };
    if (kind === 'hammer') {                              // wooden-handled iron hammer
      piece(ctx, rect(-1.2, -2, 2.4, 18), PAL.kraftDk, { ...S, seed });
      piece(ctx, rect(-6, -6, 12, 6), '#6E6A66', { ...S, seed: seed + 1, texOpts: { bloom: '30,30,40' } });
    } else {                                              // iron chisel
      piece(ctx, [[0, -1.4], [18, -1.0], [22, 0], [18, 1.0], [0, 1.4]], '#7D7873', { ...S, seed: seed + 2 });
      piece(ctx, rect(-6, -2.2, 7, 4.4), '#5E5955', { ...S, seed: seed + 3 });
    }
    ctx.restore();
  }

  // Close-up forearm (mustard sleeve) entering from (x0,y0) to a fist at (x1,y1).
  function forearm(ctx, x0, y0, x1, y1, w, seed = 131, shade = 0) {
    const a = Math.atan2(y1 - y0, x1 - x0), L = Math.hypot(x1 - x0, y1 - y0);
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(a);
    piece(ctx, [[-20, -w * 0.62], [L * 0.45, -w * 0.58], [L * 0.45, w * 0.58], [-20, w * 0.62]], shade ? PAL.mustardDk : PAL.mustard, { seed, border: 3, texOpts: { bloom: '150,100,20', hatch: 1.4 } });
    piece(ctx, [[L * 0.42, -w * 0.45], [L * 0.86, -w * 0.4], [L * 0.86, w * 0.4], [L * 0.42, w * 0.45]], shade ? PAL.skinDk : PAL.skin, { seed: seed + 1, border: 2.5 });
    piece(ctx, PAPER_ELL(L * 0.95, 0, w * 0.55, w * 0.5), shade ? PAL.skinDk : PAL.skin, { seed: seed + 2, border: 2.5 });
    ctx.strokeStyle = 'rgba(90,50,30,0.5)'; ctx.lineWidth = 2;
    for (let k = -1; k <= 1; k++) { ctx.beginPath(); ctx.moveTo(L * 0.98, k * w * 0.22); ctx.lineTo(L * 1.1, k * w * 0.22); ctx.stroke(); }  // knuckles
    ctx.restore();
  }

  // stone chips / fragments
  function chips(ctx, pts, seed = 101, size = 8) {
    const r = rng(seed);
    for (const [x, y, k] of pts) {
      const s = size * (0.6 + r() * 0.8) * (k ?? 1), n = 5 + Math.floor(r() * 3), p = [];
      for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2 + r() * 0.5; p.push([x + Math.cos(a) * s * (0.6 + r() * 0.5), y + Math.sin(a) * s * (0.6 + r() * 0.5)]); }
      piece(ctx, p, r() < 0.5 ? PAL.rose : PAL.roseLt, { seed: seed + x | 0, border: 1.2, amp: 0.5, step: 4, blur: 3, sy: 2 });
    }
  }

  // ---------- Jordan inset (simplified outline; Petra marked) ----------
  const JORDAN = [[35.0, 29.4], [36.0, 29.2], [36.8, 30.0], [37.9, 30.5], [37.0, 31.5], [39.2, 32.2], [38.8, 33.4], [36.8, 32.3], [35.8, 32.7], [35.55, 32.4], [35.55, 31.8], [35.4, 31.2], [35.2, 30.5]];
  function jordanMap(ctx, x, y, w, seed = 121) {
    const lon0 = 34.6, lat1 = 33.6, k = w / (39.6 - lon0);
    const pr = ([lo, la]) => [x + (lo - lon0) * k, y + (lat1 - la) * k];
    piece(ctx, rect(x, y, w, (lat1 - 29.0) * k), PAL.parch, { seed, border: 4 });
    piece(ctx, JORDAN.map(pr), PAL.kraft, { seed: seed + 1, border: 2.5, amp: 1, step: 8 });
    const [px, py] = pr([35.44, 30.33]);
    ctx.save(); ctx.beginPath(); ctx.arc(px, py, w * 0.035, 0, 7); ctx.fillStyle = PAL.terra; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = PAL.white; ctx.stroke(); ctx.restore();
    return { petra: [px, py], jordan: pr([36.9, 31.2]) };
  }

  // ---------- simplified living city ----------
  function city(ctx, X, Y, W, H, seed = 141) {
    const P = (u, v) => [X + u * W, Y + v * H], R = (u, v, du, dv) => rect(X + u * W, Y + v * H, du * W, dv * H);
    const S = { border: 2, amp: 1, step: 9, blur: 5, sy: 3, sx: 2 };
    // cliff on the right with small rock-cut tomb facades
    piece(ctx, [P(0.55, 0.0), P(1.0, 0.0), P(1.0, 0.75), P(0.62, 0.75), P(0.58, 0.4)], PAL.rose, { seed, amp: 5, step: 18, border: 0 });
    for (const [u, v] of [[0.66, 0.18], [0.80, 0.30], [0.70, 0.46]]) {
      piece(ctx, R(u, v, 0.1, 0.16), PAL.roseLt, { ...S, seed: seed + u * 100 });
      piece(ctx, R(u + 0.035, v + 0.08, 0.03, 0.08), PAL.navy, { ...S, seed: seed + v * 100, border: 1 });
    }
    // valley floor
    piece(ctx, [P(0.0, 0.62), P(1.0, 0.70), P(1.0, 1.0), P(0.0, 1.0)], PAL.kraft, { seed: seed + 3, border: 0 });
    // freestanding temple
    piece(ctx, R(0.08, 0.40, 0.26, 0.26), PAL.parchDk, { ...S, seed: seed + 4 });
    piece(ctx, [P(0.06, 0.40), P(0.21, 0.31), P(0.36, 0.40)], PAL.roseLt, { ...S, seed: seed + 5 });
    for (const u of [0.10, 0.16, 0.22, 0.28]) piece(ctx, R(u, 0.43, 0.025, 0.22), PAL.white, { ...S, seed: seed + 6 + u * 10, border: 1 });
    // houses (flat roofs) and market stalls with awnings
    for (const [u, v, w, h, c] of [[0.38, 0.55, 0.12, 0.12, PAL.parch], [0.48, 0.60, 0.10, 0.10, PAL.parchDk], [0.02, 0.68, 0.10, 0.10, PAL.parch]]) {
      piece(ctx, R(u, v, w, h), c, { ...S, seed: seed + u * 77 });
      piece(ctx, R(u + w * 0.35, v + h * 0.5, w * 0.25, h * 0.5), PAL.navy, { ...S, seed: seed + v * 77, border: 1 });
    }
    for (const [u, c] of [[0.18, PAL.terra], [0.30, PAL.teal], [0.42, PAL.mustard]]) {
      piece(ctx, R(u, 0.80, 0.1, 0.07), PAL.kraftDk, { ...S, seed: seed + u * 31 });
      piece(ctx, [P(u - 0.01, 0.80), P(u + 0.11, 0.80), P(u + 0.1, 0.76), P(u, 0.76)], c, { ...S, seed: seed + u * 53 });
    }
  }

  root.PAPER = { PAL, setBoil, rng, wobble, poly, rect, ellipsePts, piece, tracing, texture, backdrop, cliff, facade, urnTomb, artisan, tool, forearm, chips, jordanMap, city };
})(typeof window !== 'undefined' ? window : globalThis);
