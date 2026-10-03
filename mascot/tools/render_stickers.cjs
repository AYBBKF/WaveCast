// Render the BEAN sticker pack with headless Chromium.
//   node mascot/tools/render_stickers.cjs [size=2048]
// -> mascot/stickers/NN_<pose>.png        die-cut stickers (white border), transparent background
//    mascot/cutouts/NN_<pose>.png         borderless cutouts for animation, transparent background
//    mascot/bean_sticker_pack_contact_sheet.png
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SIZE = +process.argv[2] || 2048;
const LABELS = ['Neutral', 'Smug grin', 'Laughing', 'Shocked', 'Annoyed', 'Thinking', 'Embarrassed', 'Talking'];

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const page = await browser.newPage();
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.setContent('<!doctype html><html><body></body></html>');
  await page.addScriptTag({ path: path.join(ROOT, 'build/bean.js') });
  const font = fs.readFileSync(path.join(ROOT, '../short/fonts/Fredoka.ttf')).toString('base64');

  const out = await page.evaluate(async ({ SIZE, LABELS, font }) => {
    const ff = new FontFace('Fredoka', `url(data:font/ttf;base64,${font})`, { weight: '300 700' });
    await ff.load(); document.fonts.add(ff);
    const res = { stickers: [], cutouts: [] }, tiles = [];
    for (const name of BEAN.ORDER) {
      const { cutout, diecut } = BEAN.renderSticker(name, SIZE);
      res.stickers.push(diecut.toDataURL('image/png')); res.cutouts.push(cutout.toDataURL('image/png'));
      tiles.push(diecut);
    }
    // Contact sheet: 4 x 2 grid on cream.
    const T = 620, PAD = 50, LAB = 70, W = PAD + 4 * (T + PAD), H = PAD + 2 * (T + LAB + PAD);
    const sh = document.createElement('canvas'); sh.width = W; sh.height = H;
    const c = sh.getContext('2d');
    c.fillStyle = '#F3EADF'; c.fillRect(0, 0, W, H);
    tiles.forEach((t, i) => {
      const x = PAD + (i % 4) * (T + PAD), y = PAD + Math.floor(i / 4) * (T + LAB + PAD);
      c.fillStyle = '#EADCCB'; c.beginPath(); c.roundRect(x, y, T, T, 36); c.fill();
      c.drawImage(t, x, y, T, T);
      c.fillStyle = '#2B1D17'; c.font = '600 38px Fredoka'; c.textAlign = 'center';
      c.fillText(`${i + 1}  ${LABELS[i]}`, x + T / 2, y + T + 50);
    });
    res.sheet = sh.toDataURL('image/png');
    return res;
  }, { SIZE, LABELS, font });

  for (const d of ['stickers', 'cutouts']) fs.mkdirSync(path.join(ROOT, d), { recursive: true });
  const names = ['neutral', 'smug_grin', 'laughing', 'shocked', 'annoyed', 'thinking', 'embarrassed', 'talking'];
  const save = (p, url) => fs.writeFileSync(path.join(ROOT, p), Buffer.from(url.split(',')[1], 'base64'));
  names.forEach((n, i) => {
    const f = `${String(i + 1).padStart(2, '0')}_${n}.png`;
    save(`stickers/${f}`, out.stickers[i]); save(`cutouts/${f}`, out.cutouts[i]);
  });
  save('bean_sticker_pack_contact_sheet.png', out.sheet);
  await browser.close();
  console.log('rendered', names.length, 'stickers at', SIZE);
})();
