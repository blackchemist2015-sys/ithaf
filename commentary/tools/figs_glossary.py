# -*- coding: utf-8 -*-
"""Explanatory figures for the glossary of terms (prefix G)."""
import math
from figs import SVG, P, INK, RED, BLUE, GREEN, GOLD, FAINT, quadrant

PURPLE = '#6b2d6b'

def ell(s, cx, cy, rx, ry, c=INK, w=1.4, dash=None, rot=0):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" stroke="{c}" stroke-width="{w}" fill="none"{d} transform="rotate({rot} {cx:.1f} {cy:.1f})"/>')

def half_ell(s, cx, cy, rx, ry, front=True, c=INK, w=1.6, rot=0):
    # front half (lower) solid, back half dashed
    sweep = 0 if front else 1
    d = '' if front else ' stroke-dasharray="5,4"'
    s.add(f'<path d="M{cx-rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 0 {sweep} {cx+rx:.1f},{cy:.1f}" stroke="{c}" stroke-width="{w}" fill="none"{d} transform="rotate({rot} {cx:.1f} {cy:.1f})"/>')

def g01_chord_sine():
    s = SVG(760, 560)
    cx, cy, R = 330, 290, 220
    s.circle(cx, cy, R, INK, 2)
    s.dot(cx, cy, 4); s.text(cx - 10, cy + 18, 'المركز', 14, INK, 'r')
    a = 50
    A = P(cx, cy, R, -a); B = P(cx, cy, R, a)
    E = (cx + R, cy)
    s.line(cx, cy, *A, INK, 1.2); s.line(cx, cy, *E, INK, 1.2)
    s.line(*A, *B, RED, 2.4)
    s.text(A[0] + 14, (A[1] + B[1]) / 2 + 70, 'الوتر', 16, RED, 'l', bold=True)
    F = (A[0], cy)
    s.line(*A, *F, BLUE, 4)
    s.text(A[0] - 10, (A[1] + cy) / 2, 'الجيب (نصف الوتر)', 16, BLUE, 'r', bold=True)
    s.line(cx, cy, *F, GREEN, 4)
    s.text((cx + F[0]) / 2, cy + 22, 'جيب التمام', 16, GREEN, bold=True)
    s.line(F[0], cy, cx + R, cy, PURPLE, 4)
    s.text((F[0] + cx + R) / 2 + 6, cy + 22, 'السهم', 16, PURPLE, bold=True)
    s.arc(cx, cy, R + 14, -a, 0, GOLD, 3)
    x, y = P(cx, cy, R + 40, -a / 2); s.text(x, y, 'القوس', 16, GOLD, 'l', bold=True)
    s.arc(cx, cy, R + 14, -90, -a, '#888888', 2)
    x, y = P(cx, cy, R + 40, -(90 + a) / 2 - 4); s.text(x, y, 'تمام القوس', 15, '#666666', 'l')
    s.arc(cx, cy, 40, -a, 0, GOLD, 2)
    s.text(cx, cy + R + 40, 'جيب القوس نصف وتر ضعفها، وجيب التمام جيب ما بقي من القوس إلى تسعين، والسهم ما بين منتصف الوتر والقوس', 15)
    s.save('G01_chord_sine')

def g02_angles():
    s = SVG(880, 300)
    base = 230
    # right angle + perpendicular
    x = 720
    s.line(x - 110, base, x + 110, base, INK, 2); s.line(x, base, x, base - 150, INK, 2)
    s.path(f'M{x},{base-18} L{x+18},{base-18} L{x+18},{base}', RED, 1.6)
    s.text(x, base + 28, 'قائمة، والقائم عمود', 16, INK, bold=True)
    x = 440
    s.line(x - 110, base, x + 110, base, INK, 2)
    s.line(x - 110 + 40, base, *(P(x - 70, base, 170, -35)), INK, 2)
    s.arc(x - 70, base, 50, -35, 0, RED, 2)
    s.text(x, base + 28, 'حادة (أصغر من القائمة)', 16, INK, bold=True)
    x = 160
    s.line(x - 110, base, x + 110, base, INK, 2)
    o = (x + 40, base)
    s.line(*o, *P(o[0], o[1], 170, -140), INK, 2)
    s.arc(o[0], o[1], 40, -140, 0, RED, 2)
    s.text(x, base + 28, 'منفرجة (أكبر من القائمة)', 16, INK, bold=True)
    s.save('G02_angles')

