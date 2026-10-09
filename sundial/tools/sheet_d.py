"""التصميم (د): حلقة الاستواء — مزولة استوائية أسطوانية تقرأ الوقت الرسمي مباشرة (Rohr: الفصل 3 §2، والفصل 5 §3، والفصل 9 لوحة 47)."""
from common import *
from math import degrees as deg

D = DesignD()
BRONZE = '#c79a4a'; BRONZE_D = '#7a5a1c'


def band_outline(a_list=(-D.half_w, D.half_w), n=60):
    """أطراف الحلقة في العالم: الحافتان والطرفان."""
    e1 = [D.world(H, a_list[0]) for H in frange(-D.H_ext, D.H_ext, 2*D.H_ext/n)]
    e2 = [D.world(H, a_list[1]) for H in frange(-D.H_ext, D.H_ext, 2*D.H_ext/n)][::-1]
    return e1 + e2


def meridian_ring(n=120, r=None):
    r = r or D.Rm
    return [(0.0, r*cos(rad(t)), D.zc + r*sin(rad(t))) for t in frange(0, 360, 360/n)]


def d01():
    sh = Sheet(); v = View(470, 297, 30)
    frame(sh, 'المسقط العام والواجهات', ['كرة ذات حلق: حلقة زوال وحلقة استواء عريضة', 'ومحور قطبي عليه خرزة الظل'], 'D-01', '1:30 و1:75 (على لوح A1)',
          'التصميم (د): حلقة الاستواء',
          ['• نوعها: مزولة استوائية أسطوانية (Heliochronometer) على مثال',
           '   ما وصفه Rohr في الفصل التاسع (لوحة 47): حلقة عريضة حافتاها',
           '   المداران، وعليها خطوط الساعات والبروج ومعادلة الزمن.',
           f'• الحلقة الاستوائية: نصف قطر {D.Rb:.2f} م، عرض {2*D.half_w:.2f} م، تمتد',
           f'   {D.H_ext:.0f}° شرق الزوال وغربه؛ مستواها موازٍ لمعدل النهار.',
           f'• حلقة الزوال: نصف قطر {D.Rm:.2f} م في مستوى خط نصف النهار،',
           f'   ومركز الكرة على ارتفاع {D.zc:.2f} م فوق مركز الساحة.',
           f'• المحور القطبي يميل {LAT:.4f}° نحو الشمال، وفي وسطه خرزة',
           '   قطرها 90 مم: ظلها على الحلقة يدل على الساعة والتاريخ معًا.',
           '• عند الظهر الحقيقي يقع ظل حلقة الزوال على خط الظهر تمامًا.',
           '• المواد: برونز مصبوب على هيكل من الصلب 316L، وقاعدة',
           '   من الجرانيت الأحمر بأسوان، وأرضية النجمة الثمانية.'])
    girih_pattern(sh, 'gD', 0.9*v.k, color=GOLD, op=0.16)
    calendar_ring(sh, v, 6.35, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, 6.35*v.k, fill='#f6f1e6', sw=0.6)
    sh.circle(c, 6.35*v.k, fill='url(#gD)', sw=0)
    for rot, col in ((0, '#e7dcc3'), (22.5, '#ddd0b2')):
        sh.poly(star_n(c[0], c[1], 5.4*v.k, 5.4*v.k*0.7654, 8, rot), close=True, fill=col, stroke=GOLD, sw=0.4)
    sh.circle(c, 3.0*v.k, fill='#3b3a38', stroke=GOLD, sw=0.5)
    sh.circle(c, 1.1*v.k, fill='#8c2f1f', stroke=INK, sw=0.4)
    sh.text(c[0], v.p(0, -2.45)[1], 'دائرة الجلوس (بازلت)', 2.4, 'middle', KUFI, '#fffdf8', 700)
    # الحلقة في المسقط
    ob = band_outline()
    sh.path(v.d([(p[0], p[1]) for p in ob], True), fill=BRONZE, stroke=INK, sw=0.4, op=0.95)
    sh.path(v.d([(p[0], p[1]) for p in meridian_ring()], True), stroke=BRONZE_D, sw=2.2)
    a, b = (0, D.zc) , None
    r0 = [D.zc + 0*0]
    p1 = (0.0, -D.Rm*0.98*cos(rad(LAT)), 0); p2 = (0.0, D.Rm*0.98*cos(rad(LAT)), 0)
    sh.path(v.d([(p1[0], p1[1]), (p2[0], p2[1])]), stroke=INK, sw=0.8)
    sh.circle(v.p(0, 0), 1.6, fill=GOLD, sw=0.3)
    sh.text(v.p(2.6, 0)[0], v.p(0, 1.6)[1], 'الحلقة الاستوائية (مسقط)', 2.5, 'start', KUFI, INK, 700)
    sh.line(v.p(1.5, 1.0), v.p(2.5, 1.55), stroke=GREY, sw=0.2)
    # خط الزوال والقبلة
    sh.path(v.d([(0, 3.05), (0, 6.3)]), stroke=GOLD, sw=1.0)
    sh.path(v.d([(0, -3.05), (0, -6.3)]), stroke=GOLD, sw=1.0)
    qa = qibla()
    sh.path(v.d([(3.4*sin(rad(qa)), 3.4*cos(rad(qa))), (6.2*sin(rad(qa)), 6.2*cos(rad(qa)))]), stroke=BLUE, sw=0.9)
    xq, yq = v.p(4.9*sin(rad(qa)) + 0.2, 4.9*cos(rad(qa)) + 0.2)
    sh.text(xq, yq, f'القبلة {ar_digits(f"{qa:.1f}")}°', 2.6, 'middle', KUFI, BLUE, 700, rot=qa - 90)
    sh.para(v.p(2.4, 0)[0], v.p(0, 5.25)[1], ['## اقرأ الساعة', '١. قف جنوب الكرة وانظر إلى باطن الحلقة.', '٢. ظل الخرزة يقع على منحنى «ثمانية» لكل ساعة:',
            '    اقرأ الرقم مباشرة بتوقيت مصر بلا جداول.', '٣. خطوط البروج تحت الظل تدل على التاريخ.'], 2.3, 1.55)
    north_arrow(sh, 805, 470); scale_bar(sh, v, 768, 510, 2, 1)
    # الواجهة الشرقية 1:50 (الشمال يمين)
    ve = View(795, 150, 75); k = ve.k
    sh.text(795, 70, 'الواجهة الشرقية — 1:75 (الشمال يمينًا)', 3.0, 'middle', KUFI, INK, 700)
    gy = ve.p(0, 0)[1]
    sh.line(ve.p(-2.6, 0), ve.p(2.6, 0), sw=0.5)
    sh.rect(ve.p(-0.7, 0)[0], ve.p(0, 0.25)[1], 1.4*k, 0.25*k, fill='#a8452e', sw=0.3)
    sh.poly([ve.p(p[1], p[2]) for p in meridian_ring()], close=True, stroke=BRONZE_D, sw=1.6)
    sh.poly([ve.p(p[1], p[2]) for p in ob], close=True, fill=BRONZE, stroke=INK, sw=0.3, op=0.9)
    a1 = (0, -D.Rm*cos(rad(LAT)), D.zc - D.Rm*sin(rad(LAT))); a2 = (0, D.Rm*cos(rad(LAT)), D.zc + D.Rm*sin(rad(LAT)))
    sh.line(ve.p(a1[1], a1[2]), ve.p(a2[1], a2[2]), stroke=INK, sw=0.7)
    sh.circle(ve.p(0, D.zc), 0.045*k + 0.6, fill=GOLD, sw=0.3)
    sh.ltr(ve.p(2.5, 0)[0], (gy + ve.p(0, D.zc)[1])/2, f'{D.zc:.2f}', 2.3, 'start', rot=-90)
    sh.line(ve.p(2.45, 0), ve.p(2.45, D.zc), stroke=GREY, sw=0.2)
    sh.ltr(ve.p(0, 0)[0], ve.p(0, D.zc + D.Rm)[1] - 3, f'{D.zc + D.Rm:.2f}', 2.3)
    # الواجهة الجنوبية 1:50
    vs = View(795, 300, 75)
    sh.text(795, 222, 'الواجهة الجنوبية — 1:75', 3.0, 'middle', KUFI, INK, 700)
    sh.line(vs.p(-2.6, 0), vs.p(2.6, 0), sw=0.5)
    sh.rect(vs.p(-0.7, 0)[0], vs.p(0, 0.25)[1], 1.4*k, 0.25*k, fill='#a8452e', sw=0.3)
    sh.line(vs.p(0, D.zc - D.Rm), vs.p(0, D.zc + D.Rm), stroke=BRONZE_D, sw=1.6)
    sh.poly([vs.p(p[0], p[2]) for p in ob], close=True, fill=BRONZE, stroke=INK, sw=0.3, op=0.9)
    sh.circle(vs.p(0, D.zc), 0.045*k + 0.6, fill=GOLD, sw=0.3)
    lo = D.world(0, -D.half_w)
    sh.text(vs.p(0, 0)[0], vs.p(0, 0)[1] + 5, f'أدنى نقطة في الحلقة {lo[2]:.2f} م فوق الأرض', 2.1, 'middle', SANS, INK)
    return sh


