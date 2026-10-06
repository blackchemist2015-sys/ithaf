# -*- coding: utf-8 -*-
"""Generate SVG figures for the commentary on Ithaf al-Mahbub."""
import math, os, json, re
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures', 'svg')
os.makedirs(OUT, exist_ok=True)

INK = '#2b1d12'
RED = '#b0301f'
FAINT = '#d9b9a6'
BLUE = '#1f4e79'
GREEN = '#2e6b3a'
GOLD = '#8a6d1c'

ABJAD = {5: 'ه', 10: 'ي', 15: 'يه', 20: 'ك', 25: 'كه', 30: 'ل', 35: 'له', 40: 'م', 45: 'مه',
         50: 'ن', 55: 'نه', 60: 'س', 65: 'سه', 70: 'ع', 75: 'عه', 80: 'ف', 85: 'فه', 90: 'ص'}

def ar_num(n):
    s = str(n)
    return s.translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))

class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = []
    def add(self, s):
        self.items.append(s)
    def line(self, x1, y1, x2, y2, c=INK, w=1.2, dash=None, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d} opacity="{op}" stroke-linecap="round"/>')
    def circle(self, x, y, r, c=INK, w=1.2, fill='none', dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" stroke="{c}" stroke-width="{w}" fill="{fill}"{d}/>')
    def dot(self, x, y, r=3.5, c=INK):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}"/>')
    def path(self, d, c=INK, w=1.2, fill='none', dash=None, op=1):
        dd = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}"{dd} opacity="{op}" stroke-linejoin="round"/>')
    def text(self, x, y, s, size=17, c=INK, anchor='m', bold=False, rot=None):
        # anchor: m=middle, r=text lies to the right of x, l=text lies to the left of x
        a = {'m': 'middle', 'l': 'end', 'r': 'start'}[anchor]  # l: left edge at x ; r: right edge at x (rtl)
        b = ' font-weight="700"' if bold else ''
        tr = f' transform="rotate({rot:.1f} {x:.1f} {y:.1f})"' if rot is not None else ''
        s = s.replace('&', '&amp;').replace('<', '&lt;')
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{c}" text-anchor="{a}" direction="rtl" dominant-baseline="middle"{b}{tr}>{s}</text>')
    def arrow(self, x1, y1, x2, y2, c=INK, w=1.3):
        self.line(x1, y1, x2, y2, c, w)
        ang = math.atan2(y2 - y1, x2 - x1)
        L = 9
        p1 = (x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4))
        p2 = (x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))
        self.add(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{c}"/>')
    def arc(self, cx, cy, r, a1, a2, c=INK, w=1.2, dash=None):
        """arc from angle a1 to a2 (degrees, svg coords: 0=+x, 90=+y down)"""
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        x2, y2 = cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2))
        large = 1 if abs(a2 - a1) > 180 else 0
        sweep = 1 if a2 > a1 else 0
        self.path(f'M{x1:.1f},{y1:.1f} A{r:.1f},{r:.1f} 0 {large} {sweep} {x2:.1f},{y2:.1f}', c, w, dash=dash)
    def save(self, name):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'font-family="Amiri, serif"><rect width="100%" height="100%" fill="#ffffff"/>')
        with open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf8') as f:
            f.write(head + '\n'.join(self.items) + '</svg>')

def P(cx, cy, r, ang):
    return cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))

# ---------------------------------------------------------------- quadrant
def quadrant(s, cx, cy, R, grid=True, labels=True, abjad=True, fine=True, extras=False,
             sights=True, small=False):
    u = R / 60.0
    if grid:
        for k in range(1, 60):
            y = cy + k * u
            xe = cx + math.sqrt(max(R * R - (k * u) ** 2, 0))
            heavy = (k % 5 == 0)
            if fine or heavy:
                s.line(cx, y, xe, y, INK if heavy else FAINT, 0.9 if heavy else 0.5)
            x = cx + k * u
            ye = cy + math.sqrt(max(R * R - (k * u) ** 2, 0))
            if fine or heavy:
                s.line(x, cy, x, ye, INK if heavy else FAINT, 0.9 if heavy else 0.5)
    # edges
    s.line(cx, cy, cx + R, cy, INK, 2.2)
    s.line(cx, cy, cx, cy + R, INK, 2.2)
    s.arc(cx, cy, R, 0, 90, INK, 2.2)
    s.arc(cx, cy, R + 14 * (0.6 if small else 1), 0, 90, INK, 1.0)
    for d in range(0, 91):
        L = 14 if d % 5 == 0 else 6
        if small:
            L *= 0.6
            if d % 5:
                continue
        x1, y1 = P(cx, cy, R, d)
        x2, y2 = P(cx, cy, R + L, d)
        s.line(x1, y1, x2, y2, INK, 0.8)
    if abjad and not small:
        for d in range(5, 91, 5):
            x, y = P(cx, cy, R + 27, d - 2.5)
            s.text(x, y, ABJAD[d], 13, INK)
            x, y = P(cx, cy, R + 44, d - 2.5)
            s.text(x, y, ABJAD[95 - d] if 95 - d in ABJAD else '', 13, RED)
    if sights:
        hs = 16 if not small else 10
        for xx in (cx + R * 0.18, cx + R * 0.82):
            s.path(f'M{xx-hs/2:.1f},{cy:.1f} L{xx-hs/2:.1f},{cy-hs:.1f} L{xx+hs/2:.1f},{cy-hs:.1f} L{xx+hs/2:.1f},{cy:.1f}', INK, 1.4, fill='#f3e6d8')
    s.circle(cx, cy, 3.5, INK, 1.2, fill='#ffffff')
    if extras:
        for r, c in ((24, RED), (19, GREEN), (14, BLUE)):
            s.arc(cx, cy, r * u, 0, 90, c, 1.6)
        # tajyib semicircles
        s.arc(cx + R / 2, cy, R / 2, 0, 180, GOLD, 1.4)
        s.arc(cx, cy + R / 2, R / 2, -90, 90, GOLD, 1.4)
        # asr curve
        pts = []
        for i in range(1, 900):
            H = i / 10.0
            Hr = math.radians(H)
            a = math.atan(1 / (1 + 1 / math.tan(Hr)))
            r = R * math.sin(a) / math.sin(Hr)
            pts.append(P(cx, cy, r, H))
        pts.insert(0, (cx + R, cy))
        pts.append((cx, cy + R * math.sin(math.radians(45))))
        s.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), '#6b2d6b', 1.6)
        # temporal hour arcs: circles through centre with centre on sittini, through arc point 15k
        for k in range(1, 6):
            th = math.radians(15 * k)
            D = R / math.sin(th)
            rr = D / 2
            ccx, ccy = cx, cy + rr
            # draw arc from centre to arc point
            x2, y2 = P(cx, cy, R, 15 * k)
            s.path(f'M{cx:.1f},{cy:.1f} A{rr:.1f},{rr:.1f} 0 0 1 {x2:.1f},{y2:.1f}', '#777777', 1.0, dash='5,3')
    return u

def thread(s, cx, cy, R, ang, bead=None, u=None, c=RED, plumb=True, ext=1.12):
    x2, y2 = P(cx, cy, R * ext, ang)
    s.line(cx, cy, x2, y2, c, 1.8)
    if plumb:
        s.circle(x2, y2, 5, c, 1.2, fill='#ffffff')
    if bead is not None:
        bx, by = P(cx, cy, bead * u, ang)
        s.add(f'<rect x="{bx-5:.1f}" y="{by-5:.1f}" width="10" height="10" fill="#ffffff" stroke="{RED}" stroke-width="2"/>')
        return bx, by

def panel(s, cx, cy, R, title, ang, bead=None, to_sittini=False, to_arc=False, munkus=False,
          mark_s=None, mark_t=None, arc_label=None, arc_from_end=False, note=None, mark_arc=None):
    u = quadrant(s, cx, cy, R, fine=False, abjad=False, small=True)
    s.text(cx + R / 2, cy - 38, title, 18, INK, bold=True)
    s.text(cx - 14, cy + R + 4, '٩٠°', 12, INK, 'r')
    s.text(cx + R + 4, cy - 12, '٠°', 12, INK, 'l')
    if mark_s is not None:
        for v, lab in mark_s:
            y = cy + v * u
            s.line(cx - 6, y, cx + 6, y, BLUE, 2)
            s.text(cx - 10, y, lab, 14, BLUE, 'r')
    if mark_t is not None:
        for v, lab in mark_t:
            x = cx + v * u
            s.line(x, cy - 5, x, cy + 5, BLUE, 2)
            s.text(x, cy - 16, lab, 14, BLUE)
    b = thread(s, cx, cy, R, ang, bead, u)
    if b:
        bx, by = b
        if to_sittini:
            s.line(bx, by, cx, by, BLUE, 1.6, dash='5,3')
        if munkus:
            s.line(bx, by, bx, cy, BLUE, 1.6, dash='5,3')
        if to_arc:
            xe = cx + math.sqrt(max(R * R - (by - cy) ** 2, 0))
            s.line(bx, by, xe, by, BLUE, 1.6, dash='5,3')
            s.dot(xe, by, 3.5, BLUE)
    if arc_label:
        # arc of the angle near the circumference
        if arc_from_end:
            s.arc(cx, cy, R + 22, ang, 90, GREEN, 2.2)
            mid = (ang + 90) / 2
        else:
            s.arc(cx, cy, R + 22, 0, ang, GREEN, 2.2)
            mid = ang / 2
        x, y = P(cx, cy, R + 34, mid)
        s.text(x, y, arc_label, 15, GREEN, 'l', bold=True)
    if mark_arc:
        for a, lab in mark_arc:
            x, y = P(cx, cy, R, a)
            s.dot(x, y, 4, GREEN)
            x, y = P(cx, cy, R + 30, a)
            s.text(x, y, lab, 14, GREEN)
    if note:
        for i, line in enumerate(note):
            s.text(cx + R / 2, cy + R + 50 + 22 * i, line, 15, INK)

