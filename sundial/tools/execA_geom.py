"""هندسة التنفيذ للتصميم (أ) كما في اللوحتين A-01 وA-02: وجه دائري Ø12.70 م، وحلقة تقويم إلى Ø14.50 م،
وشاخص مثلث ارتفاع عقدته 2.40 م فوق (0, 0.55)، وسمك نصل 30 مم. الوحدات بالمتر، x شرقًا وy شمالًا حقيقيًّا."""
from math import radians as rad, degrees as deg, sin, cos, tan, atan2, hypot, pi
from shapely.geometry import Polygon, LineString, Point, box, MultiLineString
from shapely.ops import unary_union
from dials import *
from common import sign_curves, star_n, SPECIAL
from exec_geom import to_grid, GAMMA

T_BLADE = 0.030
R_FACE, R_RING = 6.35, 7.25
TILE = 0.90
JOINT = 0.002
SLOT = 0.020                     # نصف عرض شق النصل في البلاط (15 نصل + 5 فاصل)


class GeoA:
    def __init__(self, scale=1.0, blade=T_BLADE):
        self.s = s = scale
        self.t = blade
        A = DesignA()
        self.lat = LAT
        self.h, self.fy = A.h*s, A.foot[1]*s
        self.yb = A.base[1]*s
        self.R, self.Rr = R_FACE*s, R_RING*s
        self.nodus = (0.0, self.fy, self.h)
        self.A = A

    def P(self, segs):
        return [[(x*self.s, y*self.s) for x, y in sg] for sg in segs]

    def families(self):
        """(الأسرة، التسمية، المقاطع، مواصفة الحفر بالمم، اللون)."""
        A, s, t = self.A, self.s, self.t
        out = []
        for H, segs in A.hours.items():
            q = round(H/3.75) % 4
            dx = (-t/2 if (H + A.corr) < 0 else t/2)
            fam = 'HOUR' if q == 0 else ('HOUR30' if q == 2 else 'HOUR15')
            spec = {'HOUR': 'راتنج أسود 8', 'HOUR30': 'راتنج أسود 4', 'HOUR15': 'راتنج رمادي 2'}[fam]
            out.append((fam, f'{12 + H/15:05.2f}', [[(x*s + dx, y*s) for x, y in sg] for sg in segs], spec))
        for dec, names, dates, lam, segs in A.signs:
            sol = abs(abs(dec) - OBLIQUITY) < 0.01 or abs(dec) < 0.01
            out.append(('DECL', '/'.join(names), self.P(segs), 'نحاس 8' if sol else 'نحاس 5'))
        out += [('ASR1', 'k=1', self.P(A.asr1), 'راتنج فيروزي 8'), ('ASR2', 'k=2', self.P(A.asr2), 'راتنج فيروزي 5 متقطع'),
                ('NOON', 'Jan-Jun', self.P(A.noon_ana[0]), 'راتنج بنفسجي 5'), ('NOON', 'Jul-Dec', self.P(A.noon_ana[1]), 'راتنج بنفسجي 5 متقطع')]
        out.append(('MERID', 'noon', [[(0, self.fy), (0, self.R)]], f'نحاس {t*1000:.0f}'))
        qa = rad(A.qibla_az)
        ql = LineString([(0, self.fy), (8*s*sin(qa), self.fy + 8*s*cos(qa))]).intersection(Point(0, 0).buffer(self.R, 256))
        out.append(('QIBLA', f'{A.qibla_az:.2f}', [list(ql.coords)], 'راتنج أزرق 8'))
        ticks = []
        for mo in range(1, 13):
            for dd in (1, 11, 21):
                d = dt.date(REF_YEAR, mo, dd); dec, eot, _ = sun_on(d)
                p = project(self.nodus, dec, 0); side = -1 if mo <= 6 else 1; L = (0.16 if dd == 1 else 0.08)*s
                ticks.append([(side*t/2, p[1]), (side*(t/2 + L), p[1])])
        out.append(('TICKS', 'date ticks', ticks, 'نحاس 3'))
        return [f for f in out if f[2] and any(len(sg) > 1 for sg in f[2])]

    def tiles(self):
        """بلاط الوجه: شبكة مربعة 0.90 م، فواصلها على خط الزوال وخط الاعتدال، مقصوصة بالدائرة وبشق النصل."""
        s, R = self.s, self.R
        circle = Point(0, 0).buffer(R, 512)
        slot = box(-SLOT*s, self.yb - SLOT*s, SLOT*s, self.fy + SLOT*s)
        n = int(R/(TILE*s)) + 1
        out = []
        for i in range(-n, n):
            for j in range(-n, n):
                sq = box(i*TILE*s, j*TILE*s, (i + 1)*TILE*s, (j + 1)*TILE*s)
                g = sq.intersection(circle).difference(slot)
                if g.is_empty or g.area < 0.0025*s*s: continue
                col = chr(ord('A') + i + n); row = n - j
                out.append(dict(id=f'{col}{row:02d}', poly=g, square=sq, full=abs(g.area - sq.area) < 1e-6, origin=(i*TILE*s, j*TILE*s), merged=None))
        # الشرائح الصغيرة (< 0.06 م²) تُضم إلى البلاطة المجاورة نحو المركز حتى لا تُقص قطع هشة
        small = [t for t in out if t['poly'].area < 0.06*s*s]
        for t in small:
            c = t['poly'].centroid
            nb = max((u for u in out if u is not t and u not in small),
                     key=lambda u: u['poly'].boundary.intersection(t['poly'].boundary).length)
            nb['poly'] = unary_union([nb['poly'], t['poly']]).buffer(0)
            nb['full'] = False; nb['merged'] = t['id']
        return [t for t in out if t not in small]

    def ring_sectors(self, n=36):
        out = []
        for k in range(n):
            a0, a1 = k*360/n, (k + 1)*360/n
            pts = [(self.R*sin(rad(a)), self.R*cos(rad(a))) for a in frange(a0, a1, 1)] + \
                  [(self.Rr*sin(rad(a)), self.Rr*cos(rad(a))) for a in frange(a1, a0, -1)]
            out.append(dict(id=f'R{k+1:02d}', poly=Polygon(pts), a0=a0, a1=a1))
        return out

    def gnomon(self, embed=0.10, frame=0.12, tile=0.24, web=0.03):
        """النصل في مستوى الزوال (y, z): الحد الخارجي، وفتحات النجوم الثمانية المقطوعة، وحدود المنطقة الداخلية."""
        s = self.s; embed, frame, tile, web = embed*s, frame*s, tile*s, web*s
        y0 = self.yb - embed/tan(rad(self.lat))
        outer = Polygon([(y0, -embed), (self.fy, self.h), (self.fy, -embed)])
        inner = Polygon([(self.yb, 0), (self.fy, self.h), (self.fy, 0)]).buffer(-frame, join_style=2)
        safe = inner.buffer(-web, join_style=2)
        stars = []
        yy = self.fy - tile/2 - frame
        while yy > self.yb:
            zz = tile/2 + frame
            while zz < self.h:
                st = Polygon(star_n(yy, zz, tile*0.48, tile*0.30, 8, 22.5))
                if safe.contains(st): stars.append(st)
                zz += tile
            yy -= tile
        return dict(outer=outer, inner=inner, stars=stars, y0=y0, embed=embed,
                    net_area=outer.area - sum(p.area for p in stars))
