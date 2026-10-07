"""أدوات بسيطة لكتابة لوحات SVG بالمليمتر (A1 أفقي افتراضيًا)."""
from math import cos, sin, radians as rad, atan2, degrees as deg
import html

INK = '#1d1b19'; GOLD = '#b8862b'; TERRA = '#b4532a'; TEAL = '#1f7a74'; BLUE = '#2f5d8a'; GREY = '#8a847c'
LIGHT = '#e9e3d6'; RED = '#c0392b'; PURPLE = '#6b4c8a'
KUFI = "'Noto Kufi Arabic', 'Amiri', sans-serif"; NASKH = "'Amiri', serif"; SANS = "'IBM Plex Sans Arabic', 'Amiri', sans-serif"


def f(v): return f'{v:.2f}'.rstrip('0').rstrip('.')


class View:
    """تحويل من إحداثيات العالم (متر، الشمال لأعلى) إلى إحداثيات اللوحة (مم) بمقياس رسم 1:scale."""
    def __init__(self, cx, cy, scale, rot=0.0):
        self.cx, self.cy, self.k, self.rot = cx, cy, 1000.0/scale, rot

    def p(self, x, y):
        return (self.cx + x*self.k, self.cy - y*self.k)

    def d(self, pts, close=False):
        s = ' '.join(('M' if i == 0 else 'L') + f(a) + ',' + f(b) for i, (a, b) in enumerate(self.p(*q) for q in pts))
        return s + (' Z' if close else '')


class Sheet:
    def __init__(self, w=841, h=594):
        self.w, self.h, self.els, self.defs = w, h, [], []

    def add(self, s): self.els.append(s)

    def path(self, d, stroke=INK, sw=0.25, fill='none', dash=None, op=None, cap='round', extra=''):
        a = f' stroke-dasharray="{dash}"' if dash else ''
        o = f' opacity="{op}"' if op is not None else ''
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" stroke-linecap="{cap}" stroke-linejoin="round"{a}{o} {extra}/>')

    def line(self, a, b, **kw): self.path(f'M{f(a[0])},{f(a[1])} L{f(b[0])},{f(b[1])}', **kw)

    def poly(self, pts, close=False, **kw):
        self.path(' '.join(('M' if i == 0 else 'L') + f(x) + ',' + f(y) for i, (x, y) in enumerate(pts)) + (' Z' if close else ''), **kw)

    def circle(self, c, r, stroke=INK, sw=0.25, fill='none', dash=None, op=None):
        a = f' stroke-dasharray="{dash}"' if dash else ''
        o = f' opacity="{op}"' if op is not None else ''
        self.add(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{a}{o}/>')

    def rect(self, x, y, w, h, stroke=INK, sw=0.25, fill='none', rx=0, op=None):
        o = f' opacity="{op}"' if op is not None else ''
        self.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{o}/>')

    def text(self, x, y, s, size=3.0, anchor='middle', font=SANS, fill=INK, weight=400, rot=0, op=None, base='central', ls=None):
        t = f' transform="rotate({f(rot)} {f(x)} {f(y)})"' if rot else ''
        o = f' opacity="{op}"' if op is not None else ''
        l = f' letter-spacing="{ls}"' if ls else ''
        anchor = {'start': 'end', 'end': 'start'}.get(anchor, anchor)   # المرسى فيزيائي: start يسار وend يمين
        self.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}" text-anchor="{anchor}" dominant-baseline="{base}" '
                 f'font-family="{font}" font-weight="{weight}" fill="{fill}" direction="rtl"{t}{o}{l}>{html.escape(str(s))}</text>')

    def ltr(self, x, y, s, size=3.0, anchor='middle', font=SANS, fill=INK, weight=400, rot=0, op=None):
        t = f' transform="rotate({f(rot)} {f(x)} {f(y)})"' if rot else ''
        o = f' opacity="{op}"' if op is not None else ''
        self.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}" text-anchor="{anchor}" dominant-baseline="central" '
                 f'font-family="{font}" font-weight="{weight}" fill="{fill}" direction="ltr"{t}{o}>{html.escape(str(s))}</text>')

    def para(self, x, y, lines, size=2.6, lh=1.55, font=SANS, fill=INK, weight=400, anchor='end'):
        for i, s in enumerate(lines):
            if s.startswith('##'):
                self.text(x, y + i*size*lh, s[2:].strip(), size*1.12, anchor, KUFI, fill, 700)
            else:
                self.text(x, y + i*size*lh, s, size, anchor, font, fill, weight)
        return y + len(lines)*size*lh

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" viewBox="0 0 {self.w} {self.h}">'
                f'<defs>{"".join(self.defs)}</defs><rect width="{self.w}" height="{self.h}" fill="#fffdf8"/>' + '\n'.join(self.els) + '</svg>')

    def save(self, path):
        open(path, 'w', encoding='utf-8').write(self.svg())


