# KhanFT Paper - a title for showing documents: a page (screenshot) comes in as a paper card, with up to three
# highlights (start point + length, drawn from A to B), scroll for tall pages, zoom to a point, a second page that
# stacks on top, and entrance / exit styles. Timing that needs to land on a word is done with FCP keyframes on the
# published sliders (Draw, Scroll, Zoom, Stack); "Auto" options animate without keyframes.
import os, sys, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
HERE = os.path.dirname(os.path.abspath(__file__))
FW, FH = 3840, 2160
W, H, M = 2080, 1880, 28                # card size, page margin inside the card
PW, HIN = W - 2*M, H - 2*M              # page width, visible window height
PH_MIN, PH_MAX, PH0 = HIN, 12000, 2802  # Page Height range; default = the sample page
NAVY = hexc('10192b')
c = Card('KhanFT Paper'); d = c.d
P = d.publish

def ink_shadow(x, op, blur, dist):
    return x.replace('<parameter name="Lighting" id="230"',
                     '<parameter name="Drop Shadow" id="208" flags="8589940752"><foldFlags>131083</foldFlags>'
                     f'<parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="{op}"/>'
                     f'<parameter name="Blur" id="213" flags="8606711824" default="5" value="{blur}"/>'
                     f'<parameter name="Distance" id="212" flags="8606711824" default="5" value="{dist}"/>'
                     '<parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="4.7123889803846897"/></parameter>\n'
                     '<parameter name="Lighting" id="230"', 1)

def blend(x, mode):
    o = re.search(r'<parameter name="Opacity" id="202"[^>]*/>', x).group(0)
    return x.replace(o, o + f'<parameter name="Blend Mode" id="203" flags="8606777360" default="0" value="{mode}"/>', 1)

def g(name, children='', beh_fn=None, **kw):
    gid = d.new(); b = beh_fn(gid) if beh_fn else ''
    return gid, d.group(name, gid, children=children, beh=b, **kw)[1]

def rig_slider(name, target, chan, widget, lo, hi, pname, afffac='GRP'):
    return d.rig(name, target, afffac, chan, widget, [(1, lo), (2, hi)], pname=pname, rng=B)

def ease(p): return ease_io(p)
MID = 2.4 + (END - 2.0 - 2.4) / 2       # middle of the stretchable part of the clip

# ---------------- widgets (inspector order is set by the publish calls below)
ENTR = ['Paper Tilt', 'Rise In', 'Fade Up', 'Fade', 'Zoom', 'Slide from Right', 'Slide from Left'] + DROP_IN + ['Cut']
EXIT = ['Fall Back', 'Fade Down', 'Fade', 'Zoom Out', 'Slide to Left', 'Slide to Right'] + DROP_DOWN + DROP_OUT + ['Cut']
W_ENT = d.w_popup('Entrance', ENTR, 0)
W_ESPD = d.w_popup('Entrance Speed', SPEEDS, 1)
W_EXT = d.w_popup('Exit', EXIT, 0)
W_XSPD = d.w_popup('Exit Speed', SPEEDS, 1)
W_BLUR = d.w_slider('Drop Blur Amount', 0.5, 0, 100)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
BGS = ['None', 'Dim', 'Teal', 'Navy', 'Paper', 'Custom']
W_BG = d.w_popup('Background', BGS, 1)
W_PH = d.w_slider('Page Height', round((PH0 - PH_MIN) / (PH_MAX - PH_MIN), 5), PH_MIN, PH_MAX)
W_ASC = d.w_check('Auto Scroll', False)
W_SCR = d.w_slider('Scroll', 0, 0, 10000)
W_ZM = d.w_slider('Zoom', 0, 0, 200)        # extra zoom in %, 0 = none
W_SRC = d.w_check('Show Source', True)
STACK = ['Off', 'Auto', 'Manual']
W_STK = d.w_popup('Page 2', STACK, 0)
W_STA = d.w_slider('Stack', 0, 0, 100)

def tilt_in(feel, speed):
    dd = dur(feel, speed) * 1.15; f = arrive(feel); r = lambda p: 1 - f(p)
    return dict(py=keys(0.0, dd, lambda p: -700*r(p)), rx=keys(0.0, dd, lambda p: -0.55*r(p)), sx=keys(0.0, dd, lambda p: 1 - 0.08*r(p)),
                rz=keys(0.0, dd, lambda p: -0.05*r(p)), op=keys(0.0, dd*0.45, smooth))
