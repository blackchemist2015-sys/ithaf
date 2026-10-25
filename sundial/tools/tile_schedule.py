"""جدول قطع الرخام والجرانيت: لكل قطعة شكلها والحفر الواقع عليها وكمياته، مع ملخص العدد."""
import re, csv, collections, html as H
import datetime as dt
from execA_geom import *
from common import *
import sheet_a
from shapely.geometry import Point, LineString
from shapely import affinity

OUT = '../execution_A'
G = GeoA()
K = 1000/30                                   # مم على لوحة A-01 لكل متر
VX = lambda x: 500 + x*K
VY = lambda y: 297 - y*K
MX = lambda X: (X - 500)/K
MY = lambda Y: (297 - Y)/K
FAM = collections.OrderedDict([('HOUR', 'ساعات 8'), ('HOUR30', 'أنصاف 4'), ('HOUR15', 'أرباع 2'), ('DECL', 'بروج نحاس'), ('MERID', 'زوال نحاس 30'),
                               ('ASR1', 'عصر 8'), ('ASR2', 'عصر ثانٍ 5'), ('NOON', 'منحنى 12'), ('QIBLA', 'قبلة 8'), ('TICKS', 'تدريج الأيام')])
RHO_M, RHO_G, T = 2700, 2650, 0.04


def face_svg():
    sh = sheet_a.a01()
    return sh, ''.join(sh.defs), '\n'.join(e for e in sh.els if not e.startswith('<image') and 'url(#gA)' not in e)


def texts(sh):
    out = []
    for e in sh.els:
        if not e.startswith('<text'): continue
        x = float(re.search(r' x="([-\d.]+)"', e).group(1)); y = float(re.search(r' y="([-\d.]+)"', e).group(1))
        t = H.unescape(re.sub(r'<[^>]+>', '', re.search(r'>(.*)</text>', e, re.S).group(1))).replace('⁦', '').replace('⁩', '').strip()
        if t: out.append((MX(x), MY(y), t))
    return out


def stars():
    A = G.A; out = []
    for d, ut, dec in kaaba_transits(REF_YEAR):
        _, eot, _ = sun(jd(d.year, d.month, d.day, ut)); Hh = 15*(ut + LON/15 + eot/60 - 12)
        out.append((*project(A.nodus, dec, Hh), 'نجمة الكعبة (مينا زرقاء Ø80)'))
    for d, lbl, col in SPECIAL:
        dec, eot, _ = sun_on(d); out.append((*project(A.nodus, dec, 0), 'نجمة يوم خاص (نحاس Ø60)'))
    return out


def ring_items():
    """عناصر حلقة التقويم بزاويتها: (الزاوية، النوع، النص)."""
    items = []
    d = dt.date(REF_YEAR, 1, 1)
    while d.year == REF_YEAR:
        items.append((ring_angle(d), 'tick1' if d.day == 1 else ('tick5' if d.day % 5 == 0 else 'tick'), ''))
        if d.day == 15: items.append((ring_angle(d), 'month', GREG_MONTHS[d.month - 1]))
        d += dt.timedelta(days=1)
    from common import COPTIC_STARTS
    for i, (m, dd) in enumerate(COPTIC_STARTS):
        s0 = dt.date(REF_YEAR, m, dd); items.append((ring_angle(s0), 'cbound', ''))
        items.append((ring_angle(s0 + dt.timedelta(days=15 if i < 12 else 2)), 'coptic', COPTIC_MONTHS[i]))
    for k in range(12):
        a0 = ring_angle(date_of_longitude(30*k)); a1 = ring_angle(date_of_longitude((30*k + 30) % 360))
        if a1 < a0: a1 += 360
        items += [(a0, 'zbound', ''), (((a0 + a1)/2) % 360, 'zodiac', 'برج ' + SIGNS[k])]
    for k in range(28):
        a0 = ring_angle(date_of_longitude(k*360/28)); a1 = ring_angle(date_of_longitude(((k + 1)*360/28) % 360))
        if a1 < a0: a1 += 360
        items += [(a0, 'mbound', ''), (((a0 + a1)/2) % 360, 'mansion', MANSIONS[k])]
    for dd, lbl in [(dt.date(REF_YEAR, 1, 1), 'رأس السنة الميلادية'), (dt.date(REF_YEAR, 9, 11), 'النيروز'), (date_of_longitude(0), 'الاعتدال الربيعي')]:
        items.append((ring_angle(dd), 'head', lbl))
    return items


