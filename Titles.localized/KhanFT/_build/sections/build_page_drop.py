# KhanFT Section Type 2 - Page Drop (title) + Page Drop Transition
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
SCR = '/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/'
FW, FH, OV = 3840, 2160, 500
EDGE = 1800   # card colour extends this far past the frame so its soft glows never show a trailing haze while it moves
INK = hexc('15161b'); GREYTXT = hexc('6a6e80'); SLATE = hexc('3d3a4b')

# ======================================================= title
c = Card('KhanFT Section Type 2 – Page Drop'); d = c.d   # blur now per animation (Directional Blur), not project-wide
PRESETS = [('Cloud', hexc('ffffff'), hexc('eef0f5'), hexc('d9dde8')),
           ('Paper', hexc('fffdf6'), hexc('f5efe2'), hexc('e2d8c3')),
           ('Mint', hexc('ffffff'), hexc('e9f5f0'), hexc('cfe5dc')),
           ('Blush', hexc('ffffff'), hexc('f8eeee'), hexc('e9d6d6')),
           ('Custom', hexc('ffffff'), hexc('eef0f5'), hexc('d9dde8'))]
ENTR = ['Cut', 'Drop In – Blur', 'Rise In', 'Slide from Right', 'Fade'] + DROP_IN[1:] + ['Fade Up', 'Zoom', 'Slide from Left']
EXIT = ['Cut', 'Drop Down – Blur', 'Rise Out', 'Slide to Left', 'Fade'] + DROP_DOWN[1:] + DROP_OUT + ['Fade Down', 'Zoom Out', 'Slide to Right']
ENT0, EXT0 = ENTR.index('Drop In – Stretch'), EXIT.index('Drop Down – Stretch')   # defaults
W_PRE = d.w_popup('Card Colour', [p[0] for p in PRESETS], 0)
W_SHC = d.w_check('Show Counter', True)
W_ENT = d.w_popup('Entrance', ENTR, ENT0)
W_EXT = d.w_popup('Exit', EXIT, EXT0)
W_BLUR = c.hi(lambda: d.w_slider('Drop Blur Amount', 0.5, 0, 100), 'drop_id', 95000)
W_ESPD = c.hi(lambda: d.w_popup('Entrance Speed', SPEEDS, 1), 'drop_id', 95000)
W_XSPD = c.hi(lambda: d.w_popup('Exit Speed', SPEEDS, 1), 'drop_id', 95000)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
c.W_RESET = d.w_check('Reset Layout', False)
P = d.publish
DIST_Y, DIST_X = FH + 120, FW + 120                 # transition slate
TDY, TDX = FH//2 + EDGE + 100, FW//2 + EDGE + 100     # title card (fully off screen)

card_in, card_out = card_motion('in', TDX, TDY), card_motion('out', TDX, TDY)
def rise(delay, dist):
    def f(feel):
        dd = DUR[feel]*0.9; dl = delay*(0.7 if feel == 'Snappy' else 1)
        if feel == 'Gentle Bounce':
            return dict(py=[(0, -dist), (dl, -dist)] + keys(dl, dd, lambda p: -dist*(1-spring(p, ov=0.12)))[1:],
                        op=[(0, 0), (dl, 0)] + keys(dl, dd*0.35, smooth)[1:])
        return dict(py=[(0, -dist), (dl, -dist)] + keys(dl, dd, lambda p: -dist*(1-ease_out4(p)))[1:],
                    op=[(0, 0), (dl, 0)] + keys(dl, dd*0.6, smooth)[1:])
    return f

bgs = ''; BG = {}
for i, (nm, hi, mid, edge) in enumerate(PRESETS):
    g1, a = d.rect(f'{nm} Light', 2800, 2000, hi, px=-850, py=-30, rnd=1000, feather=1200)
    g2, m = d.rect(f'{nm} Base', 4200, 2900, mid, rnd=1400, feather=1100)
    g3, b = d.rect(f'{nm} Edge', FW+2*EDGE, FH+2*EDGE, edge)
    gg = d.new()
    _, x = d.group(f'{nm} Card', gg, children=a+m+b, op=1 if i == 0 else 0,
                   beh=d.rig(f'Rig {nm}', gg, 'GRP', './1/200/202', W_PRE, [(j+1, 1 if j == i else 0) for j in range(len(PRESETS))], pname='Opacity'))
    bgs += x; BG[nm] = (g1, g2, g3)
_, bgs = d.group('Card Colours', children=bgs)
c.media['Media/Grain.png'] = os.path.join(SRC, 'Grain.png')
GR, _, grain = d.image('Grain', 'Grain', 'Media/Grain.png', 1920, 1080, dropzone=False, s=2.05, op=0.05)

