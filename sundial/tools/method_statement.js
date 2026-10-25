// طريقة التنفيذ وجدول الكميات للتصميم (أ) — ملف Word قابل للتعديل (من اليمين لليسار).
const fs = require('fs'), path = require('path');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
        LevelFormat, BorderStyle, PageNumber, Footer, Header } = require('docx');
const OUT = path.join(__dirname, '..', 'execution_A');
const FONT = 'Arial';
const csv = f => fs.readFileSync(path.join(OUT, 'csv', f), 'utf8').replace(/^﻿/, '').trim().split('\n').map(l => l.split(','));

const run = (t, o = {}) => new TextRun({ text: t, font: FONT, rightToLeft: true, size: o.size || 22, bold: o.bold, color: o.color });
const P = (t, o = {}) => new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, spacing: { after: 100, line: 300 }, children: [run(t, o)], ...(o.p || {}) });
const H = (t, lvl) => new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, heading: lvl, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text: t, font: FONT, rightToLeft: true, bold: true, size: lvl === HeadingLevel.HEADING_1 ? 32 : 26, color: lvl === HeadingLevel.HEADING_1 ? '7A4A1C' : '2A2622' })] });
const B = (t) => new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, numbering: { reference: 'b', level: 0 }, spacing: { after: 60, line: 290 }, children: [run(t)] });
const N = (t) => new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, numbering: { reference: 'n', level: 0 }, spacing: { after: 80, line: 290 }, children: [run(t)] });
const border = { style: BorderStyle.SINGLE, size: 4, color: 'BFB5A0' };
function table(head, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, hd) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: { top: border, bottom: border, left: border, right: border },
    shading: hd ? { type: ShadingType.CLEAR, fill: 'E8DFCC', color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, children: [run(String(t), { bold: hd, size: 20 })] })] });
  return new Table({ visuallyRightToLeft: true, width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, widths[i], true)) }), ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i], false)) }))] });
}

const boq = csv('X07_BOQ.csv').slice(1);
const pts = csv('X01_control_points.csv').slice(1);
const noon = csv('X06_noon_check.csv').slice(1);

const C = [];
C.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { before: 1800, after: 200 }, children: [new TextRun({ text: 'مزولة الفسطاط', font: FONT, rightToLeft: true, bold: true, size: 56, color: '2A2622' })] }));
C.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: 'طريقة التنفيذ وخطة الفحص وجدول الكميات — التصميم (أ): مزولة الشاخص القطبي', font: FONT, rightToLeft: true, size: 28, color: '7A4A1C' })] }));
C.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 1200 }, children: [run('حدائق تلال الفسطاط — المرحلة الثانية • البند SF-12 • الإصدار 1')] }));

C.push(H('1. الغرض والمراجع', HeadingLevel.HEADING_1));
C.push(P('يصف هذا المستند كيف ينفذ المقاول المزولة الشمسية في الموقع خطوة بخطوة، ومن المسؤول عن كل خطوة، وما يُفحص قبل الانتقال إلى ما بعدها. يُقرأ مع الرسومات التنفيذية X-00 إلى X-07، وملفات القص DXF وجداول الإحداثيات CSV.'));
C.push(P('المزولة ساعة دقيقة: خطأ صغير في اتجاه خط الزوال أو ميل الشاخص يظهر خطأً في الوقت يراه كل زائر. لذلك تُنفذ بالإحداثيات المحسوبة لا بالقياس من الرسم، وتمر بنقاط توقف لا تُتجاوز إلا بموافقة المستشار الفلكي.'));
C.push(H('2. الأطراف والمهارات المطلوبة', HeadingLevel.HEADING_1));
[['المقاول العام', 'الأعمال الترابية والخرسانية وتنسيق الأطراف والسلامة.'],
 ['مقاول الرخام', 'مصنع بماكينة CNC للقص والحفر، وخبرة في التطعيم بالنحاس والراتنج.'],
 ['مصنع الحديد', 'قطع بالماء (Waterjet) لألواح 316L سمك 30 مم، ولحام ستانلس معتمد.'],
 ['المساح', 'جهاز GNSS-RTK ومحطة شاملة بدقة زاوية 1″ على الأقل.'],
 ['المستشار الفلكي', 'اعتماد رسومات الورشة، وحضور نقاط التوقف، والمعايرة النهائية.']].forEach(([a, b]) => C.push(B(`${a}: ${b}`)));

C.push(H('3. قبل البدء: الاعتمادات', HeadingLevel.HEADING_1));
['رسومات ورشة للشاخص ولوح القاعدة من المصنع مبنية على ملف A_gnomon_cut.dxf.', 'عينات: رخام الوجه، وجرانيت الحلقة والحافة، وشريط النحاس، وألوان الراتنج الستة.',
 'بلاطة تجريبية واحدة (مثل H08) مقصوصة ومحفورة ومطعمة من ملفها لاعتماد جودة الحفر والتطعيم.',
 'نتيجة اختبار النموذج المصغر 1:15 (اللوحات M-01 إلى M-04) موقعة من المستشار.',
 'برنامج زمني يوضح أن التحقق الشمسي يقع في أيام مشمسة وفي وقت الظهر الحقيقي.'].forEach(t => C.push(N(t)));