def tile_rows():
    fams = G.families()
    lines = [(f, LineString(sg)) for f, l, segs, sp in fams for sg in segs if len(sg) > 1]
    tx = texts(face_svg()[0]); st = stars()
    rows = []
    for t in G.tiles():
        p = t['poly']; L = collections.OrderedDict((k, 0.0) for k in FAM)
        for f, ls in lines:
            i = ls.intersection(p)
            if not i.is_empty: L[f] += i.length
        ins = [s for x, y, s in tx if p.contains(Point(x, y))]
        sts = [s for x, y, s in st if p.contains(Point(x, y))]
        x0, y0, x1, y1 = p.bounds
        rows.append(dict(id=t['id'], kind='كاملة' if t['full'] else ('مقصوصة + مضمومة ' + t['merged'] if t['merged'] else 'مقصوصة'),
                         poly=p, w=(x1 - x0)*1000, h=(y1 - y0)*1000, area=p.area, kg=p.area*T*RHO_M, L=L, texts=ins, stars=sts,
                         slot=p.distance(Point(0, (G.yb + G.fy)/2)) < 0.03 and abs(p.bounds[0]) < 0.001 or abs(p.bounds[2]) < 0.001 and p.bounds[1] < G.fy))
    return rows


def ring_rows():
    items = ring_items()
    tx = texts(face_svg()[0])
    rows = []
    for r in G.ring_sectors():
        inside = lambda a: r['a0'] <= a % 360 < r['a1']
        cnt = collections.Counter(k for a, k, s in items if inside(a))
        names = [s for a, k, s in items if inside(a) and s]
        p = r['poly']; x0, y0, x1, y1 = p.bounds
        rows.append(dict(id=r['id'], poly=p, a0=r['a0'], a1=r['a1'], area=p.area, kg=p.area*T*RHO_G,
                         ticks=cnt['tick'] + cnt['tick5'] + cnt['tick1'], t1=cnt['tick1'], names=names, heads=[s for a, k, s in items if inside(a) and k == 'head']))
    return rows


def fmt(v): return f'{v:.2f}'


def page(defs, content, cells, title, pno, ptot):
    W, Hh = 420, 297
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}mm" height="{Hh}mm" viewBox="0 0 {W} {Hh}">',
         f'<defs>{defs}<g id="F">{content}</g></defs><rect width="{W}" height="{Hh}" fill="#fffdf8"/>',
         '<rect x="6" y="6" width="408" height="285" fill="none" stroke="#1d1b19" stroke-width="0.5"/>']
    sh = Sheet(W, Hh); sh.els = []
    sh.text(410, 14, title, 5, 'end', KUFI, INK, 700)
    sh.text(410, 21, 'مزولة الفسطاط — التصميم (أ) • جدول قطع الحجر وحفرها • الرسم بمقياس 1:16 للبلاط و1:25 للحلقة', 2.8, 'end', SANS, GREY)
    sh.ltr(12, 14, f'X-08 / {pno} of {ptot}', 3.2, 'start', SANS, INK, 700)
    s += sh.els
    s += cells
    s.append('</svg>')
    return '\n'.join(s)


