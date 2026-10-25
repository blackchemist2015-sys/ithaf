"""تحويل لوحات Sheet إلى DXF قابل للتعديل في AutoCAD (طبقة لكل لون، ونصوص عربية مُشكَّلة بالترتيب المرئي).
الوحدات: مم على ورق اللوحة (المقياس مكتوب في جدول العنوان)."""
import re, html
import ezdxf
from ezdxf.enums import TextEntityAlignment
import arabic_reshaper
from bidi.algorithm import get_display

NUM = r'-?[\d.]+(?:e-?\d+)?'


def ar(s):
    s = html.unescape(s).replace('⁦', '').replace('⁩', '')
    return get_display(arabic_reshaper.reshape(s)) if re.search('[؀-ۿ]', s) else s


def hexrgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def attr(el, name, default=None):
    m = re.search(rf'\s{name}="([^"]*)"', el)
    return m.group(1) if m else default


def path_pts(d):
    """M/L/Z/A → قوائم نقاط (A يُقرَّب بخط إلى نقطة النهاية)."""
    toks = re.findall(r'[MLAZ]|' + NUM, d)
    polys, cur, i, cmd, closed = [], [], 0, None, False
    while i < len(toks):
        t = toks[i]
        if t in 'MLAZ':
            cmd = t; i += 1
            if t == 'Z':
                if cur: polys.append((cur, True)); cur = []
                continue
            if t == 'M' and cur: polys.append((cur, False)); cur = []
            continue
        if cmd in ('M', 'L'):
            cur.append((float(toks[i]), float(toks[i + 1]))); i += 2
        elif cmd == 'A':
            vals = toks[i:i + 7]; cur.append((float(vals[5]), float(vals[6]))); i += 7
        else: i += 1
    if cur: polys.append((cur, False))
    return polys


def sheet_to_dxf(sheet, path, title=''):
    doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM
    doc.styles.add('AR', font='arial.ttf')
    msp = doc.modelspace(); H = sheet.h
    layers = {}

    def layer(col):
        col = (col or '#000000').lower()
        if col in ('none', ''): col = '#000000'
        if col.startswith('url'): col = '#999999'
        name = 'C' + col.lstrip('#')
        if name not in layers:
            l = doc.layers.add(name); l.rgb = hexrgb(col); layers[name] = l
        return name

    P = lambda x, y: (x, H - y)
    for el in sheet.els:
        if el.startswith('<image'): continue
        stroke = attr(el, 'stroke'); fill = attr(el, 'fill')
        col = stroke if stroke and stroke != 'none' else fill
        sw = float(attr(el, 'stroke-width', '0.25') or 0.25)
        lw = max(13, min(200, int(round(sw*100/5)*5)))
        da = {'layer': layer(col), 'lineweight': lw if sw > 0 else 13}
        if el.startswith('<path'):
            for pts, closed in path_pts(attr(el, 'd', '')):
                if len(pts) > 1: msp.add_lwpolyline([P(*p) for p in pts], close=closed, dxfattribs=da)
        elif el.startswith('<circle'):
            msp.add_circle(P(float(attr(el, 'cx')), float(attr(el, 'cy'))), float(attr(el, 'r')), dxfattribs=da)
        elif el.startswith('<rect'):
            x, y, w, h = (float(attr(el, k)) for k in ('x', 'y', 'width', 'height'))
            msp.add_lwpolyline([P(x, y), P(x + w, y), P(x + w, y + h), P(x, y + h)], close=True, dxfattribs=da)
        elif el.startswith('<text'):
            txt = re.search(r'>(.*)</text>', el, re.S).group(1)
            if not txt.strip(): continue
            x, y, size = float(attr(el, 'x')), float(attr(el, 'y')), float(attr(el, 'font-size'))
            anchor, direc = attr(el, 'text-anchor', 'start'), attr(el, 'direction', 'ltr')
            if anchor == 'middle': al = TextEntityAlignment.MIDDLE_CENTER
            elif (anchor == 'start') == (direc == 'ltr'): al = TextEntityAlignment.MIDDLE_LEFT
            else: al = TextEntityAlignment.MIDDLE_RIGHT
            rot = 0.0
            m = re.search(r'rotate\((' + NUM + ')', el)
            if m: rot = -float(m.group(1))
            t = msp.add_text(ar(txt), height=size*0.72, rotation=rot, dxfattribs={'layer': layer(fill), 'style': 'AR'})
            t.set_placement(P(x, y), align=al)
    doc.saveas(path)