def ops(name, panels, R=230, H=None, gap=120):
    n = len(panels)
    W = max(n * (R + gap) + 300, 760)
    H = H or R + 190
    s = SVG(W, H)
    # panels laid out right-to-left (Arabic reading order)
    for i, p in enumerate(panels):
        cx = W - 240 - R - i * (R + gap)
        cy = 80
        panel(s, cx, cy, R, **p)
        if i < n - 1:
            s.arrow(cx - 30, cy + R / 2, cx - gap + 20, cy + R / 2, GOLD, 2)
    s.save(name)

# ================================================================ FIGURES
def fig_quadrant_full():
    W, H = 1320, 960
    s = SVG(W, H)
    cx, cy, R = 430, 170, 600
    u = quadrant(s, cx, cy, R, extras=True)
    ang = 52
    bx, by = thread(s, cx, cy, R, ang, 38, u)
    x2, y2 = P(cx, cy, R * 1.12, ang)
    def lab(px, py, tx, ty, t, c=INK):
        s.line(px, py, tx, ty, c, 0.9)
        s.dot(px, py, 2.5, c)
        s.text(tx + (6 if tx > px else -6), ty, t, 19, c, 'l' if tx > px else 'r', bold=True)
    L = cx - 40
    lab(cx, cy, cx - 40, cy - 60, 'المركز (الخَرْم، البُخش)')
    lab(cx + R * 0.82, cy - 16, cx + R * 0.70, cy - 80, 'الهُدفتان', RED)
    lab(cx + R * 0.45, cy, cx + R * 0.30, cy - 105, 'جيب التمام (خط المشرق والمغرب)')
    lab(cx + 48 * u, cy + 3 * u, cx + R * 0.78, cy - 145, 'الجيوب المنكوسة (موازية للستيني)', BLUE)
    lab(*P(cx, cy, 14 * u, 84), L, cy + 14 * u, 'دائرة بُعد القطر (١٤ لتونس)', BLUE)
    lab(*P(cx, cy, 19 * u, 84), L, cy + 19 * u + 8, 'دائرة نصف الفضلة (١٩ لتونس)', GREEN)
    lab(*P(cx, cy, 24 * u, 84), L, cy + 24 * u + 16, 'دائرة الميل (٢٤)', RED)
    lab(cx, cy + 32 * u, L, cy + 32 * u, 'الستيني (خط الزوال، الجيب الأعظم)')
    lab(cx + 6 * u, cy + 41 * u, L, cy + 41 * u, 'الجيوب المبسوطة (موازية لجيب التمام)', BLUE)
    lab(bx, by, L, cy + 50 * u, 'المُرِيّ (الخرزة)', RED)
    lab(*P(cx + R / 2, cy, R / 2, 160), L, cy + 57 * u, 'دائرتا التجييب', GOLD)
    lab(*P(cx, cy, R * 0.79, 72), cx + R * 0.35, cy + R + 95, 'قوس العصر', '#6b2d6b')
    lab(*P(cx, cy, R * 0.75, 15), cx + R + 60, cy + 120, 'الساعات الزمانية', '#555555')
    lab(x2, y2, cx + R + 20, cy + R + 40, 'الخيط والشاقول', RED)
    lab(*P(cx, cy, R + 14, 60), cx + R * 0.9, cy + R + 110, 'قوس الارتفاع (٩٠ جزءًا)')
    s.text(cx + R + 60, cy + 8, 'أول القوس', 17, INK, 'l')
    s.text(cx - 6, cy + R + 50, 'آخر القوس', 17, INK, 'r')
    s.save('Q00_rub_mujayyab')

def fig_proportion():
    s = SVG(760, 600)
    cx, cy, R = 120, 70, 400
    u = quadrant(s, cx, cy, R, fine=False, abjad=False, small=True, sights=False)
    ang = 38
    r1, r2 = 30, 52
    a1 = P(cx, cy, r1 * u, ang); a2 = P(cx, cy, r2 * u, ang)
    thread(s, cx, cy, R, ang, None, u)
    for (x, y), lab in ((a1, 'ب'), (a2, 'د')):
        s.line(x, y, cx, y, BLUE, 1.8, dash='6,3')
        s.dot(x, y, 4.5, RED)
        s.text(x + 14, y - 10, lab, 20, RED, 'l', bold=True)
    s.text(cx - 16, a1[1], 'ج', 20, BLUE, 'r', bold=True)
    s.text(cx - 16, a2[1], 'هـ', 20, BLUE, 'r', bold=True)
    s.text(cx - 14, cy - 8, 'أ', 20, INK, 'r', bold=True)
    s.text(cx + R / 2 + 60, cy + R + 50,
           'المثلثان أ ب ج و أ د هـ متشابهان: ب ج ⁄ أ ب = د هـ ⁄ أ د = جيب الزاوية ⁄ ٦٠', 18, INK)
    s.text(cx + R / 2 + 60, cy + R + 80, '«ضَعْ على الأول، وعَلِّمْ على الثاني، وانقُلْ إلى الثالث، يخرجْ لك الرابع»', 18, RED)
    s.save('Q01_proportion')

def fig_altitude():
    s = SVG(860, 560)
    # sun upper right
    sx, sy = 120, 70
    for k in range(12):
        a = k * 30
        s.line(sx + 34 * math.cos(math.radians(a)), sy + 34 * math.sin(math.radians(a)),
               sx + 48 * math.cos(math.radians(a)), sy + 48 * math.sin(math.radians(a)), GOLD, 2)
    s.circle(sx, sy, 26, GOLD, 2, fill='#f7e2a0')
    s.text(sx, sy + 70, 'الشمس', 17, GOLD, bold=True)
    h = 35
    # quadrant rotated: jayb al-tamam edge points to the sun (direction up-left at altitude h)
    cx, cy, R = 600, 300, 230
    dirx, diry = -math.cos(math.radians(h)), -math.sin(math.radians(h))  # toward sun
    # sittini direction is perpendicular, pointing down-left
    px, py = -diry * -1, dirx * -1
    px, py = math.sin(math.radians(h)) * -1 * -1, 0
    # simpler: build quadrant points manually
    tx, ty = cx + R * dirx, cy + R * diry  # end of jayb tamam
    sxn, syn = math.cos(math.radians(90 + h)) * -1, math.sin(math.radians(90 + h)) * -1
    # sittini direction rotate dir by -90 (clockwise) -> points down-left
    six, siy = diry * -1 * -1, -dirx
    six, siy = -diry, dirx
    six, siy = (math.sin(math.radians(h)) * -1, math.cos(math.radians(h)))
    ex, ey = cx + R * six, cy + R * siy
    s.line(cx, cy, tx, ty, INK, 2.4)
    s.line(cx, cy, ex, ey, INK, 2.4)
    # arc from jayb end to sittini end
    a_t = math.degrees(math.atan2(diry, dirx)); a_s = math.degrees(math.atan2(siy, six))
    s.arc(cx, cy, R, a_s, a_t + 360 if a_t < a_s else a_t, INK, 2.4)
    # sights on jayb al-tamam
    for f in (0.2, 0.8):
        x, y = cx + R * f * dirx, cy + R * f * diry
        nx, ny = -siy * 0 + -six * 0, 0
        ox, oy = -six * 14, -siy * 14
        s.line(x, y, x + ox, y + oy, INK, 6)
    # sun ray along sights
    s.line(sx + 30, sy + 22, cx + 30 * dirx * -1, cy + 30 * diry * -1, GOLD, 1.4, dash='7,4')
    # plumb line vertical
    s.line(cx, cy, cx, cy + R + 50, RED, 2)
    s.circle(cx, cy + R + 56, 7, RED, 1.5, fill='#ffffff')
    s.text(cx + 14, cy + R + 56, 'الشاقول', 16, RED, 'l')
    # angle between plumb and sittini = h
    s.arc(cx, cy, R * 0.55, 90, a_s, GREEN, 2.4)
    mx, my = P(cx, cy, R * 0.55 + 26, (90 + a_s) / 2)
    s.text(mx, my, 'الارتفاع', 16, GREEN, bold=True)
    # horizon
    s.line(40, cy + R + 90, 820, cy + R + 90, INK, 1, dash='4,4')
    s.text(780, cy + R + 76, 'الأفق', 15, INK)
    s.line(sx, sy, sx + 300 * math.cos(math.radians(h)), sy + 300 * math.sin(math.radians(h)), GOLD, 0.5)
    s.text(cx + 60, cy - 120, 'الخط ذو الهُدفتين (جيب التمام) نحو الشمس', 16, INK, 'l')
    s.text(ex - 10, ey + 22, 'الستيني (الخالي من الهدف)', 16, INK, 'r')
    s.text(430, 535, 'يُحرَّك الربع حتى تستر الهدفةُ العليا السفلى بظلها، ويُقرأ الارتفاع من جهة الخط الخالي من الهدف', 16, INK)
    s.save('B01_altitude')

