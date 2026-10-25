"""هندسة الرسومات التنفيذية للتصميم (أ) — الرخامة الجامعة لعرض الفسطاط — وللنموذج المصغر.
الوحدات بالمتر؛ x شرقًا وy نحو الشمال الحقيقي، والأصل مركز الدائرة؛ z رأسيًّا من منسوب التشطيب ±0.00."""
from shatir import *
from common import sign_curves

FUS = dict(lat=LAT, W=11.40, Dp=5.60, h=1.60, fy=-1.76, corr=LON - ZONE_MERIDIAN, fajr_alt=-19.5)
from math import radians as rad, degrees as deg, sin, cos, tan
from shapely.geometry import Polygon

GAMMA = GRID_CONV           # تقارب الشبكة (°): الشمال الشبكي شرق الحقيقي


class Dial(Marble):
    """رخامة بسمك نصل: خطوط الساعات المستوية تُزاح نصف السمك (الصباح غربًا والمساء شرقًا)."""
    def __init__(self, scale=1.0, blade=0.020, **over):
        p = dict(FUS); p.update(over)
        for k in ('W', 'Dp', 'h', 'fy'): p[k] = p[k]*scale
        super().__init__(**p)
        self.scale, self.t = scale, blade

    def equal_hour(self, q):
        H = q + self.corr
        dx = -self.t/2 if H < 0 else self.t/2
        return [[(x + dx, y) for x, y in s] for s in super().equal_hour(q)]


def families(M):
    """كل الخطوط المحفورة: (الأسرة، التسمية، المقاطع، مواصفة الحفر)."""
    out = []
    for d, n, dates, lam in sign_curves():
        sol = abs(abs(d) - OBLIQUITY) < 0.01
        spec = 'brass 8' if sol or d == 0 else 'brass 5'
        out.append(('DECL', '/'.join(n), M.decl(d), spec))
    for m in range(-105*4, 105*4 + 1, 20):
        whole = m % 60 == 0
        out.append(('HOUR' if whole else 'HOUR20', f'{12 + m/60:05.2f}', M.equal_hour(m/4), 'resin-black 6' if whole else 'resin-black 2'))
    for n in range(1, 14):
        out.append(('RISE', f'{n}', M.since_rise(n), 'resin-green 3'))
        out.append(('SET', f'{n}', M.to_set(n), 'resin-yellow 3'))
    for k in range(1, 12):
        out.append(('TEMP', f'{k}', M.temporal(k), 'resin-blue 2 dashed'))
    out += [('ASR1', 'k=1', M.asr(1), 'resin-purple 6'), ('ASR2', 'k=2', M.asr(2), 'resin-red 6'),
            ('FAJR', '13.5h', M.fajr_remaining(13.5), 'resin-teal 4 dashed')]
    out.append(('MERID', 'noon', [[(0, -M.Dp/2), (0, M.Dp/2)]], f'brass {M.t*1000:.0f}'))
    return [f for f in out if f[2]]


def gnomon_profile(M, w=0.12, R=0.10, embed=0.07):
    """مقطع النصل في مستوى الزوال: (y, z). الضلع القطبي يمر بنقطة القاعدة B على المنسوب 0 وبالعقدة N.
    يمتد النصل تحت المنسوب بمقدار embed حتى لوح القاعدة. الفتحة الداخلية بإطار عرضه w وأركان مقوسة R."""
    s = M.scale; w, R, embed = w*s, R*s, embed*s
    yb, fy, h = M.base[1], M.fy, M.h
    y0 = yb - embed/tan(rad(M.lat))
    outer = Polygon([(y0, -embed), (fy, h), (fy, -embed)])
    hole = Polygon([(yb, 0), (fy, h), (fy, 0)]).buffer(-w, join_style=2).buffer(-R).buffer(R)
    return outer, hole, (y0, -embed)


def to_grid(x, y, E0=SITE_E, N0=SITE_N):
    g = rad(GAMMA)
    return E0 + x*cos(g) - y*sin(g), N0 + y*cos(g) + x*sin(g)


SLAB_COLS, SLAB_ROWS = 12, 8         # ألواح 0.95 × 0.70 م
ROWS = 'أبجدهوزح'


def slab_name(c, r):
    return f'{ROWS[r]}{c + 1}'


def export_dxf(path, M, extra=None):
    import ezdxf
    doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    cols = {'DECL': 30, 'HOUR': 7, 'HOUR20': 8, 'RISE': 3, 'SET': 2, 'TEMP': 5, 'ASR1': 6, 'ASR2': 1, 'FAJR': 4, 'MERID': 40,
            'OUTLINE': 7, 'SLABS': 9, 'GNOMON': 1, 'TEXT': 7}
    for n, c in cols.items(): doc.layers.add(n, color=c)
    k = 1000.0
    for fam, lbl, segs, spec in families(M):
        for sg in segs:
            msp.add_lwpolyline([(x*k, y*k) for x, y in sg], dxfattribs={'layer': fam})
    W2, D2 = M.W/2*k, M.Dp/2*k
    msp.add_lwpolyline([(-W2, -D2), (W2, -D2), (W2, D2), (-W2, D2)], close=True, dxfattribs={'layer': 'OUTLINE'})
    if extra: extra(msp, k)
    doc.saveas(path)
