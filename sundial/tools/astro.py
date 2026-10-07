"""الحسابات الفلكية لمزولة تلال الفسطاط.

كل الزوايا بالدرجات ما لم يُذكر غير ذلك. الإحداثيات على وجه المزولة:
x نحو الشرق، y نحو الشمال الحقيقي، والوحدة المتر، والأصل مركز دائرة المزولة.
الخوارزميات: موقع الشمس ومعادلة الزمن بصيغ NOAA/Meeus المختصرة (دقة نحو 0.01° و10 ثوانٍ).
"""
from math import sin, cos, tan, asin, acos, atan, atan2, sqrt, radians as rad, degrees as deg, floor, pi
import datetime as dt

# ---------------------------------------------------------------- الموقع
# مركز المزولة مقيسًا من لوحة CD.H1.00.LS.04.02.04.01 (شبكة الحزام الأحمر، مصر 1907)
SITE_E, SITE_N = 638413.3, 810602.7
TZ = 2.0            # توقيت مصر الرسمي (EET) UTC+2؛ والتوقيت الصيفي UTC+3
ZONE_MERIDIAN = 30.0
OBLIQUITY = 23.4362  # ميل دائرة البروج لسنة 2027 تقريبًا


def redbelt_to_wgs84(E, N):
    """تحويل إحداثيات الحزام الأحمر (EPSG:22992) إلى خط عرض وطول WGS84."""
    a, f = 6378200.0, 1 / 298.3          # هيلمرت 1906
    lat0, lon0, k0, FE, FN = rad(30), rad(31), 1.0, 615000.0, 810000.0
    e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    def M(p):
        return a * ((1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * p - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * sin(2*p)
                    + (15*e2**2/256 + 45*e2**3/1024) * sin(4*p) - (35*e2**3/3072) * sin(6*p))
    m = M(lat0) + (N - FN) / k0
    mu = m / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    e1 = (1 - sqrt(1 - e2)) / (1 + sqrt(1 - e2))
    p1 = mu + (3*e1/2 - 27*e1**3/32) * sin(2*mu) + (21*e1**2/16 - 55*e1**4/32) * sin(4*mu) \
        + (151*e1**3/96) * sin(6*mu) + (1097*e1**4/512) * sin(8*mu)
    C1 = ep2 * cos(p1)**2; T1 = tan(p1)**2
    N1 = a / sqrt(1 - e2 * sin(p1)**2); R1 = a * (1 - e2) / (1 - e2 * sin(p1)**2) ** 1.5
    D = (E - FE) / (N1 * k0)
    lat = p1 - (N1 * tan(p1) / R1) * (D**2/2 - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*ep2) * D**4/24)
    lon = lon0 + (D - (1 + 2*T1 + C1) * D**3/6) / cos(p1)
    # إزاحة المرجع إلى WGS84 (Egypt 1907 → WGS84: -130, 110, -13 م)
    def ecef(lat, lon, a, e2):
        n = a / sqrt(1 - e2 * sin(lat)**2)
        return n*cos(lat)*cos(lon), n*cos(lat)*sin(lon), n*(1-e2)*sin(lat)
    X, Y, Z = ecef(lat, lon, a, e2)
    X, Y, Z = X - 130, Y + 110, Z - 13
    a2, f2 = 6378137.0, 1/298.257223563; e22 = f2*(2-f2)
    lon2 = atan2(Y, X); pp = sqrt(X*X + Y*Y); lat2 = atan2(Z, pp*(1-e22))
    for _ in range(6):
        n = a2 / sqrt(1 - e22*sin(lat2)**2); lat2 = atan2(Z + e22*n*sin(lat2), pp)
    conv = deg(lon - lon0) * sin(lat)     # تقارب الشبكة: زاوية الشمال الشبكي عن الحقيقي
    return deg(lat2), deg(lon2), conv


LAT, LON, GRID_CONV = redbelt_to_wgs84(SITE_E, SITE_N)
KAABA = (21.42252, 39.82621)


# ---------------------------------------------------------------- الشمس
def jd(y, m, d, h=0.0):
    if m <= 2: y -= 1; m += 12
    A = y // 100; B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5 + h/24


def jd_to_date(J):
    J += 0.5; Z = int(J); F = J - Z
    A = Z if Z < 2299161 else Z + 1 + int((Z - 1867216.25)/36524.25) - int(int((Z - 1867216.25)/36524.25)/4)
    B = A + 1524; C = int((B - 122.1)/365.25); D = int(365.25*C); E = int((B - D)/30.6001)
    day = B - D - int(30.6001*E) + F
    m = E - 1 if E < 14 else E - 13; y = C - 4716 if m > 2 else C - 4715
    return dt.date(y, m, int(day))