def g03_sphere():
    s = SVG(760, 620)
    cx, cy, R = 380, 300, 230
    s.circle(cx, cy, R, INK, 2)
    s.line(cx, cy - R - 40, cx, cy + R + 40, RED, 1.8)
    s.dot(cx, cy - R, 5, RED); s.dot(cx, cy + R, 5, RED)
    s.text(cx + 12, cy - R - 22, 'القطب', 16, RED, 'l', bold=True)
    s.text(cx + 12, cy + R + 24, 'القطب', 16, RED, 'l', bold=True)
    s.text(cx + 12, cy - 120, 'المحور', 15, RED, 'l')
    half_ell(s, cx, cy, R, 55, True, BLUE, 2.4); half_ell(s, cx, cy, R, 55, False, BLUE, 2)
    s.text(cx + R - 60, cy + 70, 'المنطقة (دائرة عظيمة)', 15, BLUE, bold=True)
    for k in (0.45, 0.8):
        yy = cy - R * k
        rx = R * math.sqrt(1 - k * k)
        half_ell(s, cx, yy, rx, 55 * rx / R, True, GREEN, 1.6); half_ell(s, cx, yy, rx, 55 * rx / R, False, GREEN, 1.2)
    s.text(cx - R * 0.5 - 30, cy - R * 0.62, 'دوائر صغار متوازية', 15, GREEN, 'r', bold=True)
    ell(s, cx, cy, R, 70, GOLD, 1.8, rot=-50)
    s.text(cx + 150, cy + 175, 'دائرة عظيمة مائلة', 15, GOLD, 'l', bold=True)
    s.dot(cx, cy, 4); s.text(cx - 10, cy + 18, 'المركز', 14, INK, 'r')
    s.text(cx, cy + R + 66, 'العظيمة تنصّف الكرة ومركزها مركز الكرة، والصغيرة لا تنصفها', 15)
    s.save('G03_sphere')

def g04_horizontal():
    s = SVG(780, 600)
    cx, cy, R = 390, 330, 250
    s.arc(cx, cy, R, 180, 360, INK, 2)
    half_ell(s, cx, cy, R, 70, True, INK, 2.2); half_ell(s, cx, cy, R, 70, False, INK, 1.4)
    s.text(cx - R + 30, cy + 80, 'دائرة الأفق', 15, INK, 'l', bold=True)
    Z = (cx, cy - R); s.dot(*Z, 5); s.text(cx, cy - R - 18, 'سمت الرأس', 16, INK, bold=True)
    s.line(cx, cy, *Z, '#999999', 1, dash='4,3')
    s.dot(cx, cy, 4)
    # star
    st = (cx + 120, cy - 160)
    foot = (cx + 175, cy + 40)
    s.path(f'M{Z[0]},{Z[1]} Q{cx+170},{cy-150} {foot[0]},{foot[1]}', GREEN, 1.6)
    s.text(cx + 210, cy - 120, 'دائرة الارتفاع', 14, GREEN, 'l')
    s.dot(*st, 7, GOLD); s.text(st[0] - 12, st[1] - 14, 'الكوكب', 15, GOLD, 'r', bold=True)
    s.path(f'M{st[0]},{st[1]} Q{cx+178},{cy-50} {foot[0]},{foot[1]}', RED, 4)
    s.text(st[0] + 80, st[1] + 80, 'الارتفاع', 16, RED, 'l', bold=True)
    s.path(f'M{Z[0]},{Z[1]} Q{cx+40},{cy-230} {st[0]},{st[1]}', PURPLE, 3)
    s.text(cx + 40, cy - 245, 'تمام الارتفاع', 15, PURPLE, 'l', bold=True)
    E = (cx + R, cy)
    s.dot(*E, 5); s.text(E[0] + 10, E[1], 'المشرق', 15, INK, 'l', bold=True)
    s.dot(cx - R, cy, 5); s.text(cx - R - 10, cy, 'المغرب', 15, INK, 'r', bold=True)
    s.dot(cx, cy + 70, 5); s.text(cx, cy + 92, 'الجنوب', 15, INK, bold=True)
    s.dot(cx, cy - 70, 4); s.text(cx - 10, cy - 84, 'الشمال', 14, INK, 'r')
    s.add(f'<path d="M{E[0]:.1f},{E[1]:.1f} A{R},70 0 0 1 {foot[0]:.1f},{foot[1]:.1f}" stroke="{BLUE}" stroke-width="4" fill="none"/>')
    s.text(cx + 250, cy + 60, 'السمت', 16, BLUE, 'l', bold=True)
    s.text(cx, cy + 140, 'الإحداثيات الأفقية: الارتفاع على دائرة الارتفاع، والسمت على الأفق من نقطة المشرق أو المغرب', 15)
    s.save('G04_horizontal')

