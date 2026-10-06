const fs = require('fs'), path = require('path');
const D = require('docx');
const { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, PageBreak, TableOfContents, Footer, PageNumber, LevelFormat } = D;

const ROOT = __dirname;
const BASE = path.join(ROOT, '..'); // commentary/
const FONT = 'Traditional Arabic';
const font = { ascii: 'Times New Roman', hAnsi: 'Times New Roman', cs: FONT, eastAsia: FONT };
const INK = '2B1D12', RED = 'B0301F';
const PAGE_W = 11906, MARGIN = 1300, CONTENT_W = PAGE_W - 2 * MARGIN; // A4

function runs(text, base = {}) {
  // inline **bold**
  const out = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const p of parts) {
    if (!p) continue;
    const bold = p.startsWith('**');
    const t = bold ? p.slice(2, -2) : p;
    out.push(new TextRun({ text: t, rightToLeft: true, font, size: base.size || 32, sizeComplexScript: base.size || 32,
      bold: bold || base.bold, boldComplexScript: bold || base.bold, color: base.color || INK, italics: base.italics }));
  }
  return out;
}
function para(text, opt = {}) {
  return new Paragraph({ bidirectional: true, alignment: opt.align || AlignmentType.JUSTIFIED,
    spacing: { after: opt.after ?? 120, line: opt.line || 360 }, indent: opt.indent, numbering: opt.numbering,
    border: opt.border, shading: opt.shading, keepNext: opt.keepNext,
    children: runs(text, opt) });
}
function imgSize(file) {
  const b = fs.readFileSync(file);
  if (b[0] === 0x89) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), type: 'png', b };
  // jpeg
  let i = 2;
  while (i < b.length) {
    if (b[i] !== 0xFF) { i++; continue; }
    const m = b[i + 1], len = b.readUInt16BE(i + 2);
    if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC)
      return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7), type: 'jpg', b };
    i += 2 + len;
  }
  throw new Error('size ' + file);
}
function image(file, widthIn, maxHIn = 8.2) {
  const s = imgSize(file);
  let w = widthIn * 96, h = w * s.h / s.w;
  if (h > maxHIn * 96) { h = maxHIn * 96; w = h * s.w / s.h; }
  return new ImageRun({ type: s.type, data: s.b, transformation: { width: Math.round(w), height: Math.round(h) } });
}
function resolve(p) { return path.join(BASE, p); }
let figNo = 0;
function caption(text) {
  return new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: runs(text, { size: 26, color: '5A4632', bold: false }) });
}
const noBorder = { top: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, bottom: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
  left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } };
const thin = { style: BorderStyle.SINGLE, size: 4, color: 'B9A48C' };
const cellBorders = { top: thin, bottom: thin, left: thin, right: thin };

function pair(orig, redraw, cap) {
  const half = Math.floor(CONTENT_W / 2);
  const mk = (file, label) => new TableCell({ width: { size: half, type: WidthType.DXA }, borders: noBorder,
    verticalAlign: 'center',
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [image(resolve(file), 3.0, 3.4)] }),
      new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: runs(label, { size: 24, color: RED, bold: true }) })] });
  return [new Table({ width: { size: half * 2, type: WidthType.DXA }, columnWidths: [half, half], visuallyRightToLeft: true,
    rows: [new TableRow({ cantSplit: true, children: [mk(orig, 'الأصل المخطوط'), mk(redraw, 'إعادة الرسم')] })] }),
    caption(cap)];
}
function table(lines) {
  const rows = lines.map(l => l.split('|').map(s => s.trim()));
  const n = rows[0].length;
  let widths;
  if (n === 3) widths = [0.22, 0.43, 0.35]; else if (n === 5) widths = [0.34, 0.08, 0.17, 0.25, 0.16]; else if (n === 4) widths = [0.2, 0.25, 0.2, 0.35];
  else widths = Array(n).fill(1 / n);
  const cw = widths.map(x => Math.floor(x * CONTENT_W));
  const tw = cw.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: cw, visuallyRightToLeft: true,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => new TableCell({
      width: { size: cw[j], type: WidthType.DXA }, borders: cellBorders,
      shading: i === 0 ? { type: ShadingType.CLEAR, fill: 'EFE3D3', color: 'auto' } : (i % 2 === 0 ? { type: ShadingType.CLEAR, fill: 'FBF7F1', color: 'auto' } : undefined),
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ bidirectional: true, alignment: (n === 5 && j > 0) ? AlignmentType.CENTER : AlignmentType.RIGHT,
        spacing: { after: 0, line: 300 }, children: runs(c, { size: 26, bold: i === 0 }) })] })) })) });
}

