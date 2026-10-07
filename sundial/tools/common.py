"""عناصر مشتركة بين اللوحات: حلقة التقويم، النقش الهندسي، التواريخ الخاصة."""
from dials import *
from svg import *
import datetime as dt

WS = dt.date(REF_YEAR - 1, 12, 22)          # الانقلاب الشتوي: صفر الحلقة (الشمال)
YEAR_LEN = 365.2422

COPTIC_STARTS = [(9, 11), (10, 11), (11, 10), (12, 10), (1, 9), (2, 8), (3, 10), (4, 9), (5, 9), (6, 8), (7, 8), (8, 7), (9, 6)]


def ring_angle(date):
    """زاوية التاريخ على حلقة التقويم: الانقلاب الشتوي شمالًا ثم مع عقارب الساعة."""
    d = dt.date(REF_YEAR, date.month, date.day)
    return ((d - WS).days % 365.2422) / YEAR_LEN * 360


def polar(view, r, th):
    return view.p(r*sin(rad(th)), r*cos(rad(th)))


def arc_d(view, r, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0)/1.5))
    return view.d([(r*sin(rad(a0 + (a1 - a0)*i/n)), r*cos(rad(a0 + (a1 - a0)*i/n))) for i in range(n + 1)])


def ring_text(sh, view, r, th, s, size, font=SANS, fill=INK, weight=400):
    x, y = polar(view, r, th)
    rot = th if (th % 360) < 90 or (th % 360) > 270 else th + 180
    sh.text(x, y, s, size, 'middle', font, fill, weight, rot)


def girih_pattern(sh, pid, tile_mm, color=GOLD, op=0.22, sw=0.18):
    """نقش النجمة الثمانية والصليب (نقش مملوكي) كنمط SVG."""
    t = tile_mm; c = t/2
    st = star_n(c, c, t/2, t/2*0.62, 8, 22.5)
    d = ' '.join(('M' if i == 0 else 'L') + f(x) + ',' + f(y) for i, (x, y) in enumerate(st)) + ' Z'
    inner = star_n(c, c, t*0.2, t*0.2*0.7654, 8, 0)
    d2 = ' '.join(('M' if i == 0 else 'L') + f(x) + ',' + f(y) for i, (x, y) in enumerate(inner)) + ' Z'
    sh.defs.append(f'<pattern id="{pid}" width="{f(t)}" height="{f(t)}" patternUnits="userSpaceOnUse">'
                   f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op}"/>'
                   f'<path d="{d2}" fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op*0.8}"/></pattern>')


def calendar_ring(sh, view, r_in, r_out, labels_out=True):
    """حلقة التقويم: الأشهر الميلادية والقبطية والبروج ومنازل القمر ورؤوس السنين."""
    w = r_out - r_in
    r_tick = r_out - 0.16*w; r_g = r_out - 0.32*w; r_gc = (r_tick + r_g)/2 - 0.02*w
    b1 = r_out - 0.42*w; b2 = r_out - 0.66*w; b3 = r_out - 0.86*w
    sh.path(view.d([(r_out*sin(rad(a)), r_out*cos(rad(a))) for a in range(0, 361, 2)]), fill='#efe5cf', sw=0)
    sh.path(view.d([(r_in*sin(rad(a)), r_in*cos(rad(a))) for a in range(0, 361, 2)]), fill='#fbf7ee', sw=0)
    for r, sw in [(r_out, 0.6), (r_tick, 0.2), (b1, 0.3), (b2, 0.3), (b3, 0.3), (r_in, 0.6)]:
        sh.circle(view.p(0, 0), r*view.k, sw=sw)
    # الأيام
    d = dt.date(REF_YEAR, 1, 1)
    while d.year == REF_YEAR:
        th = ring_angle(d)
        L = 0.16*w if d.day == 1 else (0.10*w if d.day % 5 == 0 else 0.05*w)
        sh.line(polar(view, r_out, th), polar(view, r_out - L, th), sw=0.3 if d.day == 1 else 0.15)
        if d.day == 1:
            sh.line(polar(view, r_out, th), polar(view, b1, th), sw=0.35)
            mid = ring_angle(d + dt.timedelta(days=15))
            ring_text(sh, view, (r_tick + b1)/2, mid, GREG_MONTHS[d.month - 1], w*0.16*view.k, KUFI, INK, 700)
        d += dt.timedelta(days=1)
    # الأشهر القبطية
    starts = [dt.date(REF_YEAR, m, dd) for m, dd in COPTIC_STARTS]
    for i, s0 in enumerate(starts):
        th = ring_angle(s0); sh.line(polar(view, b1, th), polar(view, b2, th), sw=0.3)
        ln = 30 if i < 12 else 5
        mid = ring_angle(s0 + dt.timedelta(days=ln/2))
        ring_text(sh, view, (b1 + b2)/2, mid, COPTIC_MONTHS[i], w*(0.15 if i < 12 else 0.08)*view.k, NASKH, TERRA, 700)
    # البروج
    for k in range(12):
        lam = 30*k; d0 = date_of_longitude(lam); d1 = date_of_longitude((lam + 30) % 360)
        th0 = ring_angle(d0); th1 = ring_angle(d1)
        if th1 < th0: th1 += 360
        sh.line(polar(view, b2, th0), polar(view, b3, th0), sw=0.3)
        ring_text(sh, view, (b2 + b3)/2, (th0 + th1)/2, 'برج ' + SIGNS[k], w*0.13*view.k, KUFI, BLUE, 700)
    # منازل القمر (اصطلاح ابتداء الشرطين من رأس الحمل)
    for k in range(28):
        lam = k*360/28
        d0 = date_of_longitude(lam); d1 = date_of_longitude((lam + 360/28) % 360)
        th0 = ring_angle(d0); th1 = ring_angle(d1)
        if th1 < th0: th1 += 360
        sh.line(polar(view, b3, th0), polar(view, r_in, th0), sw=0.2)
        ring_text(sh, view, (b3 + r_in)/2, (th0 + th1)/2, MANSIONS[k], w*0.085*view.k, NASKH, GREY, 400)
    # رؤوس السنين
    eq = date_of_longitude(0)
    heads = [(dt.date(REF_YEAR, 1, 1), 'رأس السنة الميلادية', '١ يناير'),
             (dt.date(REF_YEAR, 9, 11), 'رأس السنة القبطية (النيروز)', '١ توت = ١١ سبتمبر'),
             (eq, 'رأس السنة الفلكية: الاعتدال الربيعي', 'دخول الشمس برج الحمل')]
    for d, a, b in heads:
        th = ring_angle(d)
        x, y = polar(view, r_out - 0.08*w, th)
        sh.poly(star_n(x, y, w*0.16*view.k, w*0.16*view.k*0.55, 8, th), close=True, fill=GOLD, stroke=INK, sw=0.2)
        if labels_out:
            x2, y2 = polar(view, r_out + 0.55, th)
            sh.line(polar(view, r_out + 0.03, th), polar(view, r_out + 0.32, th), stroke=GOLD, sw=0.5)
            sh.text(x2, y2 - 2.0, a, 2.9, 'middle', KUFI, TERRA, 700)
            sh.text(x2, y2 + 2.4, b, 2.5, 'middle', SANS, INK)
    return heads