def fall_back(feel, speed):
    dd = dur(feel, speed); t0 = END - dd - 0.02; gg = leave(feel)
    hold = lambda v: [(0, v), (t0, v)]; seg = lambda fn: keys(t0, dd, fn)[1:]
    return dict(rx=hold(0) + seg(lambda q: -0.75*gg(q)), sx=hold(1) + seg(lambda q: 1 - 0.25*smooth(q)),
                op=hold(1) + seg(lambda q: 1 - smooth(q)), py=hold(0) + seg(lambda q: 260*smooth(q)))
base_in, base_out = card_motion('in', 5200, 3200), card_motion('out', 5200, 3200)
def drv_in(st, feel, speed): return tilt_in(feel, speed) if st == 'Paper Tilt' else base_in(st, feel, speed)
def drv_out(st, feel, speed): return fall_back(feel, speed) if st == 'Fall Back' else base_out(st, feel, speed)

# ---------------- background (stays put while the card moves)
c.media['Media/Grain.png'] = os.path.join(SRC, 'Grain.png')
PRESETS = {'Teal': (hexc('7be6d2'), hexc('22a493'), hexc('0a5a53')), 'Navy': (hexc('24395a'), hexc('18263c'), hexc('0e1726')),
           'Paper': (hexc('fffbf2'), hexc('f6eedb'), hexc('e6d9bb')), 'Custom': (hexc('24395a'), hexc('18263c'), hexc('0e1726'))}
bgs = ''; BGC = {}
for i, nm in enumerate(BGS):
    if nm == 'None': continue
    if nm == 'Dim':
        DIMR, x = d.rect('Dim', FW + 400, FH + 400, (0, 0, 0), op=0.45)
    else:
        hi, mid, edge = PRESETS[nm]
        g1, a = d.rect(f'{nm} Glow', 3000, 1900, hi, rnd=950, feather=1200)
        g2, m = d.rect(f'{nm} Mid', 4300, 3000, mid, rnd=1500, feather=1200)
        g3, b = d.rect(f'{nm} Edge', FW + 400, FH + 400, edge)
        x = a + m + b; BGC[nm] = (g1, g2, g3)
    _, x = g(f'{nm} Background', x, op=1 if i == 1 else 0,
             beh_fn=lambda gid: d.rig(f'Rig {nm}', gid, 'GRP', './1/200/202', W_BG, [(j+1, 1 if j == i else 0) for j in range(len(BGS))], pname='Opacity'))
    bgs += x
_, background = g('Background', bgs, op=[(0, 0), (0.45, 1), (END - 0.55, 1), (END - 0.05, 0)])

# ---------------- page 1: card > window (crop) > zoom > scroll > [highlights + page image]
# highlights: origin = top centre of the visible window; Start = left end of the stroke
HL_STYLES = ['Highlighter', 'Underline', 'Box']
HL_DRAW = ['Auto', 'Keyframe']
HL0 = [dict(px=-479, py=-831, len=843, h=64, show=True, style=0), dict(px=-884, py=-1633, len=1768, h=104, show=True, style=2),
       dict(px=-884, py=-1915, len=556, h=64, show=False, style=0)]