C.push(H('4. خطوات التنفيذ في الموقع', HeadingLevel.HEADING_1));
const steps = [
 ['4.1 التوقيع المساحي', ['ثبّت P0 (مركز الدائرة) وP7 وP8 (طرفا خط الزوال) بجهاز GNSS-RTK من إحداثيات الجدول أدناه، بمسامير نحاسية في كتل خرسانية صغيرة خارج منطقة الحفر مع نقاط مرجعية بديلة.',
   'خط الزوال يتجه إلى الشمال الحقيقي لا الشبكي ولا المغناطيسي؛ الفرق عن الشمال الشبكي 0.1214° ويُراعى في الحساب.',
   'تحقق شمسي (نقطة التوقف H1): يُثبت شاخص رأسي مؤقت (خيط شاقول) على P0، ويُعلّم ظله في وقت الظهر الحقيقي لليوم من الجدول؛ يجب أن يقع على خط P0–P7 بفرق لا يتجاوز 2 مم على 5 م.']],
 ['4.2 الحفر والأساسات', ['حفر حتى −0.50 تحت الدائرة، وإحلال ودمك 95%، وأساس حصوي 250 مم.',
   'صب أساس الشاخص (5.0 × 1.0 × 0.6 م) أولًا. تُثبت المسامير الاثنا عشر M24 بقالب خشبي أو معدني يُقص من ملف DXF بحيث يقع محورها على خط الزوال تمامًا (±3 مم). (H2)',
   'صب البلاطة 150 مم وتسوية سطحها ±3 مم عند −0.07، مع ترك جيب لوح القاعدة. معالجة رطبة 7 أيام.']],
 ['4.3 التصنيع في المصنع (بالتوازي)', ['الشاخص: قطع لوح 316L سمك 30 مم بالماء، ثم فحص الأبعاد مقابل جدول الإحداثيات في X-05، وزاوية الضلع 30.0054° ±0.05°، واستقامته ±0.5 مم/م. (H3)',
   'تُلحم الشمسة على رأس النصل، ويُجهز ثقب الكرة بحيث يكون مركزها نقطة العقدة N. يُطلى الشاخص بطلاء سيراميكي برونزي، وتُحمى الحافة القطبية.',
   'البلاط: كل بلاطة تُقص وتُحفر من ملفها في مجلد dxf/tiles، والأصل ركنها الجنوبي الغربي. يُكتب رقمها على ظهرها بقلم دائم.',
   'رص جاف لربع الوجه في المصنع للتحقق من استمرار الخطوط عبر الفواصل ±0.5 مم. (H4)']],
 ['4.4 تركيب الشاخص', ['يُرفع الشاخص (≈ 1.1 طن) برافعة متحركة بحمالات نسيجية، ويوضع على صواميل الضبط فوق المسامير.',
   'يُضبط محور النصل على خط الزوال بالمحطة الشاملة، وزاوية الضلع بميزان رقمي، وموضع مركز الكرة (y = +0.550، z = 2.400) ±3 مم أفقيًا و±2 مم رأسيًا.',
   'تحقق شمسي قبل الحقن (H5): في وقت الظهر الحقيقي من الجدول يجب أن يقع ظل الحافة القطبية على خط الزوال، وظل الكرة على موضعه المحسوب. ثم تُحقن المونة غير المنكمشة.']],
 ['4.5 تركيب البلاط والحلقة', ['يبدأ التركيب من البلاط الملاصق لخطي الزوال والاعتدال (فواصل رئيسية)، ثم يتجه إلى المحيط، كل بلاطة في موضعها برقمها وبالمحطة الشاملة.',
   'مونة لصق 30 مم بتغطية كاملة، وفواصل 2 مم إيبوكسي بلون الحجر، وفاصل بولي يوريثان 5 مم حول النصل.',
   'استواء الوجه ±1 مم على 3 م والكلي ±3 مم، ويُفحص بشبكة نقاط كل متر بالميزان الرقمي. (H6)',
   'ثم قطاعات الحلقة R01–R36، والحافة الحمراء، والمجرى المحيطي.']],
 ['4.6 الأعمال النهائية', ['تطعيم أقراص الأرقام والنجوم والنصوص بقوالب تُطبع من الرسم X-03، ثم شريط النحاس لخط الزوال بعرض 30 مم فوق الفاصل.',
   'صقل نهائي للسطح، وحماية بغطاء خشبي حتى التسليم، وتركيب الكرة وأنبوب الرصد.']],
 ['4.7 المعايرة والاستلام (H7)', ['في يوم مشمس تُسجل 5 قراءات على الأقل بين 9 صباحًا و3 عصرًا، وتُقارن بالساعة الرسمية بعد إضافة تصحيح معادلة الزمن.',
   'يُقبل العمل إذا لم يتجاوز الفرق دقيقة واحدة في كل القراءات، ويُحرر محضر استلام يوقعه المقاول والمستشار والمالك.']]];
