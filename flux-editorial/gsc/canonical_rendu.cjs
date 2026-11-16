// Compare le canonical/meta robots du HTML brut avec ceux du DOM après exécution JS (Chromium).
// Usage : node canonical_rendu.js <fichier_urls> > rendu.json
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const urls = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean);
  const b = await chromium.launch(); const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' });
  const out = [];
  for (const u of urls) {
    const p = await ctx.newPage(); let raw = '', status = 0;
    try {
      const r = await p.goto(u, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000); status = r.status(); raw = await r.text();
      const rawCanon = [...raw.matchAll(/<link[^>]+rel=["']canonical["'][^>]*href=["']([^"']+)/gi)].map(m => m[1]);
      const dom = await p.evaluate(() => ({ canon: [...document.querySelectorAll('link[rel=canonical]')].map(l => l.href), robots: [...document.querySelectorAll('meta[name=robots],meta[name=googlebot]')].map(m => m.content), h1: document.querySelectorAll('h1').length }));
      out.push({ url: u, status, rawCanon, domCanon: dom.canon, robots: dom.robots, h1: dom.h1, identique: JSON.stringify(rawCanon) === JSON.stringify(dom.canon) });
    } catch (e) { out.push({ url: u, erreur: String(e) }); }
    await p.close();
  }
  await b.close(); console.log(JSON.stringify(out, null, 1));
})();