HCOL = [hexc('ffd640'), hexc('ffd640'), hexc('ffd640')]
hl_xml = ''; HLW = []
for n, h0 in enumerate(HL0, 1):
    W_SH = d.w_check(f'Highlight {n}', h0['show'])
    W_ST = d.w_popup(f'Highlight {n} Style', HL_STYLES, h0['style'])
    W_DM = d.w_popup(f'Highlight {n} Draw', HL_DRAW, 0)
    W_DP = d.w_slider(f'Highlight {n} Progress', 1, 0, 100)
    W_LN = d.w_slider(f'Highlight {n} Length', round(h0['len'] / 3000, 5), 0, 3000)
    W_HT = d.w_slider(f'Highlight {n} Height', round(h0['h'] / 300, 5), 0, 300)
    L0 = h0['len']; shapes = ''
    HLR = None
    for si, st in enumerate(HL_STYLES):
        if st == 'Highlighter':
            sid, sx = d.rect(f'Highlight {n} Marker', L0, 64, HCOL[n-1], op=0.55, rnd=6); sx = blend(sx, 4); HLR = sid
        elif st == 'Underline':
            sid, sx = d.rect(f'Highlight {n} Underline', L0, 8, hexc('ec8c0d'), py=-34, rnd=4)
        else:
            sid, sx = d.rect(f'Highlight {n} Box', L0 + 24, 80, (1, 1, 1), rnd=10, fill=False, outline=(hexc('e0352b'), 7))
        sx = sx.replace('</scenenode>', d.rig(f'Rig Highlight {n} {st} Length', sid, 'SHP', './2/353/160/1', W_LN,
                                              [(1, 0 + (24 if st == 'Box' else 0)), (2, 3000 + (24 if st == 'Box' else 0))], pname='Width', rng=B) + '</scenenode>')
        _, sx = g(f'Highlight {n} {st}', sx, op=1 if si == h0['style'] else 0,
                  beh_fn=lambda gid: d.rig(f'Rig Highlight {n} {st}', gid, 'GRP', './1/200/202', W_ST, [(j+1, 1 if j == si else 0) for j in range(3)], pname='Opacity'))
        shapes += sx
    _, x = g(f'Highlight {n} Offset', shapes, px=L0/2, beh_fn=lambda gid: rig_slider(f'Rig Highlight {n} Offset', gid, './1/100/101/1', W_LN, 0, 1500, 'X'))
    _, x = g(f'Highlight {n} Thickness', x, sy=h0['h']/64, beh_fn=lambda gid: rig_slider(f'Rig Highlight {n} Height', gid, './1/100/105/2', W_HT, 0, 300/64, 'Y'))
    _, x = g(f'Highlight {n} Progress', x, sx=1, beh_fn=lambda gid: rig_slider(f'Rig Highlight {n} Progress', gid, './1/100/105/1', W_DP, 0, 1, 'X'))
    t0 = 1.15 + 0.45*(n-1)
    auto = [(0, 0), (t0, 0)] + keys(t0, 0.55, ease)[1:]
    _, x = g(f'Highlight {n} Auto Draw', x, sx=auto,
             beh_fn=lambda gid: d.rig(f'Rig Highlight {n} Draw', gid, 'GRP', './1/100/105/1', W_DM, [(1, auto), (2, 1)], pname='X'))
    HS, x = g(f'Highlight {n} Start', x, px=h0['px'], py=h0['py'])
    _, x = g(f'Highlight {n} Show', x, op=1 if h0['show'] else 0,
             beh_fn=lambda gid: d.rig(f'Rig Highlight {n} Show', gid, 'GRP', './1/200/202', W_SH, [(1, 0), (2, 1)], pname='Opacity'))
    hl_xml = x + hl_xml
    HLW.append((n, W_SH, W_ST, HLR, HS, W_LN, W_HT, W_DM, W_DP))
_, hls = g('Highlights', hl_xml, py=HIN/2)

# page image: a drop zone PW wide; Page Height sets its height and keeps its top at the window's top
c.media['Media/Paper Page 1.png'] = os.path.join(HERE, 'paper', 'Paper Page 1.png')
c.media['Media/Paper Page 2.png'] = os.path.join(HERE, 'paper', 'Paper Page 2.png')
DZ1, _, img1 = d.image('Page 1', 'Page 1', 'Media/Paper%20Page%201.png', PW, PH0, dropzone=True)
img1 = img1.replace('</scenenode>', rig_slider('Rig Page Height', DZ1, './2/314', W_PH, PH_MIN, PH_MAX, 'Height', afffac='IMG') + '</scenenode>')
top = lambda ph: HIN/2 - ph/2
_, img1 = g('Page Top', img1, py=top(PH0), beh_fn=lambda gid: rig_slider('Rig Page Top', gid, './1/100/101/2', W_PH, top(PH_MIN), top(PH_MAX), 'Y'))
content = hls + img1
# scroll: Scroll slider (px, keyframe it) + Auto Scroll (top to bottom across the middle of the clip)
_, content = g('Scroll', content, beh_fn=lambda gid: rig_slider('Rig Scroll', gid, './1/100/101/2', W_SCR, 0, 10000, 'Y'))
a0, a1 = 2.0, END - 2.3
def ascurve(ph): return [(0, 0), (a0, 0)] + keys(a0, a1 - a0, sine_io, n=24)[1:] if ph <= HIN else [(t, round(v*(ph - HIN), 2)) for t, v in [(0, 0), (a0, 0)] + keys(a0, a1 - a0, sine_io, n=24)[1:]]
ADRV = d.new()
c.drivers += d.group('Auto Scroll Driver', ADRV, py=ascurve(PH0),
                     beh=d.rig('Rig Auto Scroll', ADRV, 'GRP', './1/100/101/2', W_PH, [(1, ascurve(PH_MIN)), (2, ascurve(PH_MAX))], pname='Y'))[1]
