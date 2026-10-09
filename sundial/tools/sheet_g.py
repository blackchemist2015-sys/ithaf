"""اللوحات المشتركة: G-01 لوح معادلة الزمن ومواقيت الظهر والعصر، G-02 حلزون رأس السنة الهجرية والأحداث الفلكية، S-00 الموقع."""
from common import *
import base64, os


def g01():
    sh = Sheet()
    frame(sh, 'لوح معادلة الزمن ومواقيت الظهر والعصر', ['لوح برونزي للجمهور 1.60 × 1.00 م', 'مشترك بين التصاميم الثلاثة'], 'G-01', '1:4 للوح (على لوح A1)',
          'لوحات مشتركة',
          ['• الوقت الشمسي الحقيقي (المزولة) يسبق الساعة أو يتأخر',
           '   عنها لسببين: إهليلجية مدار الأرض، وميل محورها.',
           '• الفرق بينهما «معادلة الزمن» ويبلغ +16 و−14 دقيقة.',
           f'• فرق الطول: الفسطاط شرق خط 30° بـ {LON-30:.4f}°، أي',
           f'   {(LON-30)*4:.2f} دقيقة (مدمج في خطوط التصميمين أ وب).',
           '• القاعدة: الوقت الرسمي = وقت المزولة − معادلة الزمن',
           '   − فرق الطول (+ ساعة في التوقيت الصيفي).',
           '• المواقيت محسوبة لعرض 30.0054° وطول 31.2443°، والعصر',
           '   بظل المثل (الشافعي)، دون احتياط الدقائق المعتاد.',
           '• التوقيت الصيفي: من آخر جمعة في أبريل إلى آخر خميس',
           '   في أكتوبر (نظام 2023).',
           '• عرض المنحنى على مثال لوح حديقة بريمن النباتية',
           '   (Rohr، الفصل 9، لوحة 50): «المزولة متأخرة / متقدمة».'])
    # اللوح نفسه 1600×1000 مم بمقياس 1:4 => 400×250
    x0, y0, W, H = 300, 60, 400, 250
    sh.rect(x0, y0, W, H, fill='#d9b46a', sw=0.8, rx=3)
    sh.rect(x0 + 5, y0 + 5, W - 10, H - 10, fill='#f6ead0', sw=0.4, rx=2)
    for cx in (x0 + 18, x0 + W - 18):
        sh.poly(star_n(cx, y0 + 18, 9, 5.6, 8, 22.5), close=True, fill='#d9b46a', sw=0.3)
    sh.text(x0 + W/2, y0 + 18, 'معادلة الزمن: لماذا تختلف المزولة عن ساعتك؟', 8.5, 'middle', KUFI, '#5b3d16', 700)
    sh.text(x0 + W/2, y0 + 30, 'وقت مصر = وقت المزولة + تصحيح اليوم   (وأضف ساعة في التوقيت الصيفي)', 4.6, 'middle', NASKH, INK, 700)
    eot_graph(sh, x0 + 30, y0 + 48, W - 60, 120, title=False, fs=1.9, show_eot=False)
    sh.text(x0 + W/2, y0 + 42, 'التصحيح بالدقائق (لخطوط مصححة بفرق الطول)', 4.0, 'middle', SANS, TERRA, 700)
    sh.para(x0 + W - 12, y0 + 196, ['الأرض تسير حول الشمس في مدار إهليلجي فتسرع في يناير وتبطئ في يوليو،',
            'ومحورها مائل 23.44° فيتغير سير الشمس الظاهري على خط الاستواء السماوي.',
            'من الأمرين معًا ينشأ هذا المنحنى الذي يرسمه ظل الشمس على الأرض على هيئة الرقم ٨.'], 3.6, 1.55, NASKH, INK, 400)
    sh.ltr(x0 + 120, y0 + 236, 'EoT ≈ 9.87·sin 2B − 7.53·cos B − 1.5·sin B ,   B = 360°(N − 81)/365', 4.0, 'middle', SANS, '#5b3d16', 600)
    sh.text(x0 + W - 12, y0 + 236, 'الصيغة التقريبية (N رقم اليوم في السنة):', 3.4, 'end', NASKH, INK, 700)
    # جدول مواقيت الظهر والعصر
    tx, ty = 815, 335
    sh.text(tx, ty, 'مواقيت الشروق والظهر والعصر والغروب بتوقيت مصر (لموقع المزولة)', 4.0, 'end', KUFI, INK, 700)
    cols = ['التاريخ', 'الشروق', 'الظهر', 'العصر', 'الغروب', 'معادلة الزمن', 'التصحيح']
    cw = 92
    rows = []
    for m in range(1, 13):
        for d in (1, 15):
            dd = dt.date(REF_YEAR, m, d); dec, eot, _ = sun_on(dd); dst = egypt_dst(dd)
            rows.append((f'{d} {GREG_MONTHS[m-1]}' + (' ص' if dst else ''), fmt_hm(clock_from_H(-sunrise_H(dec), eot, dst=dst)),
                         fmt_hm(clock_from_H(0, eot, dst=dst)), fmt_hm(clock_from_H(asr_H(dec), eot, dst=dst)),
                         fmt_hm(clock_from_H(sunrise_H(dec), eot, dst=dst)), f'{eot:+.1f}', f'{-eot:+.1f}'))
    half = 12; colw = [22, 14, 13, 13, 14, 15, 14]
    for blk in range(2):
        bx = tx - blk*(sum(colw) + 12)*1.47
        xs = []; xx = bx
        for w in colw: xs.append(xx - w*1.47/2); xx -= w*1.47
        for j, cn in enumerate(cols): sh.text(xs[j], ty + 10, cn, 2.5, 'middle', SANS, INK, 700)
        for i, r in enumerate(rows[blk*half:(blk + 1)*half]):
            yy = ty + 17 + i*6.6
            if i % 2 == 0: sh.rect(xx, yy - 3.3, bx - xx, 6.6, fill='#f2ead8', sw=0)
            for j, val in enumerate(r):
                (sh.text if j == 0 else sh.ltr)(xs[j], yy, val, 2.5, 'middle', SANS, TEAL if j == 3 else (GOLD if j == 2 else INK), 600 if j in (2, 3) else 400)
    sh.text(tx, ty + 104, '«ص»: تاريخ يقع في التوقيت الصيفي (UTC+3). الدقائق مقربة؛ وتقويم الهيئة المصرية للمساحة يضيف احتياطًا يسيرًا.', 2.4, 'end', SANS, GREY)
    sh.text(tx, ty + 112, 'معادلة الزمن = الوقت الشمسي الحقيقي − الوقت المتوسط؛ والتصحيح = −معادلة الزمن (يُضاف إلى قراءة المزولة).', 2.4, 'end', SANS, GREY)
    return sh


