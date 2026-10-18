# KhanFT Section Type 5 - Ledger Orbit
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import math

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
SCR = '/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/'
OB = os.path.join(SRC, 'orbit')
FW, FH, OV = 3840, 2160, 500
c = Card('KhanFT Section Type 5 – Ledger Orbit'); d = c.d
PRESETS = [('Graphite', hexc('202123'), hexc('151617'), hexc('0b0b0c')),
           ('Midnight', hexc('172033'), hexc('0f1624'), hexc('080b12')),
           ('Espresso', hexc('2a1e17'), hexc('1c140f'), hexc('0f0a07')),
           ('Custom', hexc('202123'), hexc('151617'), hexc('0b0b0c'))]
SETS = [('Coin and Stones', ['Gold Coin', 'Jade Stone', 'Grey Stone']),
        ('Three Coins', ['Gold Coin', 'Silver Coin', 'Bronze Coin']),
        ('Custom Images', [None, None, None])]
ENTR = ['Cut', 'Fade', 'Zoom']
EXIT = ['Cut', 'Fade', 'Zoom Out']
W_PRE = d.w_popup('Background', [p[0] for p in PRESETS], 0)
W_SET = d.w_popup('Objects', [s[0] for s in SETS], 0)
W_RING = d.w_check('Show Ring', True)
W_SPD = d.w_slider('Orbit Speed', 0.5, 0, 100)
W_ENT = d.w_popup('Entrance', ENTR, 0)
W_EXT = d.w_popup('Exit', EXIT, 0)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
c.W_RESET = d.w_check('Reset Layout', False)
P = d.publish

def card_in(st, feel):
    din = DUR[feel]
    if st == 'Fade': return dict(op=keys(0.0, din*0.6, smooth))
    f = (lambda p: 1.07 - 0.07*ease_out4(p)) if feel != 'Gentle Bounce' else (lambda p: 1.07 - 0.07*spring(p, ov=0.25))
    return dict(sx=keys(0.0, din, f), op=keys(0.0, din*0.5, smooth))
def card_out(st, feel):
    dout = DUR[feel]*0.7; t0 = END - dout - 0.02
    if st == 'Fade': return dict(op=[(0, 1), (t0, 1)] + keys(t0, dout, lambda q: 1-smooth(q))[1:])
    return dict(sx=[(0, 1), (t0, 1)] + keys(t0, dout, lambda q: 1+0.05*ease_in(q))[1:],
                op=[(0, 1), (t0, 1)] + keys(t0, dout, lambda q: 1-smooth(q))[1:])

# ---------- background
bgs = ''; BG = {}
for i, (nm, hi, mid, edge) in enumerate(PRESETS):
    g1, a = d.rect(f'{nm} Glow', 3000, 2000, hi, px=-500, rnd=1000, feather=1200)
    g2, m = d.rect(f'{nm} Mid', 4300, 3000, mid, rnd=1500, feather=1200)
    g3, b = d.rect(f'{nm} Edge', FW+2*OV, FH+2*OV, edge)
    gg = d.new()
    _, x = d.group(f'{nm} Background', gg, children=a+m+b, op=1 if i == 0 else 0,
                   beh=d.rig(f'Rig {nm}', gg, 'GRP', './1/200/202', W_PRE, [(j+1, 1 if j == i else 0) for j in range(len(PRESETS))], pname='Opacity'))
    bgs += x; BG[nm] = (g1, g2, g3)
_, bgs = d.group('Backgrounds', children=bgs)
c.media['Media/Lines.png'] = os.path.join(OB, 'Lines.png')
LN, _, lines = d.image('Lines', 'Lines', 'Media/Lines.png', 1920, 1080, dropzone=False, s=2.05, op=0.025)
c.media['Media/Grain.png'] = os.path.join(SRC, 'Grain.png')
GR, _, grain = d.image('Grain', 'Grain', 'Media/Grain.png', 1920, 1080, dropzone=False, s=2.05, op=0.08)
vb = ''
for nm, w, h, x, y in (('Top', FW+1600, 900, 0, FH/2+150), ('Bottom', FW+1600, 900, 0, -FH/2-150),
                       ('Left', 900, FH+1600, -FW/2-150, 0), ('Right', 900, FH+1600, FW/2+150, 0)):
    _, r = d.rect(f'Vignette {nm}', w, h, (0, 0, 0), px=x, py=y, feather=750); vb += r
VIG, vig = d.group('Vignette', children=vb, op=0.5)

