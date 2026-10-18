# motion_layer.py - the subtle moving layer of KhanFT Section Type 6 (Colour Motion):
# Quiet Rings, Light Sweep, Drifting Dot Grid, Floating Shapes - picked by 'Motion Layer',
# with 'Motion Strength' (layer opacity) and 'Motion Speed' (Slow / Normal / Fast).
import os, math
from PIL import Image, ImageDraw, ImageFilter
from common import *

MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'motion')
LAYERS = ['Quiet Rings', 'Light Sweep', 'Drifting Dot Grid', 'Floating Shapes', 'None']
MSPEEDS = ['Slow', 'Normal', 'Fast']
MMUL = {'Slow': 0.6, 'Normal': 1.0, 'Fast': 1.6}
BAND = ('motion_id', 120000)
STRENGTH = 0.5       # default layer opacity; element opacities are set for this, so 100% = twice as strong


def _png(name, make):
    os.makedirs(MEDIA, exist_ok=True)
    p = os.path.join(MEDIA, name)
    if not os.path.exists(p): make().save(p, optimize=True)
    return p


def _ring(r, w, dash):
    """white ring PNG, radius r px, line w px; dash = None (solid) or (on, off) in px along the circle"""
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
        a = im.resize((W, H)); out = Image.new('RGBA', (W, H), (255, 255, 255, 0)); out.putalpha(a); return out
    return make


