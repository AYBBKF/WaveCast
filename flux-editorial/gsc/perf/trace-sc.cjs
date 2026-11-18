// Liste des scripts Google chargés et hits envoyés pour un scénario (1 passage)
const { chromium, devices } = require('playwright'); const fs = require('fs');
const src = fs.readFileSync(__dirname + '/scenarios.cjs', 'utf8'); const RX = eval('(' + src.match(/const RX = (\{[\s\S]*?\n\});/)[1] + ')');
(async () => { const [url, sc] = [process.argv[2], process.argv[3]]; const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
  if (sc !== 'actuel') await p.route(u => u.href === url, async r => { const resp = await r.fetch(); let body = await resp.text(); if (RX[sc]) body = body.replace(RX[sc], sc === 'A3' ? '/0tqe/?id=GT-PZQ8SJ83' : ''); if (sc === 'A2') body = body.replace("gtag('set', 'developer_id.dY2E1Nz', true);", "gtag('set', 'developer_id.dY2E1Nz', true); gtag('config', 'AW-18347114778');"); await r.fulfill({ response: resp, body }); });
  const L = []; p.on('request', r => { const u = r.url(); if (/gtag\/js|0tqe|collect|viewthrough|rmkt/.test(u)) L.push(u.replace('https://', '').replace(/\?.*$/, '') + ((u.match(/[?&](id|tid|en)=[^&]+/g) || []).join(''))); });
  await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 }); await p.waitForTimeout(4000); console.log(sc + ':\n  ' + L.join('\n  ')); await b.close(); })();
