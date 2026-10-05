// 3x3 storyboard contact sheet for the Petra Reel: code-drawn paper-cut planning sketch.
'use strict';
const { PAL, piece, tracing, backdrop, cliff, facade, urnTomb, artisan, tool, forearm, chips, jordanMap, city, rect, rng } = PAPER;
const PW = 420, PH = 746, G = 34, HEAD = 200, FOOT = 92;
const SW = 3 * PW + 4 * G, SH = HEAD + 3 * (PH + FOOT) + G;
const cv = document.getElementById('c'); cv.width = SW; cv.height = SH;
const ctx = cv.getContext('2d');

// Arabic caption on a torn parchment strip (RTL, Cairo).
function caption(text, y = PH - 120, size = 34) {
  ctx.save(); ctx.direction = 'rtl'; ctx.textAlign = 'center';
  ctx.font = `700 ${size}px Cairo`;
  while (ctx.measureText(text).width > PW - 90 && size > 18) { size -= 1; ctx.font = `700 ${size}px Cairo`; }   // fit inside the panel
  const w = ctx.measureText(text).width + 50;
  piece(ctx, rect(PW / 2 - w / 2, y - size * 0.95, w, size * 1.7), PAL.parch, { seed: text.length * 7, border: 3, amp: 2 });
  ctx.fillStyle = PAL.navy; ctx.textBaseline = 'middle'; ctx.fillText(text, PW / 2, y - size * 0.1);
  ctx.restore();
}
function label(text, x, y, size = 24, col = PAL.navy, align = 'center') {
  ctx.save(); ctx.font = `700 ${size}px Cairo`; ctx.direction = 'rtl'; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.lineWidth = 6; ctx.strokeStyle = 'rgba(255,253,247,0.9)'; ctx.strokeText(text, x, y); ctx.fillStyle = col; ctx.fillText(text, x, y); ctx.restore();
}
function plate(text, x, y, size = 24, fill = PAL.parch, col = PAL.navy) {
  ctx.save(); ctx.font = `700 ${size}px Cairo`; ctx.direction = 'rtl';
  const w = ctx.measureText(text).width + size * 1.2;
  piece(ctx, rect(x - w / 2, y - size * 0.85, w, size * 1.6), fill, { seed: text.length * 13 + size, border: 2.5, amp: 1.5 });
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = col; ctx.fillText(text, x, y); ctx.restore();
}
function arrowDown(x, y0, y1, col = PAL.navy) {        // code-drawn explanatory arrow
  ctx.save(); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 9; ctx.lineCap = 'round';
  ctx.setLineDash([2, 16]); ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y1 - 26); ctx.stroke(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(x - 20, y1 - 30); ctx.lineTo(x, y1); ctx.lineTo(x + 20, y1 - 30); ctx.closePath(); ctx.fill(); ctx.restore();
}
function sky(seed) { backdrop(ctx, 0, 0, PW, PH, PAL.parch, seed); }

// facade framing shared by panels 2, 4, 6, 9 (same viewpoint/scale/layout)
const FX = 70, FY = 150, FW = 280, FH = 420;
function cliffAround(seed) { cliff(ctx, -20, 40, PW + 40, PH, seed, { strata: 8 }); }

