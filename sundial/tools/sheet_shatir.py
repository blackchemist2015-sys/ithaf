"""A-03: رخامة ابن الشاطر الأصلية بالحساب لعرض دمشق؛ A-04: الرخامة نفسها لعرض الفسطاط داخل الدائرة."""
from common import *
from shatir import *
import base64, sys

GREEN = '#3c9a4a'; YELLOW = '#d4a516'; PURP = '#7b3fa0'; BROWN = '#8a3b24'; NAVY = '#2c4a8a'

DAM = dict(lat=33.5, W=2.069, Dp=1.017, h=0.29, fy=-0.32, corr=0.0, fajr_alt=-18.0)
FUS = dict(lat=LAT, W=11.40, Dp=5.60, h=1.60, fy=-1.76, corr=LON - ZONE_MERIDIAN, fajr_alt=-19.5)


def draw_marble(sh, M, P, k, big=False, labels=True):
    """رسم وجه الرخامة وكل أسر الخطوط. P: من متر إلى مم."""
    W2, D2 = M.W/2, M.Dp/2
    sh.poly([P(-W2, -D2), P(W2, -D2), P(W2, D2), P(-W2, D2)], close=True, fill='#eeeae2', stroke=INK, sw=0.8)
    sh.poly([P(-W2 + 0.012*M.W, -D2 + 0.024*M.Dp), P(W2 - 0.012*M.W, -D2 + 0.024*M.Dp), P(W2 - 0.012*M.W, D2 - 0.024*M.Dp), P(-W2 + 0.012*M.W, D2 - 0.024*M.Dp)], close=True, stroke=GREY, sw=0.25)
    L = lambda segs, col, sw, dash=None: [sh.poly([P(*q) for q in s], stroke=col, sw=sw, dash=dash) for s in segs]
    s0 = 1.0 if big else 0.7
    # الساعات الزمانية
    for kk in range(1, 12):
        L(M.temporal(kk), NAVY, 0.25*s0, '1.2 0.8')
    # الدائر من الطلوع والباقي للغروب
    for n in range(1, 14):
        L(M.since_rise(n), GREEN, 0.45*s0)
        L(M.to_set(n), YELLOW, 0.45*s0)
    # الساعات المستوية (كل 20 دقيقة والساعة غليظة)
    for m in range(-105*4, 105*4 + 1, 20):
        q = m/4
        L(M.equal_hour(q), INK, (0.55 if m % 60 == 0 else 0.15)*s0)
    # البروج
    for dec, names, dates, lam in sign_curves():
        sol = abs(abs(dec) - OBLIQUITY) < 0.01
        L(M.decl(dec), BROWN if dec else GOLD, (1.0 if sol or dec == 0 else 0.4)*s0)
    # العصران وقوس الفجر
    L(M.asr(1), PURP, 1.0*s0); L(M.asr(2), RED, 0.9*s0)
    L(M.fajr_remaining(13.5), TEAL, 0.9*s0, '2 1')
    # خط الزوال
    sh.line(P(0, -D2), P(0, D2), stroke=GOLD, sw=1.0*s0)
    # الشاخص (مسقط) وعقدته
    b = M.base; y0 = max(b[1], -D2)
    sh.line(P(0, y0), P(0, M.fy), stroke=INK, sw=2.2*s0)
    sh.circle(P(0, M.fy), 1.2*s0, fill=GOLD, stroke=INK, sw=0.3)
    if not labels: return
    # أرقام الساعات المستوية على الحافة الشمالية
    for T in range(6, 19):
        q = 15*(T - 12)
        segs = M.equal_hour(q)
        if not segs: continue
        top = max((p for s in segs for p in s), key=lambda p: p[1])
        if True:
            x, y = P(*top)
            sh.circle((x, y - 3.4*s0), 2.6*s0, fill='#fffdf8', stroke=INK, sw=0.25)
            sh.text(x, y - 3.2*s0, ar_digits(T % 12 or 12), 3.4*s0, 'middle', KUFI, INK, 700)
    # أعداد الدائر والباقي عند طرفي مدار الجدي
    for n in range(1, 10):
        for segs, col in ((M.since_rise(n), GREEN), (M.to_set(n), YELLOW)):
            if not segs: continue
            p = max((p for s in segs for p in s), key=lambda p: p[1])
            x, y = P(*p)
            if p[1] > D2 - 0.30*M.Dp:
                sh.text(x, y - 1.8*s0, ar_digits(n), 2.1*s0, 'middle', SANS, col, 700)