# ---------- orbit (Rate-driven: spin a radius arm, counter-spin the object, squash the circle into an ellipse)
RX, RY = 560, 330; K = RY/RX
OMEGA = 2*math.pi/14.0
SLOT_SIZE = [1.0, 0.85, 0.8]
slots = ''; DZS = []; RATES = []
for i in range(3):
    imgs = ''
    for si, (snm, objs) in enumerate(SETS):
        nm = objs[i]
        vis = [(j+1, 1 if j == si else 0) for j in range(len(SETS))]
        if nm:
            rel = f'Media/{nm}.png'; c.media[rel] = os.path.join(OB, f'{nm}.png')
            iid, _, x = d.image(f'Slot {i+1} {nm}', f'Slot {i+1} {nm}', rel.replace(' ', '%20'), 600, 600, dropzone=False,
                                op=1 if si == 0 else 0, shadow=(0.55, 45, 50, 4.7124))
        else:
            iid, _, x = d.image(f'Custom Object {i+1}', f'Custom Object {i+1}', None, 600, 600, dropzone=True, op=0, shadow=(0.55, 45, 50, 4.7124))
            DZS.append(iid)
        x = x.replace('</scenenode>', d.rig(f'Rig Slot {i+1} {snm}', iid, 'IMG', './1/200/202', W_SET, vis, pname='Opacity') + '</scenenode>')
        imgs += x
    phi = math.radians(i*120 + 30)
    # object: counter-squash, counter-spin (+ a slow tumble of its own)
    _, g = d.group(f'Slot {i+1} Size', children=imgs, sx=SLOT_SIZE[i]*0.95, sy=SLOT_SIZE[i]*0.95)
    tb = d.new(); rid, rx = d.rate(tb, 'Tumble', './1/100/109/3', 0.12*(1 if i % 2 else -1)); RATES.append((rid, 0.12*(1 if i % 2 else -1)))
    _, g = d.group(f'Slot {i+1} Tumble', tb, children=g, beh=rx)
    _, g = d.group(f'Slot {i+1} Unsquash', children=g, sy=round(1/K, 5))
    cs = d.new(); rid, rx = d.rate(cs, 'Counter Spin', './1/100/109/3', round(-OMEGA, 5)); RATES.append((rid, -OMEGA))
    _, g = d.group(f'Slot {i+1} Upright', cs, children=g, rz=-phi, beh=rx)
    _, g = d.group(f'Slot {i+1} Arm', children=g, px=RX)
    sp = d.new(); rid, rx = d.rate(sp, 'Orbit Spin', './1/100/109/3', round(OMEGA, 5)); RATES.append((rid, OMEGA))
    _, g = d.group(f'Slot {i+1} Orbit', sp, children=g, rz=phi, beh=rx)
    slots += g
spd = ''.join(d.rig(f'Rig Orbit Speed {rid}', rid, 'RATE', './200', W_SPD, [(1, 0), (2, round(base*2, 5))], pname='Rate', rng=B) for rid, base in RATES)
_, slots = d.group('Ellipse', children=slots, sy=K, beh=spd)
c.media['Media/Ring.png'] = os.path.join(OB, 'Ring.png')
RING, _, ring = d.image('Ring', 'Ring', 'Media/Ring.png', 1400, 900, dropzone=False, op=0.35)
_, ring = d.group('Ring Fit', children=ring, sx=round(2*RX/1400, 4), sy=round(2*RY/900, 4))
RSH = d.new(); _, ring = d.group('Ring Show', RSH, children=ring, beh=d.rig('Rig Ring', RSH, 'GRP', './1/200/202', W_RING, [(1, 0), (2, 1)], pname='Opacity'))
_, orbit = d.group('Orbit Tilt', children=slots + ring, rz=-0.244)
def orbit_in(feel):
    dd = DUR[feel] + 0.3
    return dict(op=keys(0.0, dd*0.6, smooth), sx=keys(0.0, dd, lambda p: 0.9+0.1*(spring(p, ov=0.06) if feel == 'Gentle Bounce' else ease_out4(p))))
OA = d.new(); _, orbit = d.group('Orbit Anim', OA, children=orbit, beh=c.feel_links(OA, orbit_in))
OSZ = d.new(); _, orbit = d.group('Orbit Size', OSZ, children=orbit)
ORBP, orbit = c.place('Orbit Position', orbit, -1080, 0)

