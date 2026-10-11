"""خامة أرضية المزولة (التصميم أ بوجه رخامة ابن الشاطر) لاستعمالها في المنظور ثلاثي الأبعاد."""
import sys
from sheet_shatir import *

sh = Sheet(300, 300)
v = View(150, 150, 50)
girih_pattern(sh, 'gT', 0.9*v.k)
calendar_ring(sh, v, 6.35, R_SITE, labels_out=False)
c = v.p(0, 0)
sh.circle(c, 6.35*v.k, fill='#f3ede0', sw=0.4)
sh.circle(c, 6.35*v.k, fill='url(#gT)', sw=0)
M = Marble(**FUS)
draw_marble(sh, M, v.p, v.k, big=False)
x, y = v.p(0, M.Dp/2 - 0.32)
sh.text(x, y, 'وُضعت هذه الآلة الجامعة على هيئة رخامة ابن الشاطر لعرض ل الفسطاط', 2.4, 'middle', NASKH, '#5b3d16', 700)
s = sh.svg().replace('<rect width="300" height="300" fill="#fffdf8"/>', '')
open(sys.argv[1], 'w').write(s)