def g05_equatorial():
    s = SVG(780, 620)
    cx, cy, R = 390, 310, 240
    s.circle(cx, cy, R, INK, 2)
    N = (cx, cy - R); s.dot(*N, 5); s.text(cx, cy - R - 18, 'قطب المعدل الشمالي', 15, INK, bold=True)
    s.dot(cx, cy + R, 5); s.text(cx, cy + R + 22, 'القطب الجنوبي', 14, INK)
    half_ell(s, cx, cy, R, 65, True, BLUE, 2.4); half_ell(s, cx, cy, R, 65, False, BLUE, 1.4)
    s.text(cx - R + 10, cy + 84, 'معدل النهار (دائرة الاستواء)', 15, BLUE, 'l', bold=True)
    ell(s, cx, cy, R, 65, RED, 2, rot=-23.5)
    s.text(cx + 130, cy - 120, 'منطقة البروج', 15, RED, 'l', bold=True)
    Ar = (cx - R + 2, cy)
    s.dot(*Ar, 5, GOLD); s.text(Ar[0] - 8, Ar[1] - 14, 'رأس الحمل', 15, GOLD, 'r', bold=True)
    st = (cx + 90, cy - 150)
    foot = (cx + 120, cy + 60)
    s.path(f'M{N[0]},{N[1]} Q{cx+150},{cy-120} {foot[0]},{foot[1]}', GREEN, 1.6)
    s.text(cx + 160, cy - 30, 'دائرة الميل', 14, GREEN, 'l')
    s.dot(*st, 7, GOLD); s.text(st[0] - 12, st[1] - 10, 'الكوكب', 15, GOLD, 'r', bold=True)
    s.path(f'M{st[0]},{st[1]} Q{cx+125},{cy-40} {foot[0]},{foot[1]}', PURPLE, 4)
    s.text(st[0] + 50, st[1] + 70, 'البُعد (الميل)', 15, PURPLE, 'l', bold=True)
    s.add(f'<path d="M{Ar[0]:.1f},{Ar[1]:.1f} A{R},65 0 0 0 {foot[0]:.1f},{foot[1]:.1f}" stroke="{BLUE}" stroke-width="4.5" fill="none"/>')
    s.text(cx - 80, cy + 110, 'المطالع المستقيمة (المطلع)', 15, BLUE, bold=True)
    s.text(cx, cy + R + 60, 'الإحداثيات الاستوائية: البُعد عن معدل النهار، والمطالع المستقيمة على المعدل', 15)
    s.save('G05_equatorial')

