const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
  await p.addInitScript(() => {
    window.__ls = []; window.__h = [];
    new PerformanceObserver(l => l.getEntries().forEach(e => window.__ls.push({ t: Math.round(e.startTime), v: +e.value.toFixed(4), src: (e.sources || []).map(s => (s.node && (s.node.className || s.node.nodeName)) + ' ' + JSON.stringify(s.previousRect) + '->' + JSON.stringify(s.currentRect)) }))).observe({ type: 'layout-shift', buffered: true });
    const tick = () => { const f = document.querySelector('.forminator-custom-form, form.forminator-ui'); const a = document.querySelector('.aside'); if (f) window.__h.push([Math.round(performance.now()), f.offsetHeight, a && Math.round(a.getBoundingClientRect().top + scrollY), getComputedStyle(f).display]); if (performance.now() < 8000) setTimeout(tick, 100); }; document.addEventListener('DOMContentLoaded', tick);
  });
  await p.goto(process.argv[2], { waitUntil: 'load' }); await p.waitForTimeout(6000);
  const r = await p.evaluate(() => ({ ls: window.__ls, h: window.__h.filter((x, i, a) => i === 0 || x[1] !== a[i - 1][1] || x[2] !== a[i - 1][2]) }));
  console.log(JSON.stringify(r, null, 0)); await b.close();
})();
