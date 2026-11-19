const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [u, sel] of [['/ia/contact/', '#forminator-module-3117'], ['/rejoignez-nous/', 'form.forminator-custom-form'], ['/agents-ia/', 'form.forminator-custom-form']]) for (const v of ['A', 'C']) {
    const ctx = await b.newContext({ ...devices['Pixel 5'] }); const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 80)));
    const posts = []; await p.route('**/admin-ajax.php', r => { if (r.request().method() === 'POST') { posts.push((r.request().postData() || '').match(/action=([a-z_\-]+)/)?.[1] || 'form-data'); return r.abort(); } return r.continue(); });
    await p.goto('https://fluxintelligent.com' + u + (v === 'C' ? '?fi_inline=2' : '?ff=1'), { waitUntil: 'load' }); await p.waitForTimeout(4000);
    const f = p.locator(sel).first();
    const vis = await f.isVisible().catch(() => false);
    const inp = f.locator('input[type=text], input[type=email]').first();
    let typed = false; if (await inp.count()) { await inp.fill('Test'); typed = (await inp.inputValue()) === 'Test'; await inp.fill(''); }
    const btn = f.locator('button[type=submit], .forminator-button-submit').first();
    if (await btn.count()) { await btn.scrollIntoViewIfNeeded(); await btn.click().catch(() => {}); await p.waitForTimeout(1500); }
    const errors = await f.locator('.forminator-error-message, .forminator-has_error').count();
    const ts = await f.locator('.forminator-turnstile').count();
    console.log(u, v, JSON.stringify({ visible: vis, typed, clientErrorsOnEmptySubmit: errors, turnstileBox: ts, ajaxPosts: posts, jsErrors: errs }));
    await ctx.close();
  }
  await b.close();
})();