def g06_ecliptic():
    s = SVG(820, 620)
    cx, cy, R = 410, 310, 240
    s.circle(cx, cy, R, INK, 2)
    half_ell(s, cx, cy, R, 60, True, RED, 2.6); half_ell(s, cx, cy, R, 60, False, RED, 1.4)
    s.text(cx - R + 10, cy + 80, 'منطقة البروج', 15, RED, 'l', bold=True)
    ell(s, cx, cy, R, 60, BLUE, 1.8, rot=23.5)
    s.text(cx + 120, cy + 140, 'معدل النهار', 15, BLUE, 'l', bold=True)
    K = (cx, cy - R); s.dot(*K, 5, RED); s.text(cx, cy - R - 18, 'قطب البروج', 15, RED, bold=True)
    Pn = P(cx, cy, R, -90 - 23.5); s.dot(*Pn, 5, BLUE); s.text(Pn[0] - 10, Pn[1] - 14, 'قطب المعدل', 15, BLUE, 'r', bold=True)
    Ar = (cx - R + 2, cy); s.dot(*Ar, 5, GOLD); s.text(Ar[0] - 8, Ar[1] - 14, 'رأس الحمل', 14, GOLD, 'r', bold=True)
    st = (cx + 70, cy - 140)
    foot = (cx + 95, cy + 58)
    s.path(f'M{K[0]},{K[1]} Q{cx+120},{cy-120} {foot[0]},{foot[1]}', GREEN, 1.6)
    s.text(cx + 140, cy - 60, 'دائرة العرض', 14, GREEN, 'l')
    s.dot(*st, 7, GOLD); s.text(st[0] - 12, st[1] - 10, 'الكوكب', 15, GOLD, 'r', bold=True)
    s.path(f'M{st[0]},{st[1]} Q{cx+100},{cy-30} {foot[0]},{foot[1]}', PURPLE, 4)
    s.text(st[0] + 40, st[1] + 80, 'العرض', 15, PURPLE, 'l', bold=True)
    s.add(f'<path d="M{Ar[0]:.1f},{Ar[1]:.1f} A{R},60 0 0 0 {foot[0]:.1f},{foot[1]:.1f}" stroke="{RED}" stroke-width="5" fill="none"/>')
    s.text(cx - 80, cy + 100, 'الطول (الدرجة) من أول الحمل', 15, RED, bold=True)
    s.text(cx, cy + R + 60, 'الإحداثيات البروجية: الطول على منطقة البروج، والعرض على دائرة العرض المارة بقطبي البروج', 15)
    s.save('G06_ecliptic')

def g07_spheres3():
    s = SVG(1000, 430)
    titles = ['الكرة المنتصبة (الفلك الدولابي)\nعرض صفر: خط الاستواء', 'الكرة المائلة (الفلك الحمائلي)\nعرض بين صفر وتسعين', 'الكرة الرحوية (الفلك الرحوي)\nعرض تسعين: تحت القطب']
    lats = [0, 40, 90]
    for i, (t, la) in enumerate(zip(titles, lats)):
        cx = 1000 - 170 - i * 330
        cy, R = 200, 120
        s.circle(cx, cy, R, INK, 1.6)
        s.line(cx - R - 20, cy, cx + R + 20, cy, INK, 2.4)
        s.text(cx + R + 18, cy - 12, 'الأفق', 13, INK, 'r')
        ang = la
        ax = P(cx, cy, R + 20, -ang); bx = P(cx, cy, R + 20, 180 - ang)
        s.line(*bx, *ax, RED, 1.4, dash='5,3')
        for k in (-0.6, -0.3, 0, 0.3, 0.6):
            # diurnal circles perpendicular to axis: chord at distance k*R along axis
            ux, uy = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
            px, py = -uy, ux
            c0 = (cx + k * R * ux, cy + k * R * uy)
            half = R * math.sqrt(1 - k * k)
            s.line(c0[0] - half * px, c0[1] - half * py, c0[0] + half * px, c0[1] + half * py, BLUE if k == 0 else GREEN, 2 if k == 0 else 1.3)
        l1, l2 = t.split('\n')
        s.text(cx, cy + R + 50, l1, 15, INK, bold=True)
        s.text(cx, cy + R + 74, l2, 13.5, INK)
    s.text(500, 25, 'المدارات اليومية (بالأخضر) ومعدل النهار (بالأزرق) بالنسبة إلى الأفق في الأوضاع الثلاثة', 15)
    s.save('G07_three_spheres')

