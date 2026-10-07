"""جداول التوقيع: نقاط كل خط ومنحنى (بالمتر من مركز الدائرة، x شرقًا وy شمالًا حقيقيًا)."""
import csv, os
from sheet_a import A, T_BLADE
from sheet_b import B, HOURS_B, date_ticks
from sheet_c import C
from dials import *

OUT = '../setting_out'
os.makedirs(OUT, exist_ok=True)


def thin(seg, step=0.05):
    out = [seg[0]]
    for p in seg[1:]:
        if (p[0] - out[-1][0])**2 + (p[1] - out[-1][1])**2 >= step*step: out.append(p)
    if out[-1] != seg[-1]: out.append(seg[-1])
    return out


def write(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['element', 'label', 'segment', 'point', 'x_east_m', 'y_north_m'])
        for el, lbl, segs in rows:
            for si, s in enumerate(segs):
                for pi, (x, y) in enumerate(thin(s)):
                    w.writerow([el, lbl, si, pi, f'{x:.4f}', f'{y:.4f}'])


rows = []
for H, segs in A.hours.items():
    dx = -T_BLADE/2 if H < 0 else T_BLADE/2
    rows.append(('hour_line', f'H={H + A.corr:+.3f}deg EET-mean T={12 + H/15:.2f}', [[(x + dx, y) for x, y in s] for s in segs]))
for dec, names, dates, lam, segs in A.signs:
    rows.append(('declination', f'dec={dec:+.3f} {"/".join(names)}', segs))
rows += [('asr', 'shafii k=1', A.asr1), ('asr', 'hanafi k=2', A.asr2),
         ('analemma_12EET', 'Jan-Jun', A.noon_ana[0]), ('analemma_12EET', 'Jul-Dec', A.noon_ana[1]),
         ('meridian', 'true noon', [[(0, A.base[1]), (0, A.R_FACE)]]),
         ('gnomon', f'style base -> nodus foot, nodus height {A.h}', [[A.base, A.foot]])]
write('A_ibn_al_shatir.csv', rows)

rows = [('ellipse', f'M={B.M} m={B.m:.4f}', [[B.hour_point(t) for t in frange(0, 360, 1)]])]
for T in HOURS_B:
    rows.append(('hour_star', f'{T}:00 EET', [[B.clock_point(T)]]))
rows.append(('date_scale', 'x=0', [[(0, y) for dd, dec, y in date_ticks()]]))
write('B_human_gnomon.csv', rows)

rows = [('aperture_foot', f'aperture height {C.H}', [[C.foot[:2]]])]
for T, (f1, f2) in C.analemmas.items():
    rows += [('analemma', f'{T:05.2f} EET Jan-Jun', f1), ('analemma', f'{T:05.2f} EET Jul-Dec', f2)]
for dec, names, dates, lam, segs in C.signs:
    rows.append(('declination', f'dec={dec:+.3f} {"/".join(names)}', segs))
rows += [('asr', 'shafii k=1', C.asr1), ('meridian', 'true noon', C.meridian)]
write('C_eye_of_the_sun.csv', rows)
print(os.listdir(OUT))
