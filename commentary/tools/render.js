const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.join(__dirname, '..', 'figures', 'svg'), out = path.join(__dirname, '..', 'figures', 'png');
  const FONTS = process.env.AMIRI_DIR || __dirname; // folder holding amiri-*.woff2 (npm @fontsource/amiri)
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const pg = await b.newPage({ deviceScaleFactor: 2 });
  const only = process.argv[2];
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg') && (!only || f.startsWith(only)))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const w = +svg.match(/width="(\d+)"/)[1], h = +svg.match(/height="(\d+)"/)[1];
    await pg.setViewportSize({ width: w, height: h });
    const font = (file, wt, range) => `@font-face{font-family:Amiri;font-weight:${wt};src:url(file://${FONTS}/${file}) format('woff2');unicode-range:${range}}`;
    const ar = 'U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC';
    const html = `<html><head><style>${font('amiri-arabic-400-normal.woff2',400,ar)}${font('amiri-arabic-700-normal.woff2',700,ar)}${font('amiri-latin-400-normal.woff2',400,'U+0000-00FF,U+2000-206F,U+2190-21FF,U+2200-22FF')}body{margin:0}</style></head><body>${svg}</body></html>`;
    fs.writeFileSync(path.join(__dirname, '_tmp.html'), html);
    await pg.goto('file://' + path.join(__dirname, '_tmp.html'));
    await pg.evaluate(() => document.fonts.ready);
    await pg.waitForTimeout(150);
    await pg.screenshot({ path: path.join(out, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: w, height: h } });
  }
  await b.close();
})();