def fig_ch3_shadow():
    s = SVG(820, 420)
    # gnomon and shadows
    gx, gy = 600, 320
    s.line(80, gy, 780, gy, INK, 2)
    s.line(gx, gy, gx, gy - 160, INK, 4)
    s.text(gx + 14, gy - 80, 'المقياس (القامة = ١٢ إصبعًا)', 15, INK, 'l')
    hx = gx - 160 / math.tan(math.radians(35))
    s.line(gx, gy - 160, hx, gy, GOLD, 1.6, dash='6,4')
    s.line(hx, gy, gx, gy, RED, 5)
    s.text((hx + gx) / 2, gy + 22, 'الظل المبسوط (المستوي)', 16, RED)
    s.arc(hx, gy, 60, -35, 0, GREEN, 2)
    s.text(hx + 80, gy - 18, 'الارتفاع', 15, GREEN, 'l')
    # wall with reversed shadow
    wx = 200
    s.line(wx, gy, wx, gy - 260, INK, 3)
    s.line(wx, gy - 230, wx + 120, gy - 230, INK, 4)
    s.text(wx + 60, gy - 248, 'مقياس أفقي في جدار', 14, INK)
    yy = gy - 230 + 120 * math.tan(math.radians(35))
    s.line(wx + 120, gy - 230, wx, yy, GOLD, 1.6, dash='6,4')
    s.line(wx, gy - 230, wx, yy, RED, 5)
    s.text(wx - 10, (yy + gy - 230) / 2, 'الظل المنكوس (المعكوس)', 15, RED, 'r')
    s.text(410, 395, 'الظل المبسوط = القامة × ظتا الارتفاع ، والمنكوس = القامة × ظا الارتفاع', 16, INK)
    s.save('B03_shadows')

def fig_meridian():
    s = SVG(760, 560)
    cx, cy, R = 380, 290, 220
    s.circle(cx, cy, R, INK, 2)
    s.line(cx - R - 30, cy, cx + R + 30, cy, INK, 2)
    s.text(cx + R + 36, cy, 'الجنوب', 15, INK, 'l')
    s.text(cx - R - 36, cy, 'الشمال', 15, INK, 'r')
    s.text(cx + R - 30, cy + 16, 'الأفق', 15, INK)
    s.dot(cx, cy - R, 4); s.text(cx - 10, cy - R - 16, 'سمت الرأس', 15, INK, 'r')
    phi = 36 + 40 / 60
    # north pole at altitude phi above north horizon (left)
    pole = P(cx, cy, R, 180 + phi)
    s.line(*P(cx, cy, R, phi), *pole, BLUE, 1.6)
    s.dot(*pole, 4.5, BLUE); s.text(pole[0] - 50, pole[1] - 8, 'القطب الشمالي', 15, BLUE)
    s.arc(cx, cy, R + 18, 180, 180 + phi, BLUE, 2.4)
    x, y = P(cx, cy, R + 52, 180 + phi / 2); s.text(x, y, 'العرض', 15, BLUE, bold=True)
    # equator perpendicular to axis: at angle (from south horizon) 90-phi up
    eq = P(cx, cy, R, -(90 - phi))
    s.line(cx, cy, *eq, RED, 1.6)
    s.line(cx, cy, *P(cx, cy, R, 180 - (90 - phi)), RED, 1.0, dash='4,3')
    s.text(eq[0] + 50, eq[1] - 6, 'معدل النهار', 15, RED, 'l')
    s.arc(cx, cy, R * 0.45, -(90 - phi), 0, RED, 2)
    x, y = P(cx, cy, R * 0.45 + 50, -(90 - phi) / 2); s.text(x, y, 'تمام العرض', 14, RED)
    d = 23 + 35 / 60
    sun = P(cx, cy, R, -(90 - phi + d))
    s.line(cx, cy, *sun, GOLD, 1.6)
    s.dot(*sun, 7, GOLD); s.text(sun[0] + 14, sun[1] - 14, 'الشمس في غاية ارتفاعها (آخر الجوزاء)', 14, GOLD, 'l')
    s.arc(cx, cy, R * 0.75, -(90 - phi + d), -(90 - phi), GOLD, 2.4)
    x, y = P(cx, cy, R * 0.75 + 26, -(90 - phi + d / 2)); s.text(x, y, 'الميل', 14, GOLD, bold=True)
    s.arc(cx, cy, R * 0.25, -(90 - phi + d), 0, GREEN, 2)
    s.text(cx + 100, cy + 70, 'الغاية = تمام العرض + الميل الشمالي', 16, GREEN)
    s.text(cx, cy + R + 40, 'العرض = ٩٠° − الغاية + الميل الشمالي = ٩٠ − ٧٦;٥٥ + ٢٣;٣٥ ≈ ٣٦;٤٠ لتونس', 16, INK)
    s.save('B05_meridian')

def fig_dair():
    s = SVG(820, 560)
    cx, cy, R = 410, 270, 220
    # diurnal circle seen as ellipse-ish: draw circle (equatorial projection)
    s.circle(cx, cy, R, INK, 2)
    s.line(cx - R - 30, cy + 70, cx + R + 30, cy + 70, INK, 2)
    s.text(cx + R + 34, cy + 70, 'الأفق', 15, INK, 'l')
    s.line(cx, cy - R - 20, cx, cy + R + 20, RED, 1.6)
    s.text(cx, cy - R - 32, 'دائرة نصف النهار', 15, RED)
    # rising point (east) where y=cy+70 on circle, left side = east? we take east on right
    dy = 70; dx = math.sqrt(R * R - dy * dy)
    E = (cx + dx, cy + dy); Wp = (cx - dx, cy + dy)
    s.dot(*E, 4.5); s.text(E[0] + 12, E[1] + 18, 'الطلوع', 15, INK, 'l')
    s.dot(*Wp, 4.5); s.text(Wp[0] - 12, Wp[1] + 18, 'الغروب', 15, INK, 'r')
    sun_a = -40
    sun = P(cx, cy, R, sun_a)
    s.dot(*sun, 8, GOLD); s.text(sun[0] + 16, sun[1] - 14, 'الشمس', 15, GOLD, 'l')
    aE = math.degrees(math.atan2(dy, dx))
    s.arc(cx, cy, R + 16, sun_a, aE, GREEN, 3)
    x, y = P(cx, cy, R + 50, (sun_a + aE) / 2); s.text(x, y, 'الدائر', 16, GREEN, bold=True)
    s.arc(cx, cy, R + 16, -90, sun_a, BLUE, 3)
    x, y = P(cx, cy, R + 50, (sun_a - 90) / 2); s.text(x, y, 'فضل الدائر', 16, BLUE, bold=True)
    s.arc(cx, cy, R - 18, -90, aE, RED, 2, dash='5,3')
    x, y = P(cx, cy, R - 60, -60); s.text(x, y, 'نصف قوس النهار', 15, RED)
    s.arc(cx, cy, R - 40, 0, aE, '#6b2d6b', 2.4)
    x, y = P(cx, cy, R - 80, aE / 2 + 2); s.text(x - 20, y, 'نصف الفضلة', 14, '#6b2d6b')
    s.line(cx - R, cy, cx + R, cy, INK, 0.8, dash='3,3')
    s.text(cx - R + 60, cy - 12, 'موضع معدل النهار', 13, INK)
    s.text(cx, cy + R + 50, 'نصف قوس النهار = ٩٠° + نصف الفضلة (في البروج الشمالية) ، والدائر = نصف القوس − فضل الدائر', 16, INK)
    s.save('B08_dair')

def fig_qibla_sphere():
    s = SVG(760, 600)
    cx, cy, R = 380, 280, 230
    s.circle(cx, cy, R, INK, 2)
    s.text(cx, cy - R - 18, 'الشمال', 15)
    s.text(cx, cy + R + 22, 'الجنوب', 15)
    s.text(cx + R + 36, cy, 'المشرق', 15)
    s.text(cx - R - 36, cy, 'المغرب', 15)
    s.line(cx - R, cy, cx + R, cy, INK, 1.2)
    s.line(cx, cy - R, cx, cy + R, INK, 1.2)
    a = 18
    q = P(cx, cy, R, a)
    s.line(cx, cy, *q, RED, 3)
    s.dot(*q, 6, RED); s.text(q[0] + 14, q[1] + 22, 'جهة مكة', 16, RED, 'l', bold=True)
    s.arc(cx, cy, R * 0.6, 0, a, GREEN, 2.6)
    x, y = P(cx, cy, R * 0.6 + 30, a / 2); s.text(x + 30, y, 'سمت القبلة ١٨°', 15, GREEN, bold=True)
    s.arc(cx, cy, R * 0.38, a, 90, BLUE, 2)
    x, y = P(cx, cy, R * 0.38 + 32, 60); s.text(x, y, 'انحراف ٧٢°', 14, BLUE)
    s.dot(cx, cy, 5); s.text(cx - 10, cy - 18, 'تونس', 16, INK, 'r', bold=True)
    s.text(cx, cy + R + 55, 'سمت القبلة بتونس عند الشارح: ١٨ درجة من نقطة المشرق إلى الجنوب', 16, INK)
    s.save('B14_qibla_horizon')