def frame(sh, title, sub, number, scale_txt, design, notes=()):
    """إطار اللوحة وجدول العنوان على اليسار (اتجاه القراءة من اليمين)."""
    W, H = sh.w, sh.h
    sh.rect(10, 10, W - 20, H - 20, sw=0.7)
    x0 = 12; bw = 150
    sh.rect(x0, 12, bw, H - 24, sw=0.35)
    xr = x0 + bw - 5
    y = 24
    sh.text(xr, y, 'مشروع حدائق الفسطاط — المرحلة الثانية', 4.2, 'end', KUFI, INK, 700); y += 7
    sh.text(xr, y, 'منطقة الحدائق التراثية • البند SF-12: المزولة الشمسية', 3.0, 'end', SANS, GREY); y += 6
    sh.line((x0 + 4, y), (x0 + bw - 4, y), sw=0.3); y += 9
    sh.text(xr, y, design, 5.4, 'end', KUFI, TERRA, 700); y += 9
    sh.text(xr, y, title, 4.0, 'end', KUFI, INK, 700); y += 6.5
    for s in sub:
        sh.text(xr, y, s, 2.8, 'end', SANS, GREY); y += 4.6
    y += 3
    sh.line((x0 + 4, y), (x0 + bw - 4, y), sw=0.3); y += 7
    if notes:
        sh.text(xr, y, 'ملاحظات', 3.4, 'end', KUFI, INK, 700); y += 6
        for s in notes:
            sh.text(xr, y, s, 2.55, 'end', SANS, INK); y += 4.3
    # خانة البيانات أسفل
    yb = H - 70
    sh.line((x0, yb), (x0 + bw, yb), sw=0.35)
    rows = [('الموقع', 'φ = 30.0054° ش  •  λ = 31.2443° ق'), ('مركز المزولة (الحزام الأحمر)', 'E 638413.3  •  N 810602.7'),
            ('القطر', '14.50 م'), ('مقياس الرسم', scale_txt), ('التاريخ', 'أكتوبر 2026'), ('الحالة', 'مقترح تصميمي للمفاضلة')]
    for i, (k, v) in enumerate(rows):
        yy = yb + 6 + i*7.2
        sh.text(xr, yy, k, 2.5, 'end', SANS, GREY)
        sh.ltr(x0 + 5, yy, v, 2.7, 'start', SANS, INK, 600) if any(c.isdigit() for c in v) and not any('؀' <= c <= 'ۿ' for c in v[:3]) else sh.text(x0 + 5, yy, v, 2.7, 'start', SANS, INK, 600)
    sh.rect(x0 + 4, H - 26, 34, 12, sw=0.4)
    sh.ltr(x0 + 21, H - 20, number, 5.2, 'middle', SANS, INK, 700)


def north_arrow(sh, x, y, conv=0.1214, r=11):
    sh.circle((x, y), r, sw=0.3)
    sh.poly([(x, y - r*0.95), (x + r*0.32, y + r*0.55), (x, y + r*0.25), (x - r*0.32, y + r*0.55)], close=True, fill=INK, sw=0.2)
    sh.text(x, y - r - 4.5, 'الشمال الحقيقي', 3.0, 'middle', KUFI, INK, 700)
    sh.text(x, y + r + 4.5, f'الشمال الشبكي منحرف {conv:.2f}° شرقًا', 2.3, 'middle', SANS, GREY)


def scale_bar(sh, view, x, y, meters=5, step=1):
    k = view.k
    for i in range(meters):
        sh.rect(x + i*k, y, k, 2.2, sw=0.25, fill=(INK if i % 2 == 0 else 'none'))
    for i in range(0, meters + 1, step):
        sh.ltr(x + i*k, y + 5.2, f'{i}', 2.4)
    sh.text(x + meters*k + 3, y + 1.1, 'م', 2.6, 'start')


def star8(cx, cy, r, rot=0):
    """نجمة ثمانية (خاتم سليمان) من مربعين."""
    return star_n(cx, cy, r, r*0.7654, 8, rot)


def star_n(cx, cy, r_out, r_in, n, rot=0):
    pts = []
    for i in range(2*n):
        a = rad(rot + i*180/n); rr = r_out if i % 2 == 0 else r_in
        pts.append((cx + rr*sin(a), cy - rr*cos(a)))
    return pts
