// Simulation locale : 'actuel' = HTML tel que servi ; 'sans-passerelle' = suppression du seul snippet injecté par Cloudflare
const { chromium, devices } = require('playwright');
const INJ = /<script>\(function\(w,i,g\)\{w\[g\]=w\[g\]\|\|\[\];[\s\S]*?google_tags_first_party'\);<\/script><script async src="\/0tqe\/"><\/script>\s*<script>[\s\S]*?developer_id\.dY2E1Nz', true\);\s*<\/script>/;
(async () => {
  const [url, mode, runs] = [process.argv[2], process.argv[3], +process.argv[4] || 3];
  const b = await chromium.launch(); const res = [];
  for (let i = 0; i < runs; i++) {
    const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
    const cdp = await ctx.newCDPSession(p); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    let removed = false;
    if (mode === 'sans-passerelle') await p.route(u => u.href === url, async r => { const resp = await r.fetch(); let body = await resp.text(); if (INJ.test(body)) { body = body.replace(INJ, ''); removed = true; } await r.fulfill({ response: resp, body }); });
    const hits = []; let jsBytes = 0;
    p.on('request', r => { const u = r.url(); if (/collect|gtag\/js|0tqe/.test(u)) hits.push(u.replace(/\?.*$/, '').replace('https://', '') + ((u.match(/[?&](tid|id|en)=[^&]+/g) || []).join(''))); });
    p.on('response', async r => { if (r.request().resourceType() === 'script') { try { jsBytes += (await r.body()).length } catch (e) {} } });
    await p.addInitScript(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push([e.startTime, e.duration]))).observe({ type: 'longtask', buffered: true }); });
    await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 }); await p.waitForTimeout(5000);
    const m = await p.evaluate(() => { const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0; const tbt = window.__lt.filter(x => x[0] >= fcp).reduce((s, x) => s + Math.max(0, x[1] - 50), 0); const lcp = new Promise(res => new PerformanceObserver(l => { const e = l.getEntries(); res(e[e.length - 1].startTime) }).observe({ type: 'largest-contentful-paint', buffered: true })); return lcp.then(v => ({ tbt: Math.round(tbt), lcp: Math.round(v), tags: Object.keys(window.google_tag_manager || {}).filter(k => /^(AW|G|GT)-/.test(k)) })); });
    res.push({ ...m, jsKo: Math.round(jsBytes / 1024), removed, adsPV: hits.some(h => /ccm\/collect.*AW-18347114778.*page_view/.test(h)), ga4PV: hits.some(h => /g\/collect.*G-1JX1J3TWVZ.*page_view/.test(h)), hits });
    await ctx.close();
  }
  await b.close();
  const med = k => { const v = res.map(r => r[k]).sort((a, b) => a - b); return v[Math.floor(v.length / 2)] };
  console.log(`${mode.padEnd(16)} ${url.replace('https://fluxintelligent.com', '')} | TBT~${med('tbt')}ms LCP~${med('lcp')}ms JS=${med('jsKo')}Ko | snippet retiré=${res.every(r => r.removed)} | Ads page_view=${res.map(r => r.adsPV)} GA4 page_view=${res.map(r => r.ga4PV)} | conteneurs=${res[0].tags}`);
  console.log('   hits:', res[0].hits.join(' | '));
})();