def g02():
    sh = Sheet()
    frame(sh, 'رؤوس السنين والأحداث الفلكية', ['حلزون السنة الهجرية: 33 عامًا تدور فيها', '1 محرم على فصول السنة كلها'], 'G-02', '1:6 للقرص (على لوح A1)',
          'لوحات مشتركة',
          ['• السنة القمرية 354 يومًا فتتقدم 1 محرم نحو 11 يومًا كل',
           '   عام شمسي، فتدور على الفصول دورة كاملة في 33 عامًا.',
           '• القرص البرونزي (قطر 1.6 م) يرسم هذه الدورة حلزونًا:',
           '   الزاوية = موضع اليوم في السنة الشمسية (كحلقة المزولة)،',
           '   ونصف القطر يزيد عامًا بعد عام من 1448 إلى 1481هـ.',
           '• التواريخ بالتقويم الحسابي وقد تختلف يومًا عن الرؤية.',
           '• رأس السنة القبطية 1 توت = 11 سبتمبر (12 سبتمبر قبل',
           '   السنة الكبيسة)، ورأس السنة الميلادية 1 يناير، ورأس',
           '   السنة الفلكية دخول الشمس برج الحمل (الاعتدال الربيعي).',
           '• يوضع القرص على قاعدة منخفضة بجوار المزولة.'])
    v = View(400, 310, 6)
    c = v.p(0, 0); R0, R1 = 0.22, 0.74
    sh.circle(c, 0.80*v.k, fill='#d9b46a', sw=0.6)
    sh.circle(c, 0.77*v.k, fill='#f6ead0', sw=0.3)
    # أشهر حول القرص
    for m in range(12):
        th = ring_angle(dt.date(REF_YEAR, m + 1, 1))
        sh.line(polar(v, R0 - 0.03, th), polar(v, 0.77, th), stroke=GREY, sw=0.2)
        mid = ring_angle(dt.date(REF_YEAR, m + 1, 15))
        ring_text(sh, v, 0.755, mid, GREG_MONTHS[m], 4.2, KUFI, INK, 700)
    for ah in range(1448, 1482, 1):
        r = R0 + (ah - 1448)*(R1 - R0)/33
        sh.circle(c, r*v.k, stroke=GREY, sw=0.08, op=0.6)
    pts = []
    for ah in range(1448, 1482):
        d = hijri_new_year(ah)
        r = R0 + (ah - 1448)*(R1 - R0)/33
        pts.append((ah, d, polar(v, r, ring_angle(d))))
    # حلزون متصل (تقريب)
    path = []
    for i in range(len(pts) - 1):
        ah, d, _ = pts[i]; d2 = pts[i+1][1]
        t0 = ring_angle(d); t1 = ring_angle(d2)
        if t1 > t0: t1 -= 360
        for k in range(11):
            t = t0 + (t1 - t0)*k/10; r = R0 + (ah - 1448 + k/10)*(R1 - R0)/33
            path.append(polar(v, r, t))
    sh.poly(path, stroke=TERRA, sw=0.6)
    for ah, d, (x, y) in pts:
        sh.circle((x, y), 2.2, fill=TERRA if ah % 5 else GOLD, sw=0.2)
        if ah % 3 == 0 or ah in (1448, 1481):
            sh.text(x + 2.2, y - 2.2, f'{ar_digits(ah)}هـ: {ar_digits(d.day)} {GREG_MONTHS[d.month-1]} {ar_digits(d.year)}', 2.6, 'start', SANS, INK, 600)
    sh.poly(star_n(c[0], c[1], 9, 4.5, 8), close=True, fill=GOLD, sw=0.3)
    sh.text(c[0], c[1] - 0.86*v.k, 'حلزون رأس السنة الهجرية (1448–1481هـ)', 4.2, 'middle', KUFI, INK, 700)
    # جدول الأحداث الفلكية
    tx, ty = 815, 70
    sh.text(tx, ty, 'تقويم الأحداث الفلكية التي تظهر على المزولة', 4.0, 'end', KUFI, INK, 700)
    ev = []
    for y in (2027, 2028, 2029, 2030):
        for lam, nm in [(0, 'الاعتدال الربيعي (رأس الحمل)'), (90, 'الانقلاب الصيفي (أطول نهار)'), (180, 'الاعتدال الخريفي'), (270, 'الانقلاب الشتوي (أقصر نهار)')]:
            ev.append((date_of_longitude(lam, y), nm))
        for d, ut, dec in kaaba_transits(y):
            ev.append((d, f'تعامد الشمس على الكعبة {ar_digits(fmt_hm(ut + 3))} بتوقيت مصر الصيفي'))
        ev += [(dt.date(y, 2, 22), 'تعامد الشمس على وجه رمسيس الثاني بأبي سمبل'), (dt.date(y, 10, 22), 'تعامد الشمس على وجه رمسيس الثاني بأبي سمبل'),
               (coptic_new_year(y), 'رأس السنة القبطية: عيد النيروز (1 توت)'), (dt.date(y, 1, 1), 'رأس السنة الميلادية')]
        for ah in range(1448, 1453):
            hd = hijri_new_year(ah)
            if hd.year == y: ev.append((hd, f'رأس السنة الهجرية {ar_digits(ah)}هـ (حسابي ±1 يوم)'))
    ev.append((dt.date(2027, 8, 2), 'كسوف الشمس: كلي في الأقصر وجزئي عميق في القاهرة'))
    ev = sorted(e for e in ev if dt.date(2027, 1, 1) <= e[0] <= dt.date(2028, 12, 31))
    for i, (d, nm) in enumerate(ev):
        yy = ty + 10 + i*7.0
        if i % 2 == 0: sh.rect(tx - 300, yy - 3.5, 300, 7.0, fill='#f2ead8', sw=0)
        sh.ltr(tx - 3, yy, d.isoformat(), 2.6, 'end', SANS, INK, 600)
        sh.text(tx - 34, yy, nm, 2.6, 'end', SANS, INK)
    sh.text(tx, ty + 14 + len(ev)*7.0, 'الحساب لموقع المزولة؛ وأوقات الاعتدالين والانقلابين بالتاريخ المحلي.', 2.3, 'end', SANS, GREY)
    return sh


