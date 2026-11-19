const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
  await p.goto(process.argv[2], { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const cdp = await ctx.newCDPSession(p); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  const { root } = await cdp.send('DOM.getDocument', { depth: -1 });
  const { nodeIds } = await cdp.send('DOM.querySelectorAll', { nodeId: root.nodeId, selector: process.argv[3] });
  const m = await cdp.send('CSS.getMatchedStylesForNode', { nodeId: nodeIds[nodeIds.length - 1] });
  for (const r of m.matchedCSSRules) { const c = r.rule.style.cssProperties.filter(x => /^(color|background(-color)?)$/.test(x.name) && x.value); if (c.length) console.log(r.rule.selectorList.text, '=>', c.map(x => x.name + ':' + x.value).join('; ')); }
  console.log('computed', await p.$$eval(process.argv[3], e => { const s = getComputedStyle(e[e.length - 1]); return s.color + ' / ' + s.backgroundColor; }));
  await b.close();
})();