def _dots(W, H, pitch, rad):
    def make():
        big = Image.new('L', (W, H), 0); g = ImageDraw.Draw(big)
        for y in range(pitch//2, H, pitch):
            for x in range(pitch//2, W, pitch):
                # centre strong, edges fainter; hard image edges fully faded
                dx, dy = (x - W/2)/(W*0.36), (y - H/2)/(H*0.36)
                m = 1.0 - 0.75*min(1, math.hypot(dx, dy)**2)
                e = min(1, x/500, (W-x)/500, y/500, (H-y)/500)
                v = int(255*m*max(0, e))
                if v > 3: g.ellipse((x-rad, y-rad, x+rad, y+rad), fill=v)
        big = big.filter(ImageFilter.GaussianBlur(1.2))
        out = Image.new('RGBA', (W, H), (255, 255, 255, 0)); out.putalpha(big); return out
    return make


def _shape(s, radius, w):
    def make():
        S = s + 4*w; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
        box = (2*w, 2*w, 2*w+s, 2*w+s)
        if radius == 'circle': g.ellipse(box, outline=(255, 255, 255, 255), width=w)
        else: g.rounded_rectangle(box, radius=radius, outline=(255, 255, 255, 255), width=w)
        return im
    return make


def motion_layer(c, d, FW, FH, layer=0, speed='Normal'):
    """returns (xml, publish) - publish(P) adds the three controls to the inspector.
    Never call run() inside another run() lambda: the band cursor is only stored when the outer call returns."""
    def run(fn): return c.hi(fn, *BAND)
    W_LAY = run(lambda: d.w_popup('Motion Layer', LAYERS, layer))
    W_SPD = run(lambda: d.w_popup('Motion Speed', MSPEEDS, MSPEEDS.index(speed)))

    def img(name, path, w, h, op, px=0, py=0):
        rel = f'Media/Motion {name}.png'; c.media[rel] = path
        _, _, x = run(lambda: d.image(f'Motion {name}', f'Motion {name}', rel.replace(' ', '%20'), w, h, dropzone=False, px=px, py=py, op=op))
        return x

    def osc(gid, name, chan, amp, period, phase=0.0):
        """oscillate with a full cycle of `period` s at Normal speed; Motion Speed rigs its rate"""
        cpm = 60.0/period
        oid, ox = run(lambda: d.osc(gid, name, chan, amp, round(cpm*MMUL[speed], 5), phase=phase))   # base = the default speed
        ox += run(lambda: d.rig(f'Rig {name} Speed', oid, 'OSC', './202', W_SPD, [(j+1, round(cpm*MMUL[sp], 5)) for j, sp in enumerate(MSPEEDS)], pname='Speed'))
        return ox

    def rate(gid, name, chan, r):
        bid, bx = run(lambda: d.rate(gid, name, chan, round(r*MMUL[speed], 6)))
        bx += run(lambda: d.rig(f'Rig {name} Speed', bid, 'RATE', './200', W_SPD, [(j+1, round(r*MMUL[sp], 6)) for j, sp in enumerate(MSPEEDS)], pname='Rate'))
        return bx

    def option(i, name, children, beh=''):
        gid = run(d.new)
        _, x = run(lambda: d.group(f'Motion {name}', gid, children=children, op=1 if i == layer else 0,
                                   beh=beh + d.rig(f'Rig Motion {name}', gid, 'GRP', './1/200/202', W_LAY,
                                                   [(j+1, 1 if j == i else 0) for j in range(len(LAYERS))], pname='Opacity')))
        return x

    k = 2.0   # element opacity x STRENGTH(0.5) = the mockup's look
    # 1. Quiet Rings - faint rings round the title, turning very slowly, breathing
    rings = ''
    spec = [(600, 5, (5, 36), 160, 1), (860, 5, None, 0, 0), (1160, 4, (160, 104), 220, -1), (1520, 4, None, 0, 0), (1920, 6, (8, 56), 260, 1)]
    for i, (r, w, dash, per, sgn) in enumerate(spec):
        x = img(f'Ring {i+1}', _png(f'ring{i+1}.png', _ring(r, w, dash)), 2*r + 4*w, 2*r + 4*w, round(0.12*k*(1 - i*0.12), 3))
        gid = run(d.new)
        beh = rate(gid, f'Ring {i+1} Turn', './1/100/109/3', sgn*2*math.pi/per) if per else ''
        _, x = run(lambda: d.group(f'Ring {i+1}', gid, children=x, beh=beh))
        rings = x + rings
    bg = run(d.new)
    beh = osc(bg, 'Rings Breathe X', './1/100/105/1', 0.0175, 14.0) + osc(bg, 'Rings Breathe Y', './1/100/105/2', 0.0175, 14.0)
    _, rings = run(lambda: d.group('Rings Breathe', bg, children=rings, beh=beh))
    out = option(0, 'Quiet Rings', rings)

    # 2. Light Sweep - a soft wide band of light glides across, then rests off screen
    BW, BH = 2080, 4560
    x = img('Beam', _png('beam.png', _beam(BW, BH)), BW, BH, round(0.14*k, 3))
    gr = run(d.new); _, x = run(lambda: d.group('Beam Tilt', gr, children=x, rz=math.radians(-18)))
    gs = run(d.new)
    beh = osc(gs, 'Sweep', './1/100/101/1', 4800, 24.0, phase=-math.pi/2)
    _, x = run(lambda: d.group('Beam Sweep', gs, children=x, beh=beh))
    out = option(1, 'Light Sweep', x) + out

    # 3. Drifting Dot Grid - a faint dot field drifting slowly on a diagonal
    DW, DH = 5200, 3500
    x = img('Dots', _png('dots.png', _dots(DW, DH, 112, 6)), DW, DH, round(0.2*k, 3))
    gd = run(d.new)
    beh = osc(gd, 'Drift X', './1/100/101/1', 420, 64.0) + osc(gd, 'Drift Y', './1/100/101/2', 210, 64.0, phase=math.pi/3)
    _, x = run(lambda: d.group('Dot Drift', gd, children=x, beh=beh))
    out = option(2, 'Drifting Dot Grid', x) + out

    # 4. Floating Shapes - faint outlined squares and circles near the edges, drifting and tilting
    shapes = ''
    spec = [(9, 16, 480, 88, 8, 19), (84, 14, 600, 'circle', 8, 23), (14, 74, 680, 'circle', 6, 25), (88, 72, 440, 72, 8, 17),
            (30, 8, 240, 48, 6, 15), (70, 88, 280, 'circle', 6, 21), (3, 45, 320, 'circle', 6, 18), (96, 44, 360, 64, 6, 20)]
    for i, (xp, yp, s, rad, w, per) in enumerate(spec):
        x = img(f'Shape {i+1}', _png(f'shape{i+1}.png', _shape(s, rad, w)), s + 4*w, s + 4*w, round(0.13*k, 3))
        gid = run(d.new); ph = i*0.9
        beh = (osc(gid, f'Shape {i+1} X', './1/100/101/1', 90, 2*per, phase=ph) + osc(gid, f'Shape {i+1} Y', './1/100/101/2', 80, 2*per*0.85, phase=ph + 1.1)
               + osc(gid, f'Shape {i+1} Tilt', './1/100/109/3', 0.21, 2*per*1.15, phase=ph + 2.0))
        _, x = run(lambda: d.group(f'Shape {i+1}', gid, children=x, px=(xp/100 - 0.5)*FW, py=(0.5 - yp/100)*FH, beh=beh))
        shapes = x + shapes
    out = option(3, 'Floating Shapes', shapes) + out

    ML = run(d.new)
    _, xml = run(lambda: d.group('Motion Layer', ML, children=out, op=STRENGTH))

    def publish(P):
        P(W_LAY, './2/100', 'Motion Layer'); P(ML, './1/200/202', 'Motion Strength'); P(W_SPD, './2/100', 'Motion Speed')
    return xml, publish
