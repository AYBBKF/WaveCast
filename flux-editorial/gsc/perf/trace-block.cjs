const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'] });
  if (process.argv[3] === 'block') await ctx.route(/fluxintelligent\.com\/0tqe\//, r => r.abort());
  const p = await ctx.newPage(); const hits = [];
  p.on('request', r => { const u = r.url(); if (/collect|viewthroughconversion|1p-user-list|gtag\/js|0tqe/.test(u)) hits.push(u.replace(/\?.*$/, '') + ' ' + ((u.match(/[?&](tid|id|en)=[^&]+/g) || []).join(''))); });
  await p.goto(process.argv[2], { waitUntil: 'networkidle', timeout: 60000 }); await p.waitForTimeout(4000);
  // simulation d'un clic sur un lien de contact / devis pour vérifier les événements
  const tags = await p.evaluate(() => Object.keys(window.google_tag_manager || {}).filter(k => /^(AW|G|GT)-/.test(k)));
  console.log(process.argv[3] || 'normal', '| conteneurs:', tags.join(','), '\n ' + hits.join('\n '));
  await b.close();
})();