def s00(plan_png):
    sh = Sheet()
    frame(sh, 'موقع المزولة في المخطط العام', ['من لوحة فرش الأعمال الخارجية CD.H1.00.LS.04.02.04.01', 'وبيانات التوقيع الفلكي'], 'S-00', 'المخطط 1:250 مكبرًا',
          'الموقع والتوقيع',
          ['• المركز مقيس من شبكة الإحداثيات في اللوحة (الحزام الأحمر،',
           '   مصر 1907)، ويُراجع بالرفع المساحي قبل التنفيذ.',
           f'• خط العرض {LAT:.5f}° ش، وخط الطول {LON:.5f}° ق (WGS84).',
           f'• الشمال الحقيقي عند الموقع منحرف {GRID_CONV:.3f}° غربًا عن شمال',
           '   الشبكة: على طول 7.25 م يعادل ذلك 15 مم، فيُراعى.',
           '• توقيع خط الزوال: بجهاز GNSS أو المحطة الشاملة بالاتجاه',
           '   الحقيقي، ويُتحقق منه بظل شاخص رأسي عند الزوال',
           '   الحقيقي المحسوب لليوم (جدول G-01).',
           '• الوجه أفقي بميزان رقمي (±1 مم على 3 م).',
           '• الأبعاد: دائرة 14.50 م كما في المخطط (البند SF-12).'])
    data = base64.b64encode(open(plan_png, 'rb').read()).decode()
    sh.add(f'<image href="data:image/jpeg;base64,{data}" x="180" y="40" width="640" height="420" preserveAspectRatio="xMidYMid meet"/>')
    sh.rect(180, 40, 640, 420, sw=0.4)
    north_arrow(sh, 200, 485)
    # جدول
    tx, ty = 820, 480
    rows = [('القطر', '14.50 م'), ('مركز الدائرة E / N', '638413.3 / 810602.7'), ('خط العرض / الطول', f'{LAT:.5f}° / {LON:.5f}°'),
            ('فرق الطول عن خط 30°', f'{(LON-30)*4:.2f} دقيقة'), ('اتجاه القبلة', f'{qibla():.2f}° من الشمال الحقيقي'),
            ('تقارب الشبكة', f'{GRID_CONV:.4f}°')]
    for i, (k, val) in enumerate(rows):
        yy = ty + i*7
        sh.text(tx, yy, k, 2.8, 'end', SANS, GREY)
        sh.ltr(tx - 90, yy, val, 2.8, 'end', SANS, INK, 600)
    return sh


if __name__ == '__main__':
    g01().save('../drawings/svg/G-01.svg'); g02().save('../drawings/svg/G-02.svg')
    import sys
    if len(sys.argv) > 1: s00(sys.argv[1]).save('../drawings/svg/S-00.svg')
