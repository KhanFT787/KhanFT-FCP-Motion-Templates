# motion_layer.py - the subtle moving layer of the KhanFT Colour Motion cards, picked by 'Motion Layer',
# with 'Motion Strength' (layer opacity) and 'Motion Speed' (Slow / Normal / Fast).
#   kind='calm'    Type 6 - Colour Motion  (rings, glow, sweeps ...)
#   kind='finance' Type 7 - Finance Motion (chart line, candles, bars, digits, tickers, coins)
#   kind='graphic' Type 8 - Graphic Motion (globe, cube, floor, hills, orbits, scan)
# Sizes follow the 960x540 mockups x4. Element opacities are set for STRENGTH 0.5 (x2 = the mockup look).
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from common import *

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'motion')
FONTS = os.path.join(HERE, 'fonts')
CALM_BASE = ['Quiet Rings', 'Light Sweep', 'Drifting Dot Grid', 'Floating Shapes']     # Type 6's first four keep their ids
SETS = {
    'calm': CALM_BASE + ['Breathing Glow', 'Soft Bokeh', 'Turning Squares', 'Soft Rays', 'Aurora Ribbons', 'Twinkle Stars', 'None'],
    'finance': ['Chart Line', 'Candlesticks', 'Market Bars', 'Floating Digits', 'Ticker Bands', 'Rising Coins', 'None'],
    'graphic': ['Wire Globe', 'Wire Cube', 'Perspective Floor', 'Parallax Hills', 'Orbit Dots', 'Scan Line', 'None'],
}
LAYERS = SETS['calm']
MSPEEDS = ['Slow', 'Normal', 'Fast']
MMUL = {'Slow': 0.6, 'Normal': 1.0, 'Fast': 1.6}
BAND = ('motion_id', 120000)
BAND_X = ('motion_x', 150000)    # Type 6 layers added later (so the first four and Motion Strength keep their ids)
STRENGTH = 0.5
PH = 1.0         # Oscillate Phase units per radian
RUN_S = 90       # scrolling layers are long enough for this many seconds at Fast


def _png(name, make):
    os.makedirs(MEDIA, exist_ok=True)
    p = os.path.join(MEDIA, name)
    if not os.path.exists(p): make().save(p, optimize=True)
    return p


def _white(alpha):
    out = Image.new('RGBA', alpha.size, (255, 255, 255, 0)); out.putalpha(alpha); return out


def _aa(W, H, draw, ss=2, blur=0, col=(255, 255, 255)):
    """supersampled white (or col) drawing: draw(g, ss) paints alpha on an L image ss times larger"""
    def make():
        big = Image.new('L', (W*ss, H*ss), 0); draw(ImageDraw.Draw(big), ss)
        a = big.resize((W, H), Image.LANCZOS)
        if blur: a = a.filter(ImageFilter.GaussianBlur(blur))
        out = Image.new('RGBA', (W, H), col + (0,)); out.putalpha(a); return out
    return make


def jr(i, a, m1, m2):
    """the mockups' hash random"""
    v = math.fmod(math.sin(i*m1 + a*m2)*43758.5453, 1)
    return (v + 1) % 1