def g08_zodiac():
    s = SVG(760, 760)
    cx, cy, R = 380, 380, 270
    s.circle(cx, cy, R, RED, 2); s.circle(cx, cy, R - 70, RED, 1.2)
    names = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']
    for i, n in enumerate(names):
        a = 180 + i * 30  # Aries begins at the vernal point (left); northern signs above
        x1, y1 = P(cx, cy, R, a); x2, y2 = P(cx, cy, R - 70, a)
        s.line(x1, y1, x2, y2, RED, 1.2)
        x, y = P(cx, cy, R - 35, a + 15)
        s.text(x, y, n, 15, INK, bold=True)
    s.line(cx - R - 20, cy, cx + R + 20, cy, BLUE, 1.4, dash='6,4')
    s.line(cx, cy - R - 20, cx, cy + R + 20, GOLD, 1.4, dash='6,4')
    s.text(cx - R - 10, cy + 18, 'الاعتدال الربيعي', 13, BLUE, 'r')
    s.text(cx + R + 10, cy + 18, 'الاعتدال الخريفي', 13, BLUE, 'l')
    s.text(cx, cy - R - 30, 'الانقلاب الصيفي (رأس السرطان)', 13, GOLD)
    s.text(cx, cy + R + 32, 'الانقلاب الشتوي (رأس الجدي)', 13, GOLD)
    s.text(cx, cy - 70, 'البروج الشمالية', 16, GREEN, bold=True)
    s.text(cx, cy + 70, 'البروج الجنوبية', 16, PURPLE, bold=True)
    s.text(cx + 80, cy - 10, 'الهابطة: من السرطان إلى القوس', 13, INK, 'l')
    s.text(cx - 80, cy - 10, 'الصاعدة: من الجدي إلى الجوزاء', 13, INK, 'r')
    # arrow for direction of signs (توالي)
    s.arc(cx, cy, R - 110, 200, 250, INK, 1.6)
    p = P(cx, cy, R - 110, 250)
    s.arrow(*P(cx, cy, R - 110, 245), *p, INK)
    s.text(*P(cx, cy, R - 135, 225), 'التوالي', 13, INK)
    s.save('G08_zodiac')

def g09_mansions():
    names = ['الشرطان', 'البطين', 'الثريا', 'الدبران', 'الهقعة', 'الهنعة', 'الذراع', 'النثرة', 'الطرف', 'الجبهة', 'الزبرة', 'الصرفة',
             'العواء', 'السماك', 'الغفر', 'الزبانى', 'الإكليل', 'القلب', 'الشولة', 'النعائم', 'البلدة', 'سعد الذابح', 'سعد بلع',
             'سعد السعود', 'سعد الأخبية', 'الفرغ المقدم', 'الفرغ المؤخر', 'بطن الحوت']
    s = SVG(820, 820)
    cx, cy, R = 410, 410, 330
    s.circle(cx, cy, R, RED, 2); s.circle(cx, cy, R - 90, RED, 1.2); s.circle(cx, cy, 150, INK, 1)
    zod = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']
    for i, z in enumerate(zod):
        a = 180 + i * 30
        s.line(*P(cx, cy, R - 90, a), *P(cx, cy, 150, a), INK, 0.8)
        s.text(*P(cx, cy, 195, a + 15), z, 13, INK)
    for i, n in enumerate(names):
        a = 180 + i * 360 / 28
        s.line(*P(cx, cy, R, a), *P(cx, cy, R - 90, a), RED, 1)
        mid = a + 360 / 56
        x, y = P(cx, cy, R - 45, mid)
        s.text(x, y, n, 11.5, INK, rot=(mid + 90) if math.sin(math.radians(mid)) > 0 else (mid - 90))
    s.text(cx, cy, 'لكل برج منزلتان وثلث', 14, GOLD, bold=True)
    s.save('G09_mansions')