def sun(J):
    """(الميل δ، معادلة الزمن بالدقائق، طول الشمس البروجي λ) عند يوم جولياني J (بتوقيت عالمي)."""
    T = (J - 2451545.0) / 36525
    L0 = (280.46646 + T*(36000.76983 + 0.0003032*T)) % 360
    Mn = 357.52911 + T*(35999.05029 - 0.0001537*T)
    e = 0.016708634 - T*(0.000042037 + 0.0000001267*T)
    C = sin(rad(Mn))*(1.914602 - T*(0.004817 + 0.000014*T)) + sin(rad(2*Mn))*(0.019993 - 0.000101*T) + sin(rad(3*Mn))*0.000289
    true_long = L0 + C
    om = 125.04 - 1934.136*T
    lam = true_long - 0.00569 - 0.00478*sin(rad(om))
    eps0 = 23 + (26 + (21.448 - T*(46.815 + T*(0.00059 - T*0.001813)))/60)/60
    eps = eps0 + 0.00256*cos(rad(om))
    dec = deg(asin(sin(rad(eps))*sin(rad(lam))))
    y = tan(rad(eps/2))**2
    E = y*sin(2*rad(L0)) - 2*e*sin(rad(Mn)) + 4*e*y*sin(rad(Mn))*cos(2*rad(L0)) \
        - 0.5*y*y*sin(4*rad(L0)) - 1.25*e*e*sin(2*rad(Mn))
    return dec, 4*deg(E), lam % 360


def sun_on(date, hour_local=12.0, tz=TZ):
    return sun(jd(date.year, date.month, date.day, hour_local - tz))


def sunvec(dec, H, lat=None):
    """متجه الشمس (شرق، شمال، أعلى) لميل dec وزاوية ساعية H (موجبة بعد الزوال)."""
    lat = LAT if lat is None else lat
    p, d, h = rad(lat), rad(dec), rad(H)
    U = sin(p)*sin(d) + cos(p)*cos(d)*cos(h)
    E = -cos(d)*sin(h)
    N = cos(p)*sin(d) - sin(p)*cos(d)*cos(h)
    return E, N, U


def altaz(dec, H, lat=None):
    E, N, U = sunvec(dec, H, lat)
    return deg(asin(max(-1, min(1, U)))), deg(atan2(E, N)) % 360


def hour_angle_for_alt(dec, alt, lat=None):
    lat = LAT if lat is None else lat
    c = (sin(rad(alt)) - sin(rad(lat))*sin(rad(dec))) / (cos(rad(lat))*cos(rad(dec)))
    if abs(c) > 1: return None
    return deg(acos(c))


def asr_altitude(dec, k=1, lat=None):
    """ارتفاع الشمس عند العصر: ظل الشاخص = k × طوله + ظل الزوال (k=1 الشافعي، k=2 الحنفي)."""
    lat = LAT if lat is None else lat
    return deg(atan(1 / (k + tan(rad(abs(lat - dec))))))


def asr_H(dec, k=1, lat=None):
    return hour_angle_for_alt(dec, asr_altitude(dec, k, lat), lat)


def sunrise_H(dec, lat=None):
    return hour_angle_for_alt(dec, -0.833, lat)


def clock_from_H(H, eot, lon=None, dst=False):
    """الوقت الرسمي (ساعات) المقابل لزاوية ساعية H ومعادلة زمن eot (دقائق)."""
    lon = LON if lon is None else lon
    lat_time = 12 + H/15                      # الوقت الشمسي الحقيقي (المزولة)
    lmt = lat_time - eot/60                   # الوقت المحلي المتوسط
    return lmt - (lon - ZONE_MERIDIAN)/15 + (1 if dst else 0)


def H_from_clock(T, eot, lon=None, dst=False):
    lon = LON if lon is None else lon
    return 15*((T - (1 if dst else 0)) + (lon - ZONE_MERIDIAN)/15 + eot/60 - 12)


def egypt_dst(date):
    """التوقيت الصيفي في مصر منذ 2023: من آخر جمعة في أبريل إلى آخر خميس في أكتوبر."""
    def last(y, m, wd):
        d = dt.date(y, m + 1, 1) - dt.timedelta(days=1)
        while d.weekday() != wd: d -= dt.timedelta(days=1)
        return d
    return last(date.year, 4, 4) <= date <= last(date.year, 10, 3)


def ecl_to_dec(lam):
    return deg(asin(sin(rad(OBLIQUITY))*sin(rad(lam))))


def qibla(lat=None, lon=None):
    lat = LAT if lat is None else lat; lon = LON if lon is None else lon
    p1, p2, dl = rad(lat), rad(KAABA[0]), rad(KAABA[1] - lon)
    return deg(atan2(sin(dl), cos(p1)*tan(p2) - sin(p1)*cos(dl))) % 360


