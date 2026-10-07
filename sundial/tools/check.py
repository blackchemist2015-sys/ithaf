"""فحوص مستقلة لصحة الهندسة: تُشغَّل قبل اعتماد اللوحات."""
from dials import *
from math import atan2, degrees, hypot

A = DesignA(); B = DesignB(); C = DesignC()
worst = 0
# (1) التصميم أ: طرف ظل العقدة يقع على خط الساعة المار بملتقى الضلع القطبي
for dec in (-23.44, -11.47, 0, 11.47, 23.44):
    for H in (-60, -30, -7.5, 15, 45, 75):
        p = project(A.nodus, dec, H)
        if not p: continue
        E, N, U = sunvec(dec, H)
        # اتجاه ظل الضلع القطبي: إسقاط نقطة ثانية على الضلع (منتصفه)
        mid = (A.foot[0], (A.foot[1] + A.base[1])/2, A.h/2)
        q = project(mid, dec, H)
        bx, by = A.base
        cross = (p[0] - bx)*(q[1] - by) - (p[1] - by)*(q[0] - bx)
        worst = max(worst, abs(cross)/hypot(p[0] - bx, p[1] - by))
print(f'أ: أقصى بعد لطرف الظل عن خط الساعة = {worst*1000:.3f} مم')
# (2) التصميم ب: الخط من موضع الوقوف إلى علامة الساعة يوازي ظل قائم رأسي
worst = 0
for dec in (-23.44, -10, 0, 10, 23.44):
    for H in (-75, -45, -15, 0, 20, 50, 80):
        E, N, U = sunvec(dec, H)
        if U <= 0.05: continue
        shadow = degrees(atan2(-E, -N))
        z = B.date_y(dec); hp = B.hour_point(H)
        line = degrees(atan2(hp[0], hp[1] - z))
        worst = max(worst, abs((shadow - line + 180) % 360 - 180))
print(f'ب: أقصى فرق زاوي بين الظل والعلامة = {worst:.5f}°')
# (3) التصميم ج: البقعة عند 12:00 بتوقيت مصر تقع شرق خط الزوال بمقدار فرق الطول ومعادلة الزمن
import datetime as dt
d = dt.date(2027, 2, 11); dec, eot, _ = sun_on(d)
H = H_from_clock(12, eot)
print(f'ج: 11 فبراير 12:00 → الزاوية الساعية {H:+.3f}° (المتوقع {(LON-30) + eot/4:+.3f}°)')
# (4) الحالات المرجعية: ارتفاع الشمس عند الظهر = 90 − |φ − δ|
for dec in (-23.44, 0, 23.44):
    alt, az = altaz(dec, 0)
    assert abs(alt - (90 - abs(LAT - dec))) < 1e-9
print('ارتفاع الزوال: صحيح')