def cell(i, r, scale_mm_per_m, ring=False):
    col, row = i % 4, i//4
    cx0, cy0, cw, chh = 10 + (3 - col)*100, 27 + row*88, 100, 88       # من اليمين لليسار
    box = 56.0
    p = r['poly']; x0, y0, x1, y1 = p.bounds
    cxm, cym = (x0 + x1)/2, (y0 + y1)/2
    scale_mm_per_m = min(scale_mm_per_m, (box - 2)/max(x1 - x0, y1 - y0))
    half = box/scale_mm_per_m/2                                       # بالمتر
    vbx, vby = VX(cxm - half), VY(cym + half); vbw = 2*half*K
    dx, dy = cx0 + 4, cy0 + 6
    cid = f'c{r["id"]}'
    path = ' '.join(('M' if j == 0 else 'L') + f'{VX(x):.2f},{VY(y):.2f}' for j, (x, y) in enumerate(p.exterior.coords)) + ' Z'
    out = [f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{chh}" fill="none" stroke="#cbbfa8" stroke-width="0.3"/>',
           f'<svg x="{dx}" y="{dy}" width="{box}" height="{box}" viewBox="{vbx:.2f} {vby:.2f} {vbw:.2f} {vbw:.2f}">',
           f'<clipPath id="{cid}"><path d="{path}"/></clipPath><path d="{path}" fill="#f3eee3"/>',
           f'<g clip-path="url(#{cid})"><use href="#F"/></g>',
           f'<path d="{path}" fill="none" stroke="#b4532a" stroke-width="{0.6*vbw/box:.3f}"/>']
    if not ring:
        out.append(f'<circle cx="{VX(r["ox"]):.2f}" cy="{VY(r["oy"]):.2f}" r="{1.2*vbw/box:.2f}" fill="#c0392b"/>')
    out.append('</svg>')
    sh = Sheet(); sh.els = []
    tx = cx0 + cw - 3; y = cy0 + 8
    sh.text(tx, y, r['id'], 6, 'end', KUFI, TERRA, 700); y += 7
    if ring:
        sh.text(tx, y, f'جرانيت 40 مم • قطاع {r["a0"]:.0f}°–{r["a1"]:.0f}°', 2.4, 'end', SANS, INK); y += 4.5
        sh.text(tx, y, f'{r["area"]:.3f} م² • {r["kg"]:.0f} كجم', 2.4, 'end', SANS, INK); y += 4.5
        sh.text(tx, y, f'حزوز الأيام: {r["ticks"]} (منها {r["t1"]} رأس شهر)', 2.3, 'end', SANS, INK); y += 4.3
        names = r['names']
        for k in range(0, min(len(names), 8), 2):
            sh.text(tx, y, '، '.join(names[k:k + 2]), 2.2, 'end', NASKH, INK, 700); y += 4
        if len(names) > 8: sh.text(tx, y, f'+{len(names) - 8} نصوص أخرى', 2.1, 'end', SANS, GREY); y += 4
        if r['heads']: sh.text(tx, y, 'نجمة ذهبية: ' + '، '.join(r['heads']), 2.2, 'end', SANS, TERRA, 700)
    else:
        sh.text(tx, y, r['kind'], 2.5, 'end', SANS, INK, 700); y += 4.5
        sh.ltr(tx, y, f'{r["w"]:.0f} × {r["h"]:.0f} mm', 2.5, 'end', SANS, INK, 600); y += 4.3
        sh.text(tx, y, f'{r["area"]:.3f} م² • {r["kg"]:.0f} كجم', 2.4, 'end', SANS, INK); y += 4.8
        for k, v in r['L'].items():
            if v > 0.005:
                sh.text(tx, y, FAM[k], 2.2, 'end', SANS, INK); sh.ltr(tx - 24, y, f'{v:.2f} m', 2.2, 'end', SANS, INK, 600); y += 3.7
        if r['stars']:
            for s_ in r['stars']: sh.text(tx, y, s_, 2.1, 'end', SANS, BLUE, 700); y += 3.7
        tt = r['texts']
        if tt:
            nums = [t for t in tt if re.fullmatch('[٠-٩]+', t)]
            other = [t for t in tt if t not in nums]
            if nums: sh.text(tx, y, 'قرص رقم الساعة: ' + '، '.join(nums), 2.1, 'end', SANS, TERRA, 700); y += 3.7
            if other: sh.text(tx, y, f'نصوص محفورة: {len(other)}', 2.1, 'end', SANS, GREY); y += 3.7
    return out + sh.els


