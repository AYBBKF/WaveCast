const { chromium, devices } = require('playwright');
const CSS = process.argv[2] || '';
const P = ['/ia/automatisation-ia-casablanca/', '/ia/agence-ia-rabat/', '/ia/automatisation-ia-marrakech/', '/automatisation-ia-tanger/', '/automatisation-ia-fes/', '/automatisation-ia-agadir/', '/ia/automatisation-ia-oujda/', '/automatisation-ia-meknes/', '/ia/automatisation-ia-tetouan/', '/rejoignez-nous/'];
const lum = c => { const m = c.match(/\d+(\.\d+)?/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]); };
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] });
  for (const u of P) {
    const p = await ctx.newPage(); await p.goto('https://fluxintelligent.com' + u + '?ct=1', { waitUntil: 'load' });
    if (CSS) { await p.addStyleTag({ content: CSS }); await p.waitForTimeout(1200); }
    const r = await p.$$eval('a.btn', els => els.map(e => { const s = getComputedStyle(e); let bg = s.backgroundColor, n = e; while (bg === 'rgba(0, 0, 0, 0)' && n.parentElement) { n = n.parentElement; bg = getComputedStyle(n).backgroundColor; } return [e.className, e.innerText.trim().slice(0, 30), s.color, bg]; }));
    const bad = r.map(([c, t, fg, bg]) => { const a = lum(fg), b2 = lum(bg); const ratio = (Math.max(a, b2) + .05) / (Math.min(a, b2) + .05); return [c, t, fg, bg, +ratio.toFixed(2)]; }).filter(x => x[4] < 4.5);
    console.log(u, 'boutons', r.length, 'contraste<4.5:', JSON.stringify(bad)); await p.close();
  }
  await b.close();
})();