def fig_directions():
    s = SVG(760, 560)
    cx, cy = 380, 260
    # quadrant lying flat (plan view)
    R = 210
    az = 28
    # east-west line through
    quadrant(s, cx - R / 2, cy - R / 2, R, fine=False, abjad=False, small=True)
    ccx, ccy = cx - R / 2, cy - R / 2
    thread(s, ccx, ccy, R, az, None, None, plumb=False)
    # plumb shadow overlaps thread
    s.line(ccx - 30 * math.cos(math.radians(az)), ccy - 30 * math.sin(math.radians(az)), *P(ccx, ccy, R * 1.25, az), '#555555', 5, op=0.35)
    s.text(*P(ccx, ccy, R * 1.25 + 30, az), 'ظل خيط الشاقول منطبق على الخيط', 14, INK)
    s.arc(ccx, ccy, R * 0.45, 0, az, GREEN, 2.4)
    x, y = P(ccx, ccy, R * 0.45 + 34, az / 2); s.text(x + 10, y, 'سمت الوقت', 14, GREEN, bold=True)
    s.line(ccx - 120, ccy, ccx + R + 140, ccy, RED, 1.6, dash='8,4')
    s.text(ccx + R + 140, ccy - 16, 'خط المشرق والمغرب', 15, RED, 'r')
    s.line(ccx, ccy - 120, ccx, ccy + R + 120, BLUE, 1.6, dash='8,4')
    s.text(ccx + 8, ccy + R + 130, 'خط نصف النهار', 15, BLUE, 'l')
    s.text(cx, 540, 'يوضع الربع على أرض مستوية والخيط على سمت الوقت، ويُدار حتى ينطبق ظل الشاقول على الخيط', 16)
    s.save('B15_directions')

def fig_height():
    s = SVG(860, 470)
    gy = 380
    s.line(40, gy, 820, gy, INK, 2)
    # tower
    tx = 700
    s.path(f'M{tx},{gy} L{tx},{gy-280} L{tx+50},{gy-280} L{tx+50},{gy} Z', INK, 2, fill='#efe3d3')
    ox = 220
    eye = 50
    # person
    s.line(ox, gy, ox, gy - eye, INK, 3)
    s.circle(ox, gy - eye - 8, 8, INK, 2)
    s.line(ox, gy - eye, tx, gy - 280, RED, 1.6, dash='7,4')
    s.line(ox, gy - eye, tx, gy - eye, BLUE, 1.2, dash='4,3')
    ang = math.degrees(math.atan2(280 - eye, tx - ox))
    s.arc(ox, gy - eye, 90, -ang, 0, GREEN, 2.4)
    s.text(ox + 120, gy - eye - 26, 'الارتفاع', 15, GREEN, 'l', bold=True)
    s.text((ox + tx) / 2, gy + 22, 'ما بين القدمين وأصل القائم (المحفوظ)', 15, INK)
    s.text(tx + 60, gy - 160, 'طول القائم', 15, INK, 'l')
    s.text(ox - 10, gy - eye / 2, 'ما بين البصر والأرض', 13, INK, 'r')
    s.text(430, 450, 'الطول = المسافة × ظل الارتفاع ⁄ القامة + ما بين البصر والأرض', 16)
    s.save('B19_height')

def fig_river_well():
    s = SVG(900, 470)
    # river (right side)
    gy = 250
    s.path('M470,250 L560,250 L590,320 L790,320 L820,250 L880,250', INK, 2)
    s.path('M560,262 L590,320 L790,320 L812,262 Z', BLUE, 0, fill='#cfe0ef')
    ox = 560
    s.line(ox, gy, ox, gy - 60, INK, 3); s.circle(ox, gy - 68, 8, INK, 2)
    s.line(ox, gy - 60, 812, 262, RED, 1.6, dash='6,4')
    s.arc(ox, gy - 60, 70, 0, math.degrees(math.atan2(72, 252)), GREEN, 2)
    s.text(ox + 90, gy - 60, 'الانحطاط', 14, GREEN, 'l')
    s.text(690, 345, 'سعة النهر', 15, BLUE, bold=True)
    s.text(680, 410, 'السعة = ما بين البصر والماء × ظتا الانحطاط', 15)
    # well (left)
    wx, wy = 120, 120
    s.path(f'M{wx-60},{wy} L{wx},{wy} L{wx},{wy+300} M{wx+140},{wy+300} L{wx+140},{wy} L{wx+200},{wy}', INK, 2.4)
    s.path(f'M{wx},{wy+230} L{wx+140},{wy+230} L{wx+140},{wy+300} L{wx},{wy+300} Z', BLUE, 0, fill='#cfe0ef')
    s.line(wx, wy, wx, wy - 50, INK, 3); s.circle(wx, wy - 58, 8, INK, 2)
    s.line(wx, wy - 50, wx + 140, wy + 230, RED, 1.6, dash='6,4')
    s.line(wx, wy - 4, wx + 140, wy - 4, BLUE, 2.2)
    s.text(wx + 70, wy - 20, 'قطر فم البئر', 14, BLUE)
    s.text(wx + 160, wy + 120, 'العمق', 15, INK, 'l', bold=True)
    s.text(wx + 70, wy + 330, 'العمق = القطر × ظل الانخفاض − ما بين البصر والأرض', 15)
    s.save('B20_river_well')

# ---------------------------------------------------------------- redrawn manuscript figures
def m01_spheres():
    s = SVG(820, 760)
    cx, cy = 410, 380
    names = ['كرة الأرض', 'كرة الماء', 'كرة الهواء', 'كرة النار', 'فلك القمر', 'فلك عطارد', 'فلك الزهرة',
             'فلك الشمس', 'فلك المريخ', 'فلك المشتري', 'فلك زحل', 'فلك الثوابت (الكرسي)', 'فلك الأفلاك (العرش)']
    for i, n in enumerate(names):
        r = 40 + i * 23
        c = BLUE if i < 4 else (GOLD if i in (4, 7) else (RED if i >= 11 else INK))
        s.circle(cx, cy, r, c, 1.5 if i < 11 else 2.2)
        s.text(cx, cy - r + 11, n, 12.5, c)
    s.dot(cx, cy, 4)
    s.text(cx, cy + 14, 'مركز العالم', 12)
    # axis of world & ecliptic poles
    s.line(cx - 150, cy + 300, cx + 150, cy - 300, RED, 1.4)
    s.text(cx + 170, cy - 320, 'قطب العالم', 15, RED)
    s.text(cx - 170, cy + 320, 'قطب العالم', 15, RED)
    a = math.radians(-63.4 + 23.5)
    s.line(cx - 340 * math.cos(a), cy - 340 * math.sin(a), cx + 340 * math.cos(a), cy + 340 * math.sin(a), GREEN, 1.2, dash='6,4')
    s.text(cx + 330 * math.cos(a) + 40, cy + 330 * math.sin(a) - 20, 'قطب البروج', 15, GREEN)
    s.save('M01_spheres')

def m02_angles():
    s = SVG(900, 260)
    y = 210
    s.line(30, y, 870, y, RED, 1.8)
    xs = [110, 260, 420, 590, 760]
    # 1 straight-line angle
    s.line(xs[0] - 40, y, xs[0] - 40, y - 150, RED, 1.8); s.path(f'M{xs[0]-40},{y-150} Q{xs[0]+40},{y-60} {xs[0]+50},{y}', RED, 1.8)
    s.text(xs[0], y + 26, 'مستقيم ومنحنٍ', 14)
    s.path(f'M{xs[1]-60},{y} Q{xs[1]-60},{y-150} {xs[1]},{y-150} Q{xs[1]+40},{y-60} {xs[1]+30},{y}', RED, 1.8)
    s.text(xs[1], y + 26, 'محدّب ومقعّر', 14)
    s.path(f'M{xs[2]-80},{y} Q{xs[2]-10},{y-40} {xs[2]},{y-150} Q{xs[2]+10},{y-40} {xs[2]+80},{y}', RED, 1.8)
    s.text(xs[2], y + 26, 'مقعّران', 14)
    s.path(f'M{xs[3]-50},{y-100} Q{xs[3]},{y-200} {xs[3]+50},{y-100} Q{xs[3]},{y} {xs[3]-50},{y-100}', RED, 1.8)
    s.text(xs[3], y + 26, 'محدّبان', 14)
    s.path(f'M{xs[4]-70},{y} A90,90 0 0 1 {xs[4]+70},{y-120} A70,70 0 0 0 {xs[4]-10},{y}', RED, 1.8)
    s.text(xs[4], y + 26, 'هلالية', 14)
    s.text(450, 30, 'زوايا مسطحة يحيط بها خطّان غير مستقيمين', 17, INK, bold=True)
    s.save('M02_angles')

def m03_circle():
    s = SVG(420, 380)
    cx, cy, R = 210, 190, 140
    s.circle(cx, cy, R, RED, 2)
    s.line(cx - R, cy, cx + R, cy, RED, 2)
    s.dot(cx, cy, 4)
    s.text(cx, cy - 18, 'قُطر', 22, INK, bold=True)
    yy = cy + 70; dx = math.sqrt(R * R - 70 * 70)
    s.line(cx - dx, yy, cx + dx, yy, RED, 2)
    s.text(cx, yy - 18, 'وتر', 22, INK, bold=True)
    s.line(cx, cy, cx, yy, BLUE, 1.2, dash='4,3')
    s.line(cx, yy, cx + dx, yy, BLUE, 3)
    s.text(cx + dx / 2, yy + 22, 'الجيب = نصف الوتر', 15, BLUE)
    s.save('M03_circle')

def m04_parallels():
    s = SVG(600, 200)
    for i, y in enumerate((50, 100, 150)):
        s.line(60, y, 540, y, RED, 2)
    s.text(300, 30, 'خطوط متوازية', 18, INK, bold=True)
    s.text(300, 180, 'لا تتلاقى وإن أُخرجت في الجهتين إلى غير النهاية', 15)
    s.save('M04_parallels')