def summary(tiles, rings):
    sh = Sheet(420, 297); sh.els = []
    sh.rect(6, 6, 408, 285, sw=0.5)
    sh.text(410, 16, 'جدول قطع الحجر وحفرها — الملخص والعدد', 6, 'end', KUFI, INK, 700)
    sh.text(410, 24, 'مزولة الفسطاط — التصميم (أ) • يُقرأ مع X-02 وX-03 وملفات dxf/tiles', 2.8, 'end', SANS, GREY)
    sh.ltr(12, 14, 'X-08 / 1', 3.2, 'start', SANS, INK, 700)
    full = [t for t in tiles if t['kind'] == 'كاملة']; cut = [t for t in tiles if t['kind'] != 'كاملة']
    rows = [('بلاط رخام كامل 900 × 900 × 40', f'{len(full)}', f'{sum(t["area"] for t in full):.2f}', f'{sum(t["kg"] for t in full):.0f}'),
            ('بلاط رخام مقصوص بحد الدائرة أو شق النصل', f'{len(cut)}', f'{sum(t["area"] for t in cut):.2f}', f'{sum(t["kg"] for t in cut):.0f}'),
            ('مجموع بلاط الوجه', f'{len(tiles)}', f'{sum(t["area"] for t in tiles):.2f}', f'{sum(t["kg"] for t in tiles):.0f}'),
            ('قطاعات جرانيت حلقة التقويم (شكل واحد)', f'{len(rings)}', f'{sum(r["area"] for r in rings):.2f}', f'{sum(r["kg"] for r in rings):.0f}')]
    from exec_sheets import table
    table(sh, 410, 38, ['القطعة', 'العدد', 'المساحة م²', 'الوزن كجم'], rows, [90, 22, 28, 28], 2.8, 7.5, ltr_cols=(1, 2, 3))
    tot = collections.OrderedDict((k, sum(t['L'][k] for t in tiles)) for k in FAM)
    spec = {'HOUR': 'راتنج أسود 8 مم', 'HOUR30': 'راتنج أسود 4 مم', 'HOUR15': 'راتنج رمادي 2 مم', 'DECL': 'نحاس 5–8 مم', 'MERID': 'نحاس 30 مم',
            'ASR1': 'راتنج فيروزي 8 مم', 'ASR2': 'راتنج فيروزي 5 مم', 'NOON': 'راتنج بنفسجي 5 مم', 'QIBLA': 'راتنج أزرق 8 مم', 'TICKS': 'نحاس 3 مم'}
    rows2 = [(FAM[k], spec[k], f'{v:.1f}', f'{sum(1 for t in tiles if t["L"][k] > 0.005)}') for k, v in tot.items()]
    table(sh, 410, 90, ['خطوط الحفر', 'التطعيم', 'الطول م', 'عدد البلاطات'], rows2, [40, 50, 22, 24], 2.7, 7, ltr_cols=(2, 3))
    nums = sum(sum(1 for x in t['texts'] if re.fullmatch('[٠-٩]+', x)) for t in tiles)
    sts = collections.Counter(s for t in tiles for s in t['stars'])
    ticks = sum(r['ticks'] for r in rings); names = sum(len(r['names']) for r in rings)
    rows3 = [('أقراص أرقام الساعات نحاس Ø150', f'{nums}')] + [(k, f'{v}') for k, v in sts.items()] + \
            [('حزوز أيام السنة على الحلقة', f'{ticks}'), ('نصوص الحلقة (أشهر، قبطي، بروج، منازل، رؤوس السنين)', f'{names}'),
             ('نجوم رؤوس السنين الذهبية على الحلقة', '3'), ('لوح معادلة الزمن ونص الإرشاد (حفر 3 مم)', 'على البلاطات المبينة')]
    table(sh, 410, 180, ['عناصر التطعيم', 'العدد'], rows3, [110, 40], 2.7, 7)
    sh.para(220, 38, ['## ملاحظات التصنيع',
        '• لكل قطعة ملف قص وحفر: dxf/tiles/<الرقم>.dxf (الأصل الركن الجنوبي الغربي للمربع،',
        '   والنقطة الحمراء في الرسم هي هذا الأصل).',
        '• البلاط المقصوص كله فريد الحفر: لا تُبدَّل قطعة بأخرى ولو تشابه الشكل.',
        '• ضُمت 8 شرائح صغيرة (0.027 م²) عند أطراف المحورين إلى جاراتها',
        '   (B08 وB09 وH02 وI02 وH15 وI15 وO08 وO09) فصارت قطعة واحدة.',
        '• يُكتب رقم القطعة على ظهرها، ويُضاف 12% هالكًا للرخام و8% للجرانيت.',
        '• البلاطة الكاملة ≈ 87 كجم: تُرفع بماسك شفط أو بعاملين.',
        '• الخطوط تُحفر بالـ CNC قبل التركيب؛ أما أقراص الأرقام والنجوم',
        '   والنصوص العابرة للفواصل فتُطعّم بعد التركيب بقوالب.',
        '• عمق الحفر 6 مم لكل الخطوط، و3 مم للنصوص.',
        '• النقش الهندسي الخفيف في خلفية A-01 زخرفي اختياري، ولا يدخل في هذه الكميات.'], 2.6, 1.7)
    # مسقط مفتاحي
    k = 9.5; ox, oy = 110, 215
    P = lambda x, y: (ox + x*k, oy - y*k)
    sh.circle(P(0, 0), R_RING*k, fill='#e9e1cf', sw=0.3)
    for r in rings:
        sh.poly([P(x, y) for x, y in r['poly'].exterior.coords], close=True, stroke=GREY, sw=0.15)
    for t in tiles:
        sh.poly([P(x, y) for x, y in t['poly'].exterior.coords], close=True, fill='#f8f4ea' if t['kind'] == 'كاملة' else '#f3d9c9', stroke=GREY, sw=0.15)
        c = t['poly'].representative_point(); sh.ltr(*P(c.x, c.y), t['id'], 1.5, 'middle', SANS, INK, 600)
    sh.line(P(0, G.yb), P(0, G.fy), stroke=INK, sw=0.8)
    sh.text(ox, oy - R_RING*k - 4, 'مسقط مفتاحي (الشمال إلى أعلى) — الملوّن: مقصوص', 2.6, 'middle', KUFI, INK, 700)
    return sh.svg()


