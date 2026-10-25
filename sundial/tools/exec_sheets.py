"""الرسومات التنفيذية للتصميم (أ) والنموذج المصغر: E-01..E-05 وM-01..M-04."""
import sys, os, csv, datetime as dt
from exec_geom import *
from common import *
from sheet_shatir import draw_marble, legend, GREEN, YELLOW, PURP, BROWN, NAVY

OUT = '../execution'
for d in ('svg', 'pdf', 'png', 'dxf', 'csv'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
M = Dial()
m = Dial(scale=0.1, blade=0.003)
DES = 'التصميم (أ): المزولة الجامعة'


def mm(v): return f'{v*1000:.0f}'


def dimh(sh, a, b, y, txt, s=2.4, col=GREY):
    sh.line((a[0], y), (b[0], y), stroke=col, sw=0.2)
    for p in (a, b):
        sh.line((p[0], p[1]), (p[0], y + (1.5 if y > p[1] else -1.5)), stroke=col, sw=0.15)
        sh.line((p[0] - 1, y + 1), (p[0] + 1, y - 1), stroke=INK, sw=0.3)
    sh.ltr((a[0] + b[0])/2, y - 2.2, txt, s, 'middle', SANS, INK)


def dimv(sh, a, b, x, txt, s=2.4, col=GREY):
    sh.line((x, a[1]), (x, b[1]), stroke=col, sw=0.2)
    for p in (a, b):
        sh.line((p[0], p[1]), (x + (1.5 if x > p[0] else -1.5), p[1]), stroke=col, sw=0.15)
        sh.line((x - 1, p[1] + 1), (x + 1, p[1] - 1), stroke=INK, sw=0.3)
    sh.ltr(x + 2.2, (a[1] + b[1])/2, txt, s, 'middle', SANS, INK, rot=-90)


def table(sh, x_right, y, cols, rows, widths, size=2.3, rh=5.0, head_font=SANS, ltr_cols=()):
    """جدول من اليمين لليسار. widths بالمم."""
    xs = []; x = x_right
    for w in widths: xs.append((x - w, x)); x -= w
    tot = sum(widths)
    sh.rect(x_right - tot, y - rh/2 - 1, tot, rh + 2, fill='#e8dfcc', sw=0)
    for (a, b), c in zip(xs, cols): sh.text((a + b)/2, y, c, size, 'middle', head_font, INK, 700)
    y += rh + 2
    for i, r in enumerate(rows):
        if i % 2: sh.rect(x_right - tot, y - rh/2, tot, rh, fill='#f4eee2', sw=0)
        for j, ((a, b), v) in enumerate(zip(xs, r)):
            (sh.ltr if j in ltr_cols else sh.text)((a + b)/2, y, v, size, 'middle', SANS, INK)
        y += rh
    sh.line((x_right - tot, y - rh/2), (x_right, y - rh/2), stroke=GREY, sw=0.2)
    return y


def slab_grid(sh, P, Mx, labels=True, size=2.0):
    W2, D2 = Mx.W/2, Mx.Dp/2
    cw, rh = Mx.W/SLAB_COLS, Mx.Dp/SLAB_ROWS
    for c in range(1, SLAB_COLS): sh.line(P(-W2 + c*cw, -D2), P(-W2 + c*cw, D2), stroke='#9a9389', sw=0.18, dash='1.5 1')
    for r in range(1, SLAB_ROWS): sh.line(P(-W2, -D2 + r*rh), P(W2, -D2 + r*rh), stroke='#9a9389', sw=0.18, dash='1.5 1')
    if labels:
        for c in range(SLAB_COLS):
            for r in range(SLAB_ROWS):
                x, y = P(-W2 + (c + 0.5)*cw, D2 - (r + 0.5)*rh)
                sh.text(x, y, slab_name(c, r), size, 'middle', SANS, '#9a9389', 600)


# ------------------------------------------------------------------ E-01 مسقط التوقيع
def e01():
    sh = Sheet(); v = View(420, 300, 50); P = v.p
    frame(sh, 'مسقط التوقيع والنقاط المرجعية', ['التوقيع بالإحداثيات المحلية والشبكية', 'الشمال الحقيقي إلى أعلى اللوحة'], 'E-01', '1:50',
          DES, ['• الإحداثيات المحلية: الأصل مركز الدائرة، x شرقًا، y نحو الشمال',
                '   الحقيقي. الإحداثيات الشبكية: حزام مصر الأحمر (EPSG:22992).',
                f'• تقارب الشبكة γ = {GAMMA:.4f}°: الشمال الشبكي شرق الحقيقي؛',
                '   E = E0 + x·cosγ − y·sinγ ، N = N0 + y·cosγ + x·sinγ.',
                '• يُثبَّت P0 وP7 وP8 أولًا بجهاز GNSS (RTK) أو محطة شاملة،',
                '   ويُتحقق من خط الزوال بالرصد الشمسي (اللوحة E-05).',
                '• منسوب التشطيب ±0.00 لكل الدائرة (الوجه والحلقة)،',
                '   ويرتفع 180 مم عن منسوب الممر المحيط.',
                '• ألواح الوجه 12 × 8 لوحًا مقاس 950 × 700 × 40 مم.',
                '• الأبعاد بالمتر ما لم يُذكر غير ذلك.'])
    for r, col, fill in [(9.6, GREY, '#ece6da'), (7.25, INK, '#efe5cf'), (6.35, INK, '#f6f1e6')]:
        sh.circle(P(0, 0), r*v.k, stroke=col, sw=0.5, fill=fill)
    W2, D2 = M.W/2, M.Dp/2
    sh.poly([P(-W2, -D2), P(W2, -D2), P(W2, D2), P(-W2, D2)], close=True, fill='#fbf8f1', stroke=INK, sw=0.6)
    slab_grid(sh, P, M, size=1.8)
    sh.line(P(0, -7.6), P(0, 7.6), stroke=RED, sw=0.25, dash='4 1 0.6 1')
    sh.line(P(-7.6, 0), P(7.6, 0), stroke=RED, sw=0.25, dash='4 1 0.6 1')
    o, hole, p0 = gnomon_profile(M)
    sh.rect(*P(-0.15, M.fy + 0.12), 0.30*v.k, (M.fy + 0.12 - (p0[0] - 0.12))*v.k, stroke=TERRA, sw=0.4, fill='#f3d9c9')
    sh.line(P(0, p0[0]), P(0, M.fy), stroke=INK, sw=1.4)
    pts = [('P0', 0, 0, 'مركز الدائرة'), ('P1', -W2, D2, 'ركن الرخامة ش.غ'), ('P2', W2, D2, 'ركن الرخامة ش.ق'), ('P3', W2, -D2, 'ركن الرخامة ج.ق'),
           ('P4', -W2, -D2, 'ركن الرخامة ج.غ'), ('P5', 0, M.base[1], 'قاعدة الضلع القطبي عند ±0.00'), ('P6', 0, M.fy, f'مسقط العقدة (ارتفاعها {M.h:.3f})'),
           ('P7', 0, 7.25, 'طرف خط الزوال شمالًا'), ('P8', 0, -7.25, 'طرف خط الزوال جنوبًا'), ('P9', 7.25, 0, 'طرف خط الاعتدال شرقًا'), ('P10', -7.25, 0, 'طرف خط الاعتدال غربًا')]
    for n, x, y, _ in pts:
        a = P(x, y); sh.circle(a, 1.3, fill=RED, sw=0)
        sh.ltr(a[0] + 2, a[1] - 2.5, n, 2.4, 'start', SANS, RED, 700)
    dimh(sh, P(-W2, D2), P(W2, D2), P(0, D2)[1] - 10, f'{M.W:.2f}')
    dimv(sh, P(W2, D2), P(W2, -D2), P(W2, 0)[0] + 10, f'{M.Dp:.2f}')
    dimh(sh, P(-7.25, -7.6), P(7.25, -7.6), P(0, -7.6)[1] + 8, 'Ø 14.50')
    dimv(sh, P(-0.3, 0), P(-0.3, M.base[1]), P(-0.3, 0)[0] - 8, f'{-M.base[1]:.3f}')
    dimv(sh, P(-0.3, 0), P(-0.3, M.fy), P(-0.3, 0)[0] - 18, f'{-M.fy:.3f}')
    sh.text(P(0, 7.9)[0], P(0, 7.9)[1], 'خط الزوال (الشمال الحقيقي)', 2.6, 'middle', KUFI, RED, 700)
    sh.text(P(0.2, M.fy - 1.4)[0] + 3, P(0, M.fy - 1.4)[1], 'لوح قاعدة الشاخص', 2.3, 'start', SANS, TERRA, 700)
    rows = []
    for n, x, y, d in pts:
        E, N = to_grid(x, y)
        rows.append((n, f'{x:+.3f}', f'{y:+.3f}', f'{E:.3f}', f'{N:.3f}', d))
    table(sh, 830, 70, ['النقطة', 'x (م)', 'y (م)', 'E شبكي', 'N شبكي', 'الوصف'], rows, [12, 15, 15, 22, 22, 50], 2.2, 5.2, ltr_cols=(1, 2, 3, 4))
    with open(f'{OUT}/csv/E01_control_points.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['point', 'x_m', 'y_m', 'E_redbelt', 'N_redbelt', 'description']); [w.writerow(r) for r in rows]
    north_arrow(sh, 805, 470, GAMMA); scale_bar(sh, v, 705, 520, 5, 1)
    return sh


# ------------------------------------------------------------------ E-02 لوحة الحفر
SPEC = [('DECL', BROWN, 'مدارات البروج', 'شريط نحاس 5 × 6 مم (المنقلبان والاعتدال 8 مم)'),
        ('MERID', GOLD, 'خط الزوال', 'شريط نحاس 20 × 6 مم (بعرض النصل)'),
        ('HOUR', INK, 'الساعات المستوية', 'راتنج أسود: الساعة 6 مم، وكل 20 دقيقة 2 مم'),
        ('RISE', GREEN, 'الدائر من الطلوع', 'راتنج أخضر 3 مم'), ('SET', YELLOW, 'الباقي للغروب', 'راتنج أصفر 3 مم'),
        ('TEMP', NAVY, 'الساعات الزمانية', 'راتنج أزرق 2 مم، متقطع 40/25 مم'), ('ASR1', PURP, 'أول العصر', 'راتنج بنفسجي 6 مم'),
        ('ASR2', RED, 'العصر الثاني', 'راتنج أحمر 6 مم'), ('FAJR', TEAL, 'الباقي للفجر 13½ س', 'راتنج فيروزي 4 مم، متقطع')]


def e02():
    sh = Sheet(); v = View(470, 205, 25); P = v.p
    frame(sh, 'لوحة الحفر والتطعيم لوجه الرخامة', ['كل خطوط الوجه محسوبة لعرض 30.0054°', 'ومقسمة على ألواح التنفيذ'], 'E-02', '1:25',
          DES, ['• الوجه: رخام جلالة (أو ماثله) 40 مم مصقول مطفأ (honed).',
                '• عمق الحفر 6 مم لكل الخطوط؛ يُملأ بشريط نحاس أو راتنج',
                '   إيبوكسي ملوّن مقاوم للأشعة فوق البنفسجية.',
                '• خطوط الساعات مزاحة نصف سمك النصل (10 مم): الصباحية',
                '   غربًا والمسائية شرقًا؛ وخط الزوال بعرض النصل 20 مم.',
                '• الحفر بماكينة CNC لكل لوح منفردًا من ملف DXF المرفق',
                '   (طبقة لكل أسرة خطوط)، ثم الفحص بعد التركيب.',
                '• تفاوت موضع الخط ±1 مم، والاستمرار عبر الفواصل ±0.5 مم.',
                '• فواصل الألواح 2 مم بمونة إيبوكسي بلون الرخام.',
                '• الملفات: execution/dxf/A_face_fullscale.dxf',
                '   وexecution/csv/A_face_lines.csv (نقطة كل 25 مم).'])
    draw_marble(sh, M, P, v.k, big=False)
    slab_grid(sh, P, M, size=1.9)
    x, y = P(0, M.Dp/2 - 0.32)
    sh.text(x, y, 'وُضعت هذه الآلة الجامعة لعرض ل الفسطاط سنة ١٤٤٨هـ', 3.2, 'middle', NASKH, '#5b3d16', 700)
    dimh(sh, P(-M.W/2, M.Dp/2), P(M.W/2, M.Dp/2), P(0, M.Dp/2)[1] - 12, f'{M.W*1000:.0f}')
    dimv(sh, P(M.W/2, M.Dp/2), P(M.W/2, -M.Dp/2), P(M.W/2, 0)[0] + 8, f'{M.Dp*1000:.0f}')
    dimh(sh, P(-M.W/2, -M.Dp/2), P(-M.W/2 + 0.95, -M.Dp/2), P(0, -M.Dp/2)[1] + 7, '950')
    dimv(sh, P(-M.W/2, -M.Dp/2), P(-M.W/2, -M.Dp/2 + 0.70), P(-M.W/2, 0)[0] - 7, '700')
    y = 345
    sh.text(830, y, 'مواصفة الحفر والتطعيم', 3.4, 'end', KUFI, INK, 700); y += 8
    for fam, col, nm, spec in SPEC:
        sh.line((826, y), (814, y), stroke=col, sw=1.2)
        sh.text(811, y, nm, 2.5, 'end', SANS, INK, 700); sh.text(760, y, spec, 2.4, 'end', SANS, INK); y += 6
    # تفصيل الحفر 2:1
    ox, oy = 390, 400
    sh.text(ox + 70, oy - 10, 'تفصيل الحفر — 2:1', 3.2, 'middle', KUFI, INK, 700)
    sh.rect(ox, oy, 140, 80, fill='#efe9dc', sw=0.4)
    sh.rect(ox + 25, oy, 10, 12, fill='#c79a4a', sw=0.3); sh.rect(ox + 70, oy, 12, 12, fill='#3b3a38', sw=0.3); sh.rect(ox + 110, oy, 4, 12, fill='#3b3a38', sw=0.3)
    sh.text(ox + 30, oy + 18, 'نحاس 5 × 6', 2.2, 'middle', SANS, INK); sh.text(ox + 76, oy + 18, 'راتنج 6 × 6', 2.2, 'middle', SANS, INK); sh.text(ox + 112, oy + 18, 'راتنج 2 × 6', 2.2, 'middle', SANS, INK)
    sh.text(ox + 70, oy + 50, 'رخام 40 مم', 2.6, 'middle', SANS, GREY)
    sh.text(ox + 70, oy + 92, 'سطح الحشو مستوٍ مع الرخام بعد الصقل (±0.2 مم)', 2.3, 'middle', SANS, INK)
    legend(sh, 830, 60)
    return sh


# ------------------------------------------------------------------ E-03 القطاعات والتفاصيل
def layers_rect(sh, x0, y0, w, layers, k):
    y = y0
    for t, col, lbl in layers:
        sh.rect(x0, y, w, t*k, fill=col, sw=0.25)
        y += t*k
    return y


def e03():
    sh = Sheet()
    frame(sh, 'القطاعات وتفاصيل البناء', ['قطاع شمال–جنوب في خط الزوال', 'وتفاصيل الحافة والشاخص والفواصل'], 'E-03', '1:30 و1:5',
          DES, ['• التربة: إحلال وتسوية ودمك 95% (بروكتور المعدل).',
                '• أساس حصوي متدرج 250 مم مدموك على طبقتين.',
                '• بلاطة خرسانة مسلحة C30 سمك 150 مم، شبكتان Ø10 كل 150 مم،',
                '   فواصل تمدد عند حلقة 6.35 م فقط؛ لا فواصل تحت الوجه.',
                '• تسوية سطح البلاطة ±3 مم، ومونة لصق 30 مم إيبوكسي/أسمنتية.',
                '• الرخام 40 مم؛ حلقة التقويم جرانيت رمادي 40 مم.',
                '• الحافة جرانيت أحمر أسوان 180 × 300 مم مشطوفة 10 مم.',
                '• الصرف: الوجه أفقي تمامًا؛ تُترك فواصل الحلقة الخارجية',
                '   مفتوحة 6 مم فوق مجرى خطي خفي 100 مم على المحيط.',
                '• أساس الشاخص: تعميق البلاطة 400 مم أسفل لوح القاعدة',
                '   بعرض 800 مم وطول 3.6 م، حديد Ø12 كل 150 مم.'])
    k = 1000/30; ox, oy = 500, 150
    X = lambda y: ox + y*k
    Z = lambda z: oy - z*k
    sh.text(ox, 52, 'القطاع أ–أ: في خط الزوال (الشمال يمينًا) — 1:30', 3.6, 'middle', KUFI, INK, 700)
    sh.poly([(X(-8.2), Z(-0.18)), (X(-7.25 - 0.3), Z(-0.18)), (X(-7.25 - 0.3), Z(0)), (X(7.25 + 0.3), Z(0)), (X(7.25 + 0.3), Z(-0.18)), (X(8.2), Z(-0.18))], stroke=INK, sw=0.6)
    for a, b, z1, z2, col in [(-7.55, 7.55, -0.07, -0.22, '#c8c2b6'), (-7.55, 7.55, -0.22, -0.47, '#e3dccb')]:
        sh.rect(X(a), Z(z1), (b - a)*k, (z1 - z2)*k, fill=col, sw=0.25)
    sh.rect(X(-2.8), Z(0), 5.6*k, 0.07*k, fill='#f3eee3', sw=0.3)
    for s in (-1, 1):
        sh.rect(X(s*6.35 if s > 0 else -7.25), Z(0), 0.9*k, 0.07*k, fill='#b9b4ab', sw=0.3)
        sh.rect(X(s*7.25 if s > 0 else -7.55), Z(0), 0.3*k, 0.25*k, fill='#a8452e', sw=0.3)
    sh.rect(X(-4.9), Z(-0.22), 3.6*k, 0.40*k, fill='#c8c2b6', sw=0.3)
    o, hole, p0 = gnomon_profile(M)
    sh.poly([(X(y), Z(z)) for y, z in o.exterior.coords], close=True, fill='#9a6a3c', sw=0.4)
    sh.poly([(X(y), Z(z)) for y, z in hole.exterior.coords], close=True, fill='#fffdf8', sw=0.3)
    sh.circle((X(M.fy), Z(M.h)), 1.0, fill=GOLD, sw=0.3)
    sh.line((X(-8.2), Z(0)), (X(8.2), Z(0)), stroke=RED, sw=0.2, dash='3 1')
    sh.ltr(X(8.2) + 1, Z(0), '±0.00', 2.4, 'start', SANS, RED, 700)
    sh.ltr(X(8.2) + 1, Z(-0.18), '−0.18', 2.4, 'start', SANS, INK)
    for z, t in [(-0.07, '−0.07 سطح البلاطة'), (-0.22, '−0.22'), (-0.47, '−0.47')]:
        sh.text(X(-7.9), Z(z) + 1, t, 2.0, 'end', SANS, GREY)
    for yy, t in [(-2.8, 'رخام 40'), (-6.35, 'جرانيت التقويم'), (-7.25, 'الحافة')]:
        sh.line((X(yy) + 2, Z(0) - 1), (X(yy) + 6, Z(0) - 10), stroke=GREY, sw=0.2)
        sh.text(X(yy) + 7, Z(0) - 11, t, 2.2, 'start', SANS, INK)
    sh.text(X(-3.1), Z(-0.62) + 3, 'تعميق أساس الشاخص', 2.3, 'middle', SANS, INK)
    sh.text(X(0), Z(-0.6) + 3, 'خرسانة مسلحة 150 + أساس حصوي 250', 2.3, 'middle', SANS, INK)
    sh.text(X(-8.0), Z(0.1) - 3, 'الجنوب', 2.6, 'middle', KUFI, GREY, 700); sh.text(X(8.0), Z(0.1) - 3, 'الشمال', 2.6, 'middle', KUFI, GREY, 700)
    dimv(sh, (X(M.fy), Z(0)), (X(M.fy), Z(M.h)), X(M.fy) + 6, f'{M.h*1000:.0f}')
    # تفاصيل 1:5
    def det(x, y, title):
        sh.text(x + 60, y - 8, title, 3.0, 'middle', KUFI, INK, 700)
    k5 = 200
    # ت1 قاعدة الشاخص
    x0, y0 = 190, 330; det(x0, y0, 'ت1: قاعدة الشاخص — 1:5')
    sh.rect(x0, y0 + 0.07*k5 - 4, 120, 4, fill='#9a9389', sw=0.3)
    layers_rect(sh, x0, y0, 120, [(0.04, '#f3eee3', ''), (0.03, '#d9d2c4', ''), (0.15, '#c8c2b6', '')], k5)
    sh.rect(x0 + 40, y0 + 0.07*k5 - 2, 40, 4, fill='#5f6a72', sw=0.3)
    sh.rect(x0 + 58, y0 - 40, 4, 40 + 0.07*k5, fill='#9a6a3c', sw=0.3)
    for ax in (x0 + 46, x0 + 74):
        sh.line((ax, y0 + 0.07*k5 - 6), (ax, y0 + 0.07*k5 + 40), stroke=INK, sw=0.8)
    sh.rect(x0 + 55.5, y0, 1, 14, fill='#fffdf8', sw=0.1); sh.rect(x0 + 63.5, y0, 1, 14, fill='#fffdf8', sw=0.1)
    for t, yy in [('نصل 316L سمك 20 مم', y0 - 30), ('فاصل سيليكون 3 مم حول النصل', y0 + 4), ('لوح قاعدة 20 مم فوق مونة 30 مم غير منكمشة', y0 + 13),
                  ('مسامير كيميائية M20 A4 بطول تثبيت 200 مم', y0 + 40), ('لحام زاوية 8 مم على الجانبين', y0 - 8)]:
        sh.text(x0 + 125, yy, t, 2.2, 'start', SANS, INK)
    # ت2 الحفر والفواصل
    x0, y0 = 190, 460; det(x0, y0, 'ت2: فاصل الألواح والتطعيم — 1:5')
    layers_rect(sh, x0, y0, 120, [(0.04, '#f3eee3', ''), (0.03, '#d9d2c4', ''), (0.06, '#c8c2b6', '')], k5)
    sh.rect(x0 + 59.6, y0, 0.8, 8, fill='#a89f8c', sw=0)
    sh.rect(x0 + 25, y0, 1, 1.2, fill='#c79a4a', sw=0); sh.rect(x0 + 90, y0, 1.2, 1.2, fill='#3b3a38', sw=0)
    for t, yy in [('فاصل 2 مم إيبوكسي بلون الرخام', y0 + 4), ('شرائط النحاس والراتنج بعمق 6 مم', y0 + 12), ('مونة لصق 30 مم كاملة التغطية (لا بقع)', y0 + 20)]:
        sh.text(x0 + 125, yy, t, 2.2, 'start', SANS, INK)
    # ت3 الحافة والصرف
    x0, y0 = 560, 330; det(x0, y0, 'ت3: الحافة والصرف المحيطي — 1:5')
    sh.rect(x0, y0, 70, 8, fill='#b9b4ab', sw=0.3)
    sh.rect(x0 + 70, y0 + 6, 20, 30, fill='#fffdf8', stroke=INK, sw=0.3)
    sh.rect(x0 + 90, y0, 60, 36, fill='#a8452e', sw=0.3)
    sh.rect(x0, y0 + 14, 70, 30, fill='#c8c2b6', sw=0.3)
    for t, yy in [('جرانيت التقويم 40 مم بفواصل مفتوحة 6 مم', y0 - 2), ('مجرى خطي خفي 100 × 150 مم بغطاء شقي', y0 + 50), ('حافة جرانيت أحمر 180 × 300 مم', y0 + 40)]:
        sh.text(x0 + 155, yy, t, 2.2, 'start', SANS, INK)
    return sh


# ------------------------------------------------------------------ E-04 رسم تصنيع الشاخص
def e04():
    sh = Sheet()
    o, hole, p0 = gnomon_profile(M)
    area = o.area - hole.area; mass = area*0.02*7980
    bp_len = (M.fy + 0.15) - (p0[0] - 0.15); bp_mass = bp_len*0.30*0.02*7980
    frame(sh, 'رسم تصنيع الشاخص القطبي', ['نصل مثلث مفرّغ، ضلعه المائل موازٍ لمحور الأرض', 'وعقدة كروية عند رأسه'], 'E-04', '1:10 و1:2',
          DES, ['• المادة: صلب مقاوم للصدأ 316L، نصل 20 مم ولوح قاعدة 20 مم.',
                '• القص بالليزر أو بالماء من ملف DXF؛ الضلع القطبي مشغول',
                '   بحافة قائمة حادة (لا شطف) لتحديد الظل؛ استقامته ±0.5 مم/م.',
                '• العقدة: كرة نحاس Ø60 مم مفرزة بشق 20 مم، مركزها',
                '   على امتداد الضلع القطبي عند الإحداثي (y, z) المبيّن.',
                '• التشطيب: سفع رملي ثم طلاء PVD برونزي.',
                f'• كتلة النصل ≈ {mass:.0f} كجم، ولوح القاعدة ≈ {bp_mass:.0f} كجم.',
                '• التحقق بعد التصنيع: زاوية الضلع 30.005° ±0.05°،',
                '   ومركز العقدة 1600 ±2 مم فوق ±0.00 (1670 عن أسفل النصل).',
                '• الملف: execution/dxf/A_gnomon_fullscale.dxf'])
    k = 100; oy = 260; cx = 500 - ((M.fy + p0[0])/2)*k
    Y = lambda y: cx + y*k; Z = lambda z: oy - z*k
    sh.text(500, 52, 'واجهة النصل — 1:10 (الشمال يمينًا)', 3.6, 'middle', KUFI, INK, 700)
    sh.poly([(Y(y), Z(z)) for y, z in o.exterior.coords], close=True, fill='#d8b98a', sw=0.6)
    sh.poly([(Y(y), Z(z)) for y, z in hole.exterior.coords], close=True, fill='#fffdf8', sw=0.4)
    sh.line((Y(p0[0] - 0.3), Z(0)), (Y(M.fy + 0.4), Z(0)), stroke=RED, sw=0.25, dash='3 1')
    sh.ltr(Y(M.fy + 0.42), Z(0), '±0.00 FFL', 2.4, 'start', SANS, RED, 700)
    sh.rect(Y(p0[0] - 0.15), Z(-0.07), (bp_len)*k, 0.02*k, fill='#5f6a72', sw=0.3)
    sh.circle((Y(M.fy), Z(M.h)), 3.0, fill=GOLD, sw=0.4)
    # أبعاد
    dimh(sh, (Y(M.base[1]), Z(0)), (Y(M.fy), Z(0)), Z(-0.07) + 14, f'{(M.fy - M.base[1])*1000:.1f}')
    dimh(sh, (Y(p0[0]), Z(-0.07)), (Y(M.fy), Z(-0.07)), Z(-0.07) + 24, f'{(M.fy - p0[0])*1000:.1f}')
    dimv(sh, (Y(M.fy), Z(0)), (Y(M.fy), Z(M.h)), Y(M.fy) + 12, f'{M.h*1000:.1f}')
    dimv(sh, (Y(M.fy), Z(-0.07)), (Y(M.fy), Z(0)), Y(M.fy) + 22, '70')
    bx, bz = Y(M.base[1]), Z(0)
    sh.path(f'M{f(bx+40)},{f(bz)} A40,40 0 0 0 {f(bx+40*cos(rad(LAT)))},{f(bz-40*sin(rad(LAT)))}', stroke=BLUE, sw=0.4)
    sh.ltr(bx + 46, bz - 8, f'{LAT:.4f}°', 2.8, 'start', SANS, BLUE, 700)
    sh.text(Y(M.fy) - 3, Z(M.h) - 6, 'العقدة N', 2.5, 'end', SANS, INK, 700)
    sh.text(bx - 2, bz + 5, 'B', 2.5, 'end', SANS, INK, 700)
    # جدول الإحداثيات
    rows = [('B', 'قاعدة الضلع على المنسوب ±0.00', f'{M.base[1]:+.4f}', '0.0000'),
            ('N', 'مركز العقدة (رأس الضلع)', f'{M.fy:+.4f}', f'{M.h:.4f}'),
            ('S', 'طرف النصل السفلي جنوبًا', f'{p0[0]:+.4f}', f'{p0[1]:+.4f}'),
            ('C', 'الركن السفلي شمالًا', f'{M.fy:+.4f}', f'{p0[1]:+.4f}')]
    table(sh, 830, 370, ['النقطة', 'الوصف', 'y (م)', 'z (م)'], rows, [14, 52, 20, 20], 2.4, 6, ltr_cols=(2, 3))
    sh.text(830, 410, f'الفتحة الداخلية: إطار عرضه 120 مم موازٍ للأضلاع، وأركان مقوسة نصف قطرها 100 مم.', 2.3, 'end', SANS, INK)
    # لوح القاعدة 1:10 مسقط
    sh.text(420, 330, 'لوح القاعدة — مسقط 1:10', 3.0, 'middle', KUFI, INK, 700)
    y1, y2 = p0[0] - 0.15, M.fy + 0.15
    X2 = lambda y: 420 - ((y1 + y2)/2)*k + y*k
    sh.rect(X2(y1), 345, (y2 - y1)*k, 30, fill='#c7ccd0', sw=0.4)
    sh.rect(X2(p0[0]), 359, (M.fy - p0[0])*k, 2, fill='#9a6a3c', sw=0.2)
    anchors = [y1 + 0.10 + i*(y2 - y1 - 0.20)/3 for i in range(4)]
    for ay in anchors:
        for dx in (-10, 10): sh.circle((X2(ay), 360 + dx), 1.2, fill='#fffdf8', sw=0.3)
    dimh(sh, (X2(y1), 345), (X2(y2), 345), 340, f'{(y2 - y1)*1000:.0f}')
    sh.ltr(X2(y2) + 3, 360, '300', 2.4, 'start')
    sh.text(420, 384, f'8 ثقوب Ø24 لمسامير M20 على خطين بينهما 200 مم، بخطوة {((y2 - y1 - 0.20)/3)*1000:.0f} مم', 2.3, 'middle', SANS, INK)
    # تفصيل العقدة 1:2
    cx2, cy2 = 300, 470
    sh.text(cx2, 420, 'تفصيل العقدة — 1:2', 3.0, 'middle', KUFI, INK, 700)
    sh.circle((cx2, cy2), 15, fill='#e8c983', sw=0.5)
    sh.rect(cx2 - 5, cy2, 10, 15, fill='#fffdf8', stroke=INK, sw=0.3)
    sh.line((cx2 - 30*cos(rad(LAT)), cy2 + 30*sin(rad(LAT))), (cx2, cy2), stroke=INK, sw=0.6)
    sh.line((cx2, cy2), (cx2, cy2 + 35), stroke=INK, sw=0.6)
    sh.line((cx2 - 20, cy2), (cx2 + 20, cy2), stroke=RED, sw=0.2, dash='3 1 0.5 1'); sh.line((cx2, cy2 - 20), (cx2, cy2 + 20), stroke=RED, sw=0.2, dash='3 1 0.5 1')
    sh.text(cx2 + 22, cy2 - 6, 'كرة نحاس Ø60 مذهبة', 2.3, 'start', SANS, INK)
    sh.text(cx2 + 22, cy2 + 2, 'شق 20 مم بعمق 30 مم يُركب على رأس النصل', 2.3, 'start', SANS, INK)
    sh.text(cx2 + 22, cy2 + 10, 'مركز الكرة = N بتفاوت ±1 مم', 2.3, 'start', SANS, INK)
    # قائمة المواد
    bom = [('1', 'نصل الشاخص', '316L سمك 20', f'{area:.3f} م²', f'{mass:.0f}'),
           ('2', 'لوح القاعدة', f'316L {bp_len*1000:.0f}×300×20', '1', f'{bp_mass:.0f}'),
           ('3', 'العقدة', 'كرة نحاس Ø60', '1', '0.9'),
           ('4', 'مسامير التثبيت', 'M20 A4-70 كيميائية', '8', '—'),
           ('5', 'مونة التسوية', 'غير منكمشة 30 مم', '—', '—')]
    table(sh, 830, 440, ['م', 'البند', 'المواصفة', 'الكمية', 'كجم'], bom, [8, 30, 40, 18, 12], 2.3, 5.6, ltr_cols=(3, 4))
    return sh


# ------------------------------------------------------------------ E-05 التركيب والمعايرة
def noon_rows(year=REF_YEAR):
    rows = []
    for mo in range(1, 13):
        for d in (1, 15):
            dd = dt.date(year, mo, d); dec, eot, _ = sun_on(dd); dst = egypt_dst(dd)
            p = M.proj(dec, 0)
            rows.append((f'{d} {GREG_MONTHS[mo-1]}', fmt_hm(clock_from_H(0, eot, dst=dst)) + (' ص' if dst else ''), f'{eot:+.1f}', f'{p[1]:+.3f}', f'{M.h/ (M.fy - p[1]) if False else 0:.0f}'))
    return rows


def e05():
    sh = Sheet()
    frame(sh, 'التركيب والتوجيه والمعايرة الفلكية', ['خطوات التنفيذ وحدود التفاوت', 'وجداول التحقق بالشمس في الموقع'], 'E-05', '—',
          DES, ['• يُعمل بهذه اللوحة مع E-01 (النقاط) وE-04 (الشاخص).',
                '• «ص»: التاريخ في التوقيت الصيفي (UTC+3).',
                '• الظهر الحقيقي: لحظة مرور الشمس بخط الزوال؛ عندها يقع',
                '   ظل الضلع القطبي على خط الزوال وظل العقدة عليه أيضًا.',
                '• y ظل العقدة عند الظهر: موضع مركز ظل الكرة على خط الزوال',
                '   مقيسًا من مركز الدائرة (موجب شمالًا).',
                '• الحسابات لموقع المزولة: 30.0054° ش، 31.2443° ق.'])
    steps = ['## خطوات التركيب',
             '١. توقيع P0 وP7 وP8 بالـ GNSS-RTK وتثبيتها بمسامير نحاسية مؤقتة.',
             '٢. صب البلاطة وتعميق أساس الشاخص، وترك جيب لوح القاعدة بعمق 40 مم.',
             '٣. وضع لوح القاعدة على مسامير الضبط، وضبط محوره على خط الزوال (±1 مم).',
             '٤. تثبيت النصل مؤقتًا وضبط زاوية الضلع بميزان رقمي (30.005° ±0.05°).',
             '٥. التحقق الشمسي: عند ساعة الظهر الحقيقي في الجدول يجب أن ينطبق ظل',
             '    الضلع على خط الزوال؛ يُدار النصل حتى الانطباق ثم يُحقن المونة.',
             '٦. تركيب ألواح الرخام المحفورة بترتيب الشبكة، والتحقق من الاستواء.',
             '٧. تركيب العقدة والتحقق من موضع ظلها عند الظهر بحسب الجدول (±5 مم).',
             '٨. محضر استلام: قراءة 5 أوقات في يوم مشمس ومقارنتها بالساعة الرسمية',
             '    بعد تصحيح معادلة الزمن؛ الفرق المقبول ≤ 1 دقيقة.']
    sh.para(830, 60, steps, 3.2, 1.65)
    tol = [('استواء الوجه', '±1 مم / 3 م، والكلي ±3 مم'), ('اتجاه خط الزوال', '±0.02° (±2 مم على 5.6 م)'),
           ('زاوية الضلع القطبي', '30.0054° ±0.05°'), ('موضع العقدة أفقيًّا', '±3 مم'), ('ارتفاع العقدة', '±2 مم'),
           ('موضع الخطوط المحفورة', '±1 مم'), ('استقامة الضلع القطبي', '±0.5 مم / م')]
    table(sh, 380, 60, ['البند', 'حد التفاوت'], tol, [60, 80], 3.0, 7.5)
    rows = []
    for mo in range(1, 13):
        for d in (1, 15):
            dd = dt.date(REF_YEAR, mo, d); dec, eot, _ = sun_on(dd); dst = egypt_dst(dd)
            p = M.proj(dec, 0)
            rows.append((f'{d} {GREG_MONTHS[mo-1]}', fmt_hm(clock_from_H(0, eot, dst=dst)) + (' ص' if dst else ''), f'{eot:+.1f}', f'{p[1]:+.3f}'))
    sh.text(445, 225, 'جدول التحقق بالشمس في الموقع', 4.0, 'middle', KUFI, INK, 700)
    table(sh, 690, 240, ['التاريخ (2027)', 'الظهر الحقيقي', 'معادلة الزمن (د)', 'y ظل العقدة (م)'], rows[:12], [32, 32, 32, 32], 3.0, 8.5, ltr_cols=(1, 2, 3))
    table(sh, 330, 240, ['التاريخ (2027)', 'الظهر الحقيقي', 'معادلة الزمن (د)', 'y ظل العقدة (م)'], rows[12:], [32, 32, 32, 32], 3.0, 8.5, ltr_cols=(1, 2, 3))
    with open(f'{OUT}/csv/E05_noon_check.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['date_2027', 'true_noon_clock', 'eot_min', 'nodus_shadow_y_m']); [w.writerow(r) for r in rows]
    return sh


# ------------------------------------------------------------------ النموذج المصغر 1:10
BOARD = (-0.62, 0.62, -0.53, 0.33)
TABS = None


def model_profile():
    o, hole, p0 = gnomon_profile(m, embed=0.0001)
    from shapely.geometry import box
    tabs = [box(m.base[1] + 0.05, -0.021, m.base[1] + 0.07, 0.0), box(m.fy - 0.03, -0.021, m.fy - 0.01, 0.0)]
    for t in tabs: o = o.union(t)
    return o, hole, tabs


def m01():
    sh = Sheet()
    frame(sh, 'النموذج المصغر 1:10 — الترتيب العام', ['نموذج اختبار للتحقق من الحساب قبل التنفيذ', 'يُركب ويُختبر في القاهرة'], 'M-01', '1:5',
          'النموذج المصغر للتصميم (أ)',
          ['• مقياس النموذج 1:10 لكل الأبعاد؛ الخطوط محسوبة مباشرة',
           '   لأبعاد النموذج (لا تصغير بالطباعة) مع سمك نصل 3 مم.',
           '• الوجه: طباعة UV على ألواح Dibond 3 مم مطفأة من القالب',
           '   M-02 بمقياس 1:1 (تحقق من مسطرة 100 مم قبل اللصق).',
           '• النصل: صلب 304 سمك 3 مم مقصوص بالليزر من القالب M-03،',
           '   بلسانين يدخلان في شقّين بالقاعدة، والعقدة كرة نحاس Ø6 مم.',
           '• القاعدة: خشب بحري 18 مم مدهون، بثلاث أرجل ضبط M10',
           '   وميزان فقاعة ثنائي المحور.',
           '• التوجيه: بطريقة الظهر الحقيقي (M-04) لا بالبوصلة.',
           '• الملفات: execution/dxf/M_face_1to10.dxf وM_gnomon_1to10.dxf'])
    k = 200; ox, oy = 470, 200
    P = lambda x, y: (ox + x*k, oy - y*k)
    x0, x1, y0, y1 = BOARD
    sh.poly([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)], close=True, fill='#d9c4a0', sw=0.6)
    draw_marble(sh, m, P, k, big=False, labels=False)
    for (fx, fy) in [(-0.55, 0.27), (0.55, 0.27), (0.0, -0.49)]:
        sh.circle(P(fx, fy), 4, fill='#5f6a72', sw=0.3)
    sh.circle(P(0.45, -0.42), 6, fill='#cfe3e8', stroke=INK, sw=0.3)
    sh.text(P(0.45, -0.42)[0], P(0, -0.42)[1] + 10, 'ميزان فقاعة', 2.2, 'middle', SANS, INK)
    o, hole, tabs = model_profile()
    sh.line(P(0, m.base[1]), P(0, m.fy), stroke=INK, sw=1.2)
    for t in tabs:
        a, b = t.bounds[0], t.bounds[2]
        sh.rect(*P(-0.0016, b), 0.0032*k, (b - a)*k, fill=RED, sw=0)
    dimh(sh, P(x0, y1), P(x1, y1), P(0, y1)[1] - 10, f'{(x1 - x0)*1000:.0f}')
    dimv(sh, P(x1, y1), P(x1, y0), P(x1, 0)[0] + 10, f'{(y1 - y0)*1000:.0f}')
    dimh(sh, P(-m.W/2, -m.Dp/2), P(m.W/2, -m.Dp/2), P(0, -m.Dp/2)[1] + 30, f'وجه {m.W*1000:.0f} × {m.Dp*1000:.0f}')
    sh.text(P(0, y1)[0], P(0, y1)[1] - 18, 'الشمال الحقيقي', 2.8, 'middle', KUFI, INK, 700)
    sh.text(P(0.25, m.base[1])[0], P(0, m.base[1])[1], 'شقّا اللسانين 3.2 × 20 مم بعمق 18 مم', 2.3, 'start', SANS, RED)
    # واجهة جانبية 1:5
    vy = 400; Y = lambda y: ox + y*k; Zz = lambda z: vy - z*k
    sh.text(ox, 330, 'الواجهة الشرقية — 1:5', 3.0, 'middle', KUFI, INK, 700)
    sh.rect(Y(y0), Zz(0), (y1 - y0)*k, 0.021*k, fill='#d9c4a0', sw=0.4)
    for fy_ in (y1 - 0.06, y0 + 0.04):
        sh.rect(Y(fy_) - 4, Zz(-0.021), 8, 0.05*k, fill='#5f6a72', sw=0.3)
    sh.poly([(Y(y), Zz(z)) for y, z in o.exterior.coords], close=True, fill='#b9bec2', sw=0.4)
    sh.poly([(Y(y), Zz(z)) for y, z in hole.exterior.coords], close=True, fill='#fffdf8', sw=0.3)
    sh.circle((Y(m.fy), Zz(m.h)), 1.2, fill=GOLD, sw=0.2)
    dimv(sh, (Y(m.fy), Zz(0)), (Y(m.fy), Zz(m.h)), Y(m.fy) + 8, f'{m.h*1000:.1f}')
    dimh(sh, (Y(m.base[1]), Zz(0)), (Y(m.fy), Zz(0)), Zz(0) + 20, f'{(m.fy - m.base[1])*1000:.1f}')
    bom = [('1', 'لوح القاعدة', 'خشب بحري 18 مم 1240×860', '1'), ('2', 'وجه المزولة', 'Dibond 3 مم بطباعة UV (M-02)', '1'),
           ('3', 'النصل', 'صلب 304 سمك 3 مم ليزر (M-03)', '1'), ('4', 'العقدة', 'كرة نحاس Ø6 مم ملحومة', '1'),
           ('5', 'أرجل الضبط', 'M10 مع صواميل', '3'), ('6', 'ميزان فقاعة', 'ثنائي المحور Ø40', '1'), ('7', 'لاصق', 'شريط VHB أو لاصق إيبوكسي', '—')]
    table(sh, 830, 330, ['م', 'البند', 'المواصفة', 'العدد'], bom, [8, 26, 52, 12], 2.3, 5.6)
    return sh


def m02():
    """قالب الوجه بالحجم الطبيعي على A0."""
    sh = Sheet(1189, 841)
    v = View(594.5, 360, 1); P = v.p
    W2, D2 = m.W/2, m.Dp/2
    sh.rect(5, 5, 1179, 831, sw=0.3)
    draw_marble(sh, m, P, v.k, big=False)
    sh.text(P(0, D2 - 0.032)[0], P(0, D2 - 0.032)[1], 'نموذج اختبار 1:10 — مزولة الفسطاط', 4.0, 'middle', NASKH, '#5b3d16', 700)
    # شقا اللسانين وخط الشاخص
    o, hole, tabs = model_profile()
    sh.line(P(0, m.base[1]), P(0, m.fy), stroke=INK, sw=0.6, dash='2 1')
    for t in tabs:
        a, b = t.bounds[0], t.bounds[2]
        sh.rect(*P(-0.0016, b), 3.2, (b - a)*1000, stroke=RED, sw=0.3)
    sh.circle(P(0, m.base[1]), 1.2, fill=INK); sh.ltr(P(0, m.base[1])[0] + 3, P(0, m.base[1])[1], 'B', 3, 'start')
    sh.circle(P(0, m.fy), 1.2, fill=INK); sh.ltr(P(0, m.fy)[0] + 3, P(0, m.fy)[1] - 3, 'N (plan)', 3, 'start')
    for cx_, cy_ in [P(-W2, D2), P(W2, D2), P(W2, -D2), P(-W2, -D2)]:
        sh.line((cx_ - 8, cy_), (cx_ + 8, cy_), sw=0.3); sh.line((cx_, cy_ - 8), (cx_, cy_ + 8), sw=0.3)
    sh.rect(40, 780, 100, 4, fill=INK, sw=0); sh.ltr(90, 790, '100 mm — CHECK', 3.2, 'middle', SANS, INK, 700)
    sh.rect(20, 690, 4, 100, fill=INK, sw=0)
    sh.text(1170, 790, 'M-02 • قالب وجه النموذج بالحجم الطبيعي — اطبع بمقياس 100% على A0', 4, 'end', KUFI, INK, 700)
    sh.text(1170, 800, 'الشمال الحقيقي إلى أعلى اللوحة • الخط المتقطع: محور النصل • المستطيلان الأحمران: شقّا اللسانين', 3, 'end', SANS, GREY)
    return sh


def m03():
    """قالب النصل بالحجم الطبيعي على A3."""
    sh = Sheet(420, 297)
    o, hole, tabs = model_profile()
    k = 1000; ox = 210 - ((m.fy + m.base[1])/2)*k; oy = 210
    Y = lambda y: ox + y*k; Z = lambda z: oy - z*k
    sh.rect(5, 5, 410, 287, sw=0.3)
    sh.poly([(Y(y), Z(z)) for y, z in o.exterior.coords], close=True, fill='#e3e6e8', sw=0.3)
    sh.poly([(Y(y), Z(z)) for y, z in hole.exterior.coords], close=True, fill='#fffdf8', sw=0.3)
    sh.circle((Y(m.fy), Z(m.h)), 3, stroke=RED, sw=0.3)
    sh.line((Y(m.base[1] - 0.02), Z(0)), (Y(m.fy + 0.02), Z(0)), stroke=RED, sw=0.2, dash='2 1')
    dimh(sh, (Y(m.base[1]), Z(0)), (Y(m.fy), Z(0)), Z(0) + 30, f'{(m.fy - m.base[1])*1000:.2f}')
    dimv(sh, (Y(m.fy), Z(0)), (Y(m.fy), Z(m.h)), Y(m.fy) + 10, f'{m.h*1000:.2f}')
    sh.ltr(Y(m.base[1]) + 32, Z(0) - 6, f'{LAT:.4f}°', 3, 'start', SANS, BLUE, 700)
    sh.rect(20, 270, 100, 3, fill=INK, sw=0); sh.ltr(70, 280, '100 mm — CHECK', 3, 'middle', SANS, INK, 700)
    sh.text(400, 20, 'M-03 • قالب نصل النموذج بالحجم الطبيعي — صلب 3 مم', 4, 'end', KUFI, INK, 700)
    sh.text(400, 28, 'اطبع بمقياس 100% على A3 • الدائرة الحمراء: كرة نحاس Ø6 مركزها N • الخط المتقطع: سطح الوجه', 2.8, 'end', SANS, GREY)
    sh.text(400, 36, 'اللسانان 20 × 21 مم يدخلان في شقّي القاعدة (عمق 18 + وجه 3)', 2.8, 'end', SANS, GREY)
    return sh


def m04():
    sh = Sheet()
    frame(sh, 'بروتوكول اختبار النموذج ومعايرته', ['قراءات متوقعة محسوبة لأيام الاختبار', 'ونموذج تسجيل الرصد'], 'M-04', '—',
          'النموذج المصغر للتصميم (أ)',
          ['• الاختبار في القاهرة الكبرى (الفرق في العرض والطول مهمل).',
           '• الأوقات بالتوقيت الشتوي لمصر UTC+2 (من 30 أكتوبر 2026).',
           '• تُضبط الساعة المرجعية على توقيت الشبكة (هاتف) قبل الرصد.',
           '• «ظل الضلع على الخط T»: لحظة انطباق حافة ظل النصل على خط',
           '   الساعة T المحفور؛ تُقارن بالوقت المتوقع في الجدول.',
           '• «ظل العقدة»: مركز ظل الكرة مقيسًا بالمم من مركز الوجه',
           '   (x شرقًا، y شمالًا).',
           '• معيار القبول: فرق الوقت ≤ 1 دقيقة، وموضع ظل العقدة ≤ 2 مم.'])
    steps = ['## خطوات الاختبار',
             '١. ضع النموذج على سطح ثابت مكشوف للشمس من 9 صباحًا حتى 3 عصرًا.',
             '٢. اضبط الأرجل حتى تتوسط فقاعة الميزان في الاتجاهين.',
             '٣. التوجيه: قبل الظهر الحقيقي بدقائق أدِر النموذج حتى ينطبق ظل النصل',
             '    على خط الزوال في الوقت المبيّن تمامًا، ثم ثبّته.',
             '٤. سجّل في الأوقات المبيّنة موضع ظل العقدة ووقت عبور ظل النصل للخطوط.',
             '٥. كرّر الاختبار في ثلاثة أيام متباعدة على الأقل.',
             '٦. احسب الفروق؛ إذا تجاوزت الحد راجع الاستواء ثم زاوية النصل ثم الطباعة.']
    sh.para(830, 60, steps, 3.2, 1.65)
    dates = [dt.date(2026, 11, 5), dt.date(2026, 11, 15), dt.date(2026, 11, 25), dt.date(2026, 12, 5), dt.date(2026, 12, 15), dt.date(2026, 12, 25)]
    rows = []; tip_rows = []
    for d in dates:
        dec, eot, _ = sun_on(d); dst = egypt_dst(d)
        r = [f'{d.day} {GREG_MONTHS[d.month-1]}', fmt_hm(clock_from_H(0, eot, dst=dst))]
        for T in (9, 10, 11, 13, 14, 15):
            r.append(fmt_hm(clock_from_H(15*(T - 12) + m.corr, eot, dst=dst)))
        rows.append(r)
        tr = [f'{d.day} {GREG_MONTHS[d.month-1]}']
        for t in (10, 12, 14):
            dec2, eot2, _ = sun_on(d, t)
            p = m.proj(dec2, H_from_clock(t, eot2, dst=dst))
            tr.append(f'{p[0]*1000:+.1f} , {p[1]*1000:+.1f}')
        tip_rows.append(tr)
    sh.text(450, 60, 'الوقت المتوقع لانطباق ظل النصل على خطوط الساعات (UTC+2)', 3.8, 'end', KUFI, INK, 700)
    table(sh, 450, 72, ['التاريخ', 'الزوال', '9', '10', '11', '1', '2', '3'], rows, [34, 30, 30, 30, 30, 30, 30, 30], 3.2, 8.5, ltr_cols=(1, 2, 3, 4, 5, 6, 7))
    sh.text(830, 160, 'موضع ظل العقدة المتوقع (مم: x , y)', 3.8, 'end', KUFI, INK, 700)
    table(sh, 830, 172, ['التاريخ', '10:00', '12:00', '14:00'], tip_rows, [34, 40, 40, 40], 3.2, 8.5, ltr_cols=(1, 2, 3))
    sh.text(830, 252, 'نموذج تسجيل الرصد', 3.8, 'end', KUFI, INK, 700)
    blank = [('', '', '', '', '', '', '')]*12
    table(sh, 830, 264, ['التاريخ', 'الوقت المرصود', 'الخط', 'الوقت المتوقع', 'الفرق (د)', 'ظل العقدة x,y', 'ملاحظات'], blank, [40, 50, 30, 50, 40, 60, 110], 3.2, 11)
    sh.text(830, 420, 'الراصد: ____________    التوقيع: ____________    حالة السماء: ____________', 3.4, 'end', SANS, INK)
    with open(f'{OUT}/csv/M04_test_predictions.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['date', 'true_noon', 'line9', 'line10', 'line11', 'line13', 'line14', 'line15']); [w.writerow(r) for r in rows]
        w.writerow([]); w.writerow(['date', 'nodus_mm_10:00', 'nodus_mm_12:00', 'nodus_mm_14:00']); [w.writerow(r) for r in tip_rows]
    return sh


def dxfs():
    o, hole, p0 = gnomon_profile(M)

    def gn(msp, k):
        msp.add_lwpolyline([(y*k, z*k) for y, z in o.exterior.coords], close=True, dxfattribs={'layer': 'GNOMON'})
        msp.add_lwpolyline([(y*k, z*k) for y, z in hole.exterior.coords], close=True, dxfattribs={'layer': 'GNOMON'})
        msp.add_circle((M.fy*k, M.h*k), 30, dxfattribs={'layer': 'GNOMON'})
    import ezdxf
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM; doc.layers.add('GNOMON', color=1); gn(doc.modelspace(), 1000)
    doc.saveas(f'{OUT}/dxf/A_gnomon_fullscale.dxf')

    def slabs(msp, k):
        cw, rh = M.W/SLAB_COLS, M.Dp/SLAB_ROWS
        for c in range(SLAB_COLS):
            for r in range(SLAB_ROWS):
                x0, y0 = -M.W/2 + c*cw, M.Dp/2 - (r + 1)*rh
                msp.add_lwpolyline([(x0*k, y0*k), ((x0 + cw)*k, y0*k), ((x0 + cw)*k, (y0 + rh)*k), (x0*k, (y0 + rh)*k)], close=True, dxfattribs={'layer': 'SLABS'})
                msp.add_text(f'R{r+1}C{c+1}', dxfattribs={'layer': 'SLABS', 'height': 40}).set_placement(((x0 + 0.05)*k, (y0 + 0.05)*k))
        msp.add_line((0, M.base[1]*k), (0, M.fy*k), dxfattribs={'layer': 'GNOMON'})
    export_dxf(f'{OUT}/dxf/A_face_fullscale.dxf', M, slabs)
    mo, mh, tabs = model_profile()
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM; doc.layers.add('CUT', color=1); doc.layers.add('ENGRAVE', color=5)
    msp = doc.modelspace()
    msp.add_lwpolyline([(y*1000, z*1000) for y, z in mo.exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
    msp.add_lwpolyline([(y*1000, z*1000) for y, z in mh.exterior.coords], close=True, dxfattribs={'layer': 'CUT'})
    msp.add_circle((m.fy*1000, m.h*1000), 3, dxfattribs={'layer': 'ENGRAVE'})
    doc.saveas(f'{OUT}/dxf/M_gnomon_1to10.dxf')

    def mslots(msp, k):
        for t in tabs:
            a, b = t.bounds[0], t.bounds[2]
            msp.add_lwpolyline([(-1.6, a*k), (1.6, a*k), (1.6, b*k), (-1.6, b*k)], close=True, dxfattribs={'layer': 'GNOMON'})
    export_dxf(f'{OUT}/dxf/M_face_1to10.dxf', m, mslots)
    with open(f'{OUT}/csv/A_face_lines.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['family', 'label', 'spec', 'segment', 'point', 'x_m', 'y_m'])
        for fam, lbl, segs, spec in families(M):
            for si, s in enumerate(segs):
                last = None
                for pi, (x, y) in enumerate(s):
                    if last and (x - last[0])**2 + (y - last[1])**2 < 0.025**2 and pi != len(s) - 1: continue
                    w.writerow([fam, lbl, spec, si, pi, f'{x:.4f}', f'{y:.4f}']); last = (x, y)


if __name__ == '__main__':
    for n, fn in [('E-01', e01), ('E-02', e02), ('E-03', e03), ('E-04', e04), ('E-05', e05), ('M-01', m01), ('M-02', m02), ('M-03', m03), ('M-04', m04)]:
        fn().save(f'{OUT}/svg/{n}.svg'); print(n)
    dxfs(); print('dxf ok')