LEFT = -1640 + 1728          # text box anchor -> left edge at x=-1640
L1, L1S, l1 = d.text('Title Line 1', 'সঞ্চয় আগে,', 250, INK, align=0)
l1 = c.text_extras('Line 1', L1, l1, pad=(70, 40))
L1A = d.new(); _, l1 = d.group('Line 1 Anim', L1A, children=l1, beh=c.feel_links(L1A, rise(0.42, 60)))
L2, L2S, l2 = d.text('Title Line 2', 'খরচ পরে', 250, INK, align=0)
l2 = c.text_extras('Line 2', L2, l2, pad=(70, 40))
L2A = d.new(); _, l2 = d.group('Line 2 Anim', L2A, children=l2, beh=c.feel_links(L2A, rise(0.56, 60)))
_, l2 = d.group('Line 2 Offset', children=l2, py=-300)
TTLP, ttl = c.place('Title Position', l1 + l2, LEFT, 60)
CNT, CNTS_, cnt = d.text('Counter', '০২ / ০৫', 72, GREYTXT, align=0, tracking=2)
cnt = c.text_extras('Counter', CNT, cnt, pad=(40, 22))
CNTA = d.new(); _, cnt = d.group('Counter Anim', CNTA, children=cnt, beh=c.feel_links(CNTA, rise(0.7, 25)))
CSH = d.new(); _, cnt = d.group('Counter Show', CSH, children=cnt, beh=d.rig('Rig Show Counter', CSH, 'GRP', './1/200/202', W_SHC, [(1, 0), (2, 1)], pname='Opacity'))
CNTP, cnt = c.place('Counter Position', cnt, LEFT, 760)

ico = c.icon_block(px=1180, py=-40, size=1.3, show=True, t0=0.75)
P(W_ENT, './2/100', 'Entrance'); P(W_ESPD, './2/100', 'Entrance Speed'); P(W_EXT, './2/100', 'Exit'); P(W_XSPD, './2/100', 'Exit Speed'); P(W_BLUR, './2/100', 'Drop Blur Amount'); P(c.W_FEEL, './2/100', 'Motion Feel')
P(W_PRE, './2/100', 'Card Colour')
P(BG['Custom'][1], './2/353/113/111', 'Custom Card'); P(BG['Custom'][2], './2/353/113/111', 'Custom Edge'); P(GR, './1/200/202', 'Grain')
c.pub_extras('Icon')
P(CNT, './2/369', 'Counter Text'); P(W_SHC, './2/100', 'Show Counter'); P(CNTS_, './14/16', 'Counter Colour')
c.pub_extras('Counter'); P(CNTP, './1/100/101', 'Counter Position')
P(L1, './2/369', 'Title Line 1'); P(L1S, './14/16', 'Line 1 Colour'); c.pub_extras('Line 1')
P(L2, './2/369', 'Title Line 2'); P(L2S, './14/16', 'Line 2 Colour'); c.pub_extras('Line 2')
P(TTLP, './1/100/101', 'Title Position')
P(c.W_RESET, './2/100', 'Reset Layout')

CO = d.new(); CI = d.new()
_, card = d.group('Card Out', CO, children=grain + ico + cnt + ttl + bgs, beh=c.drop_blur(EXIT, W_EXT, W_XSPD, W_BLUR, TDY, 'Exit') + c.style_links(CO, EXIT, W_EXT, EXT0, card_out, W_XSPD))
_, card = d.group('Card In', CI, children=card, beh=c.drop_blur(ENTR, W_ENT, W_ESPD, W_BLUR, TDY, 'Entrance') + c.style_links(CI, ENTR, W_ENT, ENT0, card_in, W_ESPD))
path, s = c.save(card, OUTDIR, markers=(1.8, END-1.5), thumb=SCR + 'chk_1.png')
print('wrote', path, len(s))

# ======================================================= transition
t = Card('KhanFT Section Type 2 – Page Drop Transition', kind='transition', motion_blur=True); d = t.d
DIRS = ['Down', 'Up', 'Left', 'Right']
W_DIR = d.w_popup('Direction', DIRS, 0)
t.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
L = END   # the whole template = the transition
def vec(dirn):
    return {'Down': ('py', -1), 'Up': ('py', 1), 'Left': ('px', -1), 'Right': ('px', 1)}[dirn]
def a_out(dirn, feel):
    k, sg = vec(dirn); dist = DIST_Y if k == 'py' else DIST_X
    e = (lambda q: q**4) if feel == 'Snappy' else ease_in
    return {k: keys(0, L*0.42, lambda q: sg*dist*e(q))[:-1] + [(L*0.42, sg*dist), (L, sg*dist)]}
def b_in(dirn, feel):
    k, sg = vec(dirn); dist = DIST_Y if k == 'py' else DIST_X
    if feel == 'Gentle Bounce': f = lambda p: 1 - spring(p, ov=0.05, a=7)
    elif feel == 'Snappy': f = lambda p: 1 - ease_out4(p)
    else: f = lambda p: 1 - ease_out(p)
    t0 = L*0.5
    return {k: [(0, -sg*dist), (t0, -sg*dist)] + keys(t0, L-t0, lambda p: -sg*dist*f(p))[1:]}
AG = d.new(); BGp = d.new()
a_beh = t.style_links(AG, DIRS, W_DIR, 0, a_out)
b_beh = t.style_links(BGp, DIRS, W_DIR, 0, b_in)
_, A = d.group('A Move', AG, children=d.AB['Transition A'], beh=a_beh)
_, Bx = d.group('B Move', BGp, children=d.AB['Transition B'], beh=b_beh)
SL, slate = d.rect('Slate', FW+2*OV, FH+2*OV, SLATE)
P = d.publish
P(W_DIR, './2/100', 'Direction'); P(t.W_FEEL, './2/100', 'Motion Feel'); P(SL, './2/353/113/111', 'Slate Colour')
path, s = t.save(Bx + A + slate, OUTDIR)
print('wrote', path, len(s))