def build():
    sh, defs, content = face_svg()
    tiles = tile_rows()
    for t, g in zip(tiles, G.tiles()):
        t['ox'], t['oy'] = g['origin']
    order = sorted(tiles, key=lambda t: (t['id'][0], t['id'][1:]))
    rings = ring_rows()
    pages = [summary(tiles, rings)]
    tp = [order[i:i + 12] for i in range(0, len(order), 12)]
    rp = [rings[i:i + 12] for i in range(0, len(rings), 12)]
    ptot = 1 + len(tp) + len(rp)
    for n, grp in enumerate(tp):
        cells = sum((cell(i, r, 1000/16) for i, r in enumerate(grp)), [])
        pages.append(page(defs, content, cells, f'بلاط الوجه {grp[0]["id"]} – {grp[-1]["id"]}', n + 2, ptot))
    for n, grp in enumerate(rp):
        cells = sum((cell(i, r, 1000/25, ring=True) for i, r in enumerate(grp)), [])
        pages.append(page(defs, content, cells, f'قطاعات الحلقة {grp[0]["id"]} – {grp[-1]["id"]}', len(tp) + n + 2, ptot))
    import os; os.makedirs(f'{OUT}/schedule', exist_ok=True)
    for i, pg in enumerate(pages):
        open(f'{OUT}/schedule/X-08_{i+1:02d}.svg', 'w', encoding='utf-8').write(pg)
    with open(f'{OUT}/csv/X08_stone_schedule.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['piece', 'material', 'type', 'bbox_w_mm', 'bbox_h_mm', 'area_m2', 'weight_kg'] + [f'len_{k}_m' for k in FAM] + ['hour_numerals', 'stars', 'other_texts', 'dxf_file'])
        for t in order:
            nums = [x for x in t['texts'] if re.fullmatch('[٠-٩]+', x)]
            w.writerow([t['id'], 'رخام جلالة 40', t['kind'], f'{t["w"]:.0f}', f'{t["h"]:.0f}', f'{t["area"]:.4f}', f'{t["kg"]:.1f}'] +
                       [f'{t["L"][k]:.3f}' for k in FAM] + [' '.join(nums), ' | '.join(t['stars']), len(t['texts']) - len(nums), f'dxf/tiles/{t["id"]}.dxf'])
        for r in rings:
            x0, y0, x1, y1 = r['poly'].bounds
            w.writerow([r['id'], 'جرانيت رمادي 40', f'قطاع {r["a0"]:.0f}-{r["a1"]:.0f}°', f'{(x1-x0)*1000:.0f}', f'{(y1-y0)*1000:.0f}', f'{r["area"]:.4f}', f'{r["kg"]:.1f}'] +
                       ['']*len(FAM) + ['', ' | '.join(r['heads']), f'{r["ticks"]} ticks; ' + ' / '.join(r['names']), 'dxf/A_face.dxf (CUT layer)'])
    print(len(pages), 'pages')


if __name__ == '__main__':
    build()