def m05_horizons():
    s = SVG(760, 720)
    cx, cy, R = 380, 380, 290
    r = 90
    s.circle(cx, cy, R, RED, 2)
    s.circle(cx, cy, r, RED, 2)
    s.line(cx, cy - R, cx, cy + R, RED, 1.6)
    s.line(cx - R, cy, cx + R, cy, RED, 1.6)
    s.text(cx - R + 90, cy - 14, 'الأفق الحقيقي', 15, BLUE, bold=True)
    s.line(cx - R + 10, cy - r, cx + R - 10, cy - r, RED, 1.6)
    s.text(cx - R + 90, cy - r - 14, 'الأفق الحسي', 15, BLUE, bold=True)
    s.dot(cx, cy - r, 4)
    s.text(cx + 12, cy - r + 20, 'موضع الناظر', 14, INK, 'l')
    s.text(cx, cy - R - 18, 'سمت الرأس', 16)
    s.text(cx, cy + R + 22, 'سمت القدم (الرِّجل)', 16)
    s.text(cx + 10, cy + 20, 'مركز العالم', 14, INK, 'l')
    s.text(cx - 30, cy + r - 20, 'كرة الأرض', 14, INK)
    s.text(cx + R + 10, cy - r, 'يفصل بين', 13, INK, 'l')
    s.text(cx + R + 10, cy - r + 18, 'المرئي وغيره', 13, INK, 'l')
    s.save('M05_horizons')

def m06_altitude():
    s = SVG(860, 500)
    cx, cy, R = 430, 440, 380
    r2 = 330
    s.arc(cx, cy, R, 180, 360, RED, 2)
    s.arc(cx, cy, r2, 180, 360, RED, 1.4)
    s.line(cx - R, cy, cx + R, cy, RED, 2)
    s.text(cx - R + 20, cy + 22, 'الأفق', 15)
    s.text(cx + R - 20, cy + 22, 'الأفق', 15)
    s.line(cx, cy, cx, cy - R, RED, 1.6)
    s.dot(cx, cy - r2, 4.5)
    s.text(cx + 14, cy - r2 + 20, 'كوكب على سمت الرأس', 13, INK, 'l')
    s.text(cx + 8, cy - 150, 'العمود منطبق على الجيب', 13, INK, 'l', rot=-90)
    for side in (-1, 1):
        ang = 50
        st = (cx + side * r2 * math.cos(math.radians(ang)), cy - r2 * math.sin(math.radians(ang)))
        top = (cx + side * R * math.cos(math.radians(ang)), cy - R * math.sin(math.radians(ang)))
        s.line(cx, cy, *top, RED, 1.6)
        s.dot(*st, 5)
        s.text(st[0] + side * 30, st[1] - 12, 'كوكب', 14)
        s.line(st[0], st[1], st[0], cy, BLUE, 1.6)
        s.line(top[0], top[1], top[0], cy, GREEN, 1.4, dash='5,3')
        s.text(st[0] - side * 14, cy - 60, 'العمود', 13, BLUE, rot=-90)
        s.text(top[0] + side * 14, cy - 60, 'جيب الارتفاع', 13, GREEN, rot=-90)
        s.arc(cx, cy, R + 14, 180 if side < 0 else 360 - ang, 180 + ang if side < 0 else 360, GOLD, 2.4)
        x, y = P(cx, cy, R + 40, 180 + ang / 2 if side < 0 else 360 - ang / 2)
        s.text(x, y, 'قوس الارتفاع', 14, GOLD)
        s.text(*P(cx, cy, R + 24, 180 + ang + 20 if side < 0 else 360 - ang - 20), 'تمام الارتفاع', 13, INK)
    s.text(cx, cy + 40, 'مركز العالم', 14)
    s.save('M06_altitude_perp')

def m07_azimuths():
    s = SVG(760, 760)
    cx, cy, R = 380, 380, 300
    s.circle(cx, cy, R, RED, 2)
    s.line(cx, cy - R, cx, cy + R, RED, 1.8)
    s.line(cx - R, cy, cx + R, cy, RED, 1.8)
    s.text(cx, cy - R - 18, 'نقطة الشمال', 16, INK, bold=True)
    s.text(cx, cy + R + 22, 'نقطة الجنوب', 16, INK, bold=True)
    s.text(cx + R + 12, cy, 'نقطة المشرق', 16, INK, 'l', bold=True)
    s.text(cx - R - 12, cy, 'نقطة المغرب', 16, INK, 'r', bold=True)
    s.text(cx + 100, cy - 14, 'دائرة أول السموت', 14, INK)
    s.text(cx + 14, cy + 120, 'دائرة نصف النهار', 14, INK, 'l', rot=90)
    quads = [(-30, 'سمت شرقي شمالي'), (30, 'سمت شرقي جنوبي'), (150, 'سمت غربي جنوبي'), (210, 'سمت غربي شمالي')]
    for a, lab in quads:
        p = P(cx, cy, R, a)
        s.line(cx, cy, *p, RED, 1.4)
        s.dot(*P(cx, cy, R * 0.62, a), 4.5)
        base = 0 if a in (-30, 30) else 180
        s.arc(cx, cy, R + 12, min(base, a), max(base, a), GREEN, 3)
        x, y = P(cx, cy, R * 0.8, a / 2 if base == 0 else (a + 180) / 2)
        s.text(x, y, lab, 14, GREEN, bold=True)
        s.text(*P(cx, cy, R * 0.45, a + (8 if a > 0 else -8)), 'دائرة ارتفاع', 12, INK)
    s.text(cx, cy + R + 52, 'السمت: قوس من الأفق بين نقطة المشرق أو المغرب ودائرة الارتفاع، وتمامه إلى نقطة الشمال أو الجنوب', 15)
    s.save('M07_azimuths')

def m08_two_belts():
    s = SVG(640, 560)
    cx, cy, R = 320, 280, 200
    s.circle(cx, cy, R, RED, 2)
    s.text(cx - R - 12, cy, 'نقطة المشرق', 14, INK, 'r')
    eps = 23.5
    # ellipse projections: equator horizontal ellipse, ecliptic tilted
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="55" stroke="{BLUE}" stroke-width="1.8" fill="none"/>')
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="55" stroke="{RED}" stroke-width="1.8" fill="none" transform="rotate({-eps} {cx} {cy})"/>')
    s.text(cx + 40, cy + 72, 'معدل النهار', 15, BLUE, bold=True)
    s.text(cx + 30, cy - 120, 'منطقة البروج', 15, RED, bold=True)
    s.dot(cx - R, cy, 4); s.text(cx - R + 70, cy - 12, 'رأس الحمل', 14, INK)
    s.dot(cx + R, cy, 4); s.text(cx + R - 70, cy + 14, 'رأس الميزان', 14, INK)
    pa = (cx + 55 * math.sin(math.radians(eps)) * 0, cy - 55)
    s.text(cx, cy - 175, 'غاية الميل: رأس السرطان (٢٣;٣٥ عند الشارح)', 14, GOLD)
    s.text(cx, cy + 175, 'غاية الميل: رأس الجدي', 14, GOLD)
    s.text(cx, cy + R + 30, 'البروج الشمالية من أول الحمل إلى آخر السنبلة، والجنوبية من أول الميزان إلى آخر الحوت', 14)
    s.save('M08_two_belts')

def m09_six_signs():
    s = SVG(760, 700)
    cx, cy, R = 380, 350, 290
    s.circle(cx, cy, R, RED, 2)
    s.line(cx - R, cy, cx + R, cy, RED, 1.6)
    s.text(cx - R - 10, cy, 'قطب البروج', 15, INK, 'r')
    s.text(cx + R + 10, cy, 'قطب البروج', 15, INK, 'l')
    s.text(cx, cy - 16, 'الدائرة المارة بقطبي الاعتدالين', 14, INK)
    # six semicircles through both poles: ellipses with varying ry
    names_top = ['الحوت', 'الدلو', 'الجدي']
    names_bot = ['الحمل', 'الثور', 'الجوزاء']
    for k, ry in enumerate((R * 0.33, R * 0.66, R)):
        s.arc(cx, cy, R, 180, 360, RED, 1.8) if k == 2 else s.add(
            f'<path d="M{cx-R},{cy} A{R},{ry:.1f} 0 0 1 {cx+R},{cy}" stroke="{RED}" stroke-width="1.6" fill="none"/>')
        s.add(f'<path d="M{cx-R},{cy} A{R},{ry:.1f} 0 0 0 {cx+R},{cy}" stroke="{RED}" stroke-width="1.6" fill="none"/>')
    for k, (nt, nb) in enumerate(zip(names_top, names_bot)):
        ry = R * (0.165 + 0.33 * k)
        s.text(cx - 80, cy - ry, nt, 17, INK, bold=True)
        s.text(cx - 80, cy + ry, nb, 17, INK, bold=True)
    # ecliptic as a vertical-ish great circle
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="70" ry="{R}" stroke="{GOLD}" stroke-width="2" fill="none"/>')
    s.text(cx + 100, cy - R * 0.55, 'منطقة البروج', 15, GOLD, bold=True)
    s.text(cx, cy - R - 18, 'الميل الكلي وهو غاية الميل', 14)
    s.text(cx, cy + R + 22, 'الميل الكلي وهو غاية الميل', 14)
    s.save('M09_six_signs')