const PANELS = [
  { t: '0–3 s', title: 'Hook', note: 'Rough cliff fills frame; artisan strikes; a chip falls.', draw() {
      sky(1); cliffAround(11);
      tracing(ctx, rect(FX, FY, FW, FH), 5, 0.22);                          // ghost of the facade to come
      artisan(ctx, 110, 600, 200, 'strike', 81);
      chips(ctx, [[180, 430, 1.2], [196, 490, 0.8], [176, 540, 0.6]], 3, 9);
      label('؟', 300, 300, 120, PAL.navy);
      caption('تخيّل أن تصنع واجهة كاملة…');
    } },
  { t: '3–10 s', title: 'Transformation', note: 'Sandstone paper layers peel away; facade appears, still joined to the cliff.', draw() {
      sky(2); cliffAround(11);
      facade(ctx, FX, FY, FW, FH, 0.62, { seed: 21 });
      const r = rng(9);                                                      // layers peeling off
      for (let k = 0; k < 3; k++) {
        ctx.save(); ctx.translate(250 + k * 40, 430 + k * 30); ctx.rotate(0.25 + k * 0.18);
        piece(ctx, rect(-70, -40, 140 - k * 20, 90 - k * 10), [PAL.rose, PAL.roseDk, PAL.terra][k], { seed: 30 + k, amp: 4, border: 3 });
        ctx.restore();
      }
      caption('هذا ما فعله الأنباط');
    } },
  { t: '10–16 s', title: 'The tools', note: 'Adult hands: hammer + chisel, controlled removal, chips and tool marks. Map inset: Petra, Jordan.', draw() {
      sky(3); cliff(ctx, -20, 0, PW + 40, PH + 40, 12, { strata: 9 });
      ctx.save(); ctx.strokeStyle = 'rgba(110,50,35,0.45)'; ctx.lineWidth = 3;
      for (let k = 0; k < 18; k++) { const x = 60 + (k % 6) * 50, y = 360 + Math.floor(k / 6) * 40; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 12, y + 18); ctx.stroke(); }
      ctx.restore();
      // big adult hands (close-up)
      tool(ctx, 'chisel', 262, 470, Math.PI + 0.42, 5.4, 42);                    // chisel tip on the rock face
      forearm(ctx, PW + 30, 600, 268, 486, 64, 41, 1);                            // chisel hand (shadowed)
      tool(ctx, 'hammer', 286, 336, -2.2, 4.4, 44);                              // hammer about to strike the chisel head
      forearm(ctx, PW + 30, 200, 300, 318, 60, 43, 0);
      chips(ctx, [[140, 500, 1.4], [120, 560, 1], [170, 600, 0.8], [100, 620, 0.7]], 5, 10);
      const m = jordanMap(ctx, 24, 40, 150, 121);
      label('الأردن', m.jordan[0], m.jordan[1] - 6, 20); label('البتراء', m.petra[0] + 6, m.petra[1] + 26, 18, PAL.terra);
      caption('بالمطارق والأزاميل');
    } },
  { t: '16–23 s', title: 'Top-down', note: 'Unfinished facade: detailed top, rough bottom. Code arrow: commonly inferred top-down order.', draw() {
      sky(4); cliffAround(11);
      facade(ctx, FX, FY, FW, FH, 0.45, { seed: 21 });
      arrowDown(385, 170, 520, PAL.navy);
      artisan(ctx, 330, 600, 130, 'chisel', 81, -1);
      caption('بدأوا من الأعلى… ثم نزلوا');
    } },
  { t: '23–31 s', title: 'Architecture emerges', note: 'Close-up column freed from stone, then pull back: artisan small beside the facade.', draw() {
      sky(5); cliff(ctx, -20, 0, PW + 40, 390, 13, { strata: 6 });
      piece(ctx, rect(150, 40, 120, 300), PAL.roseLt, { seed: 51, border: 3 });          // emerging column (close-up)
      piece(ctx, rect(130, 30, 160, 34), PAL.rose, { seed: 52, border: 3 });
      piece(ctx, [[150, 200], [270, 190], [290, 340], [130, 340]], PAL.rose, { seed: 53, amp: 5, border: 3 }); // stone still wrapping it
      chips(ctx, [[120, 250, 1.2], [300, 270, 1], [110, 320, 0.8]], 7, 9);
      piece(ctx, rect(20, 400, PW - 40, 3), PAL.white, { seed: 54, border: 0, shadow: false });
      cliff(ctx, 20, 410, PW - 40, 270, 14, { strata: 5 });                                // pull-back inset
      facade(ctx, 150, 440, 120, 180, 0.8, { seed: 21 });
      artisan(ctx, 120, 622, 46, 'look', 81);
      caption('ضربة بعد ضربة', PH - 46, 32);
    } },
  { t: '31–39 s', title: 'Finished reveal', note: 'Warm light sweeps the finished facade; slow push toward the doorway.', draw() {
      sky(6); cliffAround(11);
      facade(ctx, FX, FY, FW, FH, 1, { seed: 21 });
      ctx.save(); ctx.globalCompositeOperation = 'soft-light'; const g = ctx.createLinearGradient(0, 0, PW, PH);
      g.addColorStop(0.25, 'rgba(255,220,150,0)'); g.addColorStop(0.45, 'rgba(255,215,140,0.75)'); g.addColorStop(0.6, 'rgba(255,220,150,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, PW, PH); ctx.restore();
      ctx.save(); ctx.setLineDash([10, 8]); ctx.lineWidth = 4; ctx.strokeStyle = PAL.white;  // camera target
      ctx.strokeRect(FX + 0.32 * FW, FY + 0.55 * FH, 0.36 * FW, 0.42 * FH); ctx.restore();
      caption('واجهة مدهشة');
    } },
  { t: '39–47 s', title: 'Tomb twist', note: 'Urn Tomb (documented), then restrained schematic cutaway. No bodies. Word: مقابر.', draw() {
      backdrop(ctx, 0, 0, PW, PH, PAL.navy, 7);
      urnTomb(ctx, 60, 50, 300, 330, 61);
      plate('قبر الجرّة', PW / 2, 404, 22);
      // schematic cutaway: facade thickness | doorway | carved hall behind
      piece(ctx, rect(40, 430, 340, 170), PAL.rose, { seed: 71, border: 3 });
      piece(ctx, rect(150, 455, 210, 120), PAL.parchDk, { seed: 72, border: 2 });      // hall carved into the rock
      piece(ctx, rect(60, 455, 30, 145), PAL.roseLt, { seed: 73, border: 2 });         // facade slab
      piece(ctx, rect(90, 520, 60, 55), PAL.navy, { seed: 74, border: 2 });            // doorway passage
      for (const x of [175, 240, 305]) piece(ctx, rect(x, 470, 40, 22), PAL.roseDk, { seed: x, border: 1.5 }); // wall recesses (schematic)
      plate('تصوّر مبسّط', 300, 598, 19, PAL.mustard);
      label('مقابر', PW / 2, 676, 64, PAL.mustard);
    } },
  { t: '47–55 s', title: 'Living city', note: 'Rock-cut tombs on the cliff + freestanding houses, market and temple on the valley floor.', draw() {
      sky(8);
      city(ctx, 0, 120, PW, 520, 141);
      artisan(ctx, 250, 610, 80, 'stand', 81);
      caption('بيوت وأسواق ومعابد');
    } },
  { t: '55–65 s', title: 'Payoff & loop', note: 'Rough cliff overlaid on the facade, then revealed again; final question; ends on the opening frame.', draw() {
      sky(9); cliffAround(11);
      facade(ctx, FX, FY, FW, FH, 1, { seed: 21 });
      ctx.save(); ctx.beginPath(); ctx.rect(PW / 2, 0, PW / 2, PH); ctx.clip();       // half wipe back to raw rock
      cliff(ctx, -20, 40, PW + 40, PH, 11, { strata: 8 }); ctx.restore();
      tracing(ctx, rect(PW / 2 - 4, 120, 8, 470), 3, 0.9);
      caption('أيّهما أصعب في رأيك؟');
    } },
];

