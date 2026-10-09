"""التصميم (ب): مزولة الإنسان (المزولة الإهليلجية) — B-01 المسقط وB-02 التفاصيل."""
from common import *
from math import degrees as deg

B = DesignB()
HOURS_B = list(range(5, 20))


def hour12(T):
    return ar_digits(int(T) % 12 or 12)


def date_ticks():
    out = []
    for m in range(1, 13):
        nd = (dt.date(REF_YEAR + (m == 12), m % 12 + 1, 1) - dt.date(REF_YEAR, m, 1)).days
        for d in range(1, nd + 1):
            dd = dt.date(REF_YEAR, m, d); dec, eot, _ = sun_on(dd)
            out.append((dd, dec, B.date_y(dec)))
    return out


def b01():
    sh = Sheet(); v = View(500, 297, 30)
    frame(sh, 'المسقط الحسابي للأرضية', ['الزائر هو الشاخص: يقف على تاريخ اليوم', 'فيشير ظله إلى الساعة'], 'B-01', '1:30 (على لوح A1)',
          'التصميم (ب): مزولة الإنسان',
          [f'• القطع الناقص: نصف المحور الأكبر M = {B.M:.3f} م (شرق–غرب)',
           f'   ونصف الأصغر M·sinφ = {B.m:.3f} م (شمال–جنوب).',
           '• علامة الساعة T: x = M·sin H، y = M·sinφ·cos H، حيث',
           f'   H = 15°(T−12) + {B.corr:.3f}° (فرق الطول عن خط 30° ش).',
           '• موضع الوقوف لتاريخ ميله δ: y = M·cosφ·tan δ.',
           '• الأرقام الكبيرة توقيت مصر الشتوي، والصغيرة الصيفي.',
           '• الوقت الرسمي = القراءة + تصحيح معادلة الزمن (اللوح جنوبًا).',
           '• علامات العصر على القطع الناقص بحسب الشهر: إذا وقع ظل',
           '   الواقف على علامة شهره فقد دخل وقت العصر (المثل).',
           '• تصلح لأي طول قامة؛ ويُحسن أن يقف الزائر منتصبًا.',
           '• الأرضية: حجر جيري فاتح ونجوم الساعات من البازلت',
           '   والجرانيت الأحمر، والمسطرة من البرونز.',
           '• المرجع: Rohr، Sundials، الفصل 6 §2–4 (المزولة الإهليلجية).'])
    girih_pattern(sh, 'gB', 0.9*v.k, color=TEAL, op=0.16)
    calendar_ring(sh, v, 6.35, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, 6.35*v.k, fill='#f6f1e6', sw=0.6)
    sh.circle(c, 6.35*v.k, fill='url(#gB)', sw=0)
    # القطع الناقص
    ell = [B.hour_point(t) for t in frange(0, 360, 2)]
    sh.path(v.d(ell, True), stroke=GOLD, sw=1.2)
    sh.path(v.d([(B.M*1.06*sin(rad(t)), B.m*1.10*cos(rad(t))) for t in frange(0, 360, 2)], True), stroke=GOLD, sw=0.3)
    # أنصاف الساعات
    for T in frange(4.5, 19.5, 0.5):
        if T == int(T): continue
        x, y = v.p(*B.clock_point(T)); sh.circle((x, y), 0.9, fill=INK, sw=0)
    # العصر
    asr_pts = []
    for m in range(1, 13):
        dec, eot, _ = sun_on(dt.date(REF_YEAR, m, 1))
        H = asr_H(dec)
        asr_pts.append((m, B.hour_point(H), H))
    for m, p, H in asr_pts:
        x, y = v.p(*p)
        ang = atan2(p[0], p[1]/sin(rad(LAT)))
        xo, yo = v.p(p[0] + 0.55*sin(ang), p[1] + 0.55*cos(ang)*sin(rad(LAT)))
        sh.line((x, y), (xo, yo), stroke=TEAL, sw=0.45)
        sh.circle((xo, yo), 0.6, fill=TEAL, sw=0)
    hs = sorted(asr_pts, key=lambda q: q[2])
    for i, (m, p, H) in enumerate(asr_pts):
        if m not in (1, 3, 6, 9, 12): continue
        ang = atan2(p[0], p[1]/sin(rad(LAT)))
        rr = 0.95 + 0.38*(i % 3)
        xo, yo = v.p(p[0] + rr*sin(ang), p[1] + rr*cos(ang)*sin(rad(LAT)))
        sh.text(xo, yo, GREG_MONTHS[m-1], 1.9, 'middle', SANS, TEAL, 600)
    mid = hs[len(hs)//2][1]
    xm, ym = v.p(mid[0] + 1.2, mid[1] + 0.9)
    sh.text(xm + 4, ym - 2, 'علامات العصر بحسب الشهر', 3.0, 'start', KUFI, TEAL, 700)
    # أحجار الساعات
    for T in HOURS_B:
        p = B.clock_point(T); x, y = v.p(*p)
        sh.poly(star_n(x, y, 0.36*v.k, 0.36*v.k*0.62, 8, 22.5), close=True, fill='#3b3a38' if T not in (12,) else '#8c2f1f', stroke=INK, sw=0.3)
        sh.poly(star_n(x, y, 0.22*v.k, 0.22*v.k*0.7654, 8, 0), close=True, stroke=GOLD, sw=0.25)
        sh.text(x, y - 0.6, hour12(T), 4.6, 'middle', KUFI, '#fffdf8', 700)
        sh.text(x, y + 3.6, hour12(T + 1), 2.0, 'middle', SANS, '#e8c983', 600)
    xn, yn = v.p(*B.hour_point(0))
    sh.text(xn, yn - 14, 'الزوال: أول الظهر بالتوقيت الحقيقي', 2.4, 'middle', KUFI, GOLD, 700)
    sh.line((xn, yn - 12), (xn, yn - 1), stroke=GOLD, sw=0.4)
    # مسطرة التاريخ
    ticks = date_ticks()
    ymax = B.date_y(OBLIQUITY)
    sh.path(v.d([(-0.16, -ymax - 0.15), (0.16, -ymax - 0.15), (0.16, ymax + 0.15), (-0.16, ymax + 0.15)], True), fill='#d8b26a', sw=0.4)
    for dd, dec, y in ticks:
        side = -1 if dd.month <= 6 else 1
        L = 0.16 if dd.day == 1 else (0.10 if dd.day % 5 == 0 else 0.05)
        sh.path(v.d([(side*0.0, y), (side*L, y)]), sw=0.35 if dd.day == 1 else 0.12)
        if dd.day == 1:
            x, yy = v.p(side*0.22, y)
            sh.text(x, yy, GREG_MONTHS[dd.month-1], 2.0, 'start' if side > 0 else 'end', SANS, INK, 600)
    for dec, names, dates, lam in sign_curves():
        y = B.date_y(dec)
        x0, yy = v.p(-0.16, y); x1, _ = v.p(0.16, y)
        sh.line((x0, yy), (x1, yy), stroke=TERRA, sw=0.5)
    x, y = v.p(0, 0)
    sh.poly(star_n(x, y, 2.6, 1.3, 8), close=True, fill=GOLD, stroke=INK, sw=0.2)
    sh.text(x + 4, v.p(0, ymax + 0.35)[1], 'الانقلاب الصيفي', 2.4, 'start', KUFI, TERRA, 700)
    sh.text(x + 4, v.p(0, -ymax - 0.35)[1], 'الانقلاب الشتوي', 2.4, 'start', KUFI, TERRA, 700)
    sh.text(x - 6, y - 4.5, 'الاعتدالان', 2.4, 'end', KUFI, GOLD, 700)
    sh.text(v.p(-1.6, 0)[0], v.p(0, 1.15)[1], 'يناير–يونيو', 2.2, 'end', SANS, GREY)
    sh.text(v.p(1.6, 0)[0], v.p(0, 1.15)[1], 'يوليو–ديسمبر', 2.2, 'start', SANS, GREY)
    # الواقف (مثال): 21 مارس الساعة 3 عصرًا بالتوقيت الحقيقي
    sp = (0, 0); tgt = B.hour_point(45)
    a, b = v.p(*sp), v.p(*tgt)
    sh.line(a, (a[0] + (b[0] - a[0])*0.62, a[1] + (b[1] - a[1])*0.62), stroke=INK, sw=3.2, op=0.28)
    sh.line(a, b, stroke=INK, sw=0.25, dash='1 1', op=0.6)
    # لوح التصحيح جنوبًا
    gx0, gy0 = v.p(-2.6, -3.45); gx1, gy1 = v.p(2.6, -5.35)
    eot_graph(sh, gx0, gy0, gx1 - gx0, gy1 - gy0, title=True, fs=0.9)
    # تعليمات شمالًا
    sh.para(v.p(2.4, 0)[0], v.p(0, 5.15)[1], ['## كيف تكون أنت عقرب الساعة؟',
            '١. قف على مسطرة البرونز عند شهر اليوم ويومه.', '٢. انظر إلى ظلك: يقع على نجمة الساعة.',
            '٣. أضف تصحيح اليوم من اللوح الجنوبي (وساعة صيفًا).'], 2.4, 1.6)
    # القبلة
    qa = qibla()
    p0 = (3.4*sin(rad(qa)), 3.4*cos(rad(qa))); p1 = (6.2*sin(rad(qa)), 6.2*cos(rad(qa)))
    sh.path(v.d([p0, p1]), stroke=BLUE, sw=0.9)
    xq, yq = v.p(4.9*sin(rad(qa)) + 0.18, 4.9*cos(rad(qa)) + 0.18)
    sh.text(xq, yq, f'القبلة {ar_digits(f"{qa:.1f}")}°', 2.6, 'middle', KUFI, BLUE, 700, rot=qa - 90)
    north_arrow(sh, 805, 470); scale_bar(sh, v, 768, 510, 2, 1)
    lx, ly = 830, 64
    sh.text(lx, ly, 'مفتاح الرسم', 3.6, 'end', KUFI, INK, 700); ly += 8
    for col, t in [('#3b3a38', 'نجمة الساعة (بازلت)'), ('#8c2f1f', 'الثانية عشرة (جرانيت أحمر)'), ('#d8b26a', 'مسطرة التاريخ (برونز)'),
                   (TEAL, 'علامات العصر الشهرية'), (GOLD, 'القطع الناقص (نحاس)'), (BLUE, 'خط القبلة')]:
        sh.rect(lx - 9, ly - 2, 8, 4, fill=col, sw=0.2); sh.text(lx - 12, ly, t, 2.45, 'end', SANS, INK); ly += 6.5
    return sh


def b02():
    sh = Sheet()
    frame(sh, 'تفاصيل: مسطرة التاريخ ونجمة الساعة', ['مسطرة التاريخ 1:10، ونجمة الساعة 1:10،', 'وجدول توقيع العلامات'], 'B-02', '1:10 (على لوح A1)',
          'التصميم (ب): مزولة الإنسان',
          ['• المسطرة: صفيحة برونز 12 مم مثبتة في الحجر بمستوى الأرضية،',
           '   محفور فيها تدريج الأيام والأشهر الميلادية والقبطية.',
           '• نجوم الساعات: بازلت مصقول 60 مم بقطر 720 مم، والرقم',
           '   محفور ومملوء بنحاس مصبوب.',
           '• علامات العصر: مسامير نحاسية قطر 40 مم.',
           '• الإضاءة الليلية: نقاط LED دافئة في رؤوس النجوم.',
           '• تفاوت التوقيع ±5 مم، والاتجاه من الشمال الحقيقي ±0.1°.'])
    # المسطرة 1:10 رأسية
    v = View(260, 300, 10)
    ymax = B.date_y(OBLIQUITY)
    sh.text(260, 60, 'مسطرة التاريخ — 1:10', 4.0, 'middle', KUFI, INK, 700)
    sh.path(v.d([(-0.16, -ymax - 0.12), (0.16, -ymax - 0.12), (0.16, ymax + 0.12), (-0.16, ymax + 0.12)], True), fill='#e8cf98', sw=0.5)
    sh.path(v.d([(0, -ymax - 0.12), (0, ymax + 0.12)]), sw=0.3)
    for dd, dec, y in date_ticks():
        side = -1 if dd.month <= 6 else 1
        L = 0.16 if dd.day == 1 else (0.10 if dd.day % 5 == 0 else 0.05)
        sh.path(v.d([(0, y), (side*L, y)]), sw=0.4 if dd.day == 1 else 0.16)
        if dd.day == 1:
            x, yy = v.p(side*0.19, y)
            sh.text(x, yy, f'١ {GREG_MONTHS[dd.month-1]}', 2.4, 'start' if side > 0 else 'end', SANS, INK, 600)
        elif dd.day % 10 == 0 and dd.day < 30:
            x, yy = v.p(side*0.115, y)
            sh.text(x, yy, ar_digits(dd.day), 1.5, 'start' if side > 0 else 'end', SANS, GREY)
    for dec, names, dates, lam in sign_curves():
        y = B.date_y(dec)
        x, yy = v.p(-0.62, y)
        sh.path(v.d([(-0.55, y), (0.55, y)]), stroke=TERRA, sw=0.3, dash='1 1')
        sh.text(v.p(-0.6, 0)[0], yy, ' / '.join(names), 2.3, 'end', NASKH, TERRA, 700)
        sh.ltr(v.p(0.6, 0)[0], yy, f'y = {y:+.3f}', 2.2, 'start', SANS, GREY)
    # نجمة الساعة 1:10
    c = (520, 150); k = 100
    sh.text(c[0], 80, 'نجمة الساعة — مسقط وقطاع 1:10', 4.0, 'middle', KUFI, INK, 700)
    sh.poly(star_n(c[0], c[1], 0.36*k, 0.36*k*0.62, 8, 22.5), close=True, fill='#3b3a38', sw=0.4)
    sh.poly(star_n(c[0], c[1], 0.22*k, 0.22*k*0.7654, 8, 0), close=True, stroke=GOLD, sw=0.6)
    sh.text(c[0], c[1] - 2, '٣', 22, 'middle', KUFI, '#fffdf8', 700)
    sh.text(c[0], c[1] + 15, '٤', 7, 'middle', SANS, '#e8c983', 700)
    sh.ltr(c[0], c[1] + 0.36*k + 6, 'Ø 720', 2.6)
    sh.rect(c[0] - 36, 215, 72, 6, fill='#3b3a38', sw=0.3); sh.rect(c[0] - 50, 221, 100, 4, fill='#d9d2c4', sw=0.3)
    sh.rect(c[0] - 50, 225, 100, 15, fill='#bdb6a8', sw=0.3)
    sh.text(c[0] + 56, 218, 'بازلت 60 مم بمستوى الأرضية', 2.4, 'start', SANS, INK)
    sh.text(c[0] + 56, 232, 'بلاطة خرسانية 150 مم', 2.4, 'start', SANS, INK)
    # رسم توضيحي: الإنسان شاخصًا
    sh.text(560, 265, 'لماذا يصلح أي طول قامة؟', 3.6, 'middle', KUFI, INK, 700)
    sh.para(690, 275, ['كل منحنيات المزولة الإهليلجية مسقط لمزولة استوائية على الأرض:',
            'اتجاه الظل وحده هو المهم لا طوله؛ فيكفي أن يقف الزائر منتصبًا',
            'على موضع تاريخه الذي يعوض ميل الشمس عن خط الاستواء السماوي.'], 2.5, 1.6)
    # جدول التوقيع
    x0, y0 = 450, 320
    sh.text(x0 + 180, y0, 'جدول توقيع نجوم الساعات (م، من مركز الدائرة)', 3.4, 'end', KUFI, INK, 700)
    cols = ['الساعة (شتوي)', 'الصيفي', 'H (°)', 'x شرقًا', 'y شمالًا']
    cw = 36
    for j, cname in enumerate(cols):
        sh.text(x0 + 180 - j*cw - cw/2, y0 + 8, cname, 2.4, 'middle', SANS, INK, 700)
    for i, T in enumerate(HOURS_B):
        H = 15*(T - 12) + B.corr; x, y = B.hour_point(H)
        yy = y0 + 14 + i*6.2
        if i % 2 == 0: sh.rect(x0, yy - 3.1, 180, 6.2, fill='#f2ead8', sw=0)
        vals = [f'{T}:00', f'{T+1}:00', f'{H:+.3f}', f'{x:+.3f}', f'{y:+.3f}']
        for j, val in enumerate(vals):
            sh.ltr(x0 + 180 - j*cw - cw/2, yy, val, 2.4)
    return sh


if __name__ == '__main__':
    b01().save('../drawings/svg/B-01.svg'); b02().save('../drawings/svg/B-02.svg')
