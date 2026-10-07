"""التصميم (د): رخامة ابن الصوفي — مزولة استوائية مأخوذة من «صنعة الرخامة الموازية لمعدل النهار» في مخطوط شفاء الأسقام."""
from common import *
from math import degrees as deg
import base64

D = DesignD()
MS_DIR = None   # يُمرَّر من سطر الأوامر: مجلد صور المخطوط


def month_decs(summer):
    out = []
    for m in range(1, 13):
        dec, _, _ = sun_on(dt.date(REF_YEAR, m, 1))
        if (dec > 0) == summer and D.g/tan(rad(abs(dec))) < D.Rd - 0.12:
            out.append((m, dec))
    return out


def draw_face(sh, cx, cy, k, summer, title):
    """رسم وجه القرص بشكله الحقيقي. k مم لكل متر."""
    P = lambda pe, pv: (cx + D.screen(pe, pv, summer)[0]*k, cy - D.screen(pe, pv, summer)[1]*k)
    Rd = D.Rd
    sh.circle((cx, cy), Rd*k, fill='#d6b16a', sw=0.6)
    sh.circle((cx, cy), (Rd - 0.13)*k, fill='#f7f1e3', sw=0.4)
    sh.circle((cx, cy), 0.05*k, fill='#7a5a1c', sw=0.3)
    # النصف العلوي لا يقع عليه ظل: نقش وكتابة على هيئة المخطوط
    sx, sy = cx, cy - 1.30*k
    sh.poly(star_n(sx, sy, 0.24*k, 0.24*k*0.62, 8, 22.5), close=True, fill='#efe3c4', stroke=GOLD, sw=0.4)
    sh.poly(star_n(sx, sy, 0.14*k, 0.14*k*0.7654, 8, 0), close=True, stroke=GOLD, sw=0.4)
    sh.text(sx, sy + 0.3, 'الصيفي' if summer else 'الشتوي', 0.05*k, 'middle', KUFI, '#5b3d16', 700)
    sh.text(cx, cy - 0.58*k, 'الرخامة الموازية لمعدل النهار', 0.075*k, 'middle', KUFI, '#5b3d16', 700)
    sh.text(cx, cy - 0.40*k, 'لعرض الفسطاط ٣٠° — على صنعة ابن الصوفي', 0.05*k, 'middle', NASKH, '#5b3d16', 700)
    # الساعات
    for q in frange(-120, 120, 3.75):
        H = q + D.corr
        ok = any(D.face_point(dd, H, summer) for dd in ((5, 11.5, 20, 23.44) if summer else (-5, -11.5, -20, -23.44)))
        if not ok: continue
        whole = abs(q/15 - round(q/15)) < 1e-6
        half = abs(q/7.5 - round(q/7.5)) < 1e-6
        r0 = 0.10 if whole else (0.45 if half else 1.0)
        a, b = P(r0*sin(rad(H)), r0*cos(rad(H))), P((Rd - 0.13)*sin(rad(H)), (Rd - 0.13)*cos(rad(H)))
        sh.line(a, b, stroke=INK, sw=0.6 if whole else (0.3 if half else 0.15))
        if whole:
            T = 12 + q/15
            x, y = P((Rd - 0.065)*sin(rad(H)), (Rd - 0.065)*cos(rad(H)))
            sh.text(x, y + 0.2, ar_digits(int(T) % 12 or 12), 0.09*k, 'middle', KUFI, '#3b2a0c', 700)
    # الزوال
    a, b = P(0, 0.1), P(0, Rd - 0.13)
    sh.line(a, b, stroke=GOLD, sw=1.0)
    # دوائر البروج
    for dec, names, dates, lam in sign_curves():
        if (dec > 0.1) != summer or abs(dec) < 0.1: continue
        r = D.g/tan(rad(abs(dec)))
        if r > Rd - 0.13: continue
        sh.circle((cx, cy), r*k, stroke=TERRA, sw=0.6)
        x, y = P(-0.0, -r)
        sh.text(cx, cy - r*k - 2.2, ' و'.join(names) if len(names) > 1 else 'رأس ' + names[0], 2.4, 'middle', NASKH, TERRA, 700)
    for m, dec in month_decs(summer):
        r = D.g/tan(rad(abs(dec)))
        sh.circle((cx, cy), r*k, stroke=GREY, sw=0.25, dash='1.2 0.8')
        x, y = P(r*sin(rad(-60 if summer else 60)), r*cos(rad(-60 if summer else 60)))
        sh.text(x, y, '١ ' + GREG_MONTHS[m-1], 1.9, 'middle', SANS, GREY)
    # العصر
    pts = [D.face_point(d, asr_H(d), summer) for d in frange(-23.44, 23.44, 0.2)]
    pts = [p for p in pts if p and p[0]**2 + p[1]**2 < (Rd - 0.13)**2]
    if len(pts) > 1:
        sh.poly([P(*p) for p in pts], stroke=TEAL, sw=0.9)
        x, y = P(*pts[len(pts)//2])
        sh.text(x + 3, y, 'العصر', 2.6, 'start', KUFI, TEAL, 700)
    # الكعبة (صيفي)
    if summer:
        for d, ut, dec in kaaba_transits(REF_YEAR):
            _, eot, _ = sun(jd(d.year, d.month, d.day, ut))
            H = 15*(ut + LON/15 + eot/60 - 12)
            p = D.face_point(dec, H, True)
            if p:
                x, y = P(*p); sh.poly(star_n(x, y, 1.8, 0.9, 8), close=True, fill=BLUE, sw=0)
        x, y = P(*D.face_point(21.4, 4.0, True))
        sh.text(x - 3, y + 3.5, 'الشمس فوق الكعبة', 2.0, 'end', SANS, BLUE, 600)
    sh.text(cx, cy - Rd*k - 7, title, 3.6, 'middle', KUFI, INK, 700)


def d01():
    sh = Sheet(); v = View(470, 297, 30)
    frame(sh, 'المسقط العام والواجهات', ['قرص موازٍ لمعدل النهار مائل 60° عن الأفق', 'محموله دعامتان حجريتان شرقًا وغربًا'], 'D-01', '1:30 و1:50 (على لوح A1)',
          'التصميم (د): رخامة ابن الصوفي',
          ['• مأخوذ من «صنعة الرخامة الموازية لمعدل النهار» في',
           '   مخطوط شفاء الأسقام في وضع الساعات على الرخام',
           '   لشهاب الدين أحمد بن الصوفي (لوحة M-01).',
           f'• القرص: قطر {2*D.Rd:.2f} م، مركزه على ارتفاع {D.zc:.2f} م فوق مركز الساحة،',
           f'   مستواه عمودي على المحور القطبي (يميل {90-LAT:.4f}° عن الأفق).',
           '• الوجه العلوي «الصيفي» يُضاء من الاعتدال الربيعي إلى الخريفي،',
           '   والسفلي «الشتوي» في النصف الآخر من السنة.',
           f'• المحور القطبي نحاسي قطره 50 مم، وعليه خرزتان على بعد {D.g*1000:.0f} مم',
           '   من الوجهين: ظلهما على دوائر البروج يدل على التاريخ.',
           '• ساعات القرص متساوية 15° كما في المخطوط، مزاحة بفرق الطول.',
           '• يوم الاعتدال تكون الشمس في مستوى القرص فلا يضاء وجه منهما.',
           '• أرضية الساحة: نجمة ثمانية كبرى من الحجر الجيري والبازلت،',
           '   وحلقة التقويم ولوحا معادلة الزمن ورأس السنة الهجرية.'])
    girih_pattern(sh, 'gD', 0.9*v.k, color=GOLD, op=0.16)
    calendar_ring(sh, v, 6.35, R_SITE)
    c = v.p(0, 0)
    sh.circle(c, 6.35*v.k, fill='#f6f1e6', sw=0.6)
    sh.circle(c, 6.35*v.k, fill='url(#gD)', sw=0)
    # النجمة الثمانية الكبرى في الأرضية
    for rot, col in ((0, '#e7dcc3'), (22.5, '#ddd0b2')):
        sh.poly(star_n(c[0], c[1], 5.6*v.k, 5.6*v.k*0.7654, 8, rot), close=True, fill=col, stroke=GOLD, sw=0.4, op=0.9)
    sh.poly(star_n(c[0], c[1], 3.2*v.k, 3.2*v.k*0.7654, 8, 22.5), close=True, fill='#3b3a38', stroke=GOLD, sw=0.5)
    # خط الزوال والقبلة
    sh.path(v.d([(0, -6.3), (0, 6.3)]), stroke=GOLD, sw=1.0)
    qa = qibla()
    sh.path(v.d([(3.4*sin(rad(qa)), 3.4*cos(rad(qa))), (6.2*sin(rad(qa)), 6.2*cos(rad(qa)))]), stroke=BLUE, sw=0.9)
    xq, yq = v.p(4.9*sin(rad(qa)) + 0.2, 4.9*cos(rad(qa)) + 0.2)
    sh.text(xq, yq, f'القبلة {ar_digits(f"{qa:.1f}")}°', 2.6, 'middle', KUFI, BLUE, 700, rot=qa - 90)
    # القرص في المسقط: قطع ناقص 3.6 × 1.8
    ell = [D.world(D.Rd*cos(rad(t)), D.Rd*sin(rad(t))) for t in range(0, 361, 4)]
    sh.path(v.d([(p[0], p[1]) for p in ell], True), fill='#d6b16a', stroke=INK, sw=0.5)
    inner = [D.world((D.Rd - 0.13)*cos(rad(t)), (D.Rd - 0.13)*sin(rad(t))) for t in range(0, 361, 4)]
    sh.path(v.d([(p[0], p[1]) for p in inner], True), fill='#f7f1e3', stroke=INK, sw=0.3)
    a, b = D.world(0, 0, -D.rod), D.world(0, 0, D.rod)
    sh.path(v.d([(a[0], a[1]), (b[0], b[1])]), stroke='#7a5a1c', sw=1.4)
    for sx in (-1.0, 1.0):
        sh.path(v.d([(sx*1.95 - 0.25, -0.3), (sx*1.95 + 0.25, -0.3), (sx*1.95 + 0.25, 0.3), (sx*1.95 - 0.25, 0.3)], True), fill='#8a6a3a', stroke=INK, sw=0.3)
    sh.text(c[0], v.p(0, -1.45)[1], 'القرص المائل (مسقط)', 2.6, 'middle', KUFI, '#fffdf8', 700)
    # لوحا معادلة الزمن والسنة الهجرية
    gx0, gy0 = v.p(-2.4, -3.75); gx1, gy1 = v.p(2.4, -5.45)
    eot_graph(sh, gx0, gy0, gx1 - gx0, gy1 - gy0, title=True, fs=0.85)
    sh.para(v.p(2.3, 0)[0], v.p(0, 5.3)[1], ['## اقرأ الرخامة', '١. من الربيع إلى الخريف اقرأ الوجه العلوي من الشمال،', '    ومن الخريف إلى الربيع الوجه السفلي من الجنوب.',
            '٢. ظل المحور يدل على الساعة، وظل الخرزة على دائرة اليوم.', '٣. أضف تصحيح اليوم من اللوح الجنوبي (وساعة صيفًا).'], 2.3, 1.55)
    north_arrow(sh, 805, 470); scale_bar(sh, v, 768, 510, 2, 1)
    # واجهة جنوبية 1:50
    vs = View(780, 150, 50); k = vs.k
    sh.text(780, 70, 'الواجهة الجنوبية — 1:50', 3.2, 'middle', KUFI, INK, 700)
    gy = vs.p(0, 0)[1]
    sh.line((vs.p(-2.8, 0)[0], gy), (vs.p(2.8, 0)[0], gy), sw=0.5)
    for sx in (-1.95, 1.95):
        sh.rect(vs.p(sx - 0.25, 0)[0], vs.p(0, D.zc + 0.25)[1], 0.5*k, (D.zc + 0.25)*k, fill='#e9dcc0', sw=0.4)
        sh.poly(star_n(vs.p(sx, 0)[0], vs.p(0, D.zc + 0.42)[1], 0.22*k, 0.14*k, 8, 22.5), close=True, fill='#d6b16a', sw=0.3)
    # القرص من الجنوب: قطع ناقص عرضه 3.6 وارتفاعه 3.6·sin60
    pts = [D.world(D.Rd*cos(rad(t)), D.Rd*sin(rad(t))) for t in range(0, 361, 4)]
    sh.poly([vs.p(p[0], p[2]) for p in pts], close=True, fill='#d6b16a', sw=0.5)
    pts = [D.world((D.Rd - 0.13)*cos(rad(t)), (D.Rd - 0.13)*sin(rad(t))) for t in range(0, 361, 4)]
    sh.poly([vs.p(p[0], p[2]) for p in pts], close=True, fill='#efe3c4', sw=0.3)
    sh.ltr(780, gy + 6, f'{2*D.Rd:.2f}', 2.4)
    # قطاع شمال–جنوب 1:50
    vn = View(780, 300, 50)
    sh.text(780, 222, 'قطاع شمال–جنوب — 1:50 (الشمال يمينًا)', 3.2, 'middle', KUFI, INK, 700)
    gy = vn.p(0, 0)[1]
    sh.line((vn.p(-2.8, 0)[0], gy), (vn.p(2.8, 0)[0], gy), sw=0.5)
    a, b = D.world(0, -D.Rd), D.world(0, D.Rd)
    sh.line(vn.p(a[1], a[2]), vn.p(b[1], b[2]), stroke='#b58a3c', sw=2.0)
    a, b = D.world(0, 0, -D.rod), D.world(0, 0, D.rod)
    sh.line(vn.p(a[1], a[2]), vn.p(b[1], b[2]), stroke='#7a5a1c', sw=0.8)
    for off in (D.g, -D.g):
        p = D.world(0, 0, off); sh.circle(vn.p(p[1], p[2]), 1.0, fill=GOLD, sw=0.2)
    for dd, col, lbl in [(23.44, TERRA, 'شمس الانقلاب الصيفي'), (-23.44, BLUE, 'شمس الانقلاب الشتوي')]:
        alt = 90 - abs(LAT - dd)
        cpt = vn.p(0, D.zc)
        L = 1.8*vn.k
        sh.line(cpt, (cpt[0] - L*cos(rad(alt)), cpt[1] - L*sin(rad(alt))), stroke=col, sw=0.4, dash='1.5 1')
        sh.text(cpt[0] - L*cos(rad(alt)) - 1, cpt[1] - L*sin(rad(alt)) - 2, lbl, 2.1, 'end', SANS, col, 600)
    low = D.world(0, D.Rd)
    sh.ltr(vn.p(low[1], 0)[0] + 3, gy - low[2]*vn.k/2, f'{low[2]:.2f}', 2.2, 'start')
    sh.text(vn.p(-2.6, 0)[0], gy + 5, 'الجنوب', 2.4, 'middle', KUFI, GREY, 700)
    sh.text(vn.p(2.6, 0)[0], gy + 5, 'الشمال', 2.4, 'middle', KUFI, GREY, 700)
    sh.text(780, gy + 12, f'القرص يميل {90-LAT:.2f}° عن الأفق، والمحور {LAT:.2f}° نحو القطب', 2.3, 'middle', SANS, INK)
    return sh


def d02(ms_png=None):
    sh = Sheet()
    frame(sh, 'وجها الرخامة بالحساب', ['الوجه الصيفي كما يُرى من الشمال، والشتوي من الجنوب', 'مقارنة بصورة المخطوط'], 'D-02', '1:12.5 (على لوح A1)',
          'التصميم (د): رخامة ابن الصوفي',
          ['• نصف قطر دائرة اليوم = بعد الخرزة × ظل تمام الميل:',
           '   r = g · cot |δ|، فتضيق الدوائر نحو الانقلابين.',
           '• ما كان ميله دون 11° تخرج دائرته عن القرص، فيدل',
           '   عليه ظل المحور وحده (الساعة) دون التاريخ.',
           '• خطوط الساعات أشعة متساوية كل 15°، وأرباعها رفيعة.',
           '• الأرقام بالتوقيت الشتوي المتوسط لخط 30° ش؛',
           '   الوقت الرسمي = القراءة + تصحيح معادلة الزمن.',
           '• منحنى العصر على كل وجه بحسب ميل الشمس.',
           '• النجمة الزرقاء: موضع ظل الخرزة يومي تعامد الشمس',
           '   على الكعبة (28 مايو و16 يوليو).',
           '• الكتابة على الحافة البرونزية محفورة ومملوءة.'])
    k = 80.0
    draw_face(sh, 330, 300, k, True, 'الوجه الصيفي (العلوي) — مارس إلى سبتمبر')
    draw_face(sh, 650, 300, k, False, 'الوجه الشتوي (السفلي) — سبتمبر إلى مارس')
    if ms_png:
        data = base64.b64encode(open(ms_png, 'rb').read()).decode()
        sh.add(f'<image href="data:image/jpeg;base64,{data}" x="735" y="440" width="90" height="120" preserveAspectRatio="xMidYMid meet"/>')
        sh.text(780, 565, 'المخطوط: صنعة الرخامة الموازية لمعدل النهار', 2.2, 'middle', SANS, GREY)
    return sh


if __name__ == '__main__':
    import sys
    ms = sys.argv[1] if len(sys.argv) > 1 else None
    d01().save('../drawings/svg/D-01.svg'); d02(ms).save('../drawings/svg/D-02.svg')