SPECIAL = [
    (dt.date(REF_YEAR, 1, 1), 'رأس السنة الميلادية', PURPLE),
    (dt.date(REF_YEAR, 9, 11), 'النيروز: ١ توت', PURPLE),
    (dt.date(REF_YEAR, 2, 22), 'تعامد الشمس على أبي سمبل ٢٢ فبراير', RED),
    (dt.date(REF_YEAR, 10, 22), 'تعامد الشمس على أبي سمبل ٢٢ أكتوبر', RED),
]


def fmt_hm(t):
    t = t % 24; h = int(t); m = int(round((t - h)*60))
    if m == 60: h += 1; m = 0
    return f'{h:02d}:{m:02d}'


def eot_graph(sh, x0, y0, w, h, title=True, fs=1.0, show_eot=False, color=TERRA):
    """منحنى التصحيح: الدقائق التي تُضاف إلى قراءة المزولة (= −معادلة الزمن). x0,y0 الركن الأيسر الأعلى (مم)."""
    days = year_days()
    lo, hi = -18, 16
    X = lambda doy: x0 + w*doy/365
    Y = lambda m: y0 + h*(hi - m)/(hi - lo)
    sh.rect(x0, y0, w, h, fill='#fffaf0', sw=0.4*fs)
    for m in range(lo, hi + 1, 2):
        sh.line((x0, Y(m)), (x0 + w, Y(m)), stroke=GREY if m % 10 else INK, sw=(0.25 if m == 0 else (0.12 if m % 10 else 0.18))*fs, op=0.7)
        if m % 4 == 0:
            sh.ltr(x0 - 1.2*fs, Y(m), f'{m:+d}' if m else '0', 2.1*fs, 'end', SANS, INK)
    doy = 0
    for i in range(12):
        sh.line((X(doy), y0), (X(doy), y0 + h), stroke=GREY, sw=0.15*fs)
        nd = (dt.date(REF_YEAR + (i == 11), (i + 1) % 12 + 1, 1) - dt.date(REF_YEAR, i + 1, 1)).days
        sh.text(X(doy + nd/2), y0 + h + 3*fs, GREG_MONTHS[i], 2.2*fs, 'middle', SANS, INK)
        sh.text(X(doy + nd/2), y0 + h + 6.2*fs, COPTIC_MONTHS[(i + 4) % 12] + '…', 1.7*fs, 'middle', NASKH, GREY)
        for k in range(1, nd + 1, 5) if False else []: pass
        doy += nd
    pts = [(X(i), Y(-e)) for i, (d, dec, e, lam) in enumerate(days)]
    sh.poly(pts, stroke=color, sw=0.9*fs)
    if show_eot:
        sh.poly([(X(i), Y(e)) for i, (d, dec, e, lam) in enumerate(days)], stroke=BLUE, sw=0.5*fs, dash='1.5 1')
    # القيم القصوى
    ext = []
    for i in range(1, 364):
        a, b, c = days[i-1][2], days[i][2], days[i+1][2]
        if (b > a and b > c) or (b < a and b < c): ext.append(i)
    for i in ext:
        d, dec, e, lam = days[i]
        x, y = X(i), Y(-e)
        sh.circle((x, y), 0.7*fs, fill=color, sw=0)
        sh.text(x, y + (-3*fs if -e > 0 else 3.2*fs), f'{ar_digits(d.day)} {GREG_MONTHS[d.month-1]}: {ar_digits(f"{-e:+.0f}")} د', 1.9*fs, 'middle', SANS, INK, 600)
    for i in range(1, 365):
        if days[i-1][2]*days[i][2] < 0:
            sh.circle((X(i), Y(0)), 0.6*fs, fill=INK, sw=0)
    if title:
        sh.text(x0 + w, y0 - 4*fs, 'معادلة الزمن: ما يُضاف إلى قراءة المزولة (دقائق)', 2.9*fs, 'end', KUFI, INK, 700)
        sh.text(x0, y0 - 4*fs, 'ويُزاد ٦٠ دقيقة في التوقيت الصيفي', 2.1*fs, 'start', SANS, GREY)
    return X, Y
