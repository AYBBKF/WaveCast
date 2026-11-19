const { chromium, devices } = require('playwright');
const CSS = process.argv[3] || '';
(async () => {
  const b = await chromium.launch();
  for (const [dn, dev] of [['mobile', devices['Pixel 5']], ['desktop', { viewport: { width: 1366, height: 900 } }]]) {
    let tot = [];
    for (let i = 0; i < 3; i++) {
      const ctx = await b.newContext({ ...dev }); const p = await ctx.newPage();
      await p.route(u => u.href.includes('__never__'), async r => { const resp = await r.fetch(); let body = await resp.text(); body = body.replace('</head>', '<style id="fi-cls-test">' + CSS + '</style></head>'); r.fulfill({ response: resp, body }); });
      await p.addInitScript(() => { window.__cls = 0; window.__src = []; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) { window.__cls += e.value; window.__src.push((e.sources || []).map(s => s.node && s.node.className).join('|')); } })).observe({ type: 'layout-shift', buffered: true }); });
      await p.goto(process.argv[2] + '&i=' + i, { waitUntil: 'load' }); await p.waitForTimeout(5000);
      const r = await p.evaluate(() => ({ cls: +window.__cls.toFixed(4), src: window.__src, ph: !!document.querySelector('.formcard > .forminator-ui[data-form]') }));
      tot.push(r); await ctx.close();
    }
    console.log(dn, JSON.stringify(tot));
  }
  await b.close();
})();