def m10_climes():
    s = SVG(640, 640)
    cx, cy, R = 320, 320, 260
    s.circle(cx, cy, R, RED, 2)
    s.line(cx, cy - R, cx, cy + R, RED, 1.6)
    s.text(cx - 14, cy - 120, 'دائرة نصف النهار', 14, INK, 'r', rot=-90)
    names = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع']
    ys = [cy + 0.0 * R]
    lat = [12.75, 20.5, 27.5, 33.6, 39, 43.5, 47.25, 50.5]
    prev = None
    for i, la in enumerate(lat):
        y = cy - R * math.sin(math.radians(la)) * 0 + R * (la / 66.0) * 0
    # draw equator & band lines proportional to sin(latitude)
    s.line(cx - R, cy, cx + R, cy, RED, 2)
    s.text(cx + R - 70, cy - 12, 'خط الاستواء', 14, INK)
    bands = [12.75] + lat[1:]
    for i in range(7):
        y1 = cy - R * math.sin(math.radians(lat[i]))
        y2 = cy - R * math.sin(math.radians(lat[i + 1]))
        for y in (y1, y2):
            dx = math.sqrt(R * R - (y - cy) ** 2)
            s.line(cx - dx, y, cx + dx, y, RED, 1.2)
        s.text(cx + 70, (y1 + y2) / 2, 'الإقليم ' + names[i], 13.5, INK)
    s.text(cx, cy - R - 16, 'الشمال', 15)
    s.text(cx, cy + R + 20, 'الجنوب', 15)
    s.text(cx + R + 10, cy, 'المشرق', 14, INK, 'l')
    s.text(cx - R - 10, cy, 'المغرب', 14, INK, 'r')
    s.text(cx - 110, cy + 100, 'الربع المعمور في النصف الشمالي', 14, GOLD)
    s.save('M10_climes')

def m11_ascensional():
    s = SVG(860, 640)
    cx, cy, R = 430, 330, 250
    s.circle(cx, cy, R, RED, 2)
    s.line(cx, cy - R - 60, cx, cy, INK, 1.6)
    s.dot(cx, cy - R - 60, 4); s.text(cx, cy - R - 76, 'القطب الخفي', 15)
    s.dot(cx, cy + 0, 4)
    s.text(cx + 10, cy + 14, 'القطب الظاهر', 14, INK, 'l')
    s.text(cx + 120, cy - R + 20, 'دائرة الأفق', 15, INK)
    # three ellipses = day circles & equator crossing horizon
    for dy, lab, c in ((-80, 'مدار جانب القطب الخفي', INK), (0, 'معدل النهار', BLUE), (80, 'مدار جانب القطب الظاهر', INK)):
        s.add(f'<path d="M{cx-R-90},{cy+dy} Q{cx},{cy+dy-70} {cx+R+90},{cy+dy}" stroke="{c}" stroke-width="1.6" fill="none"/>')
        s.add(f'<path d="M{cx-R-90},{cy+dy} Q{cx},{cy+dy+70} {cx+R+90},{cy+dy}" stroke="{c}" stroke-width="1.0" fill="none" stroke-dasharray="4,3"/>')
        s.text(cx, cy + dy - 46, lab, 14, c, bold=(c == BLUE))
    # triangle near east point
    E = (cx - R, cy)
    s.path(f'M{cx-R+2},{cy-2} L{cx-R+40},{cy+78} L{cx-R+6},{cy+86} Z', GOLD, 2.4, fill='#f6e7b5', op=0.9)
    s.text(cx - R - 20, cy + 40, 'الميل', 14, GOLD, 'r', bold=True)
    s.text(cx - R - 20, cy + 100, 'سعة المشرق', 14, GOLD, 'r', bold=True)
    s.text(cx - R + 70, cy + 116, 'نصف التعديل', 14, GOLD, 'l', bold=True)
    s.text(cx, cy + R + 40, 'المثلث القائم: ضلعه الأول من دائرة الميل، والثاني من الأفق (سعة المشرق)، والثالث من المدار (نصف تعديل النهار)', 14)
    s.save('M11_ascensional')

def m12_shadow_cone():
    s = SVG(620, 860)
    cx = 310
    ey = 320  # earth centre
    er = 70
    sunY, sunR = 760, 95
    s.circle(cx, sunY, sunR, RED, 0, fill='#c8442f')
    s.circle(cx, sunY, sunR * 0.55, RED, 0, fill='#ffffff')
    s.text(cx, sunY, 'جرم الشمس', 15, INK, bold=True)
    apex = (cx, 40)
    # tangent lines approx from sun edges to apex
    s.line(cx - sunR, sunY, *apex, RED, 2)
    s.line(cx + sunR, sunY, *apex, RED, 2)
    s.circle(cx, ey, 240, RED, 1.4)
    s.text(cx, ey - 240 - 14, 'فلك القمر (تقريبًا)', 13, INK)
    s.circle(cx, ey, er, RED, 2, fill='#ffffff')
    s.line(cx - er, ey, cx + er, ey, RED, 1.4)
    s.line(cx - 110, ey - 20, cx + 110, ey - 20, RED, 1.6)
    s.text(cx - 160, ey - 20, 'سطح الأفق المرئي', 13, INK)
    s.text(cx, ey + 20, 'كرة الأرض', 13, INK)
    s.text(cx, ey + er + 18, 'مركز العالم', 12, INK)
    s.text(cx + 18, 180, 'مخروط ظل الأرض (الليل)', 14, INK, 'l', rot=-82)
    s.text(cx + 220, 440, 'الصبح الكاذب', 14, BLUE, 'l')
    s.text(cx + 220, 460, '(ذنب السرحان)', 13, BLUE, 'l')
    s.line(cx + 215, 450, cx + 60, 450, BLUE, 1, dash='4,3')
    s.text(cx, 840, 'الشمس تحت الأفق تُضيء ما خرج عن مخروط الظل، فيُرى الضوء المستطيل قبل انتشار الصبح الصادق', 14)
    s.save('M12_shadow_cone')

def m13_lat66():
    s = SVG(760, 560)
    cx, cy = 380, 280
    for r, lab in ((240, 'دائرة الأفق'), (160, 'مدار قطب البروج'), (70, '')):
        s.circle(cx, cy, r, RED, 1.8)
    s.line(cx, cy - 240, cx, cy + 240, RED, 1.6)
    s.dot(cx, cy - 240, 4.5); s.text(cx, cy - 256, 'الجنوب', 15)
    s.dot(cx, cy + 240, 6); s.text(cx, cy + 258, 'الشمال', 15)
    s.dot(cx, cy, 4.5); s.text(cx + 16, cy + 4, 'سمت الرأس = قطب البروج', 14, INK, 'l')
    s.dot(cx, cy + 70, 4.5); s.text(cx + 16, cy + 74, 'قطب العالم (ارتفاعه ٦٦;٣٠)', 14, INK, 'l')
    s.dot(cx - 240, cy, 4.5); s.text(cx - 248, cy, 'المغرب: الميزان', 14, INK, 'r')
    s.dot(cx + 240, cy, 4.5); s.text(cx + 248, cy, 'المشرق: الحمل', 14, INK, 'l')
    s.text(cx - 20, cy - 200, 'الجدي على نقطة الجنوب', 13, INK, 'r')
    s.text(cx - 20, cy + 205, 'السرطان على نقطة الشمال', 13, INK, 'r')
    s.text(cx, cy + 290, 'حين يبلغ قطب البروج سمت الرأس تنطبق منطقة البروج على الأفق', 15, BLUE)
    s.save('M13_lat66')

def m14_zodiac_horizon():
    s = SVG(700, 700)
    cx, cy, R = 350, 350, 300
    s.circle(cx, cy, R, RED, 2)
    names = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']
    for i, n in enumerate(names):
        a = 180 - i * 30  # start at east? place حمل at east (right) going counterclockwise
        a = -i * 30
        mid = a - 15
        x1, y1 = P(cx, cy, R * 0.9, mid - 12)
        x2, y2 = P(cx, cy, R * 0.9, mid + 12)
        s.path(f'M{cx},{cy} L{x1:.1f},{y1:.1f} A{R*0.9:.1f},{R*0.9:.1f} 0 0 1 {x2:.1f},{y2:.1f} Z', RED, 1.4, fill='#fbf3ea')
        x, y = P(cx, cy, R * 0.66, mid)
        s.text(x, y, n, 17, INK, bold=True)
    s.dot(cx, cy, 4)
    s.text(cx + R + 8, cy, 'مشرق', 14, INK, 'l')
    s.text(cx, cy + R + 22, 'منطقة البروج منطبقة على الأفق', 15, BLUE)
    s.save('M14_zodiac_horizon')

def m15_lat_gt():
    s = SVG(760, 640)
    cx, cy = 380, 300
    for r in (250, 150, 55):
        s.circle(cx, cy, r, RED, 1.8)
    s.line(cx, cy - 250, cx, cy + 250, RED, 1.6)
    s.dot(cx, cy - 250, 4.5); s.text(cx, cy - 266, 'الجنوب', 15)
    s.dot(cx, cy + 250, 6); s.text(cx, cy + 268, 'الشمال', 15)
    s.dot(cx, cy, 4); s.text(cx + 10, cy - 10, 'سمت الرأس', 14, INK, 'l')
    s.dot(cx, cy + 90, 4.5); s.text(cx + 10, cy + 90, 'قطب العالم', 14, INK, 'l')
    s.dot(cx, cy + 40, 4.5); s.text(cx - 12, cy + 40, 'قطب البروج في غاية ارتفاعه', 13, INK, 'r')
    s.text(cx - 160, cy - 60, 'أجزاء أبدية الظهور', 14, BLUE)
    s.text(cx + 160, cy + 150, 'أجزاء أبدية الخفاء', 14, BLUE)
    s.text(cx, cy + 300, 'إذا زاد العرض على تمام الميل الكلي مال قطب البروج عن سمت الرأس بقدر الزيادة', 15)
    s.save('M15_lat_gt')