# ---------------------------------------------------------------- PNG makers (Type 6's first four)
def _ring(r, w, dash):
    def make():
        S = 2*r + 4*w; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
        c = S/2; box = (c-r, c-r, c+r, c+r)
        if not dash:
            g.ellipse(box, outline=(255, 255, 255, 255), width=w)
        else:
            on, off = dash; circ = 2*math.pi*r; n = int(circ // (on+off)); step = 360/n; a_on = step*on/(on+off)
            for k in range(n):
                a0 = k*step
                if on <= w*1.2:   # dots
                    a = math.radians(a0); x, y = c + r*math.cos(a), c + r*math.sin(a)
                    g.ellipse((x-w*0.7, y-w*0.7, x+w*0.7, y+w*0.7), fill=(255, 255, 255, 255))
                else:
                    g.arc(box, a0, a0 + a_on, fill=(255, 255, 255, 255), width=w)
        return im
    return make


def _beam(W, H):
    def make():
        im = Image.new('L', (W, 1), 0)
        im.putdata([int(255*math.exp(-((x - W/2)/(W*0.22))**2)) for x in range(W)])
        return _white(im.resize((W, H)))
    return make


def _dots(W, H, pitch, rad):
    def make():
        big = Image.new('L', (W, H), 0); g = ImageDraw.Draw(big)
        for y in range(pitch//2, H, pitch):
            for x in range(pitch//2, W, pitch):
                dx, dy = (x - W/2)/(W*0.36), (y - H/2)/(H*0.36)
                m = 1.0 - 0.75*min(1, math.hypot(dx, dy)**2)
                e = min(1, x/500, (W-x)/500, y/500, (H-y)/500)
                v = int(255*m*max(0, e))
                if v > 3: g.ellipse((x-rad, y-rad, x+rad, y+rad), fill=v)
        return _white(big.filter(ImageFilter.GaussianBlur(1.2)))
    return make


def _shape(s, radius, w):
    def make():
        S = s + 4*w; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
        box = (2*w, 2*w, 2*w+s, 2*w+s)
        if radius == 'circle': g.ellipse(box, outline=(255, 255, 255, 255), width=w)
        else: g.rounded_rectangle(box, radius=radius, outline=(255, 255, 255, 255), width=w)
        return im
    return make


# ---------------------------------------------------------------- Bangla text PNGs
_FC = {}
def font(script, weight, size):
    key = (script, weight, size)
    if key not in _FC:
        _FC[key] = ImageFont.truetype(os.path.join(FONTS, f'hind-siliguri-{script}-{weight}-normal.woff'), size, layout_engine=ImageFont.Layout.RAQM)
    return _FC[key]


def btext(g, x, y, s, size, weight=500, fill=255):
    """draws s with its baseline at y (Bengali runs in the Bengali font, the rest in Latin, ▲▼ as triangles); returns the end x"""
    runs = []
    for ch in s:
        kind = 'tri' if ch in '▲▼' else ('bn' if 'ঀ' <= ch <= '৿' or (ch == ' ' and runs and runs[-1][0] == 'bn') else 'la')
        if runs and runs[-1][0] == kind and kind != 'tri': runs[-1][1] += ch
        else: runs.append([kind, ch])
    for kind, t in runs:
        if kind == 'tri':
            h = size*0.42; w = h*1.15; yb = y - size*0.14
            pts = [(x, yb), (x + w, yb), (x + w/2, yb - h)] if t == '▲' else [(x, yb - h), (x + w, yb - h), (x + w/2, yb)]
            g.polygon(pts, fill=fill); x += w + size*0.15
        else:
            f = font('bengali' if kind == 'bn' else 'latin', weight, size)
            g.text((x, y), t, font=f, fill=fill, anchor='ls'); x += f.getlength(t)
    return x


def btext_width(s, size, weight=500):
    im = Image.new('L', (8, 8)); return btext(ImageDraw.Draw(im), 0, 4, s, size, weight)


# ---------------------------------------------------------------- build context
class _M:
    def __init__(s, c, d, FW, FH, speed, W_SPD, W_LAY, layers, layer):
        s.c, s.d, s.FW, s.FH, s.speed, s.W_SPD, s.W_LAY, s.layers, s.layer = c, d, FW, FH, speed, W_SPD, W_LAY, layers, layer
        s.band = BAND; s.k = 2.0

    def run(s, fn): return s.c.hi(fn, *s.band)
    def new(s): return s.run(s.d.new)

    def P(s, x, y):
        """mockup 960x540 point (y down) -> Motion 4K (centre origin, y up)"""
        return x*4 - s.FW/2, s.FH/2 - y*4

    def img(s, name, path, op, px=0, py=0, sc=1.0, media=None, wh=None):
        media = media or name
        rel = f'Media/Motion {media}.png'; s.c.media[rel] = path
        w, h = wh or Image.open(path).size
        _, _, x = s.run(lambda: s.d.image(f'Motion {name}', f'Motion {name}', rel.replace(' ', '%20'), w, h, dropzone=False, px=px, py=py, op=op, s=sc))
        return x

    def rect(s, name, w, h, op, px=0, py=0, col=(1, 1, 1), rnd=0):
        _, x = s.run(lambda: s.d.rect(name, w, h, col, op=op, px=px, py=py, rnd=rnd))
        return x

    def osc(s, gid, name, chan, amp, period, phase=0.0):
        """a full cycle every `period` s at Normal speed; Motion Speed rigs its rate"""
        cpm = 60.0/period
        oid, ox = s.run(lambda: s.d.osc(gid, name, chan, amp, round(cpm*MMUL[s.speed], 5), phase=round(phase*PH, 5)))
        ox += s.run(lambda: s.d.rig(f'Rig {name} Speed', oid, 'OSC', './202', s.W_SPD, [(j+1, round(cpm*MMUL[sp], 5)) for j, sp in enumerate(MSPEEDS)], pname='Speed'))
        return ox

    def rate(s, gid, name, chan, r):
        bid, bx = s.run(lambda: s.d.rate(gid, name, chan, round(r*MMUL[s.speed], 6)))
        bx += s.run(lambda: s.d.rig(f'Rig {name} Speed', bid, 'RATE', './200', s.W_SPD, [(j+1, round(r*MMUL[sp], 6)) for j, sp in enumerate(MSPEEDS)], pname='Rate'))
        return bx

    def grp(s, name, children, beh=None, **kw):
        """group; beh(gid) -> behaviour xml (built after the group id, before the group, like the first build)"""
        gid = s.new()
        b = beh(gid) if beh else ''
        _, x = s.run(lambda: s.d.group(name, gid, children=children, beh=b, **kw))
        return x

    def option(s, name, children):
        i = s.layers.index(name); n = len(s.layers); layer = s.layer
        gid = s.new()
        _, x = s.run(lambda: s.d.group(f'Motion {name}', gid, children=children, op=1 if i == layer else 0,
                                       beh=s.d.rig(f'Rig Motion {name}', gid, 'GRP', './1/200/202', s.W_LAY,
                                                   [(j+1, 1 if j == i else 0) for j in range(n)], pname='Opacity')))
        return x


X, Y, RZ, SX, SY, OP = './1/100/101/1', './1/100/101/2', './1/100/109/3', './1/100/105/1', './1/100/105/2', './1/200/202'


def scroller(m, name, path, tile_w, py, rate_px, op, direction=-1, media=None):
    """a seamless tile repeated side by side, sliding at rate_px px/s (Normal) - long enough for RUN_S s at Fast"""
    n = math.ceil((m.FW + RUN_S*rate_px*MMUL['Fast'])/tile_w) + 1
    x = ''
    for j in range(n):
        cx = -m.FW/2 + tile_w/2 + j*tile_w
        if direction > 0: cx = m.FW/2 - tile_w/2 - j*tile_w
        x = m.img(f'{name} {j+1}', path, op, px=cx, py=py, media=media or name) + x
    return m.grp(f'{name} Scroll', x, beh=lambda g: m.rate(g, f'{name} Scroll', X, direction*rate_px))


# ================================================================ Type 6 - Calm
def quiet_rings(m):
    rings = ''
    spec = [(600, 5, (5, 36), 160, 1), (860, 5, None, 0, 0), (1160, 4, (160, 104), 220, -1), (1520, 4, None, 0, 0), (1920, 6, (8, 56), 260, 1)]
    for i, (r, w, dash, per, sgn) in enumerate(spec):
        x = m.img(f'Ring {i+1}', _png(f'ring{i+1}.png', _ring(r, w, dash)), round(0.12*m.k*(1 - i*0.12), 3), wh=(2*r + 4*w, 2*r + 4*w))
        rings = m.grp(f'Ring {i+1}', x, beh=(lambda g: m.rate(g, f'Ring {i+1} Turn', RZ, sgn*2*math.pi/per)) if per else None) + rings
    return m.grp('Rings Breathe', rings, beh=lambda g: m.osc(g, 'Rings Breathe X', SX, 0.0175, 14.0) + m.osc(g, 'Rings Breathe Y', SY, 0.0175, 14.0))


def light_sweep(m):
    BW, BH = 2080, 4560
    x = m.img('Beam', _png('beam.png', _beam(BW, BH)), round(0.14*m.k, 3), wh=(BW, BH))
    x = m.grp('Beam Tilt', x, rz=math.radians(-18))
    return m.grp('Beam Sweep', x, beh=lambda g: m.osc(g, 'Sweep', X, 4800, 24.0, phase=-math.pi/2))


def dot_grid(m):
    DW, DH = 5200, 3500
    x = m.img('Dots', _png('dots.png', _dots(DW, DH, 112, 6)), round(0.2*m.k, 3), wh=(DW, DH))
    return m.grp('Dot Drift', x, beh=lambda g: m.osc(g, 'Drift X', X, 420, 64.0) + m.osc(g, 'Drift Y', Y, 210, 64.0, phase=math.pi/3))


def floating_shapes(m):
    shapes = ''
    spec = [(9, 16, 480, 88, 8, 19), (84, 14, 600, 'circle', 8, 23), (14, 74, 680, 'circle', 6, 25), (88, 72, 440, 72, 8, 17),
            (30, 8, 240, 48, 6, 15), (70, 88, 280, 'circle', 6, 21), (3, 45, 320, 'circle', 6, 18), (96, 44, 360, 64, 6, 20)]
    for i, (xp, yp, s, rad, w, per) in enumerate(spec):
        x = m.img(f'Shape {i+1}', _png(f'shape{i+1}.png', _shape(s, rad, w)), round(0.13*m.k, 3), wh=(s + 4*w, s + 4*w))
        ph = i*0.9
        shapes = m.grp(f'Shape {i+1}', x, px=(xp/100 - 0.5)*m.FW, py=(0.5 - yp/100)*m.FH,
                       beh=lambda g: (m.osc(g, f'Shape {i+1} X', X, 90, 2*per, phase=ph) + m.osc(g, f'Shape {i+1} Y', Y, 80, 2*per*0.85, phase=ph + 1.1)
                                      + m.osc(g, f'Shape {i+1} Tilt', RZ, 0.21, 2*per*1.15, phase=ph + 2.0))) + shapes
    return shapes


def breathing_glow(m):
    W, H = 950, 575       # drawn at 1/3.2 and scaled up: a soft glow needs no detail
    def make():
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.hypot((xx - W/2)/(W/2), (yy - H/2)/(H/2))
        v = np.where(r < 0.55, 1 - r/0.55*0.6, np.clip(0.4*(1 - (r - 0.55)/0.45), 0, 1))
        return _white(Image.fromarray((v*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)))
    x = m.img('Glow', _png('glow.png', make), round(0.25*m.k, 3), sc=3.2)
    return m.grp('Glow Breathe', x, op=0.675,
                 beh=lambda g: m.osc(g, 'Glow Scale X', SX, 0.08, 9.0) + m.osc(g, 'Glow Scale Y', SY, 0.08, 9.0) + m.osc(g, 'Glow Fade', OP, 0.325, 9.0))


def soft_bokeh(m):
    path = _png('bokeh.png', _aa(300, 300, lambda g, ss: g.ellipse((50*ss, 50*ss, 250*ss, 250*ss), fill=255), blur=12))
    out = ''
    for i in range(16):
        r = lambda a: jr(i, a, 91.7, 47.3)
        s, d = 18 + r(1)*46, 18 + r(2)*14
        px, py = m.P(r(3)*960 + s/2, r(4)*540 + s/2)
        x = m.img(f'Bokeh {i+1}', path, round(0.22*(0.5 + r(5)*0.7)*m.k, 3), sc=round(s*4/200, 3), media='Bokeh')
        ph = r(6)*2*math.pi
        out = m.grp(f'Bokeh {i+1}', x, px=px, py=py,
                    beh=lambda g: m.osc(g, f'Bokeh {i+1} X', X, 100, 2*d, phase=ph) + m.osc(g, f'Bokeh {i+1} Y', Y, 68, 2*d, phase=ph + 1.3)) + out
    return out


def turning_squares(m):
    out = ''
    spec = [(380, 40, 120, 1, 12), (520, 56, 160, -1, 30), (680, 72, 200, 1, 50), (860, 90, 240, -1, 8)]
    for i, (s, rad, d, sgn, rot) in enumerate(spec):
        x = m.img(f'Square {i+1}', _png(f'square{i+1}.png', _shape(s*4, rad*4, 6)), round(0.14*(1 - i*0.15)*m.k, 3))
        out = m.grp(f'Square {i+1}', x, rz=-sgn*2*math.pi*rot/d, beh=lambda g: m.rate(g, f'Square {i+1} Turn', RZ, -sgn*2*math.pi/d)) + out
    return out


def soft_rays(m):
    S = 1500
    def make():
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
        c = S/2; R = c*math.sqrt(2)
        rr = np.hypot(xx - c, yy - c)/R
        mk = np.interp(rr, [0, 0.08, 0.3, 0.6, 0.7, 2], [0, 0, 1, 0.4, 0, 0])
        ang = np.degrees(np.arctan2(yy - c, xx - c)) % 24
        ray = np.clip(np.minimum(ang, 6 - ang)/0.6 + 0.5, 0, 1)      # 6 deg rays, soft edges
        return _white(Image.fromarray((mk*ray*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)))
    x = m.img('Rays', _png('rays.png', make), round(0.1*m.k, 3), sc=4)
    return m.grp('Rays Turn', x, beh=lambda g: m.rate(g, 'Rays Turn', RZ, 2*math.pi/140))


def _ribbon(stops):
    W, H, B = 1400, 150, 120
    def make():
        a = Image.new('L', (W + 2*B, H + 2*B), 0); g = ImageDraw.Draw(a)
        g.ellipse((B, B, B + W, B + H), fill=255)
        grad = Image.new('L', (W + 2*B, 1), 0)
        vals = []
        for xx in range(W + 2*B):
            f = (xx - B)/W
            for (a0, v0), (a1, v1) in zip(stops, stops[1:]):
                if a0 <= f < a1: vals.append(int(255*(v0 + (v1 - v0)*(f - a0)/(a1 - a0)))); break
            else: vals.append(0)
        grad.putdata(vals)
        from PIL import ImageChops
        a = ImageChops.multiply(a, grad.resize(a.size)).filter(ImageFilter.GaussianBlur(38))
        return _white(a)
    return make


def aurora_ribbons(m):
    out = ''
    spec = [('Ribbon 1', [(-1, 0), (0, 0), (0.3, 1), (0.6, 0.95), (1, 0), (2, 0)], 185, 1.0, 22, 0.0, 1),
            ('Ribbon 2', [(-1, 0), (0, 0), (0.4, 0.95), (0.7, 1), (1, 0), (2, 0)], 385, 0.7, 30, 2.4, -1)]
    for nm, stops, yc, a, per, ph, sgn in spec:
        x = m.img(nm, _png(nm.lower().replace(' ', '') + '.png', _ribbon(stops)), round(0.25*a*m.k, 3), sc=4)
        x = m.grp(f'{nm} Stretch', x, sy=1.15, beh=lambda g: m.osc(g, f'{nm} Stretch', SY, sgn*0.15, per, phase=ph))
        px, py = m.P(480 - 20, yc - 5)
        out = m.grp(f'{nm} Drift', x, px=px, py=py, rz=math.radians(7),
                    beh=lambda g: (m.osc(g, f'{nm} X', X, sgn*400, per, phase=ph) + m.osc(g, f'{nm} Y', Y, sgn*100, per, phase=ph)
                                   + m.osc(g, f'{nm} Tilt', RZ, -sgn*math.radians(2), per, phase=ph))) + out
    return out


def twinkle_stars(m):
    def draw(g, ss):
        g.ellipse((24*ss, 24*ss, 40*ss, 40*ss), fill=255)
    core = _aa(64, 64, draw)
    def make():
        im = core(); a = im.getchannel('A'); glow = a.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v*0.7))
        from PIL import ImageChops
        return _white(ImageChops.lighter(a, glow))
    path = _png('star.png', make)
    out = ''
    for i in range(40):
        r = lambda a: jr(i, a, 57.3, 19.1)
        s, d = 2 + r(1)*3, 3 + r(2)*4
        px, py = m.P(r(3)*960, r(4)*540)
        x = m.img(f'Star {i+1}', path, 1, sc=round(s*4/16, 3), media='Star')
        out = m.grp(f'Star {i+1}', x, px=px, py=py, op=round(0.55*m.k/2, 3),
                    beh=lambda g: m.osc(g, f'Star {i+1} Twinkle', OP, round(0.55*m.k/2, 3), d, phase=r(5)*2*math.pi)) + out
    return out


# ================================================================ Type 7 - Finance
def chart_line(m):
    T = 3840; top = 1000; H = 1160
    pts = []
    for i in range(48):
        n = math.sin(i*1.7)*18 + math.sin(i*0.45)*34 + math.sin(i*3.3)*9
        pts.append((i*80, (330 + n)*4 - top))
    def P(i): q = pts[i % 48]; return (q[0] + (i//48)*T, q[1])
    def draw(g, ss):
        line = [(x*ss, y*ss) for x, y in (P(i) for i in range(-2, 51))]
        g.polygon(line + [(51*80*ss, H*ss), (-2*80*ss, H*ss)], fill=64)
        g.line(line, fill=255, width=8*ss, joint='curve')
    path = _png('chart_line.png', _aa(T, H, draw))
    return scroller(m, 'Chart', path, T, m.FH/2 - top - H/2, 96, round(0.2*m.k, 3))


def candlesticks(m):
    T = 3840
    one = []; price = 300
    for i in range(32):
        r = lambda a: jr(i, a, 12.9898, 78.233)
        o = price; c = price + (r(1) - 0.5)*60 + math.sin(i/32*math.pi*2)*8
        hi = min(o, c) - 8 - r(2)*20; lo = max(o, c) + 8 + r(3)*20
        one.append((i, o, c, hi, lo, c < o)); price = c + (300 - c)*0.25
    top = int(min(q[3] for q in one)*4) - 20; bot = int(max(q[4] for q in one)*4) + 20; H = bot - top
    def draw(g, ss):
        for i, o, c, hi, lo, up in one:
            x = (i*30 + 8)*4; cx = x + 28
            g.line(((cx*ss, (hi*4 - top)*ss), (cx*ss, (lo*4 - top)*ss)), fill=255, width=6*ss)
            y0, y1 = min(o, c)*4 - top, min(o, c)*4 - top + max(12, abs(c - o)*4)
            g.rectangle((x*ss, y0*ss, (x + 56)*ss, y1*ss), fill=230 if up else 0, outline=255, width=6*ss)
            if not up:   # hollow body: clear the wick inside it
                g.rectangle(((x + 6)*ss, (y0 + 6)*ss, (x + 50)*ss, (y1 - 6)*ss), fill=0)
    path = _png('candles.png', _aa(T, H, draw))
    return scroller(m, 'Candles', path, T, m.FH/2 - top - H/2, 80, round(0.16*m.k, 3))


def market_bars(m):
    BH = 1080
    def make():
        ss = 2
        v = np.repeat((255*(1 - 0.8*np.arange(BH*ss)/(BH*ss)))[:, None], 88*ss, axis=1).astype(np.uint8)
        mask = Image.new('L', (88*ss, BH*ss), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, 88*ss - 1, (BH + 40)*ss), radius=16*ss, fill=255)
        a = (v.astype(np.uint16)*np.asarray(mask)//255).astype(np.uint8)
        return _white(Image.fromarray(a).resize((88, BH), Image.LANCZOS))
    path = _png('bar.png', make)
    out = ''
    for i in range(30):
        r = lambda a: jr(i, a, 17.7, 53.1)
        base = 60 + 90*(0.5 + 0.5*math.sin(i/29*math.pi*1.6 - 0.8)) + r(1)*60; d = 5 + r(2)*5
        lo, hi = 0.7 + r(3)*0.15, 1.0 + r(4)*0.25
        x = m.img(f'Bar {i+1}', path, 1, py=BH/2, media='Bar')
        x = m.grp(f'Bar {i+1} Height', x, sy=round(base*4/BH, 4))
        px, _ = m.P(12 + i*32 + 11, 0)
        out = m.grp(f'Bar {i+1}', x, px=px, py=-m.FH/2, sy=round((lo + hi)/2, 4),
                    beh=lambda g: m.osc(g, f'Bar {i+1} Breathe', SY, round((hi - lo)/2, 4), d, phase=r(5)*2*math.pi)) + out
    return m.grp('Bars', out, op=round(0.12*m.k, 3))


def floating_digits(m):
    TW, TH = 300, 4320
    glyphs = ['৳', '%', '১', '২', '৫', '৯', '+', '৭', '০', '৩', '৮', '৪', '৬']
    paths = []
    for v in range(3):
        def draw(g, ss, v=v):
            for j in range(6):
                r = lambda a: jr(v*10 + j, a, 23.9, 61.7)
                ch = glyphs[int(r(1)*len(glyphs)) % len(glyphs)]; size = int((80 + r(2)*104)*ss)
                y = (j + 0.3 + r(3)*0.4)*TH/6*ss + size*0.35
                x = (TW*ss - size*0.6)/2 + (r(4) - 0.5)*60*ss
                btext(g, x, y, ch, size, 700)
        paths.append(_png(f'digits{v+1}.png', _aa(TW, TH, draw)))
    xs = [3, 9, 15, 21, 79, 85, 91, 97]
    out = ''
    for c, xp in enumerate(xs):
        r = lambda a: jr(c, a, 31.3, 7.7)
        rate_px = 85*(0.8 + 0.4*r(1)); off = r(2)*TH; v = c % 3
        n = math.ceil((m.FH + RUN_S*rate_px*MMUL['Fast'] + off)/TH) + 1
        x = ''
        for j in range(n):
            x = m.img(f'Digits {c+1}-{j+1}', paths[v], 1, py=m.FH/2 + TH/2 - off - j*TH, media=f'Digits {v+1}') + x
        out = m.grp(f'Digit Column {c+1}', x, px=(xp/100 - 0.5)*m.FW, beh=lambda g: m.rate(g, f'Digit Column {c+1} Rise', Y, rate_px)) + out
    return m.grp('Digits', out, op=round(0.16*m.k, 3))


def ticker_bands(m):
    BH = 136; size = 64
    lines = [('▲ ২.৪%     ৳     ▼ ০.৮%     ▲ ১.১%     ৳     ▲ ৩.০%     ▼ ১.৫%     ৳     ▲ ০.৬%     ', 924, 90, -1),
             ('৳ সঞ্চয়     ৳ বিনিয়োগ     ৳ সুদ     ৳ মুনাফা     ৳ ঝুঁকি     ', -924, 72, 1)]
    out = ''
    for b, (txt, py, rate_px, sgn) in enumerate(lines):
        W = math.ceil(btext_width(txt, size))
        path = _png(f'ticker{b+1}.png', _aa(W, BH, lambda g, ss: btext(g, 0, (BH/2 + size*0.33)*ss, txt, size*ss)))
        band = (m.rect(f'Ticker {b+1} Band', m.FW + 200, BH, 0.08, py=py) + m.rect(f'Ticker {b+1} Edge Top', m.FW + 200, 4, 0.35, py=py + BH/2)
                + m.rect(f'Ticker {b+1} Edge Bottom', m.FW + 200, 4, 0.35, py=py - BH/2))
        out = m.grp(f'Ticker {b+1}', scroller(m, f'Ticker {b+1}', path, W, py, rate_px, 1, direction=sgn) + band) + out
    return m.grp('Tickers', out, op=round(0.35*m.k, 3))


def rising_coins(m):
    S = 224
    def draw(g, ss):
        g.ellipse((4*ss, 4*ss, (S - 4)*ss, (S - 4)*ss), outline=255, width=8*ss)
        i = S*0.22; g.ellipse((i*ss, i*ss, (S - i)*ss, (S - i)*ss), outline=255, width=6*ss)
    path = _png('coin.png', _aa(S, S, draw))
    xs = [6, 17, 28, 72, 83, 94, 12, 88]
    out = ''
    for c, xp in enumerate(xs):
        r = lambda a: jr(c, a, 33.1, 11.7)
        rate_px = 2640/(16 + r(2)*10)*0.7; gap = 1800; off = r(3)*gap
        n = math.ceil((RUN_S*0.85*rate_px*MMUL['Fast'] + off)/gap) + 1
        x = ''
        for j in range(n):
            rr = lambda a: jr(c*10 + j, a, 13.7, 5.3)
            s = 26 + rr(1)*30; ph = rr(2)*2*math.pi
            coin = m.img(f'Coin {c+1}-{j+1}', path, 1, sc=round(s*4/S, 3), media='Coin')
            x = m.grp(f'Coin {c+1}-{j+1}', coin, py=-m.FH/2 + 300 - off - j*gap, sx=0.675,
                      beh=lambda g: m.osc(g, f'Coin {c+1}-{j+1} Flip', SX, 0.325, 10 + rr(3)*6, phase=ph)) + x
        out = m.grp(f'Coin Column {c+1}', x, px=(xp/100 - 0.5)*m.FW, beh=lambda g: m.rate(g, f'Coin Column {c+1} Rise', Y, rate_px)) + out
    return m.grp('Coins', out, op=round(0.18*m.k, 3))


# ================================================================ Type 8 - Graphic / 3D
def wire_globe(m):
    R = 1000; S = 2*R + 40
    def frame(g, ss):
        c = S/2*ss
        g.ellipse((c - R*ss, c - R*ss, c + R*ss, c + R*ss), outline=255, width=6*ss)
        for f in (-0.66, -0.33, 0, 0.33, 0.66):
            rx = R*math.sqrt(1 - f*f); ry = rx*0.16; cy = c + R*f*ss
            g.ellipse((c - rx*ss, cy - ry*ss, c + rx*ss, cy + ry*ss), outline=200, width=4*ss)
    def meridian(g, ss):
        c = S/2*ss; g.ellipse((c - R*ss, c - R*ss, c + R*ss, c + R*ss), outline=200, width=5*ss)
    x = m.img('Globe Frame', _png('globe_frame.png', _aa(S, S, frame)), 1)
    mp = _png('globe_meridian.png', _aa(S, S, meridian))
    for i in range(6):
        mx = m.img(f'Meridian {i+1}', mp, 1, media='Globe Meridian')
        x = m.grp(f'Meridian {i+1}', mx, sx=0, beh=lambda g: m.osc(g, f'Meridian {i+1} Turn', SX, 1, 52, phase=math.pi/2 + i*math.pi/6)) + x
    return m.grp('Globe Tilt', x, rz=math.radians(18), op=round(0.2*m.k, 3))


def wire_cube(m):
    tilt = math.radians(22); sq = math.sin(tilt)
    out = ''
    for n, (x9, y9, s9, per, sgn) in enumerate([(70, 300, 150, 30, 1), (790, 60, 100, 24, -1)]):
        s = s9*4; H = s*math.cos(tilt); w = 10
        cx, cy = m.P(x9 + s9/2, y9 + s9/2)
        path = _png(f'cube_face{n+1}.png', _aa(s + 2*w, s + 2*w, lambda g, ss: g.rectangle((w/2*ss, w/2*ss, (s + 1.5*w)*ss, (s + 1.5*w)*ss), outline=255, width=w*ss)))
        om = sgn*2*math.pi/per
        def face(nm, edges):
            x = m.img(f'Cube {n+1} {nm} Face', path, 1, media=f'Cube Face {n+1}')
            if edges:
                for k, (ex, ey) in enumerate([(1, 1), (-1, 1), (-1, -1), (1, -1)]):
                    e = m.rect(f'Cube {n+1} Edge {k+1}', 6, H, 1, py=-H/2)
                    e = m.grp(f'Cube {n+1} Edge {k+1} Upright', e, sy=round(1/sq, 5))
                    x = m.grp(f'Cube {n+1} Corner {k+1}', e, px=ex*s/2, py=ey*s/2, beh=lambda g: m.rate(g, f'Cube {n+1} Corner {k+1} Turn', RZ, -om)) + x
            x = m.grp(f'Cube {n+1} {nm} Turn', x, beh=lambda g: m.rate(g, f'Cube {n+1} {nm} Turn', RZ, om))
            return m.grp(f'Cube {n+1} {nm} Tilt', x, py=H/2 if edges else -H/2, sy=round(sq, 5))
        out = m.grp(f'Cube {n+1}', face('Top', True) + face('Bottom', False), px=cx, py=cy) + out
    return m.grp('Cubes', out, op=round(0.22*m.k, 3))


def perspective_floor(m):
    """a grid plane tipped back in 3D (Rotation X), its cross lines gliding toward the viewer"""
    G = 240; W = 24000; L = 12000
    rate_px = G/3.5
    travel = RUN_S*rate_px*MMUL['Fast']
    v = ''
    for k in range(-int(W/2/G), int(W/2/G) + 1):
        v += m.rect(f'Floor Line V{k}', 6, L + travel, 1, px=k*G, py=(L + travel)/2)
    h = ''
    for j in range(int((L + travel)/G) + 1):
        h += m.rect(f'Floor Line H{j+1}', W, 6, 1, py=j*G)
    h = m.grp('Floor Glide', h, beh=lambda g: m.rate(g, 'Floor Glide', Y, -rate_px))
    return m.grp('Floor Plane', h + v, py=-m.FH/2 - 60, rx=math.radians(-86), op=round(0.25*m.k, 3))


def parallax_hills(m):
    T, H = 3840, 1040
    k = 0.18
    spec = [(90, 40, 2, 0.4, 60, 0.6*k, (255, 255, 255)), (140, 34, 3, 1.7, 40, k, (255, 255, 255)), (190, 26, 4, 2.9, 26, 1.0*k, (0, 0, 0))]
    out = ''
    for n, (y0, amp, waves, ph, dur, a, col) in enumerate(spec):
        def draw(g, ss, y0=y0, amp=amp, waves=waves, ph=ph):
            pts = []
            for xx in range(0, T + 17, 16):
                x9 = xx/4
                y = y0 - amp*math.sin(x9/960*math.pi*2*waves + ph) - amp*0.4*math.sin(x9/960*math.pi*2*waves*2 + ph*2)
                pts.append((xx*ss, y*4*ss))
            g.polygon(pts + [((T + 16)*ss, H*ss), (0, H*ss)], fill=255)
        path = _png(f'hill{n+1}.png', _aa(T, H, draw, col=col))
        out = scroller(m, f'Hill {n+1}', path, T, -m.FH/2 + H/2, round(3840/dur, 3), round(a*m.k, 3)) + out
    return out


def orbit_dots(m):
    out = ''
    dot = _png('orbit_dot.png', _aa(48, 48, lambda g, ss: g.ellipse((4*ss, 4*ss, 44*ss, 44*ss), fill=255)))
    for n, (size, per, cnt, ds, sgn) in enumerate([(720, 60, 3, 10, 1), (980, 90, 4, 8, -1)]):
        R = size*2; S = 2*R + 20
        ring = _png(f'orbit_ring{n+1}.png', _aa(S, S, lambda g, ss: g.ellipse(((S/2 - R)*ss, (S/2 - R)*ss, (S/2 + R)*ss, (S/2 + R)*ss), outline=255, width=5*ss)))
        x = m.img(f'Orbit {n+1} Ring', ring, 0.35)
        for i in range(cnt):
            a = i/cnt*2*math.pi
            x = m.img(f'Orbit {n+1} Dot {i+1}', dot, 1, px=R*math.cos(a), py=R*math.sin(a), sc=round(ds*4/40, 3), media='Orbit Dot') + x
        out = m.grp(f'Orbit {n+1}', x, beh=lambda g: m.rate(g, f'Orbit {n+1} Turn', RZ, -sgn*2*math.pi/per)) + out
    _, py = m.P(480, 270*1.08)
    return m.grp('Orbit Tilt', out, py=py, sy=0.42, op=round(0.3*m.k, 3))


def scan_line(m):
    BH = 480
    def draw(g, ss):
        for yy in range(BH):
            f = yy/BH
            v = 0.35*f/0.85 if f < 0.85 else (0.35 + 0.65*(f - 0.85)/0.13 if f < 0.98 else 1 - (f - 0.98)/0.02)
            g.line(((0, yy), (15, yy)), fill=int(255*max(0, v)))
    path = _png('scan.png', _aa(16, BH, draw, ss=1))
    x = m.img('Scan Band', path, 1)
    x = m.grp('Scan Width', x, sx=(m.FW + 200)/16)
    return m.grp('Scan Move', x, op=round(0.25*m.k, 3), beh=lambda g: m.osc(g, 'Scan Move', Y, -1500, 20.0, phase=-math.pi/2))


BUILDERS = {
    'Quiet Rings': quiet_rings, 'Light Sweep': light_sweep, 'Drifting Dot Grid': dot_grid, 'Floating Shapes': floating_shapes,
    'Breathing Glow': breathing_glow, 'Soft Bokeh': soft_bokeh, 'Turning Squares': turning_squares, 'Soft Rays': soft_rays,
    'Aurora Ribbons': aurora_ribbons, 'Twinkle Stars': twinkle_stars,
    'Chart Line': chart_line, 'Candlesticks': candlesticks, 'Market Bars': market_bars, 'Floating Digits': floating_digits,
    'Ticker Bands': ticker_bands, 'Rising Coins': rising_coins,
    'Wire Globe': wire_globe, 'Wire Cube': wire_cube, 'Perspective Floor': perspective_floor, 'Parallax Hills': parallax_hills,
    'Orbit Dots': orbit_dots, 'Scan Line': scan_line,
}


def motion_layer(c, d, FW, FH, layer=0, speed='Normal', kind='calm'):
    """returns (xml, publish) - publish(P) adds the three controls to the inspector.
    Never call run() inside another run() lambda: the band cursor is only stored when the outer call returns."""
    layers = SETS[kind]
    W_LAY = c.hi(lambda: d.w_popup('Motion Layer', layers, layer), *BAND)
    W_SPD = c.hi(lambda: d.w_popup('Motion Speed', MSPEEDS, MSPEEDS.index(speed)), *BAND)
    m = _M(c, d, FW, FH, speed, W_SPD, W_LAY, layers, layer)
    out = ''
    for name in layers:
        if name == 'None': continue
        if kind == 'calm' and name not in CALM_BASE: m.band = BAND_X
        out = m.option(name, BUILDERS[name](m)) + out
    m.band = BAND
    ML = m.new()
    _, xml = m.run(lambda: d.group('Motion Layer', ML, children=out, op=STRENGTH))

    def publish(P):
        P(W_LAY, './2/100', 'Motion Layer'); P(ML, './1/200/202', 'Motion Strength'); P(W_SPD, './2/100', 'Motion Speed')
    return xml, publish