steps.forEach(([h, items]) => { C.push(H(h, HeadingLevel.HEADING_2)); items.forEach(t => C.push(B(t))); });

C.push(H('5. خطة الفحص ونقاط التوقف', HeadingLevel.HEADING_1));
C.push(table(['النقطة', 'البند', 'المعيار', 'المسؤول'], [
  ['H1', 'توقيع P0 وخط الزوال', 'GNSS-RTK + رصد شمسي ±2 مم/5 م', 'المساح + المستشار'], ['H2', 'تسليح الأساس والمسامير', 'قالب من DXF ±3 مم', 'الإنشائي'],
  ['H3', 'استلام الشاخص في المصنع', 'الأبعاد والزاوية والاستقامة', 'المستشار'], ['H4', 'رص جاف لربع البلاط', 'استمرار الخطوط ±0.5 مم', 'المستشار'],
  ['H5', 'ضبط الشاخص قبل الحقن', 'ظل الضلع على الزوال عند الظهر', 'المستشار'], ['H6', 'استواء البلاط', '±1 مم/3 م، كلي ±3 مم', 'المقاول + المستشار'],
  ['H7', 'المعايرة والاستلام', '5 قراءات، فرق ≤ 1 دقيقة', 'المستشار + المالك']], [900, 2900, 3300, 2000]));
C.push(H('6. حدود التفاوت', HeadingLevel.HEADING_1));
C.push(table(['البند', 'الحد'], [['استواء الوجه', '±1 مم/3 م، كلي ±3 مم'], ['اتجاه خط الزوال', '±0.02°'], ['زاوية الضلع القطبي', '30.0054° ±0.05°'],
  ['موضع العقدة', '±3 مم أفقي، ±2 مم رأسي'], ['موضع الخطوط المحفورة', '±1 مم'], ['استقامة الضلع القطبي', '±0.5 مم/م']], [4500, 4600]));
C.push(H('7. النقاط المرجعية', HeadingLevel.HEADING_1));
C.push(table(['النقطة', 'x (م)', 'y (م)', 'E شبكي', 'N شبكي', 'الوصف'], pts.map(r => [r[0], r[1], r[2], r[3], r[4], r.slice(5).join(',')]), [800, 900, 900, 1500, 1500, 3500]));
C.push(H('8. جدول التحقق عند الظهر الحقيقي (2027)', HeadingLevel.HEADING_1));
C.push(P('«ص» تعني أن التاريخ في التوقيت الصيفي (UTC+3). y ظل الكرة: موضع مركز ظل الكرة على خط الزوال بالمتر من P0.'));
C.push(table(['التاريخ', 'الظهر الحقيقي', 'معادلة الزمن (د)', 'y ظل الكرة (م)'], noon, [2200, 2400, 2200, 2300]));
C.push(H('9. جدول الكميات المبدئي', HeadingLevel.HEADING_1));
C.push(P('الكميات صافية محسوبة من الرسومات، ويضيف المقاول الهالك وفق طريقته. البنود الإنشائية تقديرية حتى المراجعة الإنشائية.'));
C.push(table(['م', 'البند', 'الوحدة', 'الكمية'], boq.map(r => [r[0], r.slice(1, -2).join(','), r[r.length - 2], r[r.length - 1]]), [600, 6300, 1000, 1200]));
C.push(H('10. السلامة والحماية والصيانة', HeadingLevel.HEADING_1));
['رفع الشاخص بخطة رفع معتمدة ومنطقة محظورة حول الرافعة.', 'حماية الحافة القطبية والوجه المصقول بغطاء حتى التسليم؛ يُمنع مرور المعدات على البلاط.',
 'الصيانة: تنظيف أسبوعي بالماء، وتلميع النحاس كل 6 أشهر، وفحص ميل الشاخص سنويًّا يوم الاعتدال.', 'لا تُستعمل مواد تنظيف حمضية على الرخام.'].forEach(t => C.push(B(t)));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: [{ reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.RIGHT, style: { paragraph: { indent: { right: 360, hanging: 260 } } } }] },
                        { reference: 'n', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.RIGHT, style: { paragraph: { indent: { right: 360, hanging: 300 } } } }] }] },
  sections: [{ properties: { page: { margin: { top: 1200, bottom: 1200, left: 1200, right: 1200 } } },
    headers: { default: new Header({ children: [new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, children: [run('مزولة الفسطاط — طريقة التنفيذ', { size: 16, color: '8A847C' })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 16 })] })] }) },
    children: C }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(OUT, 'Method_Statement_A.docx'), b); console.log('ok'); });