def m16_no_azimuth():
    s = SVG(760, 700)
    cx, cy, R = 380, 350, 290
    s.circle(cx, cy, R, RED, 2)
    s.line(cx, cy - R, cx, cy + R, RED, 1.8)
    s.line(cx - R, cy, cx + R, cy, RED, 1.8)
    s.text(cx, cy - R - 16, 'نقطة الجنوب', 15)
    s.text(cx, cy + R + 20, 'نقطة الشمال', 15)
    s.text(cx - R - 10, cy, 'نقطة المشرق', 14, INK, 'r')
    s.text(cx + R + 10, cy, 'نقطة المغرب', 14, INK, 'l')
    s.text(cx + 120, cy - 14, 'دائرة أول السموت', 13, INK)
    s.dot(cx, cy, 4.5); s.text(cx + 12, cy + 20, 'سمت الرأس', 13, INK, 'l')
    for dy, lab, w in ((-110, 'المدار الجنوبي', 1.6), (60, 'المدار الشمالي (يقطع أول السموت)', 2.2), (150, 'مدار لا يقطعها', 1.4)):
        s.add(f'<path d="M{cx-R+(0 if dy<0 else 20)},{cy+dy+40} Q{cx},{cy+dy-60} {cx+R-(0 if dy<0 else 20)},{cy+dy+40}" stroke="{RED}" stroke-width="{w}" fill="none"/>')
        s.text(cx + 150, cy + dy + 6, lab, 13, INK)
    # crossing points
    s.dot(cx - 175, cy, 5, GOLD); s.dot(cx + 175, cy, 5, GOLD)
    s.text(cx - 175, cy - 22, 'كوكب على أول السموت', 13, GOLD)
    s.text(cx, cy + R + 50, 'الارتفاع الذي لا سمت له: ارتفاع الشمس حين تقع على دائرة أول السموت (لا يكون إلا والميل شمالي أقل من العرض)', 14)
    s.save('M16_no_azimuth')

def m17_kuniya():
    s = SVG(300, 360)
    s.path('M150,40 L60,320 M150,40 L240,320 M82,250 L218,250', RED, 3)
    s.line(150, 40, 150, 300, INK, 1.2)
    s.path('M140,300 L160,300 L150,318 Z', INK, 1, fill=INK)
    s.text(150, 20, 'الكونيا', 18, INK, bold=True)
    s.text(150, 345, 'مثلث البنّائين يُعلَّق فيه الشاقول لتسوية الأرض', 13)
    s.save('M17_kuniya')

def m18_indian_circle():
    s = SVG(760, 720)
    cx, cy, R = 380, 350, 270
    s.circle(cx, cy, R, RED, 2)
    s.line(cx - R, cy, cx + R, cy, RED, 1.6)
    s.line(cx, cy - R, cx, cy + R, RED, 1.6)
    s.dot(cx, cy, 4.5)
    s.text(cx - R - 10, cy, 'مشرق', 15, INK, 'r')
    s.text(cx + R + 10, cy, 'مغرب', 15, INK, 'l')
    s.text(cx, cy + R + 22, 'شمال', 15)
    s.text(cx, cy - R - 16, 'جنوب', 15)
    s.text(cx + 100, cy - 14, 'خط المشرق والمغرب', 14, INK)
    s.text(cx + 14, cy - 140, 'خط نصف النهار', 14, INK, 'l', rot=-90)
    # shadow curve (hyperbola-like) and entry/exit points
    pin = P(cx, cy, R, 215); pout = P(cx, cy, R, 325)
    s.line(cx, cy, *pin, INK, 2); s.line(cx, cy, *pout, INK, 2)
    s.dot(*pin, 5, RED); s.dot(*pout, 5, RED)
    s.text(pin[0] - 10, pin[1] - 20, 'نقطة الدخول', 14, RED, 'r')
    s.text(pout[0] + 10, pout[1] - 20, 'نقطة الخروج', 14, RED, 'l')
    s.line(pin[0], pin[1], pout[0], pout[1], BLUE, 1.4, dash='5,3')
    s.add(f'<path d="M{cx-R*0.95},{cy-R*0.65} Q{cx},{cy-R*0.08} {cx+R*0.95},{cy-R*0.65}" stroke="{GOLD}" stroke-width="1.4" fill="none" stroke-dasharray="3,4"/>')
    s.text(cx, cy - R * 0.28, 'مسير طرف الظل', 13, GOLD)
    s.path(f'M{cx-12},{cy+6} L{cx},{cy-20} L{cx+12},{cy+6}', INK, 2)
    s.text(cx + 30, cy + 34, 'المقياس في المركز', 13, INK, 'l')
    s.text(cx, cy + R + 55, 'يُنصَّف ما بين نقطتي الدخول والخروج فيخرج خط نصف النهار، ويُقام عليه عمود فهو خط المشرق والمغرب', 14)
    s.save('M18_indian_circle')

def m19_qibla_indian():
    s = SVG(760, 720)
    cx, cy, R = 380, 340, 270
    s.circle(cx, cy, R, RED, 2)
    s.line(cx - R, cy, cx + R, cy, RED, 1.6)
    s.line(cx, cy - R, cx, cy + R, RED, 1.6)
    s.text(cx, cy - R - 16, 'جنوب', 15)
    s.text(cx, cy + R + 22, 'شمال', 15)
    s.text(cx - R - 10, cy, 'مشرق', 15, INK, 'r')
    s.text(cx + R + 10, cy, 'مغرب', 15, INK, 'l')
    dlon, dlat = 35.25, 15
    # line parallel to meridian: from point on circle at dlon from south toward east, and from north by same toward east
    a1 = P(cx, cy, R, -90 - dlon)  # south toward east(left)
    a2 = P(cx, cy, R, 90 + dlon)
    s.line(*a1, *a2, RED, 1.6)
    s.text(a1[0] - 6, a1[1] - 14, 'له ر', 16, RED, bold=True)
    s.text(a2[0] - 6, a2[1] + 18, 'له ر', 16, RED, bold=True)
    b1 = P(cx, cy, R, 180 + dlat)  # from east toward south
    b2 = P(cx, cy, R, -dlat)
    s.line(*b1, *b2, RED, 1.6)
    s.text(b1[0] - 14, b1[1], 'يه', 16, RED, 'r', bold=True)
    s.text(b2[0] + 14, b2[1], 'يه', 16, RED, 'l', bold=True)
    # intersection
    def inter(p1, p2, p3, p4):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    X = inter(a1, a2, b1, b2)
    ang = math.degrees(math.atan2(X[1] - cy, X[0] - cx))
    Q = P(cx, cy, R, ang)
    s.line(cx, cy, *Q, GREEN, 3)
    s.dot(*X, 5, GREEN)
    s.text(Q[0] - 12, Q[1] - 16, 'سمت القبلة بتونس', 15, GREEN, 'r', bold=True)
    az = 180 - ang if ang > 0 else -(180 + ang)
    s.arc(cx, cy, R * 0.35, 180, 180 + (ang + 180 if ang < 0 else ang - 180), GOLD, 2) if False else None
    s.text(cx, cy + R + 55, 'له ر = فضل ما بين الطولين ٣٥ درجة وربع ، يه = فضل ما بين العرضين ١٥ درجة', 15)
    s.text(cx, cy + R + 82, 'يخرج القوس بين خط القبلة ونقطة المشرق نحو ٢٤ درجة في هذه الطريقة المسطحة التقريبية', 14, INK)
    s.save('M19_qibla_indian')
    return abs(180 - abs(ang))

def timeline():
    s = SVG(1200, 700)
    y = 350
    s.line(40, y, 1160, y, INK, 3)
    ev = [
        (850, 'ق٣هـ/٩م', ['بغداد: أقدم وصف لربع الجيب', '(رسالة تُنسب إلى الخوارزمي)'], -1, 1),
        (1000, 'ق٤-٥هـ/١٠-١١م', ['ابن يونس بمصر:', 'الزيج الحاكمي وجداول الميقات'], 1, 1),
        (1270, 'ق٧هـ/١٣م', ['الطوسي: التذكرة', 'الجغميني: الملخص'], -1, 1),
        (1360, 'ق٨هـ/١٤م', ['ابن الشاطر بدمشق:', 'الزيج الجديد والربع التام'], 1, 2),
        (1406, '٨٠٩هـ/١٤٠٦م', ['جمال الدين المارديني بالقاهرة:', 'رسائل الربع المجيب'], -1, 2),
        (1430, 'ق٩هـ/١٥م', ['قاضي زاده الرومي:', 'شرح الملخص وأشكال التأسيس'], 1, 1),
        (1506, '٩١٢هـ/١٥٠٦م', ['سبط المارديني:', 'حاوي المختصرات والرسائل الجيبية'], -1, 1),
        (1679, '١٠٩٠هـ/١٦٧٩م', ['علي بن مامي كرباصة بتونس:', 'إتحاف المحبوب'], 1, 1),
        (1720, '١١٣٢هـ/١٧٢٠م', ['نسخة (ز) منقولة', 'عن خط المؤلف'], -1, 2),
        (1842, '١٢٥٨هـ/١٨٤٢م', ['نسخة عبد الفتاح صوان،', 'ووقفها برواق المغاربة بالأزهر'], 1, 2),
    ]
    x0, x1, t0, t1 = 90, 1110, 820, 1880
    for yr in range(900, 1900, 100):
        x = x0 + (yr - t0) / (t1 - t0) * (x1 - x0)
        s.line(x, y - 6, x, y + 6, INK, 1)
        s.text(x, y + 18, ar_num(yr) + 'م', 11, '#888888')
    for tt, d, lab, side, lvl in ev:
        x = x0 + (tt - t0) / (t1 - t0) * (x1 - x0)
        c = RED if tt in (1406, 1679) else INK
        s.dot(x, y, 6, c)
        yy = y + side * (60 + 120 * (lvl - 1))
        s.line(x, y, x, yy, c, 1)
        base = yy + side * 16
        s.text(x, base, d, 15, c, bold=True)
        for i, l in enumerate(lab):
            s.text(x, base + side * (24 + 20 * i) if side > 0 else base - 24 - 20 * (len(lab) - 1 - i), l, 13.5, c)
    s.save('T00_timeline')

