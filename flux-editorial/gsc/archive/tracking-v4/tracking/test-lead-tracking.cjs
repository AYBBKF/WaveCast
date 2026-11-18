// Banc de test ISOLÉ du suivi des leads (aucun lead réel, aucun hit Google de production).
// - charge les vraies pages, injecte fi-lead-tracking.js côté navigateur ;
// - toute requête POST vers admin-ajax.php est interceptée et reçoit une réponse simulée (le serveur réel n'est jamais appelé) ;
// - toutes les requêtes de collecte Google (GA4, Ads, passerelle /0tqe/ga|gs) sont bloquées après relevé.
const { chromium, devices } = require('playwright'); const fs = require('fs');
const SNIP = fs.readFileSync(__dirname + '/fi-lead-tracking.js', 'utf8');
const B = 'https://fluxintelligent.com';
const isCollect = u => /google-analytics\.com\/g\/collect|\/g\/collect|\/ccm\/collect|googleads\.g\.doubleclick|google\.com\/rmkt|ad\.doubleclick|\/0tqe\/(ga|gs)\/|pagead2\.googlesyndication/.test(u);
async function page(b, url, ajaxMock, cfStub) {
  const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage();
  const log = { ajax: [], collect: [] };
  await ctx.route(u => isCollect(u.href), r => { { const q = r.request(); const all = q.url() + '\n' + (q.postData() || ''); const host = q.url().replace(/\?.*$/, ''); const tid = (q.url().match(/[?&]tid=[^&]+/) || [''])[0]; (all.match(/(^|[?&\n])en=[^&\s]+/g) || ['']).forEach(e => log.collect.push(host + ' ' + tid + ' ' + e.replace(/^[?&\n]/, ''))); } r.abort(); });
  await ctx.route(/admin-ajax\.php/, async r => {
    if (r.request().method() !== 'POST') return r.continue();
    const body = r.request().postData() || ''; const act = (body.match(/name="action"\r?\n\r?\n([^\r\n]+)/) || body.match(/action=([^&]+)/) || [])[1] || '?';
    log.ajax.push(act); const m = ajaxMock(act);
    if (m === 'abort') return r.abort(); return r.fulfill({ status: m.status || 200, contentType: 'application/json', body: JSON.stringify(m.json || {}) });
  });
  if (cfStub) await ctx.route(/challenges\.cloudflare\.com\/turnstile\/v0\/api\.js/, r => r.fulfill({ contentType: 'application/javascript', body: "window.turnstile={render:function(el,o){var e=(typeof el==='string'?document.querySelector(el):el);var i=document.createElement('input');i.type='hidden';i.name=(o&&o['response-field-name'])||'cf-turnstile-response';i.value='test';e&&e.appendChild(i);setTimeout(function(){o&&o.callback&&o.callback('test')},50);return 'w1'},getResponse:function(){return 'test'},reset:function(){},remove:function(){},execute:function(){},ready:function(f){f()},isExpired:function(){return false}};setTimeout(function(){window.forminator_render_turnstile&&window.forminator_render_turnstile()},10);" }));
  await p.goto(url, { waitUntil: 'load', timeout: 90000 }); await p.waitForTimeout(3000); await p.addScriptTag({ content: SNIP });
  return { ctx, p, log };
}
const evs = p => p.evaluate(() => (window.dataLayer || []).filter(x => x && x[0] === 'event' && typeof x[1] === 'string' && !/^(gtm\.|page_view)/.test(x[1])).map(x => x[1] + ' ' + JSON.stringify(x[2] || {})));
const FM_OK = { json: { success: true, data: { success: true, message: 'Merci', behav: 'behaviour-thankyou', redirect: false } } };
const FM_KO = { json: { success: false, data: { success: false, message: 'Erreur', errors: [] } } };
(async () => {
  const b = await chromium.launch(); const R = {};
  async function contact(name, mock, fill) {
    const { ctx, p, log } = await page(b, B + '/ia/contact/', a => (/forminator/.test(a) ? mock : { json: { success: true, data: {} } }), true);
    const f = 'form.forminator-custom-form-3117'; await p.waitForSelector(f, { state: 'attached' }); await p.evaluate(s => { const e = document.querySelector(s); if (e) e.style.display = 'block'; }, f);
    if (fill) { await p.fill(f + ' input[name="name-1"]', 'Test Banc'); await p.fill(f + ' input[name="email-1"]', fill === 'invalide' ? '' : 'test@example.com'); await p.fill(f + ' textarea[name="textarea-1"]', 'Test automatisé isolé'); }
    await p.click(f + ' button[type="submit"], ' + f + ' .forminator-button-submit').catch(() => {}); await p.waitForTimeout(3500);
    if (name === 'contact_succes') { await p.click(f + ' button[type="submit"], ' + f + ' .forminator-button-submit').catch(() => {}); await p.waitForTimeout(500); }
    await p.evaluate(() => { Object.defineProperty(document, 'visibilityState', {value: 'hidden', configurable: true}); document.dispatchEvent(new Event('visibilitychange')); }); await p.waitForTimeout(1500);
    R[name] = { ajax: log.ajax, gtag: await evs(p), collect: log.collect.filter(c => /en=(generate_lead|click_|devis_|contact_)/.test(c)) }; await ctx.close();
  }
  await contact('contact_succes', FM_OK, 'ok');
  await contact('contact_refus_serveur', FM_KO, 'ok');
  await contact('contact_erreur_500', { status: 500, json: {} }, 'ok');
  await contact('contact_invalide', FM_OK, 'invalide');
  // Rechargement sans nouvelle soumission
  { const { ctx, p, log } = await page(b, B + '/ia/contact/', a => FM_OK, true); await p.reload({ waitUntil: 'load' }); await p.waitForTimeout(2000); await p.addScriptTag({ content: SNIP }); await p.waitForTimeout(1500); R['contact_rechargement'] = { ajax: log.ajax, gtag: await evs(p) }; await ctx.close(); }
  // Devis IA : ouverture, début de saisie, fdi_partiel / fdi_final simulés via le chemin réseau du plugin (window.fetch)
  async function devis(name, finalMock) {
    const { ctx, p, log } = await page(b, B + '/ia/devis/', a => a === 'fdi_partiel' ? { json: { success: true, data: { lead_id: 999001, token: 't' } } } : a === 'fdi_final' ? finalMock : { json: { success: true, data: { nonce: 'n' } } }, false);
    await p.evaluate(() => { const i = document.querySelector('#fdi-app input, #fdi-app textarea'); if (i) { i.focus(); i.value = 'x'; i.dispatchEvent(new Event('input', { bubbles: true })); } });
    await p.evaluate(async () => { const post = async a => { const f = new FormData(); f.append('action', a); try { await fetch((window.FDI && FDI.ajax) || '/wp-admin/admin-ajax.php', { method: 'POST', body: f }) } catch (e) {} }; await post('fdi_partiel'); await post('fdi_final'); await post('fdi_final'); });
    await p.waitForTimeout(1500); await p.evaluate(() => { Object.defineProperty(document, 'visibilityState', {value: 'hidden', configurable: true}); document.dispatchEvent(new Event('visibilitychange')); }); await p.waitForTimeout(6000); R[name] = { ajax: log.ajax, gtag: await evs(p), collect: log.collect.filter(c => /en=(generate_lead|devis_)/.test(c)) }; await ctx.close();
  }
  await devis('devis_succes_double_envoi', { json: { success: true, data: { lead_id: 999001 } } });
  await devis('devis_echec_serveur', { json: { success: false, data: { message: 'Erreur' } } });
  await devis('devis_coupure_reseau', 'abort');
  // Clics WhatsApp et téléphone (navigation bloquée)
  { const { ctx, p, log } = await page(b, B + '/ia/contact/', a => ({ json: {} }), true);
    await p.evaluate(() => { document.querySelectorAll('a[href^="tel:"],a[href*="wa.me"],a[href*="whatsapp"]').forEach(a => a.addEventListener('click', e => e.preventDefault())); const t = document.querySelector('a[href^="tel:"]'); const w = document.querySelector('a[href*="wa.me"],a[href*="api.whatsapp.com"]'); t && t.click(); t && t.click(); w && w.click(); });
    await p.waitForTimeout(1500); await p.evaluate(() => { Object.defineProperty(document, 'visibilityState', {value: 'hidden', configurable: true}); document.dispatchEvent(new Event('visibilitychange')); }); await p.waitForTimeout(6000); R['clics_tel_whatsapp'] = { gtag: await evs(p), collect: log.collect.filter(c => /en=click_/.test(c)) }; await ctx.close(); }
  await b.close(); console.log(JSON.stringify(R, null, 1));
})();