SCA = d.new()
nm_, chan_, cc_, sc_ = CH['py']
lid, lx = d.link('Auto Scroll', SCA, 'GRP', chan_, ADRV, cc_, mix=0, scale=sc_)
_, content = d.group('Auto Scroll', SCA, children=content, beh=lx + d.rig('Rig Auto Scroll On', lid, 'LNK', './207', W_ASC, [(1, 0), (2, 1)], pname='Custom Mix'))
# zoom about Zoom Point: outer group at +P scales, inner group at -P (linked)
ZO, ZI = d.new(), d.new()
li = d.link('Zoom Point X', ZI, 'GRP', './1/100/101', ZO, [('1', './1/100/101/1')], mix=1, scale=-1)[1] + \
     d.link('Zoom Point Y', ZI, 'GRP', './1/100/101', ZO, [('2', './1/100/101/2')], mix=1, scale=-CH['py'][3])[1]
_, content = d.group('Zoom Inner', ZI, children=content, beh=li)
_, content = g('Zoom Y', content, beh_fn=lambda gid: rig_slider('Rig Zoom Y', gid, './1/100/105/2', W_ZM, 1, 3, 'Y'))
_, content = d.group('Zoom', ZO, children=content, beh=rig_slider('Rig Zoom X', ZO, './1/100/105/1', W_ZM, 1, 3, 'X'))
_, window = g('Page 1 Window', content, crop=(PW, HIN))
CARD1, card1 = d.rect('Page 1 Card', W, H, (0.99, 0.99, 0.985), rnd=22)
card1 = ink_shadow(card1, 0.45, 70, 34)
# stacking: when page 2 lands, page 1 steps back and darkens
SHA, sha = d.rect('Page 1 Shade Auto', W, H, (0, 0, 0), op=0, rnd=22)
sha = sha.replace('</scenenode>', d.rig('Rig Page 1 Shade Auto', SHA, 'SHP', './1/200/202', W_STK, [(1, 0), (2, [(0, 0), (MID - 0.5, 0)] + keys(MID - 0.5, 1.0, lambda p: 0.4*sine_io(p))[1:]), (3, 0)], pname='Opacity') + '</scenenode>')
SHM, shm = d.rect('Page 1 Shade Manual', W, H, (0, 0, 0), op=0, rnd=22)
shm = shm.replace('</scenenode>', rig_slider('Rig Page 1 Shade Manual', SHM, './1/200/202', W_STA, 0, 0.4, 'Opacity', afffac='SHP') + '</scenenode>')
_, shm = g('Page 1 Shade Manual On', shm, op=0,
           beh_fn=lambda gid: d.rig('Rig Page 1 Shade Manual On', gid, 'GRP', './1/200/202', W_STK, [(1, 0), (2, 0), (3, 1)], pname='Opacity'))
page1 = sha + shm + window + card1

# ---------------- page 2 (stacks on top)
DZ2, _, img2 = d.image('Page 2', 'Page 2', 'Media/Paper%20Page%202.png', PW, HIN, dropzone=True)
_, win2 = g('Page 2 Window', img2, crop=(PW, HIN))
CARD2, card2 = d.rect('Page 2 Card', W, H, (0.99, 0.99, 0.985), rnd=22)
card2 = ink_shadow(card2, 0.45, 70, 34)
page2 = win2 + card2
HID = dict(px=1300, py=-2600, rz=0.12)       # page 2 waiting off screen (bottom right)
LAND = dict(px=184, py=-72, rz=0.021)         # page 2 resting on top
BACK = dict(px=-280, py=88, s=0.92, dim=0.4)  # page 1 stepped back
def auto_curve(a, b, t0=MID - 0.5, dd=1.0):
    return [(0, a), (t0, a)] + keys(t0, dd, lambda p: a + (b - a)*arrive('Smooth')(p))[1:]
PN = dict(px='X', py='Y', rz='Z', sx='X', sy='Y')
def stack_layers(xml, prefix, chans):
    """chans: list of (key, channel, off_value, on_value). Each channel gets an Auto group (Page 2 menu) and a
    Manual group (Stack slider) - one rig per group."""
    for key, chan, v_off, v_on in chans:
        kw = {key: v_off}
        _, xml = g(f'{prefix} {key} Manual', xml, **{key: (1 if key in ('sx', 'sy') else 0)},
                   beh_fn=lambda gid: d.rig(f'Rig {prefix} {key} Manual', gid, 'GRP', chan, W_STA,
                                            [(1, 1 if key in ('sx', 'sy') else 0), (2, (v_on/v_off if key in ('sx', 'sy') else v_on - v_off))], pname=PN[key], rng=B))
        autos = [(1, v_off), (2, auto_curve(v_off, v_on)), (3, v_off)]
        _, xml = g(f'{prefix} {key} Auto', xml, **kw,
                   beh_fn=lambda gid: d.rig(f'Rig {prefix} {key} Auto', gid, 'GRP', chan, W_STK, autos, pname=PN[key]))
    return xml