def g10_apogee():
    s = SVG(760, 560)
    cx, cy, R = 380, 280, 200
    e = 60
    s.circle(cx, cy, 4, INK, 1, fill=INK); s.text(cx - 10, cy + 18, 'مركز العالم (الأرض)', 14, INK, 'r')
    s.circle(cx + e, cy, R, RED, 2)
    s.dot(cx + e, cy, 4, RED); s.text(cx + e + 10, cy + 18, 'مركز الخارج', 14, RED, 'l')
    s.line(cx - R + e - 30, cy, cx + R + e + 30, cy, INK, 1, dash='5,4')
    s.dot(cx + e + R, cy, 6, GOLD); s.text(cx + e + R + 10, cy - 18, 'الأوج (أبعد بُعد)', 15, GOLD, 'l', bold=True)
    s.dot(cx + e - R, cy, 6, BLUE); s.text(cx + e - R - 10, cy - 18, 'الحضيض (أقرب قرب)', 15, BLUE, 'r', bold=True)
    s.text(cx + e, cy - R - 20, 'النصف الأوجي', 15, GOLD)
    s.text(cx + e, cy + R + 26, 'النصف الحضيضي', 15, BLUE)
    s.add(f'<path d="M{cx+e},{cy-R} A{R},{R} 0 0 1 {cx+e},{cy+R}" stroke="{GOLD}" stroke-width="4" fill="none" opacity="0.6"/>')
    s.add(f'<path d="M{cx+e},{cy+R} A{R},{R} 0 0 1 {cx+e},{cy-R}" stroke="{BLUE}" stroke-width="4" fill="none" opacity="0.6"/>')
    s.text(cx, cy + R + 60, 'الفلك الخارج المركز: يبطؤ سير الكوكب المرئي عند الأوج ويسرع عند الحضيض', 15)
    s.save('G10_apogee')

def g11_prayer():
    s = SVG(900, 480)
    x0, x1, y0 = 70, 840, 260
    s.line(x0, y0, x1, y0, INK, 2)
    s.text(x1 + 10, y0, 'الأفق', 14, INK, 'l')
    def f(t):  # t in hours 0..24 ; altitude for Tunis, summer solstice approx
        phi, d = math.radians(36.67), math.radians(23.58)
        H = math.radians((t - 12) * 15)
        return math.degrees(math.asin(math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(H)))
    X = lambda t: x0 + (t - 2) / 21 * (x1 - x0)
    Y = lambda h: y0 - h * 2.6
    pts = [(X(t / 10), Y(f(t / 10))) for t in range(20, 231)]
    s.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), GOLD, 2.6)
    s.line(x0, Y(-19), x1, Y(-19), BLUE, 1, dash='4,4'); s.text(x0 - 6, Y(-19), '−١٩°', 12, BLUE, 'r')
    s.line(x0, Y(-17), x1, Y(-17), PURPLE, 1, dash='4,4'); s.text(x0 - 6, Y(-17) - 2, '−١٧°', 12, PURPLE, 'r')
    def find(target, lo, hi):
        for k in range(200):
            m = (lo + hi) / 2
            if (f(lo) - target) * (f(m) - target) <= 0: hi = m
            else: lo = m
        return m
    ev = [(find(-19, 2, 12), 'الفجر', BLUE), (find(-0.83, 2, 12), 'الشروق', INK), (12, 'الزوال (الظهر)', RED)]
    hm = f(12); sh = 12 / math.tan(math.radians(hm)); ha = math.degrees(math.atan(12 / (sh + 12)))
    ev += [(find(ha, 12, 22), 'العصر', GREEN), (find(-0.83, 12, 22), 'المغرب', INK), (find(-17, 12, 23), 'العشاء (غيبوبة الشفق)', PURPLE)]
    for i, (t, lab, c) in enumerate(ev):
        x, y = X(t), Y(f(t))
        s.dot(x, y, 5, c)
        s.line(x, y, x, 430 - (i % 2) * 28, c, 0.8, dash='3,3')
        s.text(x, 445 - (i % 2) * 28, lab, 14, c, bold=True)
    s.text(450, 25, 'ارتفاع الشمس على مدار يوم (آخر الجوزاء بتونس) وأوقات الصلاة الميقاتية', 15, INK, bold=True)
    s.text(X(16.5), Y(f(16.5)) - 30, 'ظل كل شيء مثله + ظل الزوال', 12, GREEN)
    s.save('G11_prayer_times')

