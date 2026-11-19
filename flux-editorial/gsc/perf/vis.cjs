const { chromium, devices } = require('playwright');
const fs = require('fs');
const P = ['/', '/ia/automatisation-ia-casablanca/', '/ia/contact/', '/agents-ia/', '/automatisation-ia-pme-maroc/', '/ia/devis/'];
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const [dn, dev] of [['mobile', devices['Pixel 5']], ['desktop', { viewport: { width: 1366, height: 900 } }]]) {
    for (const p of P) {
      const shots = {};
      for (const v of ['A', 'B']) {
        const ctx = await b.newContext({ ...dev, deviceScaleFactor: 1 });
        const pg = await ctx.newPage();
        const u = 'https://fluxintelligent.com' + p + (v === 'B' ? '?fi_inline=1' : '?fi_ref=1');
        await pg.goto(u, { waitUntil: 'load', timeout: 60000 }); await pg.waitForTimeout(2500);
        await pg.evaluate(() => document.querySelectorAll('video,iframe').forEach(e => e.style.visibility = 'hidden'));
        const info = await pg.evaluate(() => ({ h: document.documentElement.scrollHeight, links: document.querySelectorAll("link[rel=stylesheet]").length, inl: document.querySelectorAll("style[id$='-inline-file']").length, forms: document.querySelectorAll('form').length, h1: (document.querySelector('h1')||{}).innerText }));
        shots[v] = { buf: await pg.screenshot({ fullPage: false }), info };
        fs.writeFileSync(`shot-${dn}-${p.replace(/\W+/g, '_')}-${v}.png`, shots[v].buf);
        await ctx.close();
      }
      out.push({ dn, p, A: shots.A.info, B: shots.B.info, same_bytes: shots.A.buf.equals(shots.B.buf) });
    }
  }
  await b.close(); console.log(JSON.stringify(out, null, 0));
})();
