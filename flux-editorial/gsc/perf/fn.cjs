const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('https://fluxintelligent.com/ia/devis/?fn=1', { waitUntil: 'load' }); await p.waitForTimeout(3000);
  const devis = await p.evaluate(() => { const a = document.getElementById('fdi-app'); const i = a && a.querySelector('input,textarea,button'); return { app: !!a, visible: !!(a && a.offsetHeight > 100), control: !!i, inlineCss: document.querySelectorAll("style[id$='-inline-file']").length }; });
  await p.goto('https://fluxintelligent.com/?fn=1', { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const nav = await p.evaluate(() => { const t = document.querySelector('[aria-controls][data-mega], .nav-toggle, button[aria-expanded]'); if (t) t.click(); return { toggle: !!t, expanded: t && t.getAttribute('aria-expanded') }; });
  const font = await p.evaluate(async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + f.weight).slice(0, 8); });
  await p.goto('https://fluxintelligent.com/ia/automatisation-ia-casablanca/?fn=1', { waitUntil: 'load' }); await p.waitForTimeout(2000);
  const casa = await p.evaluate(async () => { await document.fonts.ready; const h = document.querySelector('h1'); return { h1font: getComputedStyle(h).fontFamily, loaded: [...document.fonts].filter(f => f.status === 'loaded' && /Grotesk|Public/.test(f.family)).map(f => f.family + ' ' + f.weight) }; });
  console.log(JSON.stringify({ devis, nav, font, casa, errs }, null, 1)); await b.close();
})();