def g12_qama():
    s = SVG(860, 360)
    base = 300
    items = [(12, 'قامة الأصابع', '١٢ إصبعًا'), (7, 'قامة الأقدام', '٧ أو ٦½ أقدام'), (8, 'قامة الأشبار', '٨ أشبار'), (60, 'قامة الأجزاء', '٦٠ جزءًا')]
    for i, (n, name, lab) in enumerate(items):
        x = 760 - i * 200
        H = 220
        s.line(x, base, x, base - H, INK, 6)
        step = H / n
        for k in range(1, n):
            w = 10 if (n != 60 or k % 5 == 0) else 5
            s.line(x - w, base - k * step, x + w, base - k * step, RED, 1)
        s.text(x, base + 22, name, 15, INK, bold=True)
        s.text(x, base + 44, lab, 13.5, INK)
    s.line(40, base, 840, base, INK, 1)
    s.text(430, 30, 'المقياس الواحد يُقسم على اصطلاحات مختلفة، ويُقدَّر الظل بما يُقدَّر به المقياس', 15)
    s.save('G12_qama')

def g13_limb():
    s = SVG(760, 420)
    gy = 360
    s.line(40, gy, 720, gy, INK, 2); s.text(60, gy + 20, 'الأفق', 14, INK, 'l')
    ox = 120
    sun = (560, 150); r = 46
    s.circle(*sun, r, GOLD, 2, fill='#f7e2a0')
    for (dy, lab, c) in ((-r, 'حاجب الشمس (الحرف الأعلى)', RED), (0, 'مركز الشمس', INK), (r, 'الحرف الأسفل', BLUE)):
        p = (sun[0], sun[1] + dy)
        s.line(ox, gy - 10, *p, c, 1.4, dash='6,3')
        s.dot(*p, 4, c)
        s.text(p[0] + 60, p[1], lab, 14, c, 'l', bold=True)
    s.dot(ox, gy - 10, 5)
    s.text(ox, gy + 22, 'الراصد', 14)
    s.text(380, 400, 'بين ارتفاع الحاجب وارتفاع المركز نصف قطر الشمس (نحو ربع درجة)', 15)
    s.save('G13_sun_limb')