def legend(sh, x, y, s=1.0):
    items = [(BROWN, 1.0, None, 'مدارات البروج (المنقلبان غليظان)'), (GOLD, 1.0, None, 'خط الاعتدال وخط الزوال'),
             (INK, 0.55, None, 'الساعات المستوية (والرفيع كل ٢٠ دقيقة)'), (GREEN, 0.5, None, 'الدائر من الطلوع (ساعات مستوية)'),
             (YELLOW, 0.5, None, 'الباقي للغروب'), (NAVY, 0.3, '1.2 0.8', 'الساعات الزمانية (النهار ١٢ ساعة)'),
             (PURP, 1.0, None, 'أول العصر (ظل المثل)'), (RED, 0.9, None, 'آخر العصر المختار (ظل المثلين)'),
             (TEAL, 0.9, '2 1', 'قوس الباقي للفجر ١٣½ ساعة (زيادة الطنطاوي)')]
    sh.text(x, y, 'مفتاح الخطوط', 3.4, 'end', KUFI, INK, 700); y += 7
    for col, sw, dash, t in items:
        sh.line((x - 12, y), (x, y), stroke=col, sw=sw*1.4, dash=dash)
        sh.text(x - 14, y, t, 2.4, 'end', SANS, INK); y += 5.8
    return y


