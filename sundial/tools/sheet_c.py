"""التصميم (ج): بوابة عين الشمس — ثقب ضوئي يرسم بقعة الشمس على أرضية تقرأ الوقت الرسمي مباشرة."""
from common import *
from math import degrees as deg

C = DesignC()
DARK = '#23272d'; CREAM = '#f3e7c9'; TERRA2 = '#e0895c'; TEAL2 = '#56c2b8'; GOLD2 = '#e2b65a'; BLUE2 = '#7fb0e0'; PINK = '#e58fb0'
ECLIPSE = dt.date(2027, 8, 2)


def c01():
    sh = Sheet(); v = View(500, 297, 30)
    frame(sh, 'أرضية الضوء: المسقط الحسابي', ['بقعة الشمس من ثقب على ارتفاع %.2f م' % C.H, 'تقرأ توقيت مصر مباشرة بلا جداول'], 'C-01', '1:30 (على لوح A1)',
          'التصميم (ج): بوابة عين الشمس',
          [f'• الثقب: قطر 50 مم في قرص برونزي مائل، مركزه على ارتفاع {C.H:.2f} م',
           f'   فوق النقطة ({C.foot[0]:.2f}, {C.foot[1]:.2f}).',
           '• بقعة الضوء صورة لقرص الشمس قطرها 5–9 سم.',
           '• كل منحنى «ثمانية» هو موضع البقعة عند ساعة رسمية',
           '   (توقيت مصر) على مدار العام: الفرع المتصل لنصف السنة',
           '   الأول (يناير–يونيو) والمتقطع للثاني (يوليو–ديسمبر).',
           '• الأرقام الكبيرة شتوي، والصغيرة بين قوسين صيفي.',
           '• فرق الطول ومعادلة الزمن داخلان في الرسم: لا تصحيح.',
           '• خط الزوال (الذهبي): أول الظهر؛ والفيروزي: أول العصر.',
           '• الأرضية: بازلت أو جرانيت أسود مطفأ ليظهر الضوء،',
           '   والخطوط نحاس 6 مم والكتابة نحاس مصبوب.'])
    calendar_ring(sh, v, C.R_FACE, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, C.R_FACE*v.k, fill=DARK, sw=0.6)
    girih_pattern(sh, 'gC', 0.9*v.k, color=GOLD2, op=0.12)
    sh.circle(c, C.R_FACE*v.k, fill='url(#gC)', sw=0)
    # منحنيات التاريخ
    for dec, names, dates, lam, segs in C.signs:
        eq = abs(dec) < 0.01
        for s in segs: sh.path(v.d(s), stroke=GOLD2 if eq else TERRA2, sw=0.7 if eq else 0.45)
        s = max(segs, key=len)
        x, y = v.p(*s[0])
        lbl = ' / '.join(names)
        sh.text(x + 2.5, y - 2.2, lbl, 2.3, 'start', NASKH, TERRA2, 700)
    # منحنيات الساعات الرسمية
    for T, (first, second) in C.analemmas.items():
        whole = abs(T - round(T)) < 0.01
        for s in first: sh.path(v.d(s), stroke=CREAM, sw=0.8 if whole else 0.3)
        for s in second: sh.path(v.d(s), stroke=CREAM, sw=0.8 if whole else 0.3, dash='1.6 1.0')
        if whole and first:
            s = first[0]
            top = max(s, key=lambda p: p[1])
            x, y = v.p(*top)
            h12 = int(T) % 12 or 12
            sh.circle((x, y - 6), 3.4, fill=DARK, stroke=CREAM, sw=0.3)
            sh.text(x, y - 6.3, ar_digits(h12), 3.8, 'middle', KUFI, CREAM, 700)
            sh.text(x, y - 11.5, '(' + ar_digits(int(T + 1) % 12 or 12) + ')', 2.2, 'middle', SANS, GOLD2, 600)
    # خط الزوال والعصر
    for s in C.meridian: sh.path(v.d(s), stroke=GOLD2, sw=1.2)
    for s in C.asr1: sh.path(v.d(s), stroke=TEAL2, sw=1.0)
    s = max(C.asr1, key=len); x, y = v.p(*s[len(s)//2])
    sh.text(x + 3, y, 'أول العصر', 2.8, 'start', KUFI, TEAL2, 700)
    xm, ym = v.p(0, 4.2); sh.text(xm - 2.5, ym, 'خط الزوال: الظهر', 2.8, 'middle', KUFI, GOLD2, 700, rot=-90)
    # الأيام الخاصة
    specials = SPECIAL + [(ECLIPSE, 'كسوف ٢ أغسطس ٢٠٢٧: ترى البقعة هلالًا', PINK)]
    for i, (d, lbl, col) in enumerate(specials):
        dec, eot, _ = sun_on(d)
        col = PINK if col in (PURPLE, PINK) else '#ff8a7a'
        pts = [project(C.nodus, dec, H) for H in frange(-22, 22, 1)]
        segs = clip_polyline(pts, C.R_FACE)
        for sgm in segs: sh.path(v.d(sgm), stroke=col, sw=0.45, dash='0.8 0.6')
        end = pts[-1] if d.month >= 7 else pts[0]
        x, y = v.p(*end)
        sh.text(x + (2 if d.month >= 7 else -2), y, lbl, 2.1, 'start' if d.month >= 7 else 'end', SANS, col, 600)
    for d, ut, dec in kaaba_transits(REF_YEAR):
        _, eot, _ = sun(jd(d.year, d.month, d.day, ut))
        H = 15*(ut + LON/15 + eot/60 - 12)
        p = project(C.nodus, dec, H); x, y = v.p(*p)
        sh.poly(star_n(x, y, 2.4, 1.2, 8), close=True, fill=BLUE2, sw=0)
        ky = 1 if d.month == 7 else 0
        tx, ty = v.p(2.0, p[1] - 0.5 - 0.45*ky)
        sh.line((x + 1.5, y + 0.8), (tx - 1, ty), stroke=BLUE2, sw=0.25)
        sh.text(tx, ty, f'الشمس فوق الكعبة {ar_digits(d.day)} {GREG_MONTHS[d.month-1]} {ar_digits(fmt_hm(ut + 3))}: ظل كل قائم يشير عكس القبلة', 2.1, 'start', SANS, BLUE2, 600)
    # القبلة
    qa = qibla()
    p0 = (C.foot[0] + 0.0, C.foot[1]); 
    seg = clip_polyline([(p0[0] + t*sin(rad(qa)), p0[1] + 2.5 + t*cos(rad(qa))) for t in frange(-9, 9, 0.05)], C.R_FACE)
    # البوابة (مسقط)
    fy0 = C.foot[1] - 0.45
    for sx in (-1.9, 1.9):
        sh.path(v.d([(sx - 0.3, fy0 - 0.3), (sx + 0.3, fy0 - 0.3), (sx + 0.3, fy0 + 0.3), (sx - 0.3, fy0 + 0.3)], True), fill='#8a6a3a', stroke=INK, sw=0.3)
    sh.path(v.d([(-1.6, fy0 - 0.2), (1.6, fy0 - 0.2), (1.6, fy0 + 0.2), (-1.6, fy0 + 0.2)], True), stroke=GOLD2, sw=0.25, dash='1 1')
    sh.path(v.d([(0, C.foot[1]), (0, fy0)]), stroke=GOLD2, sw=0.25)
    x, y = v.p(*C.foot); sh.circle((x, y), 1.4, fill=GOLD2, sw=0)
    sh.text(x, y + 6, 'مسقط الثقب', 2.4, 'middle', SANS, INK, 600)
    sh.text(x - 22, v.p(0, fy0)[1], 'البوابة (مسقط)', 2.6, 'middle', KUFI, INK, 700)
    sh.para(v.p(2.6, 0)[0], v.p(0, 5.2)[1], ['## اقرأ الوقت من بقعة الضوء',
            '١. ابحث عن بقعة الشمس على الأرضية.', '٢. الشهر يحدد الفرع: المتصل يناير–يونيو والمتقطع يوليو–ديسمبر.',
            '٣. الرقم الكبير توقيت مصر الشتوي، والصغير الصيفي.', 'ومنحنيات البروج البرتقالية تدل على التاريخ.'], 2.35, 1.6, fill=CREAM)
    north_arrow(sh, 805, 470); scale_bar(sh, v, 768, 510, 2, 1)
    lx, ly = 830, 64
    sh.text(lx, ly, 'مفتاح الرسم', 3.6, 'end', KUFI, INK, 700); ly += 8
    for col, sw, dash, t in [(CREAM, 0.8, None, 'ساعة رسمية: يناير–يونيو'), (CREAM, 0.8, '1.6 1', 'ساعة رسمية: يوليو–ديسمبر'),
                             (TERRA2, 0.5, None, 'دخول البروج (التاريخ)'), (GOLD2, 1.2, None, 'خط الزوال'),
                             (TEAL2, 1.0, None, 'أول العصر'), ('#ff8a7a', 0.5, '0.8 0.6', 'أيام تراثية خاصة'), (PINK, 0.5, '0.8 0.6', 'رؤوس السنين والكسوف')]:
        sh.rect(lx - 14, ly - 2.6, 14, 5.2, fill=DARK, sw=0)
        sh.line((lx - 13, ly), (lx - 1, ly), stroke=col, sw=sw, dash=dash)
        sh.text(lx - 16, ly, t, 2.45, 'end', SANS, INK); ly += 6.5
    return sh


def c02():
    sh = Sheet()
    frame(sh, 'البوابة: واجهة وقطاع الزوال وتفاصيل الثقب', ['قوس فاطمي «منكسر» على هيئة عقود الجامع الأقمر', 'يحمل قرص الشمسة المثقوب'], 'C-02', '1:25 و1:50 و1:10 (على لوح A1)',
          'التصميم (ج): بوابة عين الشمس',
          ['• الدعامتان والعتب: حجر جيري (جلالة) على هيكل خرساني.',
           '• الشمسة: قرص برونز 1.20 م سمك 12 مم مائل 30° عن الأفق',
           '   (عمودي على شعاع ظهر الاعتدال) لتقل زاوية سقوط الضوء.',
           '• الثقب: 50 مم بحافة مشطوفة 45° من الجهة السفلية.',
           '• قمة البوابة (3.85 م) تحت مستوى الثقب حتى لا تحجب الشمس.',
           '• البوابة داخل الساحة؛ يعبرها الزوار، ودعامتاها خارج مسار البقعة.',
           '• الكتابة الكوفية في الإفريز: ﴿الشَّمْسُ وَالْقَمَرُ بِحُسْبَانٍ﴾.',
           '• تفاوت موضع الثقب: ±5 مم أفقيًا و±3 مم رأسيًا.',
           '• منحنى معادلة الزمن منقوش على الدعامة الشرقية للتعليم.'])
    # الواجهة الجنوبية 1:25
    v = View(330, 300, 25); k = v.k
    sh.text(330, 52, 'الواجهة الجنوبية للبوابة — 1:25', 4.0, 'middle', KUFI, INK, 700)
    g = v.p(0, 0)[1]
    sh.line((v.p(-3.2, 0)[0], g), (v.p(3.2, 0)[0], g), sw=0.6)
    top = C.H - 0.15
    # الكتلة
    outline = [(-2.2, 0), (-2.2, top), (2.2, top), (2.2, 0), (1.3, 0)]
    # قوس فاطمي منكسر (keel arch): نصف قطر ودوران
    def keel(sp=1.3, spring=3.0, rise=1.35):
        pts = []
        R = sp*1.25
        for t in frange(0, 1, 0.05):
            a = rad(180 - t*62)
            pts.append((sp - R + R*cos(a) + (R - sp) * 0 + sp - sp, 0))
        return pts
    arch = []
    sp, spring = 1.3, top - 0.55 - 1.6
    # منحنى: ربعا دائرة صغيرة ثم خطان مستقيمان إلى الرأس (هيئة القوس المنكسر)
    r = 0.95
    for t in frange(180, 125, -2.5):
        arch.append((-sp + r + r*cos(rad(t)), spring + r*sin(rad(t))))
    apex = (0, spring + 1.55)
    right = [(-x, y) for x, y in reversed(arch)]
    arch_full = [(-sp, 0)] + arch + [apex] + right + [(sp, 0)]
    body = [(-2.2, 0), (-2.2, top), (2.2, top), (2.2, 0)] + list(reversed(arch_full))
    sh.path(v.d(body, True), fill='#e9dcc0', sw=0.6)
    # إفريز كوفي
    sh.rect(v.p(-2.2, top)[0], v.p(0, top)[1], 4.4*k, 0.55*k, fill='#d7c49b', sw=0.3)
    sh.text(v.p(0, 0)[0], v.p(0, top - 0.28)[1], 'الشَّمْسُ وَالْقَمَرُ بِحُسْبَانٍ', 0.30*k, 'middle', KUFI, '#5b3d16', 700)
    # زخرفة: نجمة في كوشتي العقد
    for sx in (-1.55, 1.55):
        x, y = v.p(sx, top - 1.05)
        sh.poly(star_n(x, y, 0.32*k, 0.32*k*0.62, 8, 22.5), close=True, stroke='#7a5a1c', sw=0.3, fill='#f3e7c9')
    # أعمدة صغيرة
    # الشمسة (منظور من الجنوب: قطع ناقص لقرص مائل 30°)
    cx, cy = v.p(0, C.H)
    sh.path(f'M{f(cx-0.6*k)},{f(cy)} A{f(0.6*k)},{f(0.6*k*sin(rad(30)))} 0 1 0 {f(cx+0.6*k)},{f(cy)} A{f(0.6*k)},{f(0.6*k*sin(rad(30)))} 0 1 0 {f(cx-0.6*k)},{f(cy)}', fill='#c79a4a', sw=0.5)
    sh.circle((cx, cy), 0.025*k*2, fill=INK, sw=0)
    sh.line((cx, cy), (cx + 40, cy - 12), stroke=GREY, sw=0.2)
    sh.text(cx + 41, cy - 12, f'الثقب: مركزه على ارتفاع {C.H:.2f} م', 2.6, 'start', SANS, INK, 600)
    # أبعاد
    sh.line((v.p(2.7, 0)[0], g), (v.p(2.7, 0)[0], cy), stroke=GREY, sw=0.2)
    sh.ltr(v.p(2.7, 0)[0] + 3, (g + cy)/2, f'{C.H:.2f}', 2.6, 'start', rot=-90)
    sh.ltr(v.p(0, 0)[0], g + 6, '4.40', 2.6)
    # إنسان
    hx = v.p(-0.6, 0)[0]
    sh.circle((hx, g - 1.62*k), 0.11*k, sw=0.3)
    sh.poly([(hx, g - 1.5*k), (hx, g - 0.85*k), (hx - 0.18*k, g), (hx, g - 0.85*k), (hx + 0.16*k, g)], sw=0.3)
    # قطاع الزوال 1:50: الأشعة إلى الأرضية
    vs = View(640, 230, 50); ks = vs.k
    sh.text(640, 52, 'قطاع الزوال (شمال–جنوب) — 1:50: أشعة الظهر', 4.0, 'middle', KUFI, INK, 700)
    gy = vs.p(0, 0)[1]
    y0 = C.foot[1]
    X = lambda yy: vs.p(yy - 0.0, 0)[0]
    sh.line((X(-7.6), gy), (X(7.6), gy), sw=0.5)
    sh.rect(X(-7.0), gy, (14.0)*ks, 1.2, fill=DARK, sw=0)
    # البوابة قطاع
    sh.rect(X(y0 - 0.75), vs.p(0, top)[1], 0.6*ks, top*ks, fill='#e9dcc0', sw=0.4)
    hx, hy = X(y0), vs.p(0, C.H)[1]
    sh.line((hx - 0.6*ks*cos(rad(30)), hy + 0.6*ks*sin(rad(30))), (hx + 0.6*ks*cos(rad(30)), hy - 0.6*ks*sin(rad(30))), stroke='#c79a4a', sw=1.4)
    for d, col, lbl in [(dt.date(REF_YEAR, 6, 21), TERRA, 'الانقلاب الصيفي'), (dt.date(REF_YEAR, 3, 20), GOLD, 'الاعتدال'), (dt.date(REF_YEAR, 12, 21), BLUE, 'الانقلاب الشتوي')]:
        dec, _, _ = sun_on(d)
        alt = 90 - abs(LAT - dec)
        yy = y0 + C.H/tan(rad(alt))
        sh.line((hx, hy), (X(yy), gy), stroke=col, sw=0.4)
        L = 1.6
        sh.line((hx, hy), (hx - L*ks*cos(rad(alt)), hy - L*ks*sin(rad(alt))), stroke=col, sw=0.4, dash='1 1')
        sh.circle((X(yy), gy), 1.0, fill=col, sw=0)
        sh.text(X(yy), gy + 5, lbl, 2.2, 'middle', SANS, col, 700)
        sh.text(X(yy), gy + 9, f'{alt:.1f}° • {yy - y0:.2f} م', 2.0, 'middle', SANS, INK)
    sh.text(X(-7.2), gy - 4, 'الجنوب', 2.6, 'middle', KUFI, GREY, 700)
    sh.text(X(7.2), gy - 4, 'الشمال', 2.6, 'middle', KUFI, GREY, 700)
    # تفصيل الثقب 1:5
    v5 = View(640, 440, 10); k5 = v5.k
    sh.text(640, 365, 'تفصيل الشمسة والثقب — 1:10 (مسقط عمودي على القرص)', 3.6, 'middle', KUFI, INK, 700)
    c = v5.p(0, 0)
    sh.circle(c, 0.6*k5*0.55, fill='#e8c983', sw=0.5)
    sh.poly(star_n(c[0], c[1], 0.6*k5*0.5, 0.6*k5*0.5*0.62, 8, 22.5), close=True, stroke='#7a5a1c', sw=0.4)
    sh.poly(star_n(c[0], c[1], 0.12*k5, 0.12*k5*0.7654, 8, 0), close=True, stroke='#7a5a1c', sw=0.4)
    sh.circle(c, 0.025*k5, fill=INK, sw=0)
    sh.text(c[0], c[1] + 0.6*k5*0.55 + 5, 'قرص Ø1200 مم، وثقب Ø50 مم في مركز نجمة ثمانية', 2.4, 'middle', SANS, INK)
    # لوح معادلة الزمن على الدعامة
    eot_graph(sh, 200, 470, 220, 75, title=True, fs=1.0, show_eot=True)
    sh.text(420, 562, 'المتقطع الأزرق: معادلة الزمن نفسها (الوقت الشمسي − الوقت المتوسط) — للتعليم', 2.2, 'end', SANS, BLUE)
    return sh


if __name__ == '__main__':
    c01().save('../drawings/svg/C-01.svg'); c02().save('../drawings/svg/C-02.svg')
