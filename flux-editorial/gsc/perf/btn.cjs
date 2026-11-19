const { chromium, devices } = require('playwright');
(async () => { const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['Pixel 5'], deviceScaleFactor: 1 }); const p = await ctx.newPage();
 await p.goto('https://fluxintelligent.com/ia/automatisation-ia-casablanca/?sh=1', { waitUntil: 'load' }); await p.waitForTimeout(1500);
 const a = p.locator('section.sec > p > a.btn-primary').last(); await a.scrollIntoViewIfNeeded(); await (await a.evaluateHandle(e => e.closest('section'))).asElement().screenshot({ path: 'btn-casa.png' });
 await p.goto('https://fluxintelligent.com/ia/contact/?sh=1', { waitUntil: 'load' }); await p.waitForTimeout(3500);
 const s = p.locator('#forminator-module-3117 button.forminator-button-submit'); await s.scrollIntoViewIfNeeded(); await (await s.evaluateHandle(e => e.closest('.forminator-row'))).asElement().screenshot({ path: 'btn-contact.png' });
 await b.close(); })();