const SRC = process.argv[3] || path.join(ROOT, 'content.txt');
const src = fs.readFileSync(SRC, 'utf8').split('\n');
const children = [];
let i = 0;
while (i < src.length) {
  const l = src[i];
  if (!l.trim()) { i++; continue; }
  if (l.startsWith('!title ')) {
    children.push(new Paragraph({ spacing: { before: 2200, after: 400 }, children: [] }));
    children.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 500 },
      children: runs(l.slice(7), { size: 48, bold: true, color: RED }) }));
  } else if (l.startsWith('!subtitle ')) {
    children.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 300 },
      children: runs(l.slice(10), { size: 30 }) }));
  } else if (l === '!pagebreak') {
    children.push(new Paragraph({ children: [new PageBreak()] }));
  } else if (l === '!toc') {
    children.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: runs('المحتويات', { size: 36, bold: true, color: RED }) }));
    for (const h of src.filter(x => x.startsWith('# ') || x.startsWith('## '))) {
      const top = h.startsWith('# ');
      children.push(new Paragraph({ bidirectional: true, spacing: { after: top ? 80 : 20 }, indent: top ? undefined : { right: 500 },
        children: runs(h.replace(/^#+ /, ''), { size: top ? 30 : 26, bold: top, color: top ? RED : INK }) }));
    }
  } else if (l.startsWith('# ')) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, bidirectional: true, pageBreakBefore: true, children: runs(l.slice(2), { size: 44, bold: true, color: RED }) }));
  } else if (l.startsWith('## ')) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, bidirectional: true, keepNext: true, children: runs(l.slice(3), { size: 36, bold: true, color: '7A2A17' }) }));
  } else if (l.startsWith('!fig ')) {
    const [f, cap, w] = l.slice(5).split('|').map(s => s.trim());
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 }, children: [image(resolve(f), parseFloat(w) || 5)] }));
    children.push(caption(cap));
  } else if (l.startsWith('!pair ')) {
    const [a, b, cap] = l.slice(6).split('|').map(s => s.trim());
    children.push(...pair(a, b, cap));
  } else if (l === '!table') {
    const rows = []; i++;
    while (src[i] !== '!end') { if (src[i].trim()) rows.push(src[i]); i++; }
    children.push(table(rows));
    children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  } else if (l.startsWith('!note ')) {
    children.push(para(l.slice(6), { size: 26, color: '5A4632', shading: { type: ShadingType.CLEAR, fill: 'F5EEE4', color: 'auto' } }));
  } else if (l.startsWith('> ')) {
    children.push(para(l.slice(2), { size: 32, color: '3A2A6B', indent: { left: 400, right: 400 },
      border: { right: { style: BorderStyle.SINGLE, size: 18, color: RED, space: 8 } },
      shading: { type: ShadingType.CLEAR, fill: 'FBF7F1', color: 'auto' } }));
  } else if (l.startsWith('- ') && /^[A-Za-z]/.test(l.slice(2))) {
    // Latin bibliography entry: left-to-right paragraph
    children.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 80, line: 320 }, indent: { left: 500, hanging: 300 },
      children: [new TextRun({ text: '◆  ' + l.slice(2), font, size: 24, color: INK })] }));
  } else if (l.startsWith('- ')) {
    children.push(para(l.slice(2), { numbering: { reference: 'bul', level: 0 }, after: 80 }));
  } else {
    children.push(para(l));
  }
  i++;
}

const doc = new Document({
  creator: 'Claude', title: 'التعليق التراثي على إتحاف المحبوب',
  styles: {
    default: { document: { run: { font, size: 28, sizeComplexScript: 28, rightToLeft: true } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font, size: 40, sizeComplexScript: 40, bold: true, color: RED }, paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font, size: 32, sizeComplexScript: 32, bold: true, color: '7A2A17' }, paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '◆', alignment: AlignmentType.RIGHT,
    style: { paragraph: { indent: { right: 500, hanging: 300 } }, run: { color: RED, size: 16 } } }] }] },
  features: { updateFields: true },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1300, bottom: 1300, left: MARGIN, right: MARGIN } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ children: [PageNumber.CURRENT], font, size: 22 })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2] || path.join(ROOT, 'out.docx'), b); console.log('written'); });
