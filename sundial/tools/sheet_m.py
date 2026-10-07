"""M-01: من المخطوط إلى الحساب — شفاء الأسقام في وضع الساعات على الرخام لابن الصوفي."""
from common import *
import base64, sys
from math import degrees as deg

EPS_MS = 23 + 35/60          # الميل الكلي في المخطوط (23;35)
ABJAD = ['ا', 'ب', 'ج', 'د', 'ه', 'و', 'ز', 'ح', 'ط', 'ي', 'يا']


def alt(dec, H, lat=30.0):
    return deg(asin(sin(rad(lat))*sin(rad(dec)) + cos(rad(lat))*cos(rad(dec))*cos(rad(H))))


def sexa(x):
    d = int(x); m = int(round((x - d)*60))
    if m == 60: d += 1; m = 0
    return f'{d};{m:02d}'


def m01(imgs):
    sh = Sheet()
    frame(sh, 'من المخطوط إلى الحساب', ['شفاء الأسقام في وضع الساعات على الرخام', 'لشهاب الدين أحمد بن الصوفي'], 'M-01', 'بلا مقياس',
          'المرجع التراثي',
          ['• المخطوط القاهري يرسم «البسيطة» (المزولة الأفقية) لعرض «ل» = 30°،',
           '   وهو عرض الفسطاط، بالساعات المستوية والزمانية، ويضع جداول',
           '   الارتفاع والسمت والظل لكل ساعة في مداري السرطان والجدي،',
           '   ثم جداول المنحرفات والقائمات والرخامة الموازية لمعدل النهار.',
           '• أعدنا حساب جدول البسيطة بالمعادلات الحديثة على الميل الكلي',
           '   الذي استعمله المؤلف (23;35)، فجاءت الفروق دقائق قليلة.',
           '• منه أخذنا: عرض 30° ومنهجه في البسيطة (التصميم أ)،',
           '   والرخامة الموازية لمعدل النهار (التصميم د)، وتسمية دوائر',
           '   البروج على الطرفين، وخطّي العصر.',
           '• القراءة من مصوّرة مضغوطة؛ وما لم تتضح دقائقه تُرك بشرطة.'])
    # صور المخطوط
    xs = [(175, 'الصورة البسيطة لعرض ل — ساعات مستوية (ص 13)', imgs[0], 200, 250),
          (390, 'جدول البسيطة لعرض ل — ساعات مستوية (ص 12)', imgs[1], 200, 250),
          (605, 'صنعة الرخامة الموازية لمعدل النهار (ص 251)', imgs[2], 220, 250)]
    for x, cap, path, w, h in xs:
        data = base64.b64encode(open(path, 'rb').read()).decode()
        sh.add(f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="40" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>')
        sh.text(x + w/2, 296, cap, 2.6, 'middle', SANS, INK, 600)
    # إعادة رسم البسيطة على هيئة المخطوط
    v = View(320, 440, 1/ (60/1000))   # العقدة بارتفاع وحدة واحدة = 60 مم
    k = 60.0
    nod = (0, 0, 1.0)
    def proj(dec, H):
        E, N, U = sunvec(dec, H, 30.0)
        if U <= 0.05: return None
        return (-E/U, -N/U)
    P = lambda p: (320 + p[0]*k, 470 - p[1]*k)
    sh.text(320, 312, 'إعادة الرسم بالحساب: بسيطة لعرض 30° على ميل 23;35', 3.4, 'middle', KUFI, INK, 700)
    box = (175, 320, 290, 250)
    sh.rect(*box, fill='#f6ead0', sw=0.5)
    def clipbox(pts):
        segs, cur = [], []
        for p in pts:
            if p and box[0] + 3 < P(p)[0] < box[0] + box[2] - 3 and box[1] + 3 < P(p)[1] < box[1] + box[3] - 3: cur.append(P(p))
            else:
                if len(cur) > 1: segs.append(cur)
                cur = []
        if len(cur) > 1: segs.append(cur)
        return segs
    for dec, col, w in [(EPS_MS, TERRA, 0.8), (0, GOLD, 0.8), (-EPS_MS, TERRA, 0.8)]:
        H0 = deg(acos(-tan(rad(30))*tan(rad(dec))))
        for s in clipbox([proj(dec, H) for H in frange(-H0 + 1, H0 - 1, 0.5)]): sh.poly(s, stroke=col, sw=w)
    for q in range(-6, 7):
        H = 15*q
        pts = [proj(d, H) if abs(H) < deg(acos(-tan(rad(30))*tan(rad(d)))) else None for d in frange(-EPS_MS, EPS_MS, 0.5)]
        for s in clipbox(pts):
            sh.poly(s, stroke=INK, sw=0.5)
        end = [p for p in pts if p]
        if end:
            x, y = P(end[0])
            if box[1] < y < box[1] + box[3] and box[0] < x < box[0] + box[2]:
                sh.text(x, y + 4, ar_digits((12 + q) % 12 or 12), 3.4, 'middle', KUFI, INK, 700)
    for kk in range(1, 12):
        pts = []
        for d in frange(-EPS_MS, EPS_MS, 0.5):
            H0 = deg(acos(-tan(rad(30))*tan(rad(d))))
            pts.append(proj(d, -H0 + kk*2*H0/12))
        for s in clipbox(pts): sh.poly(s, stroke=RED, sw=0.35, dash='1.4 0.9')
        if pts[-1]:
            x, y = P(pts[-1])
            if box[1] + 6 < y - 4 < box[1] + box[3] and box[0] < x < box[0] + box[2]: sh.text(x, y - 4, ABJAD[kk - 1], 2.8, 'middle', NASKH, RED, 700)
    sh.circle(P((0, 0)), 1.2, fill=INK)
    sh.text(box[0] + box[2] - 4, box[1] + box[3] - 5, 'الأسود: مستوية (أرقام هندية) • الأحمر المتقطع: زمانية (أبجد)', 2.2, 'end', SANS, INK)
    sh.text(box[0] + box[2] - 4, box[1] + 6, 'مدار الجدي', 2.4, 'end', NASKH, TERRA, 700)
    sh.text(box[0] + box[2] - 4, P((0, proj(EPS_MS, 0)[1]))[1] + 6, 'مدار السرطان', 2.4, 'end', NASKH, TERRA, 700)
    # جدول المطابقة
    tx, ty = 828, 318
    sh.text(tx, ty, 'مطابقة جدول البسيطة (ارتفاع الشمس بالدرج;الدقائق)', 3.4, 'end', KUFI, INK, 700)
    def srH(d): return deg(acos(-tan(rad(30))*tan(rad(d))))
    rows = [('السرطان: الساعة ١ من الشروق', 'يا نا', '11;51', alt(EPS_MS, -srH(EPS_MS) + 15)),
            ('السرطان: الساعة ٣', 'لو نط', '36;59', alt(EPS_MS, -srH(EPS_MS) + 45)),
            ('السرطان: الساعة ٥', 'سب نا', '62;51', alt(EPS_MS, -srH(EPS_MS) + 75)),
            ('السرطان: نصف النهار', 'فج', '83;—', 90 - (30 - EPS_MS)),
            ('السرطان: أول العصر', 'ما', '41;—', deg(atan(1/(1 + tan(rad(30 - EPS_MS)))))),
            ('الجدي: نصف النهار', 'لو كه', '36;25', 90 - (30 + EPS_MS)),
            ('الجدي: أول العصر', 'كج', '23;—', deg(atan(1/(1 + tan(rad(30 + EPS_MS))))))]
    cols = ['البند', 'في المخطوط', 'بالأرقام', 'حسابنا (23;35)', 'حسابنا (الميل الحالي)']
    cx = [tx, tx - 70, tx - 105, tx - 140, tx - 185]
    for j, c in enumerate(cols): sh.text(cx[j], ty + 10, c, 2.4, 'end', SANS, GREY, 700)
    for i, (lbl, ab, num, val) in enumerate(rows):
        yy = ty + 18 + i*8
        if i % 2 == 0: sh.rect(tx - 235, yy - 4, 235, 8, fill='#f2ead8', sw=0)
        # القيمة بالميل الحالي
        e2 = OBLIQUITY
        if 'الساعة' in lbl:
            hh = int({'١': 1, '٣': 3, '٥': 5}[lbl.split('الساعة ')[1][0]])
            dec = e2
            val2 = alt(dec, -srH(dec) + 15*hh)
        elif 'السرطان: نصف' in lbl: val2 = 90 - (30 - e2)
        elif 'السرطان: أول' in lbl: val2 = deg(atan(1/(1 + tan(rad(30 - e2)))))
        elif 'الجدي: نصف' in lbl: val2 = 90 - (30 + e2)
        else: val2 = deg(atan(1/(1 + tan(rad(30 + e2)))))
        sh.text(cx[0], yy, lbl, 2.5, 'end', SANS, INK)
        sh.text(cx[1], yy, ab, 3.0, 'end', NASKH, RED, 700)
        sh.ltr(cx[2], yy, num, 2.5, 'end', SANS, INK, 600)
        sh.ltr(cx[3], yy, sexa(val), 2.5, 'end', SANS, TEAL, 700)
        sh.ltr(cx[4], yy, sexa(val2), 2.5, 'end', SANS, GREY)
    sh.para(tx, ty + 84, ['الفرق بين قراءة المخطوط وحسابنا على ميله 1 إلى 3 دقائق قوسية، أي أقل من 0.05°:',
            'دقة تكفي لمزولة يقرأ بها الناس الوقت. والفرق مع الميل الحالي سببه تناقص الميل الكلي',
            'منذ عصر المؤلف (23;35 عنده، و23;26 اليوم)، وتعتمد لوحاتنا الميل الحالي.',
            '', 'الساعة هنا ساعة مستوية تُعد من الشروق، والعصر بظل المثل.'], 2.4, 1.6)
    return sh


if __name__ == '__main__':
    m01(sys.argv[1:4]).save('../drawings/svg/M-01.svg')
