"""هندسة التصاميم الثلاثة بالحساب (بالمتر، x شرقًا وy شمالًا حقيقيًا، الأصل مركز الدائرة)."""
from astro import *

R_SITE = 7.25        # نصف قطر الدائرة المتاحة (القطر 14.5 م)


# ---------------------------------------------------------------- أدوات هندسية
def project(nodus, dec, H):
    """إسقاط العقدة (fx, fy, h) على مستوى أفقي: موضع طرف الظل أو بقعة الضوء."""
    fx, fy, h = nodus
    E, N, U = sunvec(dec, H)
    if U <= 0.02: return None
    return (fx - h*E/U, fy - h*N/U)


def inside(p, R):
    return p is not None and p[0]**2 + p[1]**2 <= R*R


def clip_polyline(pts, R):
    """قص خط منكسر بدائرة نصف قطرها R؛ يعيد قائمة أجزاء."""
    def cross(a, b):
        lo, hi = 0.0, 1.0
        ia = inside(a, R)
        for _ in range(40):
            m = (lo + hi)/2; p = (a[0] + (b[0]-a[0])*m, a[1] + (b[1]-a[1])*m)
            if inside(p, R) == ia: lo = m
            else: hi = m
        return (a[0] + (b[0]-a[0])*lo, a[1] + (b[1]-a[1])*lo)
    segs, cur = [], []
    prev = None
    for p in pts:
        if p is None:
            if len(cur) > 1: segs.append(cur)
            cur, prev = [], None; continue
        if inside(p, R):
            if prev is not None and not inside(prev, R): cur = [cross(prev, p)]
            cur.append(p)
        elif prev is not None and inside(prev, R):
            cur.append(cross(prev, p)); segs.append(cur); cur = []
        prev = p
    if len(cur) > 1: segs.append(cur)
    return segs


def frange(a, b, s):
    n = int(round((b - a)/s)); return [a + i*(b - a)/n for i in range(n + 1)]


SIGN_DECS = [(0, 180), (30, 150), (60, 120), (90, None), (330, 210), (300, 240), (270, None)]


def sign_curves():
    """منحنيات مداخل البروج: (الميل، تسمية الطرفين)."""
    out = []
    for a, b in SIGN_DECS:
        dec = ecl_to_dec(a)
        names = [SIGNS[a//30]] + ([SIGNS[b//30]] if b is not None else [])
        dates = [date_of_longitude(a)] + ([date_of_longitude(b)] if b is not None else [])
        out.append((dec, names, dates, a))
    return out


def dec_curve(nodus, dec, R, step=0.25):
    Hs = sunrise_H(dec)
    pts = [project(nodus, dec, H) for H in frange(-Hs, Hs, step)]
    return clip_polyline(pts, R)


def hour_line(nodus, H, R, decs=(-OBLIQUITY, OBLIQUITY)):
    pts = []
    for d in frange(decs[0], decs[1], 0.25):
        sr = sunrise_H(d)
        pts.append(project(nodus, d, H) if sr and abs(H) < sr else None)
    return clip_polyline(pts, R)


def asr_curve(nodus, k, R):
    pts = [project(nodus, d, asr_H(d, k)) for d in frange(-OBLIQUITY, OBLIQUITY, 0.2)]
    return clip_polyline(pts, R)


def clock_analemma(nodus, T, R, year=REF_YEAR):
    """منحنى الساعة الرسمية T (توقيت مصر الشتوي) على مدار السنة، مقسومًا إلى نصفي السنة."""
    first, second = [], []
    for d, dec, eot, lam in year_days(year, T):
        p = project(nodus, dec, H_from_clock(T, eot))
        (first if d.month <= 6 else second).append(p)
    return clip_polyline(first, R), clip_polyline(second, R)


# ---------------------------------------------------------------- التصميم (أ): مزولة ابن الشاطر الحديثة
class DesignA:
    """مزولة أفقية بشاخص قطبي مثلث (أول شاخص قطبي معروف: ابن الشاطر، دمشق 773هـ/1371م)."""
    R_FACE = 6.35          # حد الوجه المرسوم
    R_RING = 7.25          # حلقة التقويم من 6.35 إلى 7.25
    h = 2.40               # ارتفاع العقدة (رأس الشاخص) فوق الوجه
    foot = (0.0, 0.55)     # مسقط العقدة على الوجه

    def __init__(self):
        fx, fy = self.foot
        self.nodus = (fx, fy, self.h)
        self.base = (fx, fy - self.h/tan(rad(LAT)))   # ملتقى الضلع القطبي بالوجه (مركز خطوط الساعات)
        R = self.R_FACE
        self.signs = [(dec, names, dates, a, dec_curve(self.nodus, dec, R)) for dec, names, dates, a in sign_curves()]
        self.hours = {}
        self.corr = LON - ZONE_MERIDIAN            # خطوط الساعات لتوقيت خط 30° ش (المتوسط)
        for q in frange(-105, 105, 3.75):      # كل ربع ساعة؛ المفتاح = 15°×(T−12)
            self.hours[round(q, 2)] = hour_line(self.nodus, q + self.corr, R)
        self.asr1 = asr_curve(self.nodus, 1, R)
        self.asr2 = asr_curve(self.nodus, 2, R)
        self.noon_ana = clock_analemma(self.nodus, 12.0, R)
        qa = qibla()
        self.qibla_az = qa


# ---------------------------------------------------------------- التصميم (ب): مزولة الإنسان (الإهليلجية)
class DesignB:
    M = 5.75                       # نصف المحور الأكبر (شرق–غرب)
    def __init__(self):
        self.m = self.M*sin(rad(LAT))
        self.corr = LON - ZONE_MERIDIAN       # إزاحة علامات الساعات لتقرأ توقيت مصر (بلا معادلة الزمن)

    def hour_point(self, H):
        return (self.M*sin(rad(H)), self.M*sin(rad(LAT))*cos(rad(H)))

    def date_y(self, dec):
        return self.M*cos(rad(LAT))*tan(rad(dec))

    def clock_point(self, T):
        """موضع علامة الساعة الرسمية T (متوسط، دون معادلة الزمن)."""
        return self.hour_point(15*(T - 12) + self.corr)


# ---------------------------------------------------------------- التصميم (ج): عين الشمس (ثقب ضوئي ومنحنيات الساعة الرسمية)
class DesignC:
    R_FACE = 6.35
    H = 4.00                        # ارتفاع ثقب الضوء
    foot = (0.0, -3.00)             # مسقط الثقب (البوابة داخل الدائرة جنوب مركزها)

    def __init__(self):
        fx, fy = self.foot
        self.nodus = (fx, fy, self.H)
        R = self.R_FACE
        self.signs = [(dec, names, dates, a, dec_curve(self.nodus, dec, R, 0.2)) for dec, names, dates, a in sign_curves()]
        self.analemmas = {T: clock_analemma(self.nodus, T, R) for T in frange(8, 16, 0.5)}
        self.asr1 = asr_curve(self.nodus, 1, R)
        self.meridian = hour_line(self.nodus, 0.0, R)