# ---------- chapter label, rule, title
LEFT = 170 + 1728
LBL, LBLS, lbl = d.text('Chapter Label', 'অধ্যায় ৩', 74, hexc('bdbcb8'), align=0)
def lbl_in(feel):
    dd = DUR[feel]
    return dict(op=[(0, 0), (0.15, 0)] + keys(0.15, dd*0.7, smooth)[1:], py=[(0, -20), (0.15, -20)] + keys(0.15, dd, lambda p: -20*(1-ease_out4(p)))[1:])
lbl = c.text_extras('Label', LBL, lbl, pad=(40, 22), box_col=(1, 1, 1), box_op=0.12)
LA = d.new(); _, lbl = d.group('Label Anim', LA, children=lbl, beh=c.feel_links(LA, lbl_in))
RULE, rule = d.rect('Rule', 1700, 3, hexc('ffffff'), px=850, op=0.3)
_, rule = d.group('Rule Draw', children=rule, px=-1328, py=24, sx=[(0, 0), (0.3, 0)] + keys(0.3, 0.9, ease_out4)[1:], sy=1)
LBLP, lbl = c.place('Label Position', lbl + rule, LEFT, 360)
def t_beh(t_in):
    def f(tid, sub):
        _, x = d.seq_words('Words Sharpen', sub, t_in, t_in+0.75, dy=-35, spread=40, op0=0, scale=1.12); return x
    return f
T1, T1S, t1 = d.text('Title Line 1', 'চক্রবৃদ্ধির', 205, hexc('eeeeee'), align=0, beh_fn=t_beh(0.4))
T2, T2S, t2 = d.text('Title Line 2', 'জাদু', 205, hexc('cfcfcf'), align=0, beh_fn=t_beh(0.62))
t1 = c.text_extras('Line 1', T1, t1, pad=(70, 40), box_col=(1, 1, 1), box_op=0.12)
t2 = c.text_extras('Line 2', T2, t2, pad=(70, 40), box_col=(1, 1, 1), box_op=0.12)
_, t1 = d.group('Line 1 Hold', children=t1, op=[(0, 0), (0.39, 0), (0.4, 1), (END, 1)])
_, t2 = d.group('Line 2 Hold', children=t2, op=[(0, 0), (0.61, 0), (0.62, 1), (END, 1)])
_, t2 = d.group('Line 2 Offset', children=t2, py=-250)
TTLP, ttl = c.place('Title Position', t1 + t2, LEFT, 30)

P(LBL, './2/369', 'Chapter Label'); P(T1, './2/369', 'Title Line 1'); P(T2, './2/369', 'Title Line 2')
P(LBLS, './14/16', 'Label Colour'); P(T1S, './14/16', 'Line 1 Colour'); P(T2S, './14/16', 'Line 2 Colour'); P(RULE, './1/200/202', 'Line Opacity')
c.pub_extras('Label'); c.pub_extras('Line 1'); c.pub_extras('Line 2')
P(W_SET, './2/100', 'Objects')
for k, dz in enumerate(DZS): P(dz, './1/324/300', f'Custom Object {k+1}')
P(W_SPD, './2/100', 'Orbit Speed'); P(W_RING, './2/100', 'Show Ring'); P(RING, './1/200/202', 'Ring Opacity')
P(W_PRE, './2/100', 'Background')
P(BG['Custom'][0], './2/353/113/111', 'Custom Light'); P(BG['Custom'][1], './2/353/113/111', 'Custom Mid'); P(BG['Custom'][2], './2/353/113/111', 'Custom Edge')
P(W_ENT, './2/100', 'Entrance'); P(W_EXT, './2/100', 'Exit'); P(c.W_FEEL, './2/100', 'Motion Feel')
P(VIG, './1/200/202', 'Vignette'); P(LN, './1/200/202', 'Line Texture'); P(GR, './1/200/202', 'Grain')
ico = c.icon_block(px=1300, py=-650, size=0.6, show=False, t0=0.5)
P(ORBP, './1/100/101', 'Orbit Position'); P(OSZ, './1/100/105', 'Orbit Size')
P(LBLP, './1/100/101', 'Label Position'); P(TTLP, './1/100/101', 'Title Position')
P(c.W_RESET, './2/100', 'Reset Layout')

CO = d.new(); CI = d.new()
_, card = d.group('Card Out', CO, children=vig + grain + lines + ico + ttl + lbl + orbit + bgs, beh=c.style_links(CO, EXIT, W_EXT, 0, card_out))
_, card = d.group('Card In', CI, children=card, beh=c.style_links(CI, ENTR, W_ENT, 0, card_in))
path, s = c.save(card, OUTDIR, markers=(1.4, END-0.6), thumb=SCR + 'chk_4.png')
print('wrote', path, len(s))
