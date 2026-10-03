// Render the canvas timeline with headless Chromium.
//   node render.js stills 0.5,3,10        -> build/stills/t_<time>.jpg
//   node render.js video out.mp4          -> silent H.264 video piped through ffmpeg
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');           // whats_new/
const REPO = path.resolve(ROOT, '..');                // served root, so ../mascot and ../short/fonts resolve
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.ttf': 'font/ttf', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(REPO, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
});

(async () => {
  await new Promise(r => server.listen(process.env.PORT || 8765, r));
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(`http://localhost:${process.env.PORT || 8765}/whats_new/build/index.html`);
  await page.evaluate(() => window.READY);
  const grab = async t => {
    const b64 = await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95).split(',')[1]; }, t);
    return Buffer.from(b64, 'base64');
  };
  const [mode, arg] = process.argv.slice(2);
  if (mode === 'cover') {
    const b64 = await page.evaluate(() => { window.renderCover(); return document.getElementById('c').toDataURL('image/png').split(',')[1]; });
    fs.writeFileSync(path.resolve(arg), Buffer.from(b64, 'base64'));
  } else if (mode === 'stills') {
    fs.mkdirSync(path.join(ROOT, 'build/stills'), { recursive: true });
    for (const t of arg.split(',').map(Number)) fs.writeFileSync(path.join(ROOT, `build/stills/t_${t.toFixed(2)}.jpg`), await grab(t));
  } else {
    const fps = await page.evaluate(() => window.FPS), dur = await page.evaluate(() => window.DURATION);
    const n = Math.round(fps * dur);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), arg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      const buf = await grab(i / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close(); server.close();
})();