def d02():
    sh = Sheet()
    frame(sh, 'باطن الحلقة مفرودًا: الرسم الحسابي', ['منحنيات الساعة الرسمية والبروج والعصر', 'كما يراها الواقف جنوب الكرة'], 'D-02', '1:12.5 (على لوح A1)',
          'التصميم (د): حلقة الاستواء',
          ['• الإحداثي X على القوس = Rb·H (H الزاوية الساعية بالراديان)،',
           '   والإحداثي Y على العرض = −Rb·tan δ (Rohr، الفصل 3 §2).',
           '• الخط الرفيع كل 20 دقيقة: الوقت الشمسي الحقيقي.',
           '• منحنى «الثمانية» على كل ساعة: زوال الوقت المتوسط بتوقيت مصر',
           '   (Rohr، الفصل 5 §3، الشكلان 84 و85): الفرع المتصل لنصف السنة',
           '   الأول والمتقطع للثاني؛ والرقم الصغير بين قوسين صيفي.',
           '• الخطوط الأفقية: دخول البروج؛ وتدريج الأيام كل 5 أيام على',
           '   الحافتين (يمينًا يوليو–ديسمبر، ويسارًا يناير–يونيو).',
           '• الحلقة صفيحة برونز 20 مم، والخطوط محفورة 1.5 مم ومملوءة',
           '   بالمينا السوداء، والأرقام بالكوفي المحفور.'])
    k = 80.0; cx, cy = 495, 245
    X0 = D.Rb*rad(D.H_ext); Y0 = D.half_w
    P = lambda X, Y: (cx + X*k, cy - Y*k)
    sh.rect(cx - X0*k - 4, cy - Y0*k - 4, 2*X0*k + 8, 2*Y0*k + 8, fill=BRONZE, sw=0.6)
    sh.rect(cx - X0*k, cy - Y0*k, 2*X0*k, 2*Y0*k, fill='#f7f1e3', sw=0.4)
    def inb(p): return abs(p[0]) <= X0 and abs(p[1]) <= Y0
    # الوقت الحقيقي كل 20 دقيقة
    for m in range(-315, 316, 20):
        H = m/4
        if abs(H) > D.H_ext: continue
        whole = m % 60 == 0
        sh.line(P(D.Rb*rad(H), -Y0), P(D.Rb*rad(H), Y0), stroke=INK if whole else GREY, sw=0.25 if whole else 0.12, op=0.6)
    # الزوال الحقيقي
    sh.line(P(0, -Y0), P(0, Y0), stroke=GOLD, sw=1.0)
    # البروج
    for dec, names, dates, lam in sign_curves():
        Y = -D.Rb*tan(rad(dec))
        sol = abs(abs(dec) - OBLIQUITY) < 0.01
        sh.line(P(-X0, Y), P(X0, Y), stroke=GOLD if abs(dec) < 0.01 else TERRA, sw=0.6 if sol or abs(dec) < 0.01 else 0.35)
        sh.text(P(-X0, Y)[0] + 2, P(0, Y)[1] - 2, f'{names[0]} {ar_digits(dates[0].day)} {GREG_MONTHS[dates[0].month-1]}', 2.0, 'start', NASKH, TERRA, 700)
        sh.text(P(X0, Y)[0] - 2, P(0, Y)[1] - 2, f'{names[-1]} {ar_digits(dates[-1].day)} {GREG_MONTHS[dates[-1].month-1]}', 2.0, 'end', NASKH, TERRA, 700)
    # تدريج الأيام على الحافتين
    for d_, dec, eot, lam in year_days():
        if d_.day % 5 and d_.day != 1: continue
        Y = -D.Rb*tan(rad(dec)); left = d_.month <= 6
        X = -X0 if left else X0
        L = 0.10 if d_.day == 1 else 0.05
        sh.line(P(X, Y), P(X + (L if left else -L), Y), sw=0.3 if d_.day == 1 else 0.15)
    # منحنيات الساعة الرسمية
    for T in range(5, 20):
        a, b = [], []
        for d_, dec, eot, lam in year_days(REF_YEAR, T):
            H = H_from_clock(T, eot)
            p = D.band(H, dec)
            (a if d_.month <= 6 else b).append(p if inb(p) else None)
        for pts, dash in ((a, None), (b, '1.4 0.9')):
            seg = []
            for p in pts + [None]:
                if p: seg.append(P(*p))
                elif len(seg) > 1: sh.poly(seg, stroke=INK, sw=0.7, dash=dash); seg = []
                else: seg = []
        Hm = H_from_clock(T, 0)
        if abs(Hm) < D.H_ext - 3:
            for Yl in (Y0 + 0.08, -Y0 - 0.08):
                x, y = P(D.Rb*rad(Hm), Yl)
                sh.text(x, y + (-1 if Yl > 0 else 1.5), ar_digits(T % 12 or 12), 4.0, 'middle', KUFI, '#3b2a0c', 700)
            x, y = P(D.Rb*rad(Hm), -Y0 - 0.25)
            sh.text(x, y + 2, '(' + ar_digits((T + 1) % 12 or 12) + ')', 2.2, 'middle', SANS, GREY, 600)
    # العصر
    pts = [D.band(asr_H(d), d) for d in frange(-OBLIQUITY, OBLIQUITY, 0.2)]
    sh.poly([P(*p) for p in pts if inb(p)], stroke=TEAL, sw=1.0)
    p = pts[len(pts)//3]; sh.text(P(*p)[0] + 2.5, P(*p)[1], 'أول العصر', 2.6, 'start', KUFI, TEAL, 700)
    # الكعبة
    for d_, ut, dec in kaaba_transits(REF_YEAR):
        _, eot, _ = sun(jd(d_.year, d_.month, d_.day, ut))
        H = 15*(ut + LON/15 + eot/60 - 12)
        x, y = P(*D.band(H, dec))
        sh.poly(star_n(x, y, 1.8, 0.9, 8), close=True, fill=BLUE, sw=0)
    x, y = P(*D.band(9, 21.6)); sh.text(x + 3, y + 3.5, 'الشمس فوق الكعبة', 2.0, 'start', SANS, BLUE, 600)
    sh.text(cx, cy - Y0*k - 14, 'الحافة الشمالية العليا (مدار الجدي)', 2.6, 'middle', KUFI, GREY, 700)
    sh.text(cx, cy + Y0*k + 20, 'الحافة الجنوبية السفلى (مدار السرطان)', 2.6, 'middle', KUFI, GREY, 700)
    sh.text(P(-X0, 0)[0] - 3, cy, 'الغرب: الصباح', 2.4, 'end', KUFI, GREY, 700, rot=-90)
    sh.text(P(X0, 0)[0] + 3, cy, 'الشرق: المساء', 2.4, 'start', KUFI, GREY, 700, rot=90)
    # تفصيل قطاع الحلقة والخرزة
    sh.text(330, 410, 'قطاع عرضي في الحلقة والمحور — 1:10', 3.4, 'middle', KUFI, INK, 700)
    k2 = 100; ox, oy = 330, 470
    sh.rect(ox - D.half_w*k2*0.5, oy + 40, D.half_w*k2, 3, fill=BRONZE, sw=0.3)
    sh.line((ox, oy - 40), (ox, oy + 60), stroke=GREY, sw=0.2, dash='3 1 0.5 1')
    sh.circle((ox, oy), 4.5, fill=GOLD, sw=0.4)
    sh.text(ox + 8, oy, 'خرزة Ø90 مم مركزها مركز الكرة', 2.4, 'start', SANS, INK)
    sh.text(ox, oy + 50, f'صفيحة الحلقة 20 مم (العرض {2*D.half_w:.2f} م، مرسوم بنصف المقياس)', 2.2, 'middle', SANS, INK)
    # منظور محوري
    th, el = rad(-35), 0.5
    ox2, oy2, kk = 640, 520, 22.0
    def iso(x, y, z):
        X = x*cos(th) - y*sin(th); Y = x*sin(th) + y*cos(th)
        return (ox2 + X*kk, oy2 - (Y*el + z*0.866)*kk)
    sh.text(ox2, 395, 'منظور محوري', 3.4, 'middle', KUFI, INK, 700)
    sh.poly([iso(3.0*sin(rad(t)), 3.0*cos(rad(t)), 0) for t in range(0, 361, 6)], close=True, fill='#3b3a38', sw=0.3)
    sh.poly([iso(*p) for p in meridian_ring()], close=True, stroke=BRONZE_D, sw=1.4)
    sh.poly([iso(*p) for p in band_outline()], close=True, fill=BRONZE, stroke=INK, sw=0.3, op=0.9)
    a1 = (0, -D.Rm*cos(rad(LAT)), D.zc - D.Rm*sin(rad(LAT))); a2 = (0, D.Rm*cos(rad(LAT)), D.zc + D.Rm*sin(rad(LAT)))
    sh.line(iso(*a1), iso(*a2), stroke=INK, sw=0.6)
    sh.circle(iso(0, 0, D.zc), 1.4, fill=GOLD, sw=0.3)
    hx, hy = iso(2.6, -2.2, 0)
    sh.line((hx, hy), (hx, hy - 1.75*0.866*kk), sw=0.6); sh.circle((hx, hy - 1.85*0.866*kk), 0.8, fill=INK)
    return sh


if __name__ == '__main__':
    d01().save('../drawings/svg/D-01.svg'); d02().save('../drawings/svg/D-02.svg')
