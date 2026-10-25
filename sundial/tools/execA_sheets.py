"""الرسومات التنفيذية للتصميم (أ) — X-00..X-07 — والنموذج المصغر 1:15 — M-01..M-04 — مع نسخ DXF قابلة للتعديل."""
import os, csv, sys, collections
import datetime as dt
from execA_geom import *
from common import *
from exec_sheets import dimh, dimv, table
import sheet_a
from sheet_a import A as AD
import svg2dxf
import ezdxf

OUT = '../execution_A'
for d in ('svg', 'pdf', 'png', 'dxf', 'dxf_sheets', 'csv', 'dxf/tiles'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
G = GeoA()
MS = 15
g = GeoA(scale=1/MS, blade=0.002)
DES = 'التصميم (أ): مزولة الشاخص القطبي'
SHEETS = []


def reg(n, title):
    def deco(fn):
        SHEETS.append((n, title, fn)); return fn
    return deco


def lengths():
    L = collections.OrderedDict()
    for fam, lbl, segs, spec in G.families():
        k = (fam, spec)
        L[k] = L.get(k, 0) + sum(LineString(sg).length for sg in segs if len(sg) > 1)
    return L


FAM_AR = {'HOUR': 'خطوط الساعات', 'HOUR30': 'أنصاف الساعات', 'HOUR15': 'أرباع الساعات', 'DECL': 'مدارات البروج', 'ASR1': 'أول العصر',
          'ASR2': 'العصر الثاني', 'NOON': 'منحنى ١٢ ظهرًا', 'MERID': 'خط الزوال', 'QIBLA': 'خط القبلة', 'TICKS': 'تدريج الأيام'}


def tile_grid(sh, P, ids=True, size=1.6, col='#8f8a80'):
    for t in G.tiles():
        sh.poly([P(x, y) for x, y in t['poly'].exterior.coords], close=True, stroke=col, sw=0.18)
        if ids:
            c = t['poly'].representative_point() if not t['full'] else t['poly'].centroid
            x, y = P(c.x, c.y); sh.ltr(x, y, t['id'], size, 'middle', SANS, col, 600)


# ------------------------------------------------------------------ X-00 الغلاف وقائمة اللوحات
@reg('X-00', 'الغلاف وقائمة اللوحات والملاحظات العامة')
def x00():
    sh = Sheet()
    frame(sh, 'الغلاف وقائمة اللوحات', ['الرسومات التنفيذية ونموذج الاختبار', 'وطريقة التنفيذ'], 'X-00', '—', DES,
          ['• هذه المجموعة مبنية على اللوحتين A-01 وA-02 المعتمدتين للتصميم.',
           '• كل الخطوط والنقاط محسوبة بالحاسب لعرض 30.0054° ش وطول',
           '   31.2443° ق؛ وتُستعمل ملفات DXF وCSV المرفقة للتوقيع والقص.',
           '• لا يُقاس من الرسم بالمسطرة؛ تُعتمد الأرقام المكتوبة والملفات.',
           '• تُراجع الأعمال الإنشائية (الأساس، المسامير، الرياح) من مهندس',
           '   إنشائي معتمد قبل التنفيذ؛ القيم الواردة مقترحة للتسعير.',
           '• نقاط التوقف (Hold points) في اللوحة X-07 لا تُتجاوز إلا بموافقة',
           '   المستشار الفلكي كتابةً.'])
    sh.text(830, 70, 'مزولة الفسطاط', 16, 'end', KUFI, INK, 700)
    sh.text(830, 90, 'الرسومات التنفيذية للتصميم (أ) — الإصدار 1 للتسعير والتنفيذ', 6, 'end', KUFI, TERRA, 700)
    rows = [(n, t) for n, t, _ in SHEETS] + [('—', 'طريقة التنفيذ وجدول الكميات: Method_Statement_A.docx'),
                                              ('—', 'ملفات القص: dxf/ (الوجه، الحلقة، الشاخص، بلاطة لكل ملف)'),
                                              ('—', 'نسخ اللوحات القابلة للتعديل: dxf_sheets/ وsvg/')]
    table(sh, 830, 120, ['اللوحة', 'العنوان'], rows, [22, 160], 3.0, 9)
    gen = ['## مواد رئيسية', '• الوجه: رخام جلالة كريمي 40 مم مصقول مطفأ (honed).', '• حلقة التقويم: جرانيت رمادي (رمادي إسكندراني) 40 مم.',
           '• الحافة: جرانيت أحمر أسوان 300 × 180 مم.', '• الشاخص: صلب 316L لوح 30 مم مقطوع بالماء.',
           '• التطعيم: شرائط نحاس CuZn37 وراتنج إيبوكسي ملوّن مقاوم للأشعة.',
           '## اختصارات', '• FFL منسوب التشطيب ±0.00 • CNC قطع وحفر رقمي • ITP خطة الفحص',
           '• GNSS-RTK رصد بالأقمار الصناعية بدقة سنتيمترية']
    sh.para(560, 120, gen, 3.0, 1.7)
    return sh


# ------------------------------------------------------------------ X-01 التوقيع
@reg('X-01', 'مسقط التوقيع والنقاط المرجعية — 1:50')
def x01():
    sh = Sheet(); v = View(430, 300, 50); P = v.p
    frame(sh, 'مسقط التوقيع والنقاط المرجعية', ['إحداثيات محلية وشبكية', 'الشمال الحقيقي إلى أعلى'], 'X-01', '1:50', DES,
          ['• الأصل P0 مركز الدائرة؛ x شرقًا وy نحو الشمال الحقيقي.',
           '• الشبكة: حزام مصر الأحمر EPSG:22992؛ تقارب γ = 0.1214°.',
           '   E = E0 + x·cosγ − y·sinγ ، N = N0 + y·cosγ + x·sinγ',
           '• تُثبَّت P0 وP7 وP8 أولًا وتُحمى طوال مدة العمل.',
           '• خط الزوال P7–P8 يُتحقق منه شمسيًّا قبل صب البلاطة (X-07).',
           '• الفواصل الرئيسية للبلاط على خطي الزوال والاعتدال.',
           '• منسوب التشطيب ±0.00 للدائرة كلها، والممر −0.18.'])
    for r, c, fl in [(9.6, GREY, '#ece6da'), (7.25, INK, '#efe5cf'), (6.35, INK, '#f6f1e6')]:
        sh.circle(P(0, 0), r*v.k, stroke=c, sw=0.5, fill=fl)
    tile_grid(sh, P, ids=False)
    sh.line(P(0, -7.7), P(0, 7.7), stroke=RED, sw=0.25, dash='4 1 0.6 1'); sh.line(P(-7.7, 0), P(7.7, 0), stroke=RED, sw=0.25, dash='4 1 0.6 1')
    gn = G.gnomon()
    sh.rect(*P(-0.15, G.fy + 0.15), 0.30*v.k, (G.fy + 0.15 - gn['y0'] + 0.15)*v.k, stroke=TERRA, sw=0.4, fill='#f3d9c9')
    sh.line(P(0, G.yb), P(0, G.fy), stroke=INK, sw=1.5)
    pts = [('P0', 0, 0, 'مركز الدائرة'), ('P5', 0, G.yb, 'قاعدة الضلع القطبي عند ±0.00'), ('P6', 0, G.fy, 'مسقط العقدة (ارتفاعها 2.400)'),
           ('P7', 0, R_RING, 'طرف خط الزوال شمالًا'), ('P8', 0, -R_RING, 'طرف خط الزوال جنوبًا'), ('P9', R_RING, 0, 'طرف الاعتدال شرقًا'),
           ('P10', -R_RING, 0, 'طرف الاعتدال غربًا'), ('P11', 0, G.yb - 0.25, 'نهاية لوح القاعدة جنوبًا'), ('P12', 0, G.fy + 0.15, 'نهاية لوح القاعدة شمالًا')]
    for n, x, y, _ in pts:
        a = P(x, y); sh.circle(a, 1.3, fill=RED, sw=0); sh.ltr(a[0] + 2, a[1] - 2.5, n, 2.4, 'start', SANS, RED, 700)
    rows = []
    for n, x, y, d in pts:
        E, N = to_grid(x, y); rows.append((n, f'{x:+.3f}', f'{y:+.3f}', f'{E:.3f}', f'{N:.3f}', d))
    table(sh, 830, 70, ['النقطة', 'x', 'y', 'E شبكي', 'N شبكي', 'الوصف'], rows, [12, 15, 15, 22, 22, 48], 2.2, 5.2, ltr_cols=(1, 2, 3, 4))
    dimh(sh, P(-7.25, -7.7), P(7.25, -7.7), P(0, -7.7)[1] + 8, 'Ø 14.500')
    dimh(sh, P(-6.35, 6.9), P(6.35, 6.9), P(0, 6.9)[1] - 4, 'Ø 12.700')
    dimv(sh, P(-0.3, 0), P(-0.3, G.yb), P(-0.3, 0)[0] - 10, f'{-G.yb:.3f}')
    dimv(sh, P(0.3, 0), P(0.3, G.fy), P(0.3, 0)[0] + 8, f'{G.fy:.3f}')
    with open(f'{OUT}/csv/X01_control_points.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['point', 'x_m', 'y_m', 'E_redbelt', 'N_redbelt', 'description']); [w.writerow(r) for r in rows]
    north_arrow(sh, 805, 470, GAMMA); scale_bar(sh, v, 705, 525, 5, 1)
    return sh


# ------------------------------------------------------------------ X-02 تقسيم البلاط
@reg('X-02', 'تقسيم بلاط الوجه وحلقة التقويم — 1:30')
def x02():
    sh = Sheet(); v = View(480, 297, 30); P = v.p
    tiles = G.tiles(); rs = G.ring_sectors()
    frame(sh, 'تقسيم بلاط الوجه وحلقة التقويم', [f'{len(tiles)} بلاطة رخام و36 قطاع جرانيت', 'لكل قطعة رقم وملف قص'], 'X-02', '1:30', DES,
          ['• البلاط 900 × 900 × 40 مم؛ الأعمدة A… من الغرب، والصفوف من الشمال.',
           f'• {sum(t["full"] for t in tiles)} بلاطة كاملة و{sum(not t["full"] for t in tiles)} بلاطة مقصوصة بالدائرة أو بشق النصل.',
           '• كل بلاطة تُقص وتُحفر في المصنع من ملفها: dxf/tiles/<الرقم>.dxf',
           '   (الأصل ركنها الجنوبي الغربي، الوحدة مم)، ويُكتب رقمها على ظهرها.',
           '• شق النصل: 40 مم على خط الزوال من P5−20 إلى P6+20 مم.',
           '• قطاعات الحلقة 36 × 10° من الشمال باتجاه عقارب الساعة (R01…R36).',
           '• الفواصل 2 مم إيبوكسي بلون الحجر؛ لا فواصل تمدد داخل الوجه.'])
    sh.circle(P(0, 0), R_RING*v.k, fill='#e9e1cf', sw=0.6)
    for r in rs:
        sh.poly([P(x, y) for x, y in r['poly'].exterior.coords], close=True, stroke=INK, sw=0.3)
        am = rad((r['a0'] + r['a1'])/2); x, y = P(6.8*sin(am), 6.8*cos(am))
        sh.ltr(x, y, r['id'], 2.0, 'middle', SANS, INK, 700)
    sh.circle(P(0, 0), R_FACE*v.k, fill='#f8f4ea', sw=0.6)
    tile_grid(sh, P, ids=True, size=1.7, col='#5a554d')
    sh.line(P(0, G.yb), P(0, G.fy), stroke=TERRA, sw=1.4)
    tw = sum(t['poly'].area for t in tiles)
    sh.text(830, 100, 'ملخص الكميات', 3.4, 'end', KUFI, INK, 700)
    rows = [('بلاط الوجه (صافي)', f'{tw:.1f} م²'), ('عدد البلاطات', f'{len(tiles)}'), ('قطاعات الحلقة', f'36 ({pi*(R_RING**2 - R_FACE**2):.1f} م²)'),
            ('طول الحافة', f'{2*pi*R_RING:.1f} م'), ('هالك مقترح للرخام', '12%')]
    table(sh, 830, 110, ['البند', 'الكمية'], rows, [40, 30], 2.5, 6.5, ltr_cols=(1,))
    north_arrow(sh, 805, 470); scale_bar(sh, v, 735, 525, 3, 1)
    return sh


# ------------------------------------------------------------------ X-03 الحفر والتطعيم
ENGRAVE = [('خطوط الساعات', 'راتنج أسود عرض 8 مم'), ('أنصاف الساعات / الأرباع', 'راتنج أسود 4 مم / رمادي 2 مم'),
           ('المنقلبان والاعتدال', 'شريط نحاس 8 مم'), ('بقية مدارات البروج', 'شريط نحاس 5 مم'), ('خط الزوال', 'شريط نحاس 30 مم'),
           ('العصر الأول / الثاني', 'راتنج فيروزي 8 / 5 مم متقطع'), ('منحنى ١٢ ظهرًا', 'راتنج بنفسجي 5 مم'), ('القبلة', 'راتنج أزرق 8 مم'),
           ('أرقام الساعات', 'أقراص نحاس Ø150 محفورة الرقم'), ('النجوم والعلامات', 'نحاس مطعّم / مينا زرقاء Ø80'),
           ('النصوص ولوح معادلة الزمن', 'حفر 3 مم مملوء راتنج بني')]


@reg('X-03', 'لوحة الحفر والتطعيم على البلاط — 1:30')
def x03():
    meta = ('لوحة الحفر والتطعيم على البلاط', ['خطوط الوجه فوق شبكة البلاط', 'مطابقة للوحة A-01'], 'X-03', '1:30', DES,
            ['• عمق الحفر 6 مم لكل الخطوط والنصوص؛ يُملأ بالنحاس أو الراتنج',
             '   ثم يُصقل السطح كله مستويًا (±0.2 مم).',
             '• خطوط الساعات مزاحة 15 مم (نصف سمك النصل): الصباحية غربًا',
             '   والمسائية شرقًا؛ ولا تُزاح منحنيات العقدة.',
             '• الحفر بالـ CNC لكل بلاطة من ملفها؛ وتُرص البلاطات في المصنع',
             '   «رصًّا جافًّا» بالربع للتحقق من استمرار الخطوط (±0.5 مم).',
             '• الأرقام والنجوم والنصوص تُطعّم بعد التركيب بقوالب من DXF.',
             '• التفاوت: موضع الخط ±1 مم، والاستمرار عبر الفواصل ±0.5 مم.'])
    def ov(sh, v):
        tile_grid(sh, v.p, ids=False, col='#b7b0a2')
        y = 345; sh.text(830, y, 'مواصفة التطعيم', 3.4, 'end', KUFI, INK, 700); y += 7
        for a, b in ENGRAVE:
            sh.text(830, y, a, 2.4, 'end', SANS, INK, 700); sh.text(780, y, b, 2.3, 'end', SANS, INK); y += 5.4
    return sheet_a.a01(meta=meta, overlay=ov)


# ------------------------------------------------------------------ X-04 القطاعات والتفاصيل
@reg('X-04', 'القطاعات وتفاصيل البناء والأساس — 1:30 و1:5')
def x04():
    sh = Sheet()
    gn = G.gnomon()
    frame(sh, 'القطاعات وتفاصيل البناء والأساس', ['قطاع في خط الزوال، وتفاصيل البلاط والحافة', 'وأساس الشاخص'], 'X-04', '1:30 و1:20 و1:5', DES,
          ['• تربة: إحلال ودمك 95% بروكتور معدل؛ تجربة دمك كل 50 م².',
           '• أساس حصوي متدرج 250 مم على طبقتين.',
           '• بلاطة خرسانة مسلحة C30 سمك 150 مم، شبكتان Ø10 كل 150 مم.',
           '• قاعدة الشاخص: شريط خرساني 5.0 × 1.0 × 0.6 م (C30)، حديد',
           '   Ø16 كل 150 مم سفلي وعلوي، متصل بالبلاطة.',
           '• لوح القاعدة 30 مم على صواميل ضبط ومونة غير منكمشة 30 مم؛',
           '   سطحه العلوي −0.10؛ 12 مسمارًا كيميائيًّا M24 A4 تثبيت 250 مم.',
           '• التشطيب: مونة لصق 30 مم + رخام 40 مم = 70 مم فوق البلاطة.',
           '• الصرف: فواصل الحلقة الخارجية مفتوحة 6 مم فوق مجرى خطي',
           '   محيطي 100 مم يصب في شبكة الحديقة.',
           '• القيم الإنشائية مقترحة وتُراجع من مهندس إنشائي.'])
    k = 1000/30; ox, oy = 500, 150
    X = lambda y: ox + y*k; Z = lambda z: oy - z*k
    sh.text(ox, 52, 'القطاع أ–أ في خط الزوال (الشمال يمينًا) — 1:30', 3.6, 'middle', KUFI, INK, 700)
    sh.poly([(X(-8.2), Z(-0.18)), (X(-7.55), Z(-0.18)), (X(-7.55), Z(0)), (X(7.55), Z(0)), (X(7.55), Z(-0.18)), (X(8.2), Z(-0.18))], stroke=INK, sw=0.6)
    sh.rect(X(-7.55), Z(-0.07), 15.1*k, 0.15*k, fill='#c8c2b6', sw=0.25)
    sh.rect(X(-7.55), Z(-0.22), 15.1*k, 0.25*k, fill='#e3dccb', sw=0.25)
    sh.rect(X(-6.35), Z(0), 12.7*k, 0.07*k, fill='#f3eee3', sw=0.3)
    for a in (-7.25, 6.35): sh.rect(X(a), Z(0), 0.9*k, 0.07*k, fill='#b9b4ab', sw=0.3)
    for a in (-7.55, 7.25): sh.rect(X(a), Z(0), 0.3*k, 0.25*k, fill='#a8452e', sw=0.3)
    sh.rect(X(gn['y0'] - 0.5), Z(-0.22), 5.0*k, 0.6*k, fill='#bdb6a8', sw=0.3)
    sh.poly([(X(y), Z(z)) for y, z in gn['outer'].exterior.coords], close=True, fill='#9a6a3c', sw=0.4)
    for st in gn['stars']: sh.poly([(X(y), Z(z)) for y, z in st.exterior.coords], close=True, fill='#fffdf8', sw=0.15)
    sh.circle((X(G.fy), Z(G.h)), 1.5, fill=GOLD, sw=0.3)
    sh.line((X(-8.2), Z(0)), (X(8.2), Z(0)), stroke=RED, sw=0.2, dash='3 1'); sh.ltr(X(8.2) + 1, Z(0), '±0.00', 2.4, 'start', SANS, RED, 700)
    for z, t in [(-0.07, '−0.07 سطح البلاطة'), (-0.22, '−0.22'), (-0.47, '−0.47'), (-0.82, '−0.82 أسفل قاعدة الشاخص')]:
        sh.text(X(-7.9), Z(z), t, 2.0, 'end', SANS, GREY)
    dimv(sh, (X(G.fy), Z(0)), (X(G.fy), Z(G.h)), X(G.fy) + 8, f'{G.h*1000:.0f}')
    sh.text(X(-8.0), Z(0.15), 'الجنوب', 2.6, 'middle', KUFI, GREY, 700); sh.text(X(8.0), Z(0.15), 'الشمال', 2.6, 'middle', KUFI, GREY, 700)
    # مسقط الأساس 1:20
    k2 = 50; fx, fyy = 470, 270
    sh.text(fx, 238, 'مسقط أساس الشاخص ولوح القاعدة — 1:20 (الشمال يمينًا)', 3.2, 'middle', KUFI, INK, 700)
    Yp = lambda y: fx + (y - (gn['y0'] + G.fy)/2)*k2
    sh.rect(Yp(gn['y0'] - 0.5), fyy - 0.5*k2, 5.0*k2, 1.0*k2, fill='#e3dccb', stroke=INK, sw=0.4, )
    y1, y2 = gn['y0'] - 0.25, G.fy + 0.15
    sh.rect(Yp(y1), fyy - 0.15*k2, (y2 - y1)*k2, 0.30*k2, fill='#c7ccd0', sw=0.4)
    sh.rect(Yp(gn['y0']), fyy - 0.015*k2, (G.fy - gn['y0'])*k2, 0.03*k2, fill='#9a6a3c', sw=0.2)
    anc = [y1 + 0.12 + i*(y2 - y1 - 0.24)/5 for i in range(6)]
    for ay in anc:
        for dz in (-0.09, 0.09): sh.circle((Yp(ay), fyy + dz*k2), 1.2, fill='#fffdf8', sw=0.3)
    dimh(sh, (Yp(y1), fyy - 0.15*k2), (Yp(y2), fyy - 0.15*k2), fyy - 0.5*k2 - 6, f'لوح القاعدة {(y2 - y1)*1000:.0f} × 300 × 30')
    dimh(sh, (Yp(gn['y0'] - 0.5), fyy + 0.5*k2), (Yp(gn['y0'] + 4.5), fyy + 0.5*k2), fyy + 0.5*k2 + 8, 'قاعدة خرسانية 5000 × 1000 × 600')
    sh.text(fx, fyy + 0.5*k2 + 16, f'12 مسمار M24 على خطين بينهما 180 مم، خطوة {((y2 - y1 - 0.24)/5)*1000:.0f} مم — تُصب بقالب ثقب من ملف DXF', 2.3, 'middle', SANS, INK)
    # تفاصيل 1:5
    k5 = 200

    def lay(x0, y0, w, layers):
        y = y0
        for t, c in layers: sh.rect(x0, y, w, t*k5, fill=c, sw=0.25); y += t*k5
    x0, y0 = 200, 365; sh.text(x0 + 60, y0 - 10, 'ت1: البلاط والتطعيم والفاصل — 1:5', 3.0, 'middle', KUFI, INK, 700)
    lay(x0, y0, 120, [(0.04, '#f3eee3'), (0.03, '#d9d2c4'), (0.06, '#c8c2b6')])
    sh.rect(x0 + 59.6, y0, 0.8, 8, fill='#8f8a80', sw=0); sh.rect(x0 + 25, y0, 1.6, 1.2, fill='#c79a4a', sw=0); sh.rect(x0 + 90, y0, 1.6, 1.2, fill='#3b3a38', sw=0)
    for t, yy in [('فاصل 2 مم إيبوكسي', y0 + 3), ('تطعيم نحاس/راتنج عمق 6 مم', y0 + 10), ('مونة لصق 30 مم بتغطية كاملة', y0 + 17), ('بلاطة خرسانية', y0 + 24)]:
        sh.text(x0 + 125, yy, t, 2.2, 'start', SANS, INK)
    x0, y0 = 200, 455; sh.text(x0 + 60, y0 - 42, 'ت2: مرور النصل في الوجه — 1:5', 3.0, 'middle', KUFI, INK, 700)
    lay(x0, y0, 120, [(0.04, '#f3eee3'), (0.03, '#d9d2c4'), (0.03, '#9a9389'), (0.10, '#c8c2b6')])
    sh.rect(x0 + 40, y0 + 0.07*k5, 40, 0.03*k5, fill='#5f6a72', sw=0.3)
    sh.rect(x0 + 57, y0 - 35, 6, 35 + 0.07*k5, fill='#9a6a3c', sw=0.3)
    sh.rect(x0 + 55.5, y0, 1, 8, fill='#2f2f2f', sw=0); sh.rect(x0 + 63.5, y0, 1, 8, fill='#2f2f2f', sw=0)
    for ax in (x0 + 46, x0 + 74): sh.line((ax, y0 + 0.07*k5 - 6), (ax, y0 + 0.07*k5 + 55), stroke=INK, sw=0.8)
    for t, yy in [('نصل 30 مم', y0 - 25), ('فاصل بولي يوريثان 5 مم على جانبي النصل', y0 + 3), ('لوح قاعدة 30 مم سطحه −0.10', y0 + 15),
                  ('مونة غير منكمشة 30 مم وصواميل ضبط', y0 + 22), ('M24 A4 كيميائي تثبيت 250 مم', y0 + 45)]:
        sh.text(x0 + 125, yy, t, 2.2, 'start', SANS, INK)
    x0, y0 = 560, 365; sh.text(x0 + 60, y0 - 10, 'ت3: الحلقة والحافة والصرف — 1:5', 3.0, 'middle', KUFI, INK, 700)
    sh.rect(x0, y0, 70, 8, fill='#b9b4ab', sw=0.3); sh.rect(x0 + 70, y0 + 6, 20, 30, fill='#fffdf8', stroke=INK, sw=0.3)
    sh.rect(x0 + 90, y0, 60, 36, fill='#a8452e', sw=0.3); sh.rect(x0, y0 + 14, 70, 30, fill='#c8c2b6', sw=0.3)
    for t, yy in [('جرانيت الحلقة 40 مم، فواصل خارجية مفتوحة 6 مم', y0 - 3), ('مجرى خطي 100 × 150 بغطاء شقي ستانلس', y0 + 50), ('حافة جرانيت أحمر 300 × 180 مشطوفة 10', y0 + 40)]:
        sh.text(x0 + 155, yy, t, 2.2, 'start', SANS, INK)
    return sh


# ------------------------------------------------------------------ X-05 تصنيع الشاخص
@reg('X-05', 'رسم تصنيع الشاخص القطبي — 1:20')
def x05():
    sh = Sheet()
    gn = G.gnomon(); mass = gn['net_area']*0.030*7980
    frame(sh, 'رسم تصنيع الشاخص القطبي', ['لوح واحد 30 مم مقطوع بالماء', 'بإطار مصمت 120 مم ونجوم مفرغة'], 'X-05', '1:20', DES,
          ['• المادة: صلب مقاوم للصدأ 316L لوح 30 مم (EN 10088)، قطع بالماء',
           '   (Waterjet) من الملف dxf/A_gnomon_cut.dxf بتفاوت ±0.3 مم.',
           '• الضلع القطبي: حافة قائمة حادة بلا شطف، استقامتها ±0.5 مم/م؛',
           '   تُفحص بمسطرة ضبط أو جهاز ليزر بعد القطع.',
           f'• عدد النجوم المفرغة {len(gn["stars"])}، وأقل عرض بين الفتحات 30 مم.',
           f'• الكتلة ≈ {mass:.0f} كجم؛ نقطتا رفع مؤقتتان (ثقبا Ø40 في الإطار القاعدي)',
           '   تُسدّان بعد التركيب.',
           '• التشطيب: سفع زجاجي ثم طلاء سيراميكي برونزي (يُعمل على الأرض',
           '   بعد التصنيع)؛ تُحمى الحافة القطبية بشريط حتى التسليم.',
           '• بديل أخف: جلدان 10 مم على إطار داخلي (≈ 650 كجم) بنفس السمك',
           '   الكلي 30 مم؛ يحتاج حواف لكل نجمة ولحامًا أكثر.'])
    k = 50; oy = 255; cx = 500 - ((G.fy + gn['y0'])/2)*k
    Y = lambda y: cx + y*k; Z = lambda z: oy - z*k
    sh.text(500, 52, 'واجهة النصل — 1:20 (الشمال يمينًا)', 3.6, 'middle', KUFI, INK, 700)
    sh.poly([(Y(y), Z(z)) for y, z in gn['outer'].exterior.coords], close=True, fill='#d8b98a', sw=0.6)
    sh.poly([(Y(y), Z(z)) for y, z in gn['inner'].exterior.coords], close=True, stroke=GREY, sw=0.2, dash='2 1')
    for st in gn['stars']: sh.poly([(Y(y), Z(z)) for y, z in st.exterior.coords], close=True, fill='#fffdf8', sw=0.3)
    sh.poly(star_n(Y(G.fy), Z(G.h), 0.18*k, 0.18*k*0.62, 8, 22.5), close=True, fill='#e8c983', sw=0.4)
    sh.circle((Y(G.fy), Z(G.h)), 0.035*k, fill=GOLD, sw=0.3)
    sh.line((Y(gn['y0'] - 0.3), Z(0)), (Y(G.fy + 0.5), Z(0)), stroke=RED, sw=0.25, dash='3 1'); sh.ltr(Y(G.fy + 0.52), Z(0), '±0.00', 2.4, 'start', SANS, RED, 700)
    tz = 1.45; ty = G.fy
    sh.line((Y(ty), Z(tz)), (Y(ty - 0.6*cos(rad(LAT))), Z(tz - 0.6*sin(rad(LAT)))), stroke='#555', sw=0.04*k, cap='butt')
    dimh(sh, (Y(G.yb), Z(0)), (Y(G.fy), Z(0)), Z(-0.10) + 12, f'{(G.fy - G.yb)*1000:.1f}')
    dimh(sh, (Y(gn['y0']), Z(-0.10)), (Y(G.fy), Z(-0.10)), Z(-0.10) + 22, f'{(G.fy - gn["y0"])*1000:.1f}')
    dimv(sh, (Y(G.fy), Z(0)), (Y(G.fy), Z(G.h)), Y(G.fy) + 14, f'{G.h*1000:.1f}')
    dimv(sh, (Y(G.fy), Z(-0.10)), (Y(G.fy), Z(0)), Y(G.fy) + 26, '100')
    bx, bz = Y(G.yb), Z(0)
    sh.path(f'M{f(bx+40)},{f(bz)} A40,40 0 0 0 {f(bx+40*cos(rad(LAT)))},{f(bz-40*sin(rad(LAT)))}', stroke=BLUE, sw=0.4)
    sh.ltr(bx + 46, bz - 8, f'{LAT:.4f}°', 2.8, 'start', SANS, BLUE, 700)
    sh.text(Y(ty) - 32, Z(tz) + 10, 'أنبوب رصد نجم القطب Ø42.4 × 600', 2.3, 'end', SANS, INK)
    rows = [('B', 'قاعدة الضلع القطبي عند ±0.00', f'{G.yb:+.4f}', '0.0000'), ('N', 'العقدة: مركز الكرة', f'{G.fy:+.4f}', f'{G.h:.4f}'),
            ('S', 'الطرف السفلي الجنوبي', f'{gn["y0"]:+.4f}', '-0.1000'), ('C', 'الركن السفلي الشمالي', f'{G.fy:+.4f}', '-0.1000'),
            ('T', 'محور أنبوب الرصد عند الساق', f'{ty:+.4f}', f'{tz:.4f}')]
    table(sh, 830, 345, ['النقطة', 'الوصف', 'y (م)', 'z (م)'], rows, [14, 50, 20, 20], 2.4, 6, ltr_cols=(2, 3))
    sh.text(830, 390, 'y من مركز الدائرة نحو الشمال، وz من منسوب التشطيب؛ النصل في مستوى x = 0.', 2.3, 'end', SANS, GREY)
    sh.text(830, 397, 'الإطار 120 مم موازٍ للأضلاع؛ النجوم ثمانية (قطر خارجي 230 مم) على شبكة 240 مم.', 2.3, 'end', SANS, GREY)
    # تفصيل الشمسة 1:5
    c = (300, 470); k5 = 200
    sh.text(c[0], 410, 'تفصيل الشمسة والكرة — 1:5', 3.0, 'middle', KUFI, INK, 700)
    sh.poly(star_n(c[0], c[1], 0.18*k5, 0.18*k5*0.62, 8, 22.5), close=True, fill='#e8c983', sw=0.4)
    sh.circle(c, 0.035*k5, fill=GOLD, sw=0.4)
    sh.line((c[0] - 45, c[1]), (c[0] + 45, c[1]), stroke=RED, sw=0.2, dash='3 1 0.5 1'); sh.line((c[0], c[1] - 45), (c[0], c[1] + 45), stroke=RED, sw=0.2, dash='3 1 0.5 1')
    sh.text(c[0] + 50, c[1] - 8, 'الشمسة: لوح 316L 30 مم Ø360 ملحوم برأس النصل', 2.3, 'start', SANS, INK)
    sh.text(c[0] + 50, c[1], 'الكرة: نصفا كرة نحاس Ø70 على جانبيها بمسمار M10 يمر بالمركز', 2.3, 'start', SANS, INK)
    sh.text(c[0] + 50, c[1] + 8, 'مركز الكرة = N بتفاوت ±2 مم (يُقاس بالمحطة الشاملة)', 2.3, 'start', SANS, INK)
    bom = [('1', 'نصل الشاخص', '316L لوح 30 مم', f'{gn["net_area"]:.2f} م²', f'{mass:.0f}'),
           ('2', 'الشمسة', '316L لوح 30 مم Ø360', '1', '15'), ('3', 'الكرة', 'نحاس CuZn39Pb3 Ø70 نصفان', '1', '1.5'),
           ('4', 'أنبوب الرصد', '316L Ø42.4×2 طول 600', '1', '1.2'), ('5', 'لوح القاعدة', '316L 300×30 (X-04)', '1', '—')]
    table(sh, 830, 425, ['م', 'البند', 'المواصفة', 'الكمية', 'كجم'], bom, [8, 26, 46, 18, 12], 2.3, 5.8, ltr_cols=(3, 4))
    return sh


# ------------------------------------------------------------------ X-06 التركيب والمعايرة
ITP = [('H1', 'توقيع P0 وخط الزوال', 'GNSS-RTK + رصد شمسي', 'المساح + المستشار'),
       ('H2', 'تسليح وصب الأساس والمسامير', 'قالب المسامير من DXF ±3 مم', 'الإنشائي'),
       ('H3', 'استلام الشاخص في المصنع', 'الأبعاد والزاوية والاستقامة', 'المستشار'),
       ('H4', 'رص جاف لربع بلاط الوجه', 'استمرار الخطوط ±0.5 مم', 'المستشار'),
       ('H5', 'ضبط الشاخص قبل الحقن', 'ظل الضلع على الزوال عند الظهر', 'المستشار'),
       ('H6', 'استواء البلاط بعد التركيب', '±1 مم/3 م، كلي ±3 مم', 'المقاول + المستشار'),
       ('H7', 'المعايرة النهائية والاستلام', '5 قراءات، فرق ≤ 1 دقيقة', 'المستشار + المالك')]


@reg('X-06', 'تسلسل التنفيذ والتركيب والمعايرة ونقاط التوقف')
def x06():
    sh = Sheet()
    frame(sh, 'تسلسل التنفيذ والتركيب والمعايرة', ['كيف يُنفذ المقاول العمل في الموقع', 'ونقاط الفحص والتوقف'], 'X-06', '—', DES,
          ['• التفاصيل الكاملة في Method_Statement_A.docx.',
           '• «ص»: التاريخ في التوقيت الصيفي (UTC+3).',
           '• الظهر الحقيقي: عندها يقع ظل الضلع القطبي على خط الزوال',
           '   وظل الكرة على تدريج يوم الرصد.',
           '• y ظل الكرة: موضع مركز ظل الكرة على خط الزوال (م من P0).'])
    steps = ['## المراحل',
             '١. الاعتمادات: رسومات الورشة، عينات الرخام والنحاس والراتنج، بلاطة تجريبية محفورة، نتيجة النموذج 1:15.',
             '٢. التوقيع: P0 وخط الزوال بالـ GNSS-RTK ثم تحقق شمسي عند الظهر الحقيقي (H1).',
             '٣. الحفر والإحلال والدمك، ثم صب أساس الشاخص بالمسامير في قالبها، ثم البلاطة (H2). معالجة 7 أيام.',
             '٤. في المصنع بالتوازي: قطع الشاخص بالماء وفحصه (H3)، وقص البلاط وحفره بالـ CNC وتطعيمه ورصه جافًّا (H4).',
             '٥. تركيب الشاخص بالرافعة على صواميل الضبط، وضبط الاتجاه والزاوية، ثم التحقق الشمسي (H5)، ثم حقن المونة.',
             '٦. تركيب البلاط برقمه بدءًا من فواصل الزوال والاعتدال باتجاه المحيط، ثم قطاعات الحلقة والحافة (H6).',
             '٧. تطعيم الأرقام والنجوم والنصوص بالقوالب، والصقل النهائي، وتركيب الكرة وأنبوب الرصد.',
             '٨. المعايرة والاستلام: قراءات في يوم مشمس مقارنة بالجدول، ومحضر استلام (H7).']
    sh.para(830, 60, steps, 2.9, 1.7)
    table(sh, 830, 175, ['النقطة', 'البند', 'المعيار', 'المسؤول'], ITP, [16, 60, 60, 40], 2.6, 7)
    tol = [('استواء الوجه', '±1 مم / 3 م، والكلي ±3 مم'), ('اتجاه خط الزوال', '±0.02°'), ('زاوية الضلع القطبي', '30.0054° ±0.05°'),
           ('موضع العقدة أفقيًّا / رأسيًّا', '±3 مم / ±2 مم'), ('موضع الخطوط المحفورة', '±1 مم'), ('استقامة الضلع القطبي', '±0.5 مم / م')]
    table(sh, 830, 255, ['البند', 'حد التفاوت'], tol, [60, 60], 2.6, 7)
    rows = []
    for mo in range(1, 13):
        for d in (1, 15):
            dd = dt.date(REF_YEAR, mo, d); dec, eot, _ = sun_on(dd); dst = egypt_dst(dd)
            p = project(G.nodus, dec, 0)
            rows.append((f'{d} {GREG_MONTHS[mo-1]}', fmt_hm(clock_from_H(0, eot, dst=dst)) + (' ص' if dst else ''), f'{eot:+.1f}', f'{p[1]:+.3f}'))
    sh.text(505, 175, 'جدول التحقق بالشمس في الموقع (2027)', 3.4, 'middle', KUFI, INK, 700)
    table(sh, 600, 185, ['التاريخ', 'الظهر الحقيقي', 'معادلة الزمن', 'y ظل الكرة'], rows[:12], [24, 24, 22, 22], 2.4, 6.3, ltr_cols=(1, 2, 3))
    table(sh, 500, 185, ['التاريخ', 'الظهر الحقيقي', 'معادلة الزمن', 'y ظل الكرة'], rows[12:], [24, 24, 22, 22], 2.4, 6.3, ltr_cols=(1, 2, 3))
    with open(f'{OUT}/csv/X06_noon_check.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['date_2027', 'true_noon_clock', 'eot_min', 'nodus_shadow_y_m']); [w.writerow(r) for r in rows]
    return sh


# ------------------------------------------------------------------ X-07 جدول الكميات
@reg('X-07', 'جدول الكميات المبدئي')
def x07():
    sh = Sheet()
    frame(sh, 'جدول الكميات المبدئي', ['محسوب من الرسومات للتسعير', 'الكميات صافية بلا هالك ما لم يُذكر'], 'X-07', '—', DES,
          ['• الأطوال محسوبة من هندسة الخطوط نفسها.', '• يضيف المقاول الهالك وفق طريقة عمله.', '• البنود الإنشائية تقديرية حتى المراجعة الإنشائية.'])
    rows = boq_rows()
    table(sh, 830, 60, ['م', 'البند', 'الوحدة', 'الكمية'], rows, [10, 140, 20, 24], 2.6, 7.2, ltr_cols=(3,))
    with open(f'{OUT}/csv/X07_BOQ.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['item', 'description', 'unit', 'qty']); [w.writerow(r) for r in rows]
    return sh


def boq_rows():
    gn = G.gnomon(); tiles = G.tiles(); L = lengths()
    face = sum(t['poly'].area for t in tiles); ring = pi*(R_RING**2 - R_FACE**2)
    slab = pi*7.55**2
    yb1, yb2 = gn['y0'] - 0.25, G.fy + 0.15
    rows = [('1', 'حفر وإحلال ودمك تحت الساحة (عمق 0.50 م)', 'م³', f'{slab*0.5:.1f}'),
            ('2', 'أساس حصوي متدرج 250 مم', 'م³', f'{slab*0.25:.1f}'),
            ('3', 'خرسانة مسلحة C30 للبلاطة 150 مم', 'م³', f'{slab*0.15:.1f}'),
            ('4', 'خرسانة مسلحة C30 لأساس الشاخص 5.0×1.0×0.6', 'م³', '3.0'),
            ('5', 'مسامير كيميائية M24 A4-70 بطول 350 مم', 'عدد', '12'),
            ('6', f'رخام جلالة 40 مم مقصوص ومحفور ({len(tiles)} بلاطة)', 'م²', f'{face:.1f}'),
            ('7', 'جرانيت رمادي 40 مم لحلقة التقويم (36 قطاعًا)', 'م²', f'{ring:.1f}'),
            ('8', 'حافة جرانيت أحمر أسوان 300×180', 'م.ط', f'{2*pi*7.40:.1f}'),
            ('9', 'مجرى صرف خطي محيطي 100 مم بغطاء ستانلس', 'م.ط', f'{2*pi*7.40:.1f}')]
    i = 10
    for (fam, spec), v in L.items():
        rows.append((str(i), f'حفر وتطعيم: {FAM_AR.get(fam, fam)} — {spec} مم', 'م.ط', f'{v:.1f}')); i += 1
    rows += [(str(i), 'حفر وتطعيم كتابة الحلقة (الأشهر والبروج والمنازل) ولوح معادلة الزمن والنصوص', 'مقطوعية', '1'),
             (str(i + 1), 'أقراص أرقام الساعات نحاس Ø150 ونجوم مطعمة', 'عدد', '13 + 12'),
             (str(i + 2), f'الشاخص: لوح 316L 30 مم قطع بالماء ({gn["net_area"]:.2f} م²)', 'كجم', f'{gn["net_area"]*0.03*7980:.0f}'),
             (str(i + 3), f'لوح القاعدة 316L {(yb2 - yb1)*1000:.0f}×300×30', 'كجم', f'{(yb2 - yb1)*0.3*0.03*7980:.0f}'),
             (str(i + 4), 'الشمسة والكرة وأنبوب الرصد', 'مقطوعية', '1'),
             (str(i + 5), 'طلاء سيراميكي برونزي للشاخص', 'م²', f'{2*gn["net_area"]:.1f}'),
             (str(i + 6), 'أعمال التوقيع المساحي (GNSS-RTK) والتحقق', 'مقطوعية', '1'),
             (str(i + 7), 'نقل وتركيب الشاخص بالرافعة وضبطه وحقن المونة', 'مقطوعية', '1')]
    return rows


# ------------------------------------------------------------------ النموذج 1:15
@reg('M-01', 'النموذج المصغر 1:15 — الترتيب العام والمواد')
def m01():
    sh = Sheet()
    gm = g.gnomon(embed=0.0075, frame=0.12*1.4, tile=0.24*1.4, web=0.03*1.4)
    frame(sh, 'النموذج المصغر 1:15 — الترتيب العام', ['نموذج اختبار للتحقق من الحساب', 'قبل تصنيع الشاخص وحفر الرخام'], 'M-01', '1:4', 'النموذج المصغر للتصميم (أ)',
          [f'• مقياس 1:15: الوجه Ø{2*g.R*1000:.0f} مم والحلقة Ø{2*g.Rr*1000:.0f} مم، والعقدة على',
           f'   ارتفاع {g.h*1000:.1f} مم فوق ({0:.0f}, {g.fy*1000:+.1f}) مم.',
           '• الخطوط محسوبة مباشرة لأبعاد النموذج بسمك نصل 2 مم',
           '   (إزاحة خطوط الساعات ±1 مم).',
           '• الوجه: طباعة UV مباشرة على Dibond 3 مم من القالب M-02',
           '   بالحجم الطبيعي (تحقق من مسطرة 100 مم).',
           '• النصل: صلب 304 سمك 2 مم ليزر من M-03 بلسانين،',
           '   والعقدة كرة نحاس Ø4.5 مم ملحومة بالفضة؛ النجوم أكبر وأقل عددًا',
           '   من الأصل (زخرفية فقط ولا تؤثر في القراءة).',
           '• القاعدة: خشب بحري 18 مم 1050 × 1050 بثلاث أرجل M10 وميزان.',
           '• تكلفة تقريبية منخفضة؛ مدة التنفيذ 3–5 أيام عمل.'])
    k = 250; ox, oy = 450, 200
    P = lambda x, y: (ox + x*k, oy - y*k)
    sh.rect(*P(-0.525, 0.525), 1.05*k, 1.05*k, fill='#d9c4a0', sw=0.6)
    sh.circle(P(0, 0), g.Rr*k, fill='#efe5cf', sw=0.4); sh.circle(P(0, 0), g.R*k, fill='#f8f4ea', sw=0.4)
    for fam, lbl, segs, spec in g.families():
        col = {'DECL': TERRA, 'ASR1': TEAL, 'ASR2': TEAL, 'NOON': PURPLE, 'MERID': GOLD, 'QIBLA': BLUE}.get(fam, INK)
        for sg in segs:
            if len(sg) > 1: sh.poly([P(*q) for q in sg], stroke=col, sw=0.3 if fam != 'HOUR15' else 0.12)
    sh.line(P(0, g.yb), P(0, g.fy), stroke=INK, sw=1.0)
    for fx, fy in [(-0.47, 0.47), (0.47, 0.47), (0, -0.48)]: sh.circle(P(fx, fy), 4, fill='#5f6a72', sw=0.3)
    dimh(sh, P(-0.525, 0.525), P(0.525, 0.525), P(0, 0.525)[1] - 8, '1050')
    sh.text(P(0, 0.525)[0], P(0, 0.525)[1] - 16, 'الشمال الحقيقي', 2.8, 'middle', KUFI, INK, 700)
    vy = 430; Y = lambda y: ox + y*k*2; Zz = lambda z: vy - z*k*2
    sh.text(ox, 345, 'الواجهة الشرقية للنصل — 1:2', 3.0, 'middle', KUFI, INK, 700)
    sh.rect(Y(-0.30), Zz(0), 0.62*k*2, 0.021*k*2, fill='#d9c4a0', sw=0.4)
    sh.poly([(Y(y), Zz(z)) for y, z in gm['outer'].exterior.coords], close=True, fill='#b9bec2', sw=0.4)
    for st in gm['stars']: sh.poly([(Y(y), Zz(z)) for y, z in st.exterior.coords], close=True, fill='#fffdf8', sw=0.2)
    sh.circle((Y(g.fy), Zz(g.h)), 2.2, fill=GOLD, sw=0.3)
    dimv(sh, (Y(g.fy), Zz(0)), (Y(g.fy), Zz(g.h)), Y(g.fy) + 8, f'{g.h*1000:.1f}')
    dimh(sh, (Y(g.yb), Zz(0)), (Y(g.fy), Zz(0)), Zz(0) + 18, f'{(g.fy - g.yb)*1000:.1f}')
    bom = [('1', 'القاعدة', 'خشب بحري 18 مم 1050×1050', '1'), ('2', 'الوجه', 'Dibond 3 مم طباعة UV (M-02)', '1'),
           ('3', 'النصل', 'صلب 304 سمك 2 مم ليزر (M-03)', '1'), ('4', 'العقدة', 'كرة نحاس Ø4.5', '1'),
           ('5', 'أرجل الضبط', 'M10 مع صواميل', '3'), ('6', 'ميزان', 'فقاعة ثنائي المحور', '1')]
    table(sh, 830, 345, ['م', 'البند', 'المواصفة', 'العدد'], bom, [8, 22, 52, 12], 2.3, 5.8)
    return sh


@reg('M-02', 'قالب وجه النموذج بالحجم الطبيعي (1050 × 1050 مم)')
def m02():
    sh = Sheet(1050, 1050); k = 1000; c = 525
    P = lambda x, y: (c + x*k, c - y*k)
    sh.rect(3, 3, 1044, 1044, sw=0.3)
    sh.circle(P(0, 0), g.Rr*k, fill='#efe5cf', sw=0.5)
    for mo in range(12):
        th = ring_angle(dt.date(REF_YEAR, mo + 1, 1)); x0, y0 = polar_v(g.R, th); x1, y1 = polar_v(g.Rr, th)
        sh.line(P(x0, y0), P(x1, y1), sw=0.4)
        mid = ring_angle(dt.date(REF_YEAR, mo + 1, 15)); x, y = polar_v((g.R + g.Rr)/2, mid)
        rot = mid if (mid % 360) < 90 or (mid % 360) > 270 else mid + 180
        sh.text(*P(x, y), GREG_MONTHS[mo], 9, 'middle', KUFI, INK, 700, rot)
    sh.circle(P(0, 0), g.R*k, fill='#fbf8f1', sw=0.5)
    cols = {'HOUR': (INK, 0.7), 'HOUR30': (INK, 0.35), 'HOUR15': ('#8a847c', 0.18), 'DECL': (TERRA, 0.6), 'ASR1': (TEAL, 0.7), 'ASR2': (TEAL, 0.5),
            'NOON': (PURPLE, 0.5), 'MERID': (GOLD, 2.0), 'QIBLA': (BLUE, 0.6), 'TICKS': (INK, 0.3)}
    for fam, lbl, segs, spec in g.families():
        col, sw = cols.get(fam, (INK, 0.3))
        for sg in segs:
            if len(sg) > 1: sh.poly([P(*q) for q in sg], stroke=col, sw=sw, dash='3 2' if 'متقطع' in spec else None)
    for H, segs in g.A.hours.items():
        if abs(H - round(H/15)*15) > 0.01 or not segs: continue
        s0 = max(segs, key=len); far = max(s0, key=lambda p: p[0]**2 + p[1]**2)
        far = (far[0]/MS, far[1]/MS); r = hypot(*far)
        pt = (far[0]*(1 - 0.03/r), far[1]*(1 - 0.03/r)) if r > g.R - 0.005 else far
        x, y = P(*pt); sh.circle((x, y), 7, fill='#fffdf8', stroke=INK, sw=0.4)
        sh.text(x, y + 0.3, ar_digits(int(round(12 + H/15)) % 12 or 12), 9, 'middle', KUFI, INK, 700)
    for dec, names, dates, lam, segs in g.A.signs:
        s0 = max(segs, key=len); e = s0[0]; x, y = P(e[0]/MS, e[1]/MS)
        sh.text(x + 4, y - 4, f'{names[0]} {ar_digits(dates[0].day)} {GREG_MONTHS[dates[0].month-1]}', 5, 'start', NASKH, TERRA, 700)
    sh.line(P(0, g.yb), P(0, g.fy), stroke=RED, sw=0.4, dash='2 1')
    for (a, b) in tabs_model():
        sh.rect(*P(-0.0011, b), 2.2, (b - a)*1000, stroke=RED, sw=0.4)
    for cx, cy in [(30, 30), (1020, 30), (1020, 1020), (30, 1020)]:
        sh.line((cx - 10, cy), (cx + 10, cy), sw=0.3); sh.line((cx, cy - 10), (cx, cy + 10), sw=0.3)
    sh.rect(60, 990, 100, 4, fill=INK, sw=0); sh.ltr(110, 1003, '100 mm CHECK', 4, 'middle', SANS, INK, 700)
    sh.text(1030, 1000, 'M-02 • قالب وجه النموذج 1:15 بالحجم الطبيعي — اطبع بمقياس 100% • الشمال إلى أعلى', 6, 'end', KUFI, INK, 700)
    sh.text(1030, 1012, 'الخط الأحمر المتقطع: محور النصل • المستطيلان الأحمران: شقّا اللسانين 2.2 مم', 5, 'end', SANS, GREY)
    return sh


def polar_v(r, th): return (r*sin(rad(th)), r*cos(rad(th)))


def tabs_model():
    return [(g.yb + 0.03, g.yb + 0.045), (g.fy - 0.025, g.fy - 0.01)]


def model_blade():
    gm = g.gnomon(embed=0.0075, frame=0.12*1.4, tile=0.24*1.4, web=0.03*1.4)
    o = gm['outer']
    for a, b in tabs_model(): o = o.union(box(a, -0.0205, b, 0.0))
    return o, gm['stars']


@reg('M-03', 'قالب نصل النموذج بالحجم الطبيعي (A3)')
def m03():
    sh = Sheet(420, 297)
    o, stars = model_blade(); k = 1000
    ox = 210 - ((g.fy + g.yb)/2)*k; oy = 230
    Y = lambda y: ox + y*k; Z = lambda z: oy - z*k
    sh.rect(5, 5, 410, 287, sw=0.3)
    sh.poly([(Y(y), Z(z)) for y, z in o.exterior.coords], close=True, fill='#e3e6e8', sw=0.3)
    for st in stars: sh.poly([(Y(y), Z(z)) for y, z in st.exterior.coords], close=True, fill='#fffdf8', sw=0.25)
    sh.circle((Y(g.fy), Z(g.h)), 2.25, stroke=RED, sw=0.3)
    sh.line((Y(g.yb - 0.01), Z(0)), (Y(g.fy + 0.02), Z(0)), stroke=RED, sw=0.2, dash='2 1')
    dimh(sh, (Y(g.yb), Z(0)), (Y(g.fy), Z(0)), Z(0) + 32, f'{(g.fy - g.yb)*1000:.2f}')
    dimv(sh, (Y(g.fy), Z(0)), (Y(g.fy), Z(g.h)), Y(g.fy) + 12, f'{g.h*1000:.2f}')
    sh.ltr(Y(g.yb) + 30, Z(0) - 6, f'{LAT:.4f}°', 3, 'start', SANS, BLUE, 700)
    sh.rect(20, 275, 100, 3, fill=INK, sw=0); sh.ltr(70, 284, '100 mm CHECK', 3, 'middle', SANS, INK, 700)
    sh.text(400, 20, 'M-03 • قالب نصل النموذج 1:15 بالحجم الطبيعي — صلب 2 مم', 4, 'end', KUFI, INK, 700)
    sh.text(400, 28, 'الدائرة الحمراء: كرة نحاس Ø4.5 مركزها العقدة • المتقطع: سطح الوجه • اللسانان يدخلان القاعدة', 2.8, 'end', SANS, GREY)
    return sh


@reg('M-04', 'بروتوكول اختبار النموذج والقراءات المتوقعة')
def m04():
    sh = Sheet()
    frame(sh, 'بروتوكول اختبار النموذج ومعايرته', ['قراءات متوقعة لأيام الاختبار', 'ونموذج تسجيل الرصد'], 'M-04', '—', 'النموذج المصغر للتصميم (أ)',
          ['• الاختبار في القاهرة الكبرى (الفرق في الموقع مهمل).', '• الأوقات بالتوقيت الشتوي UTC+2 (بعد 29 أكتوبر 2026).',
           '• تُضبط الساعة المرجعية على توقيت الشبكة قبل الرصد.', '• معيار القبول: فرق الوقت ≤ 1 دقيقة،',
           '   وموضع ظل الكرة ≤ 1.5 مم من المتوقع.'])
    steps = ['## خطوات الاختبار', '١. ضع النموذج على سطح ثابت مكشوف للشمس من 9 صباحًا إلى 3 عصرًا.', '٢. اضبط الأرجل حتى تتوسط فقاعة الميزان في الاتجاهين.',
             '٣. التوجيه: أدِر النموذج حتى ينطبق ظل النصل على خط الزوال في وقت الظهر الحقيقي المبيّن، ثم ثبّته.',
             '٤. سجّل وقت انطباق ظل النصل على خطوط الساعات، وموضع ظل الكرة في الأوقات المبيّنة.',
             '٥. كرّر في ثلاثة أيام متباعدة؛ إن تجاوز الفرق الحد راجع الاستواء ثم زاوية النصل ثم الطباعة.']
    sh.para(830, 60, steps, 3.0, 1.7)
    dates = [dt.date(2026, 11, d) for d in (5, 15, 25)] + [dt.date(2026, 12, d) for d in (5, 15, 25)]
    rows, tips = [], []
    for d in dates:
        dec, eot, _ = sun_on(d); dst = egypt_dst(d)
        rows.append([f'{d.day} {GREG_MONTHS[d.month-1]}', fmt_hm(clock_from_H(0, eot, dst=dst))] +
                    [fmt_hm(clock_from_H(15*(T - 12) + g.A.corr, eot, dst=dst)) for T in (9, 10, 11, 13, 14, 15)])
        tr = [f'{d.day} {GREG_MONTHS[d.month-1]}']
        for t in (10, 12, 14):
            dec2, eot2, _ = sun_on(d, t); p = project(g.nodus, dec2, H_from_clock(t, eot2, dst=dst))
            tr.append(f'{p[0]*1000:+.1f} , {p[1]*1000:+.1f}')
        tips.append(tr)
    sh.text(830, 135, 'الوقت المتوقع لانطباق ظل النصل على خطوط الساعات (UTC+2)', 3.6, 'end', KUFI, INK, 700)
    table(sh, 830, 147, ['التاريخ', 'الزوال', '9', '10', '11', '1', '2', '3'], rows, [30, 26, 26, 26, 26, 26, 26, 26], 3.0, 8, ltr_cols=tuple(range(1, 8)))
    sh.text(830, 215, 'موضع ظل الكرة المتوقع (مم من مركز الوجه: x , y)', 3.6, 'end', KUFI, INK, 700)
    table(sh, 830, 227, ['التاريخ', '10:00', '12:00', '14:00'], tips, [30, 40, 40, 40], 3.0, 8, ltr_cols=(1, 2, 3))
    sh.text(830, 295, 'نموذج تسجيل الرصد', 3.6, 'end', KUFI, INK, 700)
    table(sh, 830, 307, ['التاريخ', 'الوقت المرصود', 'الخط', 'الوقت المتوقع', 'الفرق (د)', 'ظل الكرة x,y', 'ملاحظات'], [('',)*7]*10,
          [36, 46, 26, 46, 36, 56, 110], 3.0, 10)
    sh.text(830, 425, 'الراصد: ____________    التوقيع: ____________    حالة السماء: ____________', 3.2, 'end', SANS, INK)
    with open(f'{OUT}/csv/M04_test_predictions.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['date', 'true_noon', 'l9', 'l10', 'l11', 'l13', 'l14', 'l15']); [w.writerow(r) for r in rows]
        w.writerow([]); w.writerow(['date', 'nodus_10', 'nodus_12', 'nodus_14']); [w.writerow(r) for r in tips]
    return sh


# ------------------------------------------------------------------ ملفات القص DXF بالحجم الكامل
LAYCOL = {'HOUR': 7, 'HOUR30': 8, 'HOUR15': 9, 'DECL': 30, 'ASR1': 4, 'ASR2': 4, 'NOON': 6, 'MERID': 40, 'QIBLA': 5, 'TICKS': 2, 'CUT': 1, 'ID': 3}


def newdoc():
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM
    for n, c in LAYCOL.items(): doc.layers.add(n, color=c)
    return doc


def dxfs(geo, prefix, tile_files=True):
    k = 1000
    fams = geo.families()
    doc = newdoc(); msp = doc.modelspace()
    for fam, lbl, segs, spec in fams:
        for sg in segs:
            if len(sg) > 1: msp.add_lwpolyline([(x*k, y*k) for x, y in sg], dxfattribs={'layer': fam})
    msp.add_circle((0, 0), geo.R*k, dxfattribs={'layer': 'CUT'}); msp.add_circle((0, 0), geo.Rr*k, dxfattribs={'layer': 'CUT'})
    if geo is G:
        for t in geo.tiles():
            msp.add_lwpolyline([(x*k, y*k) for x, y in t['poly'].exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
            c = t['poly'].representative_point(); msp.add_text(t['id'], height=60, dxfattribs={'layer': 'ID'}).set_placement((c.x*k, c.y*k))
        for r in geo.ring_sectors():
            msp.add_lwpolyline([(x*k, y*k) for x, y in r['poly'].exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
    doc.saveas(f'{OUT}/dxf/{prefix}_face.dxf')
    if geo is G and tile_files:
        lines = [(fam, LineString(sg)) for fam, lbl, segs, spec in fams for sg in segs if len(sg) > 1]
        for t in geo.tiles():
            ox, oy = t['origin']; d = newdoc(); ms = d.modelspace()
            L = lambda pts: [((x - ox)*k, (y - oy)*k) for x, y in pts]
            ms.add_lwpolyline(L(t['poly'].exterior.coords), close=True, dxfattribs={'layer': 'CUT'})
            for fam, ls in lines:
                inter = ls.intersection(t['poly'])
                if inter.is_empty: continue
                for part in getattr(inter, 'geoms', [inter]):
                    if part.geom_type == 'LineString' and part.length > 1e-4:
                        ms.add_lwpolyline(L(part.coords), dxfattribs={'layer': fam})
            ms.add_text(t['id'], height=40, dxfattribs={'layer': 'ID'}).set_placement((40, 40))
            d.saveas(f'{OUT}/dxf/tiles/{t["id"]}.dxf')


def gnomon_dxf(geo, path, model=False):
    d = newdoc(); ms = d.modelspace(); k = 1000
    if model:
        o, stars = model_blade()
    else:
        gn = geo.gnomon(); o, stars = gn['outer'], gn['stars']
    ms.add_lwpolyline([(y*k, z*k) for y, z in o.exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
    for st in stars: ms.add_lwpolyline([(y*k, z*k) for y, z in st.exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
    ms.add_circle((geo.fy*k, geo.h*k), (2.25 if model else 35), dxfattribs={'layer': 'ID'})
    d.saveas(path)


if __name__ == '__main__':
    for n, t, fn in SHEETS:
        sh = fn(); sh.save(f'{OUT}/svg/{n}.svg'); svg2dxf.sheet_to_dxf(sh, f'{OUT}/dxf_sheets/{n}.dxf'); print(n)
    dxfs(G, 'A'); dxfs(g, 'M'); gnomon_dxf(G, f'{OUT}/dxf/A_gnomon_cut.dxf'); gnomon_dxf(g, f'{OUT}/dxf/M_gnomon_cut.dxf', model=True)
    with open(f'{OUT}/csv/A_face_lines.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['family', 'label', 'spec', 'segment', 'point', 'x_m', 'y_m'])
        for fam, lbl, segs, spec in G.families():
            for si, sg in enumerate(segs):
                for pi_, (x, y) in enumerate(sg): w.writerow([fam, lbl, spec, si, pi_, f'{x:.4f}', f'{y:.4f}'])
    with open(f'{OUT}/csv/A_tiles.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['tile', 'full', 'area_m2', 'origin_x_m', 'origin_y_m'])
        for t in G.tiles(): w.writerow([t['id'], t['full'], f'{t["poly"].area:.4f}', f'{t["origin"][0]:.3f}', f'{t["origin"][1]:.3f}'])
    print('ok')
