// يحوّل لوحات SVG إلى PDF (A1) وPNG عبر Chromium. الخطوط: Amiri وNoto Kufi Arabic وIBM Plex Sans Arabic مثبتة في النظام.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.join(__dirname, '..', 'drawings', 'svg');
  const outPdf = path.join(__dirname, '..', 'drawings', 'pdf'), outPng = path.join(__dirname, '..', 'drawings', 'png');
  fs.mkdirSync(outPdf, { recursive: true }); fs.mkdirSync(outPng, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const only = process.argv[2];
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg') && (!only || f.startsWith(only))).sort();
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const w = +svg.match(/width="([\d.]+)mm"/)[1], h = +svg.match(/height="([\d.]+)mm"/)[1];
    const html = `<html><head><style>@page{size:${w}mm ${h}mm;margin:0}body{margin:0}svg{display:block;width:${w}mm;height:${h}mm}</style></head><body>${svg}</body></html>`;
    const tmp = path.join(outPdf, '_tmp.html'); fs.writeFileSync(tmp, html);
    const pg = await b.newPage({ viewport: { width: Math.round(w * 3.78), height: Math.round(h * 3.78) }, deviceScaleFactor: process.env.DSF ? +process.env.DSF : 1.4 });
    await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(200);
    await pg.pdf({ path: path.join(outPdf, f.replace('.svg', '.pdf')), width: `${w}mm`, height: `${h}mm`, printBackground: true });
    await pg.screenshot({ path: path.join(outPng, f.replace('.svg', '.png')) });
    await pg.close(); fs.unlinkSync(tmp);
    console.log('rendered', f);
  }
  await b.close();
})();
