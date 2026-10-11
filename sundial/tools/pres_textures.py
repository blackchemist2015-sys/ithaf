"""خامات الأرضية لكل تصميم (مقصوصة من لوحات المسقط) وخامة باطن حلقة التصميم (د)، للمنظور ثلاثي الأبعاد."""
import sys, re, os
import common
from common import *

OUT = sys.argv[1]
R_MM = R_SITE*1000/30


def crop(svg, cx, cy, w, h, px_w, px_h):
    svg = re.sub(r'width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"', f'width="{px_w}" height="{px_h}" viewBox="{cx - w/2} {cy - h/2} {w} {h}"', svg, 1)
    return svg


def plaza(sh, cx):
    return crop(sh.svg(), cx, 297, 2*R_MM, 2*R_MM, 1024, 1024)


import sheet_b, sheet_c, sheet_d
open(f'{OUT}/plaza_B.svg', 'w').write(plaza(sheet_b.b01(), 500))
open(f'{OUT}/plaza_C.svg', 'w').write(plaza(sheet_c.c01(), 500))
# (د): أرضية بلا مسقط الحلقة
sh = Sheet(); v = View(470, 297, 30)
girih_pattern(sh, 'gD', 0.9*v.k, color=GOLD, op=0.16)
calendar_ring(sh, v, 6.35, R_SITE, labels_out=False)
c = v.p(0, 0)
sh.circle(c, 6.35*v.k, fill='#f6f1e6', sw=0.6); sh.circle(c, 6.35*v.k, fill='url(#gD)', sw=0)
for rot, col in ((0, '#e7dcc3'), (22.5, '#ddd0b2')):
    sh.poly(star_n(c[0], c[1], 5.4*v.k, 5.4*v.k*0.7654, 8, rot), close=True, fill=col, stroke=GOLD, sw=0.4)
sh.circle(c, 3.0*v.k, fill='#3b3a38', stroke=GOLD, sw=0.5)
sh.path(v.d([(0, 3.05), (0, 6.3)]), stroke=GOLD, sw=1.0); sh.path(v.d([(0, -3.05), (0, -6.3)]), stroke=GOLD, sw=1.0)
open(f'{OUT}/plaza_D.svg', 'w').write(plaza(sh, 470))
# باطن الحلقة (من D-02)
D = sheet_d.D
X0 = D.Rb*rad(D.H_ext)*80; Y0 = D.half_w*80
open(f'{OUT}/band_D.svg', 'w').write(crop(sheet_d.d02().svg(), 495, 245, 2*X0, 2*Y0, 2048, int(2048*Y0/X0)))
print('ok')
