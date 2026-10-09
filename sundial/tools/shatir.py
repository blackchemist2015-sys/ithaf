"""هندسة رخامة ابن الشاطر (دمشق 773هـ، نسخة الطنطاوي 1293هـ) بالحساب: وجه أفقي وشاخص قطبي، وعليه
الساعات المستوية والزمانية، والدائر من الطلوع والباقي للغروب، والعصران، وقوس الباقي للفجر، ومدارات البروج."""
from astro import *
from math import radians as rad, degrees as deg, sin, cos, tan, asin, acos, atan


def svec(lat, dec, H):
    p, d, h = rad(lat), rad(dec), rad(H)
    return (-cos(d)*sin(h), cos(p)*sin(d) - sin(p)*cos(d)*cos(h), sin(p)*sin(d) + cos(p)*cos(d)*cos(h))


def H_alt(lat, dec, alt):
    c = (sin(rad(alt)) - sin(rad(lat))*sin(rad(dec)))/(cos(rad(lat))*cos(rad(dec)))
    return None if abs(c) > 1 else deg(acos(c))


def asr_alt(lat, dec, k):
    return deg(atan(1/(k + tan(rad(abs(lat - dec))))))


def fr(a, b, s):
    n = max(1, int(round((b - a)/s))); return [a + i*(b - a)/n for i in range(n + 1)]


class Marble:
    def __init__(self, lat, W, Dp, h, fy, corr=0.0, fajr_alt=-18.0, eps=OBLIQUITY):
        self.lat, self.W, self.Dp, self.h, self.fy, self.corr, self.fajr, self.eps = lat, W, Dp, h, fy, corr, fajr_alt, eps
        self.nod = (0.0, fy, h)
        self.base = (0.0, fy - h/tan(rad(lat)))

    def proj(self, dec, H):
        E, N, U = svec(self.lat, dec, H)
        if U <= 0.03: return None
        return (-self.h*E/U, self.fy - self.h*N/U)

    def inside(self, p, m=0.0):
        return p is not None and abs(p[0]) <= self.W/2 - m and abs(p[1]) <= self.Dp/2 - m

    def clip(self, pts, m=0.0):
        segs, cur = [], []
        for p in pts:
            if self.inside(p, m): cur.append(p)
            else:
                if len(cur) > 1: segs.append(cur)
                cur = []
        if len(cur) > 1: segs.append(cur)
        return segs

    def H0(self, dec): return H_alt(self.lat, dec, -0.833)

    def family(self, Hfun, step=0.25):
        """منحنى عبر المدى السنوي للميل: Hfun(dec) → الزاوية الساعية أو None."""
        pts = []
        for d in fr(-self.eps, self.eps, step):
            H = Hfun(d)
            pts.append(self.proj(d, H) if H is not None else None)
        return self.clip(pts)

    def decl(self, dec, step=0.2):
        H0 = self.H0(dec)
        return self.clip([self.proj(dec, H) for H in fr(-H0 + 0.5, H0 - 0.5, step)])

    # الأسر
    def equal_hour(self, q):          # q بالدرجات من الزوال (ساعة مستوية)
        return self.family(lambda d: (q + self.corr) if abs(q + self.corr) < self.H0(d) - 0.5 else None)

    def since_rise(self, n):          # الدائر من الطلوع (ساعات مستوية) — خطوط مستقيمة
        return self.family(lambda d: -self.H0(d) + 15*n if 0 < 15*n < 2*self.H0(d) else None)

    def to_set(self, n):              # الباقي للغروب
        return self.family(lambda d: self.H0(d) - 15*n if 0 < 15*n < 2*self.H0(d) else None)

    def temporal(self, k):            # الساعات الزمانية: النهار اثنتا عشرة
        return self.family(lambda d: -self.H0(d) + k*2*self.H0(d)/12)

    def asr(self, k):
        return self.family(lambda d: H_alt(self.lat, d, asr_alt(self.lat, d, k)))

    def fajr_remaining(self, R):      # قوس الباقي للفجر: R ساعة حتى فجر الغد
        def f(d):
            Hf = H_alt(self.lat, d, self.fajr)
            if Hf is None: return None
            H = 360 - Hf - 15*R
            return H if abs(H) < self.H0(d) - 0.5 else None
        return self.family(f)
