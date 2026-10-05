// Render the Petra Reel canvas with headless Chromium.
//   node petra/tools/render.cjs stills 0.5,12,30     -> petra/build/stills/t_<time>.jpg
//   node petra/tools/render.cjs video out.mp4        -> silent H.264, 30 fps
//   node petra/tools/render.cjs cover out.png        -> vertical cover
//   node petra/tools/render.cjs cues out.json        -> SFX cue list for tools/build_audio.py
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.ttf': 'font/ttf', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
});

(async () => {
  const port = process.env.PORT || 8772;
  await new Promise(r => server.listen(port, r));
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(`http://localhost:${port}/build/index.html`);
  await page.evaluate(() => window.READY);
  const grab = async (t, type = 'image/jpeg') => {
    const b64 = await page.evaluate(([t, type]) => { window.renderFrame(t); return document.getElementById('c').toDataURL(type, 0.94).split(',')[1]; }, [t, type]);
    return Buffer.from(b64, 'base64');
  };
  const [mode, arg] = process.argv.slice(2);
  if (mode === 'stills') {
    fs.mkdirSync(path.join(ROOT, 'build/stills'), { recursive: true });
    for (const t of arg.split(',').map(Number)) fs.writeFileSync(path.join(ROOT, `build/stills/t_${t.toFixed(2)}.jpg`), await grab(t));
  } else if (mode === 'cover') {
    const b64 = await page.evaluate(() => { window.renderCover(); return document.getElementById('c').toDataURL('image/png').split(',')[1]; });
    fs.writeFileSync(path.resolve(arg), Buffer.from(b64, 'base64'));
  } else if (mode === 'cues') {
    fs.writeFileSync(path.resolve(arg), JSON.stringify(await page.evaluate(() => ({ total: window.DURATION, cues: window.CUES })), null, 1));
  } else {
    const fps = await page.evaluate(() => window.FPS), dur = await page.evaluate(() => window.DURATION);
    const n = Math.round(fps * dur);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), arg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      const buf = await grab(i / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close(); server.close();
})();