def build():
    fig_quadrant_full(); fig_proportion(); fig_altitude(); fig_ch3_shadow(); fig_meridian(); fig_dair()
    fig_qibla_sphere(); fig_directions(); fig_height(); fig_river_well()
    m01_spheres(); m02_angles(); m03_circle(); m04_parallels(); m05_horizons(); m06_altitude(); m07_azimuths()
    m08_two_belts(); m09_six_signs(); m10_climes(); m11_ascensional(); m12_shadow_cone(); m13_lat66()
    m14_zodiac_horizon(); m15_lat_gt(); m16_no_azimuth(); m17_kuniya(); m18_indian_circle()
    qa = m19_qibla_indian(); timeline()
    deg = lambda x: math.degrees(x)
    phi = 36 + 40 / 60
    # ---- operational panels (Tunis examples)
    ops('O02_sine', [dict(title='جيب ٣٠°: من القوس في المبسوط إلى الستيني', ang=30, bead=60, to_sittini=True,
                          mark_s=[(30, '٣٠')], mark_arc=[(30, '٣٠°')], note=['جيب ٣٠ = ٣٠ جزءًا'])])
    ops('O03_shadow', [
        dict(title='١) الخيط على الارتفاع من أول القوس', ang=35, bead=12 / math.sin(math.radians(35)), mark_s=[(12, 'القامة ١٢')],
             to_sittini=True, note=['يُنزل من الستيني بالقامة إلى الخيط ويُعلَّم بالمري']),
        dict(title='٢) الخيط على الارتفاع من آخر القوس', ang=55, bead=12 / math.sin(math.radians(35)), to_sittini=True,
             mark_s=[(12 / math.tan(math.radians(35)), '١٧;٨')], note=['يُدخل من المري إلى الستيني: الظل المبسوط ≈ ١٧;٨']),
    ])
    lam = 75  # sun at 15 deg Gemini
    ops('O04_decl', [
        dict(title='١) الخيط على الستيني والمري على ٢٤', ang=90, bead=24, mark_s=[(24, '٢٤')]),
        dict(title='٢) الخيط على درجة الشمس (٧٥° = ١٥ الجوزاء)', ang=lam, bead=24, to_arc=True, arc_label='درجة الشمس',
             note=['يُنزل من المري في المبسوط إلى القوس: الميل ≈ ٢٢;٥٠']),
    ])
    ops('O06_bud', [
        dict(title='١) المري على جيب الميل ٢٤', ang=90, bead=24, mark_s=[(24, '٢٤')]),
        dict(title='٢) الخيط على العرض ٣٦;٤٠', ang=phi, bead=24, to_sittini=True, arc_label='العرض', mark_s=[(14.33, 'بُعد القطر ١٤')],
             note=['بُعد القطر = ٢٤ × جا العرض ⁄ ٦٠ ≈ ١٤', 'الأصل = جيب الغاية ٥٨;١٦ − ١٤ = ٤٤']),
    ])
    ops('O07_fadla', [
        dict(title='١) المري على الأصل ٤٤', ang=90, bead=44, mark_s=[(44, '٤٤')]),
        dict(title='٢) يُحرَّك حتى يقع المري على بُعد القطر ١٤', ang=deg(math.asin(14 / 44)), bead=44, to_sittini=True,
             arc_label='نصف الفضلة ١٩°', mark_s=[(14, '١٤')], note=['نصف قوس النهار = ٩٠ + ١٩ = ١٠٩°', 'أي ٧ ساعات و٨ دقائق تقريبًا']),
    ])
    ops('O08_fadl', [
        dict(title='١) المري على الأصل ٤٤', ang=90, bead=44, mark_s=[(44, '٤٤')]),
        dict(title='٢) حتى يقع على الأصل المعدل ١٦ (ارتفاع ٣٠°)', ang=deg(math.asin(16 / 44)), bead=44, to_sittini=True,
             arc_label='فضل الدائر ٦٩°', arc_from_end=True, mark_s=[(16, '١٦')],
             note=['الماضي من النهار = ٢١ + ١٩ = ٤٠° ، أي ساعتان وثلثان']),
    ])
    ops('O10_fajr', [
        dict(title='الأصل المعدل للفجر = ١٤ + جيب ١٩ = ٣٣;٣٠', ang=deg(math.asin(33.5 / 44)), bead=44, to_sittini=True,
             mark_s=[(33.5, '٣٣;٣٠'), (44, '٤٤')], arc_label='٥٢° ⇐ حصة الفجر ٥٢−١٩ = ٣٣°', note=['حصة الفجر ٣٣° ≈ ساعتان و١٢ دقيقة (عند الشارح)']),
    ])
    ops('O11_amplitude', [
        dict(title='المري على جيب تمام العرض ٤٨ ثم إلى جيب الميل ٢٣', ang=deg(math.asin(23 / 48)), bead=48, to_sittini=True,
             mark_s=[(23, '٢٣'), (48, '٤٨')], arc_label='سعة المشرق ٢٨;٣٠', note=['للشمس في ١٦ من السرطان على عرض تونس']),
    ])
    ops('O12_noazimuth', [
        dict(title='المري على جيب العرض ٣٦ ثم إلى جيب الميل ٢٤', ang=deg(math.asin(24 / 36)), bead=36, to_sittini=True,
             mark_s=[(24, '٢٤'), (36, '٣٦')], arc_label='٤١ وثلثان (عند الشارح)', note=['الارتفاع الذي لا سمت له في آخر الجوزاء']),
    ])
    ops('O13_azimuth', [
        dict(title='١) الخيط على تمام العرض والمري على ٢٨;٣٠', ang=90 - phi, bead=28.5, mark_s=[(28.5 * math.sin(math.radians(90 - phi)), '')], arc_label='تمام العرض'),
        dict(title='٢) نقل الخيط إلى العرض: تعديل ٢١;٣٠', ang=phi, bead=28.5, to_sittini=True, arc_label='العرض', mark_s=[(28.5 * math.sin(math.radians(phi)), '١٧')]),
        dict(title='٣) المري على جيب تمام الارتفاع ٥٢ ثم إلى ٨', ang=deg(math.asin(8 / 52)), bead=52, to_sittini=True, mark_s=[(8, '٨')],
             arc_label='السمت ٩°', note=['السمت لارتفاع ٣٠° والغاية ٧٧°']),
    ], R=210)
    ops('O14_qibla', [
        dict(title='١) المري على الأصل ٤٥ (بميل = عرض مكة)', ang=90, bead=45, mark_s=[(45, '٤٥')]),
        dict(title='٢) الخيط على فضل الطولين من آخر القوس', ang=90 - 35.42, bead=45, to_sittini=True, mark_s=[(45 * math.cos(math.radians(35.42)), '٣٦;٢٥')],
             arc_label='٣٥;٢٥', arc_from_end=True, note=['+ بُعد القطر ١٣;١٢ = ٤٩;٣٧ جيب ارتفاع سمت مكة ⇐ ٥٦°']),
        dict(title='٣) الخيط على تمام ارتفاع مكة ٣٤°، والمري على جيب فضل الطولين', ang=34, bead=34.74, mark_s=[(34.74, '٣٤;٤٤')], arc_label='٣٤°',
             note=['ثم إلى عرض مكة والنزول في المنكوس: سمت القبلة ١٨°']),
    ], R=210)
    ops('O16_ascension', [
        dict(title='المري على جيب تمام الميل الجزئي، ثم إلى جيب بُعد الدرجة عن المنقلب', ang=60, bead=55, to_sittini=True, arc_label='المطالع (تُعدَّل بحسب الربع)'),
    ])
    ops('O19_height', [
        dict(title='الخيط على الارتفاع والنزول من جيب التمام بالمسافة', ang=40, bead=30 / math.cos(math.radians(40)), munkus=True, to_sittini=True,
             mark_t=[(30, 'المسافة ٣٠')], mark_s=[(30 * math.tan(math.radians(40)), '٢٥;١٠')], arc_label='٤٠°',
             note=['يُرجع من التقاطع إلى الستيني ثم يُزاد ما بين البصر والأرض']),
    ])
    ops('O20_well', [
        dict(title='الخيط على الانخفاض ٧٠° والنزول بقطر الفم ١٠', ang=70, bead=10 / math.cos(math.radians(70)), munkus=True, to_sittini=True,
             mark_t=[(10, '١٠')], mark_s=[(10 * math.tan(math.radians(70)), '٢٧;٢٨')], arc_label='٧٠°',
             note=['٢٧ − ٦ (ما بين البصر والأرض) = ٢١ قدمًا عمق البئر']),
    ])
    return qa

if __name__ == '__main__':
    print(build())