def g14_bud_asl():
    s = SVG(820, 620)
    cx, cy, R = 400, 300, 240
    phi = 36 + 40 / 60; d = 23 + 35 / 60
    s.circle(cx, cy, R, INK, 2)
    s.line(cx - R - 30, cy, cx + R + 30, cy, INK, 2.4); s.text(cx + R + 34, cy, 'الأفق', 15, INK, 'l', bold=True)
    pole = P(cx, cy, R, 180 + phi)
    s.line(*P(cx, cy, R, phi), *pole, RED, 1.2, dash='6,4'); s.text(pole[0] - 10, pole[1] - 10, 'القطب', 14, RED, 'r')
    # equator: perpendicular to axis
    e1 = P(cx, cy, R, -(90 - phi)); e2 = P(cx, cy, R, 180 - (90 - phi))
    s.line(*e1, *e2, BLUE, 1.6)
    s.text(e1[0] + 10, e1[1] - 4, 'معدل النهار', 14, BLUE, 'l')
    # diurnal circle for northern declination: chord parallel to equator shifted toward pole by R sin d
    ux, uy = math.cos(math.radians(180 + phi)), math.sin(math.radians(180 + phi))  # toward north pole
    C = (cx + R * math.sin(math.radians(d)) * ux, cy + R * math.sin(math.radians(d)) * uy)
    ex, ey = math.cos(math.radians(-(90 - phi))), math.sin(math.radians(-(90 - phi)))
    half = R * math.cos(math.radians(d))
    T = (C[0] + half * ex, C[1] + half * ey); Bt = (C[0] - half * ex, C[1] - half * ey)
    s.line(*Bt, *T, GOLD, 3)
    s.text(T[0] + 10, T[1] - 12, 'مدار الشمس (آخر الجوزاء)', 14, GOLD, 'l', bold=True)
    s.dot(*T, 6, GOLD)
    s.dot(*C, 5, INK); s.text(C[0] - 10, C[1] - 14, 'مركز المدار', 13, INK, 'r')
    # perpendicular from C to horizon: bud al-qutr
    s.line(C[0], C[1], C[0], cy, PURPLE, 4)
    s.text(C[0] - 10, (C[1] + cy) / 2, 'بُعد القطر', 16, PURPLE, 'r', bold=True)
    # asl: vertical from T down to level of C
    s.line(T[0], T[1], T[0], C[1], GREEN, 4)
    s.line(C[0], C[1], T[0], C[1], GREEN, 1, dash='3,3')
    s.text(T[0] + 10, (T[1] + C[1]) / 2, 'الأصل', 16, GREEN, 'l', bold=True)
    s.line(T[0], C[1], T[0], cy, PURPLE, 1.4, dash='4,3')
    s.text(cx, cy + R + 40, 'جيب الغاية = الأصل + بُعد القطر ، وجيب أي ارتفاع = بُعد القطر + الأصل × جتا فضل الدائر', 15)
    s.text(cx, cy + R + 66, '(في الميل الشمالي؛ ويُطرح بُعد القطر في الجنوبي)', 13)
    s.save('G14_bud_asl')

def g15_sights():
    s = SVG(820, 300)
    y = 160
    s.line(60, y + 40, 760, y + 40, INK, 3)
    s.text(410, y + 64, 'جيب التمام (حرف الربع)', 14, INK)
    for x in (520, 300):
        s.path(f'M{x-14},{y+40} L{x-14},{y-40} L{x+14},{y-40} L{x+14},{y+40}', INK, 2, fill='#efe3d3')
        s.circle(x, y, 5, INK, 1.5, fill='#ffffff')
    s.text(520, y - 56, 'الهدفة العليا (القريبة من المركز)', 13, INK)
    s.text(300, y - 56, 'الهدفة السفلى', 13, INK)
    s.circle(760, y, 10, INK, 2); s.text(760, y - 26, 'العين', 13)
    s.line(60, y, 750, y, RED, 1.4, dash='6,4')
    s.text(150, y - 16, 'خط النظر من الثقبتين', 13, RED)
    s.text(410, y - 100, 'الكوكب يُرصد من الثقبتين ليلًا، والشمس بستر ظل العليا للسفلى نهارًا، أو يُكتفى بالنظر من فوق الهدفتين', 14)
    s.save('G15_sights')

def build():
    for f in (g01_chord_sine, g02_angles, g03_sphere, g04_horizontal, g05_equatorial, g06_ecliptic, g07_spheres3,
              g08_zodiac, g09_mansions, g10_apogee, g11_prayer, g12_qama, g13_limb, g14_bud_asl, g15_sights):
        f()

if __name__ == '__main__':
    build()
