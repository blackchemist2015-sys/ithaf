"""التصميم (أ): مزولة ابن الشاطر الحديثة — لوحة الوجه A-01 ولوحة الشاخص A-02."""
from common import *
from math import degrees as deg

A = DesignA()
T_BLADE = 0.03            # سمك نصل الشاخص (م): خطوط الصباح من حافته الغربية وخطوط المساء من الشرقية


def hour_numeral(H):
    """رقم الساعة للخط H (بالتوقيت المتوسط لخط 30° ش، أي توقيت مصر قبل تصحيح معادلة الزمن)."""
    T = 12 + H/15
    h = int(round(T)) % 12 or 12
    return ar_digits(h)


def a01():
    sh = Sheet(); v = View(500, 297, 30)
    frame(sh, 'لوحة الوجه: الرسم الحسابي', ['خطوط الساعات والبروج والظهر والعصر والقبلة',
          'مرسومة بالحساب لعرض الفسطاط 30.0054° ش'], 'A-01', '1:30 (على لوح A1)',
          'التصميم (أ): مزولة ابن الشاطر الحديثة',
          ['• الوجه أفقي تمامًا (ميل ≤ 1:2000)، والصرف بمجرى خفي في الحلقة.',
           '• الضلع المائل للشاخص موازٍ لمحور الأرض (يميل 30.0054°).',
           '• خطوط الساعات مصححة بفرق الطول عن خط 30° ش:',
           '   الوقت الرسمي = قراءة المزولة + التصحيح (لوحة G-01)،',
           '   ويُزاد ساعة في التوقيت الصيفي.',
           '• خط الساعة الصباحية يبدأ من الحافة الغربية للنصل،',
           '   وخط المسائية من الحافة الشرقية (سمك النصل 30 مم).',
           '• منحنيات البروج يرسمها طرف ظل «الشمسة» على رأس الشاخص.',
           '• منحنى العصر: ظل الشاخص = طوله + ظل الزوال (المذهب',
           '   الشافعي المعتمد في مصر)؛ والمتقطع: المثلان (الحنفي).',
           '• التواريخ الخاصة على خط الزوال تُقرأ عند الظهر.',
           '• جميع الأطوال بالمتر، والإحداثيات من مركز الدائرة.',
           '• جداول التوقيع (الإحداثيات): ملفات CSV المرفقة.',
           '• المرجع: Rohr، Sundials، الفصل 3 §3 (المزولة الأفقية)،',
           '   والفصل 5 §1–3 (منحنيات الميل وزوال الوقت المتوسط).'])
    girih_pattern(sh, 'gA', 0.9*v.k)
    calendar_ring(sh, v, A.R_FACE, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, A.R_FACE*v.k, fill='#f8f2e4', sw=0.6)
    sh.circle(c, A.R_FACE*v.k, fill='url(#gA)', sw=0)
    sh.circle(c, A.R_FACE*v.k - 1.2, sw=0.25, stroke=GOLD)
    # خطوط الساعات
    for H, segs in A.hours.items():
        H = round(H, 2)
        q = round(H/3.75) % 4
        sw, col = (0.75, INK) if q == 0 else ((0.35, INK) if q == 2 else (0.16, GREY))
        dx = (-T_BLADE/2 if H < 0 else T_BLADE/2)
        for s in segs:
            sh.path(v.d([(x + dx, y) for x, y in s]), stroke=col, sw=sw)
    # منحنيات البروج
    for dec, names, dates, lam, segs in A.signs:
        sol = abs(abs(dec) - OBLIQUITY) < 0.01
        eq = abs(dec) < 0.01
        col = GOLD if eq else TERRA
        for s in segs:
            sh.path(v.d(s), stroke=col, sw=0.9 if (sol or eq) else 0.55)
        # التسمية عند الطرفين
        s = max(segs, key=len)
        for end, nm, dd in [(s[0], names[0], dates[0]), (s[-1], names[-1], dates[-1])]:
            x, y = v.p(*end)
            east = end[0] > 0
            lbl = f'{nm} {ar_digits(dd.day)} {GREG_MONTHS[dd.month-1]}'
            off = -1.6 if dec > -15 else 1.6
            sh.text(x + (-2 if east else 2), y - 2.4, lbl, 2.5, 'end' if east else 'start', NASKH, TERRA, 700)
    # العصر
    for segs, dash, lbl in [(A.asr1, None, 'العصر (الشافعي): أول وقت العصر'), (A.asr2, '2.2 1.2', 'العصر الثاني (الحنفي)')]:
        for s in segs:
            sh.path(v.d(s), stroke=TEAL, sw=1.0 if not dash else 0.7, dash=dash)
        s = max(segs, key=len); i = len(s)//2 if not dash else len(s)//3
        (x, y), (x2, y2) = v.p(*s[i]), v.p(*s[i+3])
        ang = deg(atan2(y2 - y, x2 - x))
        ang = ang + 180 if (ang > 90 or ang < -90) else ang
        sh.text(x + 3.2, y, lbl, 2.6, 'middle', KUFI, TEAL, 700, rot=ang)
    # خط الزوال وتدريج التواريخ
    fx, fy = A.foot
    top = sqrt(A.R_FACE**2 - 0)
    sh.path(v.d([(0, A.base[1]), (0, A.R_FACE)]), stroke=GOLD, sw=1.3)
    x, y = v.p(0, 5.55)
    sh.text(x - 2.6, y, 'خط الزوال: أول وقت الظهر', 3.0, 'middle', KUFI, GOLD, 700, rot=-90)
    for m in range(1, 13):
        for dd in (1, 11, 21):
            d = dt.date(REF_YEAR, m, dd); dec, eot, _ = sun_on(d)
            p = project(A.nodus, dec, 0)
            side = -1 if m <= 6 else 1
            L = 0.16 if dd == 1 else 0.08
            sh.path(v.d([(0, p[1]), (side*L, p[1])]), stroke=INK, sw=0.3 if dd == 1 else 0.18)
            if dd == 1:
                xx, yy = v.p(side*(L + 0.04), p[1])
                sh.text(xx, yy, f'١ {GREG_MONTHS[m-1]}', 2.0, 'end' if side < 0 else 'start', SANS, INK)
    # منحنى الساعة 12 بتوقيت مصر
    first, second = A.noon_ana
    for s in first: sh.path(v.d(s), stroke=PURPLE, sw=0.7)
    for s in second: sh.path(v.d(s), stroke=PURPLE, sw=0.7, dash='1.6 0.9')
    s = first[0]; top = max(s, key=lambda p: p[1])
    # التواريخ الخاصة: علامات على خط الزوال يمسها طرف الظل عند الظهر
    for i, (d, lbl, col) in enumerate(SPECIAL):
        dec, eot, _ = sun_on(d)
        p = project(A.nodus, dec, 0)
        side = -1 if d.month <= 6 else 1
        x, y = v.p(*p)
        sh.poly(star_n(x, y, 1.9, 0.9, 8), close=True, fill=col, sw=0)
        tx, ty = v.p(side*1.35, p[1] + (0.12 if i % 2 else -0.12))
        sh.line((x + side*2, y), (tx - side*1, ty), stroke=col, sw=0.25)
        sh.text(tx, ty, lbl, 2.2, 'start' if side > 0 else 'end', SANS, col, 600)
    # القبلة
    qa = A.qibla_az
    end = (fx + 7*sin(rad(qa)), fy + 7*cos(rad(qa)))
    seg = clip_polyline([(fx + t*sin(rad(qa)), fy + t*cos(rad(qa))) for t in frange(0, 7, 0.05)], A.R_FACE)[0]
    sh.path(v.d(seg), stroke=BLUE, sw=1.0)
    a1 = v.p(*seg[-1])
    x, y = v.p(*seg[len(seg)//2])
    sh.text(x + 2.2, y - 2.2, f'اتجاه القبلة: {ar_digits(f"{qa:.1f}")}° من الشمال الحقيقي', 2.9, 'middle', KUFI, BLUE, 700, rot=qa - 90)
    seg2 = clip_polyline([(fx - t*sin(rad(qa)), fy - t*cos(rad(qa))) for t in frange(0, 7, 0.05)], A.R_FACE)[0]
    sh.path(v.d(seg2), stroke=BLUE, sw=0.4, dash='1.5 1')
    for d, ut, dec in kaaba_transits(REF_YEAR):
        _, eot, _ = sun(jd(d.year, d.month, d.day, ut))
        H = 15*(ut + LON/15 + eot/60 - 12)
        p = project(A.nodus, dec, H)
        x, y = v.p(*p)
        sh.poly(star_n(x, y, 2.6, 1.3, 8), close=True, fill=BLUE, sw=0.2)
        loc = ut + 3
        ky = getattr(a01, '_ky', 0); a01._ky = ky + 1
        tx, ty = v.p(-2.2, p[1] - 0.55 - 0.42*ky)
        sh.line((x - 1.5, y + 1), (tx + 1, ty), stroke=BLUE, sw=0.25)
        sh.text(tx, ty, f'ظل الشمسة هنا = الشمس فوق الكعبة: {ar_digits(d.day)} {GREG_MONTHS[d.month-1]} الساعة {ar_digits(fmt_hm(loc))} (صيفي)', 2.2, 'end', SANS, BLUE, 600)
    # أرقام الساعات
    for H, segs in A.hours.items():
        if abs(H - round(H/15)*15) > 0.01 or not segs: continue
        s = max(segs, key=len)
        far = max(s, key=lambda p: (p[0])**2 + (p[1])**2)
        bx, by = A.base
        ang = atan2(far[0] - bx, far[1] - by)
        r = sqrt(far[0]**2 + far[1]**2)
        pt = (far[0] - 0.30*sin(ang), far[1] - 0.30*cos(ang)) if r > A.R_FACE - 0.05 else (far[0] + 0.25*sin(ang), far[1] + 0.25*cos(ang))
        x, y = v.p(*pt)
        sh.circle((x, y), 3.3, fill='#fffdf8', stroke=INK, sw=0.3)
        sh.text(x, y + 0.3, hour_numeral(H), 4.0, 'middle', KUFI, INK, 700)
    # الشاخص (مسقط)
    bx, by = A.base
    sh.path(v.d([(-T_BLADE/2, by), (T_BLADE/2, by), (T_BLADE/2, fy), (-T_BLADE/2, fy)], True), fill=INK, sw=0.3)
    x, y = v.p(fx, fy); sh.circle((x, y), 2.0, fill=GOLD, stroke=INK, sw=0.3)
    sh.circle(v.p(bx, by), 1.2, fill=INK)
    # أبعاد
    def dim(p1, p2, txt, off=0.6):
        a, b = v.p(*p1), v.p(*p2)
        ax, ay = a[0] + off*v.k, a[1]; bx_, by_ = b[0] + off*v.k, b[1]
        sh.line((ax, ay), (bx_, by_), stroke=GREY, sw=0.2)
        for q in [(ax, ay), (bx_, by_)]: sh.line((q[0] - 1, q[1] + 1), (q[0] + 1, q[1] - 1), stroke=GREY, sw=0.3)
        sh.ltr(ax + 2, (ay + by_)/2, txt, 2.4, 'start', SANS, GREY, rot=-90)
    dim((0, by), (0, fy), f'{fy - by:.3f}', -0.9)
    dim((0, 0), (0, fy), f'{fy:.3f}', -0.35)
    x, y = v.p(0, 0); sh.line((x - 2, y), (x + 2, y), sw=0.25); sh.line((x, y - 2), (x, y + 2), sw=0.25)
    xb, yb = v.p(bx, by); sh.text(xb + 3, yb + 3, 'ملتقى الضلع القطبي بالوجه', 2.3, 'start', SANS, INK)
    xf, yf = v.p(fx, fy); sh.text(xf + 3, yf - 3.5, f'مسقط الشمسة (ارتفاعها {A.h:.2f} م)', 2.3, 'start', SANS, INK)
    # لوح معادلة الزمن منقوشًا في الجزء الجنوبي من الوجه (لا يمر عليه ظل في ساعات النهار المعتادة)
    gx0, gy0 = v.p(-4.35, -2.45); gx1, gy1 = v.p(-0.45, -4.30)
    eot_graph(sh, gx0, gy0, gx1 - gx0, gy1 - gy0, title=True, fs=0.82)
    ix, iy = v.p(2.95, -3.0)
    sh.para(ix, iy, ['## كيف تقرأ الوقت؟', '١. اقرأ الساعة حيث يقع ظل الحافة المائلة للشاخص.',
            '٢. أضف تصحيح اليوم من منحنى معادلة الزمن (يسارًا).', '٣. في التوقيت الصيفي أضف ساعة.',
            '## وكيف تقرأ التاريخ؟', 'طرف ظل الشمسة يسير على منحنيات البروج،', 'وعند الظهر يمس تدريج الأيام على خط الزوال.',
            '## والليل؟', 'انظر عبر أنبوب الضلع المائل تجد نجم القطب.'], 2.25, 1.55)
    # مفتاح
    lx = 830; ly = 50
    sh.text(lx, ly, 'مفتاح الرسم', 3.6, 'end', KUFI, INK, 700); ly += 7
    items = [(INK, 0.75, None, 'الساعة (والخط الرفيع ربعها)'), (GOLD, 1.3, None, 'خط الزوال / الظهر'),
             (TERRA, 0.6, None, 'مداخل البروج (التاريخ)'), (GOLD, 0.9, None, 'خط الاعتدالين'),
             (TEAL, 1.0, None, 'العصر الأول'), (TEAL, 0.7, '2.2 1.2', 'العصر الثاني'),
             (PURPLE, 0.7, None, '١٢ ظهرًا بتوقيت مصر: يناير–يونيو'), (PURPLE, 0.7, '1.6 0.9', '…ويوليو–ديسمبر'),
             (BLUE, 1.0, None, 'اتجاه القبلة'), (RED, 0.5, '0.8 0.6', 'أيام تراثية خاصة')]
    for col, sw, dash, t in items:
        sh.line((lx - 12, ly), (lx, ly), stroke=col, sw=sw, dash=dash)
        sh.text(lx - 14, ly, t, 2.45, 'end', SANS, INK); ly += 6
    # جدول زوايا خطوط الساعات (Rohr: tan h = sin φ · tan H)
    ty = 150
    sh.text(lx, ty, 'زوايا خطوط الساعات', 3.2, 'end', KUFI, INK, 700); ty += 4.5
    sh.text(lx, ty, 'عند ملتقى الضلع، من خط الزوال', 2.1, 'end', SANS, GREY); ty += 4.5
    sh.ltr(lx - 40, ty, 'tan h = sin φ · tan H', 2.3, 'middle', SANS, INK, 600); ty += 6
    for T in range(6, 19):
        H = 15*(T - 12) + A.corr
        h = deg(atan2(sin(rad(LAT))*sin(rad(H)), cos(rad(H))))
        if T % 2 == 0: sh.rect(lx - 80, ty - 2.6, 80, 5.2, fill='#f2ead8', sw=0)
        sh.text(lx - 2, ty, ar_digits(T % 12 or 12) + (' ص' if T < 12 else (' ظ' if T == 12 else ' م')), 2.4, 'end', KUFI, INK, 700)
        sh.ltr(lx - 30, ty, f'H = {H:+.2f}°', 2.2, 'middle', SANS, GREY)
        sh.ltr(lx - 62, ty, f'h = {h:+.2f}°', 2.3, 'middle', SANS, INK, 600)
        ty += 5.2
    sh.text(lx, ty + 2, 'الموجب نحو الشرق (بعد الظهر)', 2.0, 'end', SANS, GREY)
    north_arrow(sh, 805, 470)
    scale_bar(sh, v, 768, 510, 2, 1)
    return sh


if __name__ == '__main__':
    import os
    os.makedirs('../drawings/svg', exist_ok=True)
    a01().save('../drawings/svg/A-01.svg')


def girih_in_triangle(sh, tri, tile, sw=0.25, col=INK):
    """نقش نجمي مفرغ مقصوص داخل مثلث (للعرض في الواجهة)."""
    import itertools
    (x0, y0), (x1, y1), (x2, y2) = tri
    xs = [x0, x1, x2]; ys = [y0, y1, y2]
    def inside_tri(px, py):
        def s(a, b, c): return (a[0]-c[0])*(b[1]-c[1]) - (b[0]-c[0])*(a[1]-c[1])
        d1, d2, d3 = s((px, py), tri[0], tri[1]), s((px, py), tri[1], tri[2]), s((px, py), tri[2], tri[0])
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    cx = min(xs)
    while cx < max(xs):
        cy = min(ys)
        while cy < max(ys):
            pts = star_n(cx, cy, tile*0.48, tile*0.30, 8, 22.5)
            if all(inside_tri(px, py) for px, py in pts):
                sh.poly(pts, close=True, stroke=col, sw=sw, fill='#fffdf8')
                sh.poly(star_n(cx, cy, tile*0.17, tile*0.13, 8, 0), close=True, stroke=col, sw=sw*0.7)
            cy += tile
        cx += tile


def a02():
    sh = Sheet()
    frame(sh, 'الشاخص القطبي: واجهات وقطاعات وتفاصيل', ['الشاخص مثلث قائم ضلعه المائل موازٍ لمحور الأرض',
          'ورأسه «الشمسة» عقدة الظل التي ترسم التاريخ'], 'A-02', '1:20 و1:5 (على لوح A1)',
          'التصميم (أ): مزولة ابن الشاطر الحديثة',
          ['• المادة: لوحان من الصلب 316L سمك 10 مم بتشطيب برونزي',
           '   (PVD) على هيكل داخلي؛ السمك الكلي 30 مم.',
           '• إطار مصمت عرضه 120 مم على الضلع المائل والقاعدة',
           '   ليبقى حد الظل مستقيمًا حادًا؛ والداخل مفرغ بنقش',
           '   النجمة الثمانية (قطع بالماء).',
           '• الشمسة: نجمة ثمانية قطرها 360 مم وكرة نحاسية 70 مم',
           '   مركزها هو العقدة الحسابية بالضبط (تفاوت ±3 مم).',
           '• أنبوب رصد نجم القطب: قطره 40 مم، طوله 600 مم، موازٍ',
           '   للضلع المائل، على ارتفاع النظر 1.45 م.',
           '• التثبيت: ألواح قاعدة ومسامير كيميائية في البلاطة',
           '   الخرسانية، وضبط الميل بمسامير معايرة قبل الحقن.',
           '• تفاوت ميل الضلع القطبي ±0.05°، والاتجاه ±0.05°.',
           '• الوجه: رخام جلالة 40 مم بتطعيم نحاسي 6×20 مم،',
           '   والكتابة محفورة ومملوءة بالراتنج الملوّن.'])
    h = A.h; L = h/tan(rad(LAT)); bx, by = A.base; fx, fy = A.foot
    # ---- الواجهة الشرقية 1:20 (الشمال يمين)
    v = View(330, 205, 20)
    def P(y, z): return v.p(y - (by + fy)/2, z)
    g0, g1 = P(by - 0.8, 0), P(fy + 1.2, 0)
    sh.line(g0, g1, sw=0.6)
    for i in range(30):
        x = g0[0] + i*(g1[0] - g0[0])/30
        sh.line((x, g0[1]), (x - 2, g0[1] + 2), sw=0.15)
    tri = [P(by, 0), P(fy, 0), P(fy, h)]
    sh.poly(tri, close=True, fill='#c79a4a', sw=0.6)
    # إطار مصمت 120 مم ونقش داخلي
    w = 0.12
    a = rad(LAT)
    inner = [P(by + w/sin(a) + w/tan(a/2) - w/sin(a), w), P(fy - w, w), P(fy - w, h - w/cos(a) - w*tan(a) + w*0)]
    # حساب دقيق للمثلث الداخلي المتوازي
    def offset_tri():
        A0 = (by, 0.0); B0 = (fy, 0.0); C0 = (fy, h)
        # المثلث الداخلي بإزاحة w لكل ضلع
        import math
        # ضلع القاعدة z=w، الضلع الرأسي y=fy-w، الضلع المائل: z = (y-by)tan a - w/cos a
        t = math.tan(a)
        yA = by + (w + w/math.cos(a))/t
        return [P(yA, w), P(fy - w, w), P(fy - w, (fy - w - by)*t - w/math.cos(a))]
    inner = offset_tri()
    sh.poly(inner, close=True, fill='#fffdf8', sw=0.3)
    girih_in_triangle(sh, inner, 0.24*v.k, 0.2)
    sh.poly(inner, close=True, sw=0.4)
    # الشمسة
    nx, ny = P(fy, h)
    sh.poly(star_n(nx, ny, 0.18*v.k, 0.18*v.k*0.62, 8, 22.5), close=True, fill=GOLD, sw=0.4)
    sh.circle((nx, ny), 0.035*v.k, fill='#7a5a1c', sw=0.3)
    # أنبوب نجم القطب
    t0 = P(fy - 0.02, 1.45); t1 = P(fy - 0.02 + 0.6*cos(a), 1.45 + 0.6*sin(a))
    sh.line(t0, t1, sw=0.04*v.k, stroke='#555', cap='butt')
    sh.line(t1, (t1[0] + 6, t1[1] - 10), stroke=GREY, sw=0.2)
    sh.text(t1[0] + 7, t1[1] - 10, 'أنبوب رصد نجم القطب (ارتفاع النظر 1.45 م)', 2.6, 'start', SANS, INK)
    # أشعة توضيحية: الضلع القطبي إلى القطب السماوي
    e = P(fy + 0.9*cos(a), h + 0.9*sin(a))
    sh.line(P(fy, h), e, stroke=BLUE, sw=0.3, dash='2 1.2')
    sh.text(e[0] + 2, e[1] - 2, 'إلى القطب السماوي (نجم القطب)', 2.8, 'start', KUFI, BLUE, 700)
    # أبعاد
    def hdim(p, q, yoff, txt):
        y = p[1] + yoff
        sh.line((p[0], y), (q[0], y), stroke=GREY, sw=0.2)
        for xx in (p[0], q[0]):
            sh.line((xx, p[1] + 1), (xx, y + (1.5 if yoff > 0 else -1.5)), stroke=GREY, sw=0.15)
            sh.line((xx - 1, y + 1), (xx + 1, y - 1), stroke=INK, sw=0.3)
        sh.ltr((p[0] + q[0])/2, y + (2.6 if yoff > 0 else -2.6), txt, 2.8)
    hdim(P(by, 0), P(fy, 0), 9, f'{L:.3f}')
    p, q = P(fy, 0), P(fy, h)
    sh.line((p[0] + 10, p[1]), (q[0] + 10, q[1]), stroke=GREY, sw=0.2)
    for yy in (p[1], q[1]): sh.line((p[0] + 9, yy - 1), (p[0] + 11, yy + 1), sw=0.3)
    sh.ltr(p[0] + 13, (p[1] + q[1])/2, f'{h:.3f}', 2.8, 'start', rot=-90)
    sh.text(P(by, 0)[0] + 26, P(by, 0)[1] - 3.2, f'{LAT:.4f}°', 2.8, 'middle', SANS, BLUE, 600)
    sh.path(f'M{f(P(by,0)[0]+20)},{f(P(by,0)[1])} A20,20 0 0 0 {f(P(by,0)[0]+20*cos(a))},{f(P(by,0)[1]-20*sin(a))}', stroke=BLUE, sw=0.3)
    sh.text(v.p(0, 0)[0], 60, 'الواجهة الشرقية للشاخص — مقياس 1:20', 4.0, 'middle', KUFI, INK, 700)
    sh.text(g0[0], g0[1] + 6, 'الجنوب', 2.8, 'middle', KUFI, GREY, 700)
    sh.text(g1[0], g1[1] + 6, 'الشمال', 2.8, 'middle', KUFI, GREY, 700)
    # إنسان للمقياس
    hx = P(fy + 1.55, 0)[0]
    gy = g0[1]; k = v.k
    sh.circle((hx, gy - 1.62*k), 0.11*k, sw=0.3)
    sh.poly([(hx, gy - 1.5*k), (hx, gy - 0.85*k), (hx - 0.18*k, gy), (hx, gy - 0.85*k), (hx + 0.16*k, gy)], sw=0.3)
    sh.poly([(hx - 0.25*k, gy - 1.05*k), (hx, gy - 1.38*k), (hx + 0.2*k, gy - 1.0*k)], sw=0.3)
    # ---- تفصيل الشمسة 1:5
    v5 = View(700, 140, 5)
    c = v5.p(0, 0)
    sh.poly(star_n(c[0], c[1], 0.18*v5.k, 0.18*v5.k*0.62, 8, 22.5), close=True, fill='#e8c983', sw=0.5)
    sh.poly(star_n(c[0], c[1], 0.13*v5.k, 0.13*v5.k*0.62, 8, 0), close=True, sw=0.3)
    sh.circle(c, 0.035*v5.k, fill='#b8862b', sw=0.4)
    sh.line((c[0] - 0.22*v5.k, c[1]), (c[0] + 0.22*v5.k, c[1]), stroke=RED, sw=0.2, dash='3 1 0.5 1')
    sh.line((c[0], c[1] - 0.22*v5.k), (c[0], c[1] + 0.22*v5.k), stroke=RED, sw=0.2, dash='3 1 0.5 1')
    sh.text(c[0], c[1] - 0.25*v5.k - 4, 'تفصيل الشمسة (العقدة) — 1:5', 3.6, 'middle', KUFI, INK, 700)
    sh.text(c[0], c[1] + 0.25*v5.k + 4, 'مركز الكرة = العقدة الحسابية؛ قطر النجمة 360 مم', 2.6, 'middle', SANS, INK)
    sh.text(c[0], c[1] + 0.25*v5.k + 9, 'ظل الكرة دائرة صغيرة تقرأ التاريخ بمركزها', 2.6, 'middle', SANS, GREY)
    sh.para(826, 222, ['## أفكار فلكية في هذا التصميم',
            '• الضلع المائل يوازي محور الأرض، فظله يدل على الساعة طول العام',
            '   (فكرة الشاخص القطبي التي تنسب إلى ابن الشاطر، دمشق 1371م).',
            '• طرف ظل الشمسة يرسم التاريخ: خطوط البروج والأيام ورؤوس السنين.',
            '• يومَي تعامد الشمس على الكعبة يقع الظل على خط القبلة تمامًا.',
            '• يومَي تعامد الشمس على وجه رمسيس في أبي سمبل يمس الظل نجمة حمراء.',
            '• منحنى «١٢ ظهرًا» يجمع فرق الطول ومعادلة الزمن في رسم واحد.',
            '• ليلًا: الأنبوب الموازي للضلع يشير إلى نجم القطب.',
            '• عرض الفسطاط 30° هو عرض جداول الميقات القاهرية',
            '   المنسوب أكثرها إلى ابن يونس المصري (ت 1009م).'], 2.45, 1.6)
    # ---- قطاع الوجه 1:5
    sx, sy = 590, 330
    sh.text(sx + 90, sy - 12, 'قطاع نموذجي في الوجه والحلقة — 1:5', 3.6, 'middle', KUFI, INK, 700)
    layers = [(0.04, '#efe6d2', 'رخام جلالة 40 مم مطعّم بشرائح نحاس 6×20 مم'),
              (0.03, '#d9d2c4', 'مونة لصق 30 مم'),
              (0.15, '#bdb6a8', 'بلاطة خرسانة مسلحة 150 مم (منسوب ±1 مم/3 م)'),
              (0.20, '#e3dccb', 'إحلال مدموك 200 مم')]
    y = sy; k5 = 200
    for t, col, lbl in layers:
        sh.rect(sx, y, 140, t*k5, fill=col, sw=0.3)
        sh.line((sx + 140, y + t*k5/2), (sx + 148, y + t*k5/2), stroke=GREY, sw=0.2)
        sh.text(sx + 150, y + t*k5/2, lbl, 2.5, 'start', SANS, INK)
        y += t*k5
    for xx in (sx + 40, sx + 85):
        sh.rect(xx, sy, 1.2, 4, fill=GOLD, sw=0)
    sh.rect(sx + 115, sy, 14, 18, fill='#fffdf8', sw=0.3)
    sh.text(sx + 122, sy + 50, 'مجرى صرف خطي خفي في الحلقة', 2.4, 'middle', SANS, INK)
    sh.text(sx + 70, sy - 4, 'الوجه أفقي تمامًا (لا ميول للصرف داخل الدائرة)', 2.5, 'middle', SANS, RED)
    # ---- منظور محوري للمزولة كلها
    th, el = rad(-35), 0.5
    ox, oy, kk = 370, 480, 19.0
    def iso(x, y, z=0):
        X = x*cos(th) - y*sin(th); Y = x*sin(th) + y*cos(th)
        return (ox + X*kk, oy - (Y*el + z*0.866)*kk)
    sh.text(ox, 375, 'منظور محوري: 21 مارس الساعة 3 عصرًا — ظل الشاخص محسوبًا', 4.0, 'middle', KUFI, INK, 700)
    sh.poly([iso(R_SITE*sin(rad(t)), R_SITE*cos(rad(t))) for t in range(0, 361, 4)], close=True, fill='#efe5cf', sw=0.5)
    sh.poly([iso(A.R_FACE*sin(rad(t)), A.R_FACE*cos(rad(t))) for t in range(0, 361, 4)], close=True, fill='#f8f2e4', sw=0.4)
    for H, segs in A.hours.items():
        if abs(H - round(H/15)*15) > 0.01: continue
        for s in segs: sh.poly([iso(*q) for q in s], stroke=INK, sw=0.25)
    for dec, names, dates, lam, segs in A.signs:
        for s in segs: sh.poly([iso(*q) for q in s], stroke=TERRA, sw=0.3)
    for s in A.asr1: sh.poly([iso(*q) for q in s], stroke=TEAL, sw=0.4)
    # ظل الشاخص يوم الاعتدال الساعة 15 بالتوقيت الحقيقي
    sp = project(A.nodus, 0.0, 45)
    sh.poly([iso(bx, by), iso(fx, fy), iso(*sp)], close=True, fill=INK, op=0.35, sw=0)
    sh.poly([iso(bx, by), iso(fx, fy), iso(fx, fy, h)], close=True, fill='#c79a4a', sw=0.4)
    nx, ny = iso(fx, fy, h); sh.circle((nx, ny), 1.3, fill=GOLD, sw=0.3)
    sh.text(iso(*sp)[0] + 3, iso(*sp)[1], 'طرف الظل على خط الاعتدال وخط الساعة ٣', 2.5, 'start', SANS, INK)
    hx, hy = iso(2.5, -4.6)
    sh.line((hx, hy), (hx, hy - 1.7*0.866*kk), sw=0.5)
    sh.circle((hx, hy - 1.8*0.866*kk), 0.6, fill=INK)
    return sh


if __name__ == '__main__':
    a02().save('../drawings/svg/A-02.svg')