(async () => {
  await document.fonts.load('700 30px Cairo');
  backdrop(ctx, 0, 0, SW, SH, PAL.kraft, 99);
  ctx.save(); ctx.fillStyle = PAL.navy; ctx.font = '700 46px Cairo'; ctx.direction = 'rtl'; ctx.textAlign = 'right';
  ctx.fillText('كيف نحت الأنباط واجهات البتراء؟', SW - G, 62);
  ctx.direction = 'ltr'; ctx.textAlign = 'left'; ctx.font = '600 24px Cairo';
  ctx.fillText('DEEP CURIOUS · Petra Reel · Storyboard v1 · 9 panels, timings provisional', G, 108);
  ctx.fillStyle = '#7A2E1E'; ctx.fillText('Code-drawn paper-cut planning sketch: NOT GPT Image 2.5 output (Higgsfield balance 0)', G, 140);
  ctx.fillStyle = PAL.navy; ctx.font = '500 20px Cairo';
  ctx.fillText('Facade geometry shared by panels 2, 4, 6, 9 (same viewpoint, scale, layout). Carving sequence = simplified illustrative reconstruction.', G, 172);
  ctx.restore();
  PANELS.forEach((p, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = G + col * (PW + G), y = HEAD + row * (PH + FOOT);
    ctx.save(); ctx.shadowColor = 'rgba(40,25,15,0.35)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6; ctx.fillStyle = PAL.white;
    ctx.fillRect(x - 8, y - 8, PW + 16, PH + 16); ctx.restore();
    ctx.save(); ctx.translate(x, y); ctx.beginPath(); ctx.rect(0, 0, PW, PH); ctx.clip(); p.draw(); ctx.restore();
    ctx.save(); ctx.fillStyle = PAL.navy; ctx.font = '700 25px Cairo'; ctx.textBaseline = 'top';
    ctx.fillText(`${i + 1} · ${p.t} · ${p.title}`, x, y + PH + 14);
    ctx.font = '500 18px Cairo'; ctx.fillStyle = '#3B3A44';
    const words = p.note.split(' '); let line = '', ly = y + PH + 46;
    for (const w of words) { const t = line ? line + ' ' + w : w; if (ctx.measureText(t).width > PW) { ctx.fillText(line, x, ly); line = w; ly += 22; } else line = t; }
    ctx.fillText(line, x, ly); ctx.restore();
  });
  window.DONE = true;
})();