def img(sh, path, x, y, w, h, cap):
    data = base64.b64encode(open(path, 'rb').read()).decode()
    sh.add(f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>')
    sh.text(x + w/2, y + h + 4, cap, 2.2, 'middle', SANS, GREY)


def a03(ref):
    sh = Sheet()
    M = Marble(**DAM)
    frame(sh, 'رخامة ابن الشاطر الأصلية: إعادة الحساب', ['الجامع الأموي بدمشق، 773هـ/1371م', 'ونسخة محمد بن مصطفى الطنطاوي 1293هـ/1876م'],
          'A-03', '1:4 للرخامة (على لوح A1)', 'التصميم (أ): المرجع',
          ['• القياسات (محاضرة محمد العبيدي): الرخامة 206.9 × 101.7 سم،',
           '   وضلع الشاخص الكبير 38.5 سم، وميل الضلع القطبي 33.5°.',
           '• النقش: «ساعات زمانية لعرض لج ل دمشق» و«يعرف منه المطالع',
           '   والطالع لعرض لج ل دمشق»، أي عرض 33;30 = 33.5°.',
           '• النقش الرئيسي: «وضع هذه الآلة الجامعة للأعمال الميقاتية',
           '   الفقير محمد بن مصطفى الشهير بالطنطاوي، وقد زدت على ما',
           '   في رخامة ابن الشاطر قوس الباقي للفجر ثلاثة عشر ساعة',
           '   ونصف مستوية سنة 1293».',
           '• النقش الثانوي: «تشرف بحفره عبد المجيد ابن المرحوم السيد',
           '   عثمان الحموي النجار سنة 1293 وأخوه عبد الغني أيضًا».',
           '• أعدنا حساب أسر الخطوط كلها بالمعادلات (Rohr، الفصل 5:',
           '   الساعات البابلية والإيطالية = الدائر والباقي، خطوط مستقيمة).',
           '• ارتفاع العقدة 29 سم وموضعها مستنبطان من تطابق المنحنيات',
           '   مع صور الرخامة؛ ويُثبتان بقياس في الموقع.',
           '• المزولتان الشمالية والجنوبية الصغيرتان لم تُعَد حسابًا لقلة',
           '   البيانات، ومواضعهما مبيّنة بإطار متقطع.'])
    k = 250.0; cx, cy = 500, 175
    P = lambda x, y: (cx + x*k, cy - y*k)
    draw_marble(sh, M, P, k, big=True)
    sh.rect(*P(-0.16, 0.50), 0.32*k, 0.13*k, stroke=GREY, sw=0.3) if False else None
    for (x0, y0, w, h, t) in [(-0.17, 0.49, 0.34, 0.12, 'المزولة الشمالية'), (-0.20, -0.36, 0.40, 0.14, 'المزولة الجنوبية')]:
        a = P(x0, y0); sh.rect(a[0], a[1], w*k, h*k, stroke=GREY, sw=0.3); 
        sh.text(a[0] + w*k/2, a[1] + h*k + 3, t, 2.3, 'middle', SANS, GREY, 600)
    sh.text(cx, cy - M.Dp/2*k - 12, 'الشمال', 3.0, 'middle', KUFI, GREY, 700)
    sh.text(cx, cy + M.Dp/2*k + 9, 'الجنوب', 3.0, 'middle', KUFI, GREY, 700)
    sh.ltr(cx, cy + M.Dp/2*k + 15, f'206.9 × 101.7 cm   •   φ = 33.5°   •   nodus h = {M.h*100:.0f} cm', 2.6, 'middle', SANS, INK, 600)
    legend(sh, 830, 60)
    # صور المرجع
    y = 345
    img(sh, ref + '/diagram.jpg', 180, y, 150, 135, 'إعادة رسم الخطوط (من المحاضرة)')
    img(sh, ref + '/aerial.jpg', 340, y, 150, 135, 'الخطوط على صورة الرخامة')
    img(sh, ref + '/gnomon.jpg', 500, y, 110, 135, 'الشاخص القطبي')
    img(sh, ref + '/inscr.jpg', 620, y, 100, 135, 'النقشان المؤرّخان')
    sh.text(830, 300, 'ما تقرؤه الرخامة', 3.4, 'end', KUFI, INK, 700)
    sh.para(830, 308, ['• الوقت من الزوال بالساعات المستوية (ظل الضلع القطبي).', '• الدائر من الطلوع والباقي للغروب (طرف الظل).',
            '• الساعة الزمانية (لأوقات الأوراد والمواعيد).', '• أول العصر وآخره المختار.', '• الباقي لطلوع الفجر (زيادة الطنطاوي).',
            '• يوم السنة بالبروج، والمطالع والطالع.'], 2.3, 1.6)
    return sh


def a04():
    sh = Sheet(); v = View(500, 297, 30)
    M = Marble(**FUS)
    frame(sh, 'رخامة ابن الشاطر لعرض الفسطاط', ['الوجه المقترح للتصميم (أ) على هيئة الرخامة الأصلية', 'كل خطوطها محسوبة لعرض 30.0054° ش'],
          'A-04', '1:30 (على لوح A1)', 'التصميم (أ): مزولة ابن الشاطر الحديثة',
          [f'• الرخامة {M.W:.2f} × {M.Dp:.2f} م بنسبة الأصل (2.03:1) تقريبًا، تكبير 5.5 مرة.',
           f'• عقدة الشاخص على ارتفاع {M.h:.2f} م، والضلع القطبي يميل {LAT:.4f}°',
           f'   ويبلغ طوله {M.h/sin(rad(LAT)):.2f} م؛ وقاعدته خارج الرخامة جنوبًا كالأصل.',
           '• الأسر كلها كما في الأصل: المستوية والزمانية والدائر والباقي',
           '   والعصران وقوس الباقي للفجر (فجر مصر: الشمس تحت الأفق 19.5°).',
           '• الساعات المستوية مزاحة بفرق الطول (4.98 دقيقة) كما في A-01،',
           '   فالوقت الرسمي = القراءة + تصحيح معادلة الزمن (G-01).',
           '• الشريط الشمالي للنقش التأسيسي المقترح:',
           '   «وضعت هذه الآلة الجامعة على هيئة رخامة ابن الشاطر',
           '   لعرض ل الفسطاط سنة ١٤٤٨هـ».',
           '• الرخامة: جلالة 60 مم على بلاطة خرسانية، والخطوط نحاس 6 مم،',
           '   والشاخص برونز مفرغ على مثال شاخص دمشق.',
           '• إحداثيات التوقيع: setting_out/A_shatir_fustat.csv'])
    girih_pattern(sh, 'gS', 0.9*v.k)
    calendar_ring(sh, v, 6.35, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, 6.35*v.k, fill='#f6f1e6', sw=0.6)
    sh.circle(c, 6.35*v.k, fill='url(#gS)', sw=0)
    draw_marble(sh, M, v.p, v.k, big=False)
    # قاعدة الشاخص خارج الرخامة
    b = v.p(*M.base); sh.line(v.p(0, -M.Dp/2), b, stroke=INK, sw=1.6)
    sh.circle(b, 1.4, fill=INK)
    sh.text(b[0] + 3, b[1], 'قاعدة الضلع القطبي', 2.3, 'start', SANS, INK)
    x, y = v.p(0, M.Dp/2 - 0.32)
    sh.text(x, y, 'وُضعت هذه الآلة الجامعة على هيئة رخامة ابن الشاطر لعرض ل الفسطاط سنة ١٤٤٨هـ', 3.6, 'middle', NASKH, '#5b3d16', 700)
    legend(sh, 830, 60)
    # واجهة الشاخص 1:50
    ve = View(842, 440, 75); k = ve.k
    sh.text(800, 380, 'الشاخص — الواجهة الشرقية 1:75', 3.0, 'middle', KUFI, INK, 700)
    yb, yf = M.base[1], M.fy
    sh.line(ve.p(yb - 0.4, 0), ve.p(yf + 1.6, 0), sw=0.5)
    # هيئة شاخص دمشق: مثلث بضلع قطبي وساق رأسية وتجويف مقوس
    outer = [ve.p(yb, 0), ve.p(yf, M.h), ve.p(yf + 0.06, M.h + 0.05), ve.p(yf + 0.10, 0)]
    sh.poly(outer, close=True, fill='#5b4a3a', sw=0.4)
    hole = [ve.p(yb + 0.75, 0.08)] + [ve.p(yf - 0.05 - 0.55*(1 - cos(rad(t))), 0.08 + (M.h*0.62)*sin(rad(t))) for t in range(0, 91, 10)] + [ve.p(yf - 0.05, 0.08)]
    sh.poly(hole, close=True, fill='#fffdf8', sw=0.3)
    sh.circle(ve.p(yf, M.h), 1.2, fill=GOLD, sw=0.3)
    sh.text(ve.p(yf, M.h)[0] + 3, ve.p(0, M.h)[1] - 2, 'العقدة', 2.3, 'start', SANS, INK)
    sh.text(ve.p(yb, 0)[0], ve.p(0, 0)[1] + 5, 'الجنوب', 2.4, 'middle', KUFI, GREY, 700)
    sh.ltr(800, ve.p(0, 0)[1] + 10, f'{LAT:.2f}°  •  h = {M.h:.2f} m  •  L = {M.h/sin(rad(LAT)):.2f} m', 2.4, 'middle', SANS, INK, 600)
    north_arrow(sh, 805, 520); scale_bar(sh, v, 768, 555, 2, 1)
    return sh


def export(path):
    import csv
    M = Marble(**FUS)
    fams = [('declination', f'{"/".join(n)}', M.decl(d)) for d, n, _, _ in sign_curves()]
    fams += [('equal_hour', f'{12 + m/60:.2f}', M.equal_hour(m/4)) for m in range(-420, 421, 20)]
    fams += [('since_sunrise', f'{n}h', M.since_rise(n)) for n in range(1, 14)]
    fams += [('to_sunset', f'{n}h', M.to_set(n)) for n in range(1, 14)]
    fams += [('temporal_hour', f'{k}', M.temporal(k)) for k in range(1, 12)]
    fams += [('asr', 'k=1', M.asr(1)), ('asr', 'k=2', M.asr(2)), ('fajr_remaining', '13.5h', M.fajr_remaining(13.5))]
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['element', 'label', 'segment', 'point', 'x_east_m', 'y_north_m'])
        for el, lbl, segs in fams:
            for si, s in enumerate(segs):
                last = None
                for pi, p in enumerate(s):
                    if last and (p[0]-last[0])**2 + (p[1]-last[1])**2 < 0.0025 and pi != len(s) - 1: continue
                    w.writerow([el, lbl, si, pi, f'{p[0]:.4f}', f'{p[1]:.4f}']); last = p
        w.writerow(['gnomon', 'nodus', 0, 0, '0.0000', f'{M.fy:.4f}'])
        w.writerow(['gnomon', f'style_base h={M.h}', 0, 1, '0.0000', f'{M.base[1]:.4f}'])


if __name__ == '__main__':
    a03(sys.argv[1]).save('../drawings/svg/A-03.svg'); a04().save('../drawings/svg/A-04.svg')
    export('../setting_out/A_shatir_fustat.csv')