page2 = stack_layers(page2, 'Page 2', [('px', './1/100/101/1', HID['px'], LAND['px']), ('py', './1/100/101/2', HID['py'], LAND['py']),
                                       ('rz', './1/100/109/3', HID['rz'], LAND['rz'])])
page1 = stack_layers(page1, 'Page 1', [('px', './1/100/101/1', 0.0001, BACK['px']), ('py', './1/100/101/2', 0.0001, BACK['py']),
                                       ('sx', './1/100/105/1', 1, BACK['s']), ('sy', './1/100/105/2', 1, BACK['s'])])

# ---------------- source line under the card
SRCT, SRCS, srct = d.text('Source', 'সূত্র: নমুনা প্রতিবেদন, ২০২৬', 56, (1, 1, 1), py=-H/2 - 110, font='KohinoorBangla-Semibold')
srct = ink_shadow(srct, 0.6, 18, 4) if '<parameter name="Lighting" id="230"' in srct else srct
_, srct = g('Source Show', srct, beh_fn=lambda gid: d.rig('Rig Source', gid, 'GRP', './1/200/202', W_SRC, [(1, 0), (2, 1)], pname='Opacity'))

# ---------------- card assembly + entrance / exit
stack = page2 + page1 + srct
CS, stack = g('Card Size', stack, sx=0.88, sy=0.88)
CP, stack = g('Card Position', stack)
CO = d.new(); CI = d.new()
_, cardx = d.group('Card Out', CO, children=stack, rx=1e-9,
                   beh=c.drop_blur(EXIT, W_EXT, W_XSPD, W_BLUR, 3200, 'Exit') + c.style_links(CO, EXIT, W_EXT, 0, drv_out, W_XSPD))
_, cardx = d.group('Card In', CI, children=cardx, rx=1e-9,
                   beh=c.drop_blur(ENTR, W_ENT, W_ESPD, W_BLUR, 3200, 'Entrance') + c.style_links(CI, ENTR, W_ENT, 0, drv_in, W_ESPD))

# ---------------- publish
P(W_ENT, './2/100', 'Entrance'); P(W_ESPD, './2/100', 'Entrance Speed'); P(W_EXT, './2/100', 'Exit'); P(W_XSPD, './2/100', 'Exit Speed')
P(W_BLUR, './2/100', 'Drop Blur Amount'); P(c.W_FEEL, './2/100', 'Motion Feel')
P(W_BG, './2/100', 'Background'); P(DIMR, './1/200/202', 'Dim Amount')
P(BGC['Custom'][0], './2/353/113/111', 'Custom Light'); P(BGC['Custom'][1], './2/353/113/111', 'Custom Mid'); P(BGC['Custom'][2], './2/353/113/111', 'Custom Edge')
P(DZ1, './1/324/300', 'Page 1 Image'); P(W_PH, './2/100', 'Page Height')
P(CP, './1/100/101', 'Card Position'); P(CS, './1/100/105', 'Card Size')
P(W_ASC, './2/100', 'Auto Scroll'); P(W_SCR, './2/100', 'Scroll')
P(W_ZM, './2/100', 'Zoom'); P(ZO, './1/100/101', 'Zoom Point')
for n, W_SH, W_ST, HLR, HS, W_LN, W_HT, W_DM, W_DP in HLW:
    P(W_SH, './2/100', f'Highlight {n}'); P(W_ST, './2/100', f'Highlight {n} Style'); P(HS, './1/100/101', f'Highlight {n} Start')
    P(W_LN, './2/100', f'Highlight {n} Length'); P(W_HT, './2/100', f'Highlight {n} Height'); P(HLR, './2/353/113/111', f'Highlight {n} Colour')
    P(W_DM, './2/100', f'Highlight {n} Draw'); P(W_DP, './2/100', f'Highlight {n} Progress')
P(W_STK, './2/100', 'Page 2'); P(DZ2, './1/324/300', 'Page 2 Image'); P(W_STA, './2/100', 'Stack')
P(SRCT, './2/369', 'Source Text'); P(W_SRC, './2/100', 'Show Source'); P(SRCS, './14/16', 'Source Colour')

_, root = d.group('KhanFT Paper', children=cardx + background)
path, s = c.save(root, OUTDIR, markers=(2.4, END - 2.0), thumb=os.path.join(HERE, 'paper', 'thumb_paper.png'))
print('wrote', path, len(s))