def kaaba_transits(year):
    """أيام تعامد الشمس على الكعبة ووقتها (عالمي)."""
    out = []
    d = dt.date(year, 1, 1)
    prev = None
    while d.year == year:
        J = jd(d.year, d.month, d.day, 9.5)
        dec, eot, _ = sun(J)
        diff = dec - KAABA[0]
        if prev is not None and prev[1]*diff <= 0:
            # أقرب اليومين
            best = prev[0] if abs(prev[1]) < abs(diff) else d
            dec, eot, _ = sun(jd(best.year, best.month, best.day, 9.5))
            ut = 12 - KAABA[1]/15 - eot/60
            out.append((best, ut, dec))
        prev = (d, diff)
        d += dt.timedelta(days=1)
    return out


# ---------------------------------------------------------------- التقاويم
COPTIC_MONTHS = ['توت', 'بابه', 'هاتور', 'كيهك', 'طوبة', 'أمشير', 'برمهات', 'برمودة', 'بشنس', 'بؤونة', 'أبيب', 'مسرى', 'النسيء']
GREG_MONTHS = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
SIGNS = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']
MANSIONS = ['الشرطين', 'البطين', 'الثريا', 'الدبران', 'الهقعة', 'الهنعة', 'الذراع', 'النثرة', 'الطرف', 'الجبهة',
            'الزبرة', 'الصرفة', 'العواء', 'السماك', 'الغفر', 'الزبانى', 'الإكليل', 'القلب', 'الشولة', 'النعائم',
            'البلدة', 'سعد الذابح', 'سعد بلع', 'سعد السعود', 'سعد الأخبية', 'الفرغ المقدم', 'الفرغ المؤخر', 'الرشاء']


def hijri_new_year(ah):
    """تاريخ 1 محرم من السنة الهجرية ah بالتقويم الحسابي (قد يختلف يومًا عن الرؤية)."""
    J = 1948439.5 + 354*(ah - 1) + floor((3 + 11*ah)/30)
    return jd_to_date(J)


def coptic_new_year(greg_year):
    """1 توت: 11 سبتمبر، و12 سبتمبر إذا كانت السنة الميلادية التالية كبيسة."""
    nxt = greg_year + 1
    leap = (nxt % 4 == 0 and nxt % 100 != 0) or nxt % 400 == 0
    return dt.date(greg_year, 9, 12 if leap else 11)


def ar_digits(s):
    return str(s).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))


REF_YEAR = 2027


def year_days(year=REF_YEAR, hour_local=12.0):
    """قائمة (التاريخ، الميل، معادلة الزمن) لكل يوم من السنة المرجعية."""
    d = dt.date(year, 1, 1); out = []
    while d.year == year:
        dec, eot, lam = sun_on(d, hour_local)
        out.append((d, dec, eot, lam)); d += dt.timedelta(days=1)
    return out


def date_of_longitude(lam_target, year=REF_YEAR):
    """أول يوم يبلغ فيه طول الشمس lam_target (لتسمية خطوط البروج بتواريخها)."""
    best = None
    for d, dec, eot, lam in year_days(year):
        diff = (lam - lam_target + 180) % 360 - 180
        if best is None or abs(diff) < abs(best[1]): best = (d, diff)
    return best[0]


if __name__ == '__main__':
    print(f'الموقع: φ={LAT:.5f}  λ={LON:.5f}  تقارب الشبكة={GRID_CONV:.4f}°')
    print(f'تصحيح الطول: {(LON-ZONE_MERIDIAN)*4:.2f} دقيقة   القبلة: {qibla():.2f}°')
    for d in [dt.date(2027, 2, 11), dt.date(2027, 5, 14), dt.date(2027, 7, 26), dt.date(2027, 11, 3)]:
        dec, eot, lam = sun_on(d); print(d, f'δ={dec:.3f} EoT={eot:.2f} λ={lam:.2f}')
    for d in [dt.date(2027, 6, 21), dt.date(2027, 12, 21), dt.date(2027, 3, 20)]:
        dec, eot, _ = sun_on(d); dst = egypt_dst(d)
        noon = clock_from_H(0, eot, dst=dst); asr = clock_from_H(asr_H(dec), eot, dst=dst)
        sr = clock_from_H(-sunrise_H(dec), eot, dst=dst); ss = clock_from_H(sunrise_H(dec), eot, dst=dst)
        f = lambda t: f'{int(t):02d}:{int(round((t % 1)*60)) % 60:02d}'
        print(d, 'شروق', f(sr), 'ظهر', f(noon), 'عصر', f(asr), 'غروب', f(ss), 'صيفي' if dst else '')
    print('الكعبة', kaaba_transits(2027))
    print('محرم', [(a, hijri_new_year(a)) for a in (1448, 1449, 1450, 1481)])
    print('توت', coptic_new_year(2027), 'الاعتدال', date_of_longitude(0))
