// Comparaison locale de scénarios de balises (aucune modification en production).
// actuel | A3 = balise GT de Site Kit chargée via /0tqe/?id=GT-PZQ8SJ83 | A2 = config AW portée par le snippet passerelle et retirée de Site Kit | A = passerelle conservée, ligne gtag("config","AW-…") de Site Kit retirée | C = snippet injecté par la passerelle retiré
// Usage : NODE_PATH=$(npm root -g) node scenarios.cjs <url> <scenario> <runs>
const { chromium, devices } = require('playwright');
const RX = {
  A: /gtag\("config", "AW-18347114778"\);/,
  A2: /gtag\("config", "AW-18347114778"\);/,
  A3: /https:\/\/www\.googletagmanager\.com\/gtag\/js\?id=GT-PZQ8SJ83/,
  C: /<script>\(function\(w,i,g\)\{w\[g\]=w\[g\]\|\|\[\];[\s\S]*?google_tags_first_party'\);<\/script><script async src="\/0tqe\/"><\/script>\s*<script>[\s\S]*?developer_id\.dY2E1Nz', true\);\s*<\/script>/,
};
(async () => {
  const [url, sc, runs] = [process.argv[2], process.argv[3], +process.argv[4] || 3];
  const b = await chromium.launch(); const res = [];
  for (let i = 0; i < runs; i++) {
    const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
    const cdp = await ctx.newCDPSession(p); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 }); await cdp.send('Network.enable');
    let applied = sc === 'actuel', nReq = 0, jsTx = 0; const types = {};
    cdp.on('Network.responseReceived', e => { types[e.requestId] = e.type; });
    cdp.on('Network.loadingFinished', e => { nReq++; if (types[e.requestId] === 'Script') jsTx += e.encodedDataLength; });
    if (sc !== 'actuel') await p.route(u => u.href === url, async r => { const resp = await r.fetch(); let body = await resp.text(); if (RX[sc].test(body)) { body = body.replace(RX[sc], sc === 'A3' ? '/0tqe/?id=GT-PZQ8SJ83' : ''); applied = true; } if (sc === 'A2') { const before = body; body = body.replace("gtag('set', 'developer_id.dY2E1Nz', true);", "gtag('set', 'developer_id.dY2E1Nz', true); gtag('config', 'AW-18347114778');"); applied = applied && before !== body; } await r.fulfill({ response: resp, body }); });
    const hits = []; p.on('request', r => { const u = r.url(); if (/collect/.test(u)) hits.push(u.replace(/\?.*$/, '') + ((u.match(/[?&](tid|en)=[^&]+/g) || []).join(''))); });
    await p.addInitScript(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push([e.startTime, e.duration]))).observe({ type: 'longtask', buffered: true }); window.__cls = 0; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__cls += e.value })).observe({ type: 'layout-shift', buffered: true }); });
    await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 }); await p.waitForTimeout(5000);
    const m = await p.evaluate(async () => { const nav = performance.getEntriesByType('navigation')[0]; const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0; const tbt = window.__lt.filter(x => x[0] >= fcp).reduce((s, x) => s + Math.max(0, x[1] - 50), 0); const lcp = await new Promise(res => new PerformanceObserver(l => { const e = l.getEntries(); res(e[e.length - 1].startTime) }).observe({ type: 'largest-contentful-paint', buffered: true })); return { tbt: Math.round(tbt), lcp: Math.round(lcp), ttfb: Math.round(nav.responseStart), cls: +window.__cls.toFixed(3), tags: Object.keys(window.google_tag_manager || {}).filter(k => /^(AW|G|GT)-/.test(k)).sort().join(',') }; });
    res.push({ ...m, nReq, jsKo: Math.round(jsTx / 1024), applied, ads: hits.filter(h => /ccm\/collect.*AW-18347114778.*page_view/.test(h)).length, ga4: hits.filter(h => /g\/collect.*G-1JX1J3TWVZ.*page_view/.test(h)).length });
    await ctx.close();
  }
  await b.close();
  const v = k => res.map(r => r[k]).sort((a, b) => a - b), med = k => v(k)[Math.floor(res.length / 2)], rng = k => `${v(k)[0]}–${v(k)[res.length - 1]}`;
  console.log(JSON.stringify({ url: url.replace('https://fluxintelligent.com', ''), sc, runs: res.length, applied: res.every(r => r.applied), tbt: med('tbt'), tbt_plage: rng('tbt'), lcp: med('lcp'), lcp_plage: rng('lcp'), ttfb: med('ttfb'), cls: med('cls'), jsKo: med('jsKo'), req: med('nReq'), ads_pv: res.map(r => r.ads).join('/'), ga4_pv: res.map(r => r.ga4).join('/'), tags: res[0].tags }));
})();
