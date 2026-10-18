# KhanFT Section Type 4 - Typed Question
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
SCR = '/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/'
FW, FH, OV = 3840, 2160, 500
WHITE = hexc('f4f6fa')
c = Card('KhanFT Section Type 4 – Typed Question'); d = c.d
PRESETS = [('Navy', hexc('24395a'), hexc('18263c'), hexc('0e1726')),
           ('Charcoal', hexc('34363c'), hexc('222428'), hexc('141517')),
           ('Forest', hexc('25453a'), hexc('183028'), hexc('0d1c17')),
           ('Plum', hexc('45284a'), hexc('2e1a33'), hexc('1b0f1e')),
           ('Custom', hexc('24395a'), hexc('18263c'), hexc('0e1726'))]
ENTR = ['Cut', 'Dissolve', 'Fade Up']
EXIT = ['Cut', 'Fade']
SPEEDS = [('Normal', 1.9)]
T0 = 0.3
W_PRE = d.w_popup('Background', [p[0] for p in PRESETS], 0)
W_CUR = d.w_check('Show Cursor', True)
W_BAR = d.w_check('Show Bar', True)
W_GRID = d.w_check('Show Grid', True)
W_ENT = d.w_popup('Entrance', ENTR, 1)
W_EXT = d.w_popup('Exit', EXIT, 0)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
c.W_RESET = d.w_check('Reset Layout', False)
P = d.publish

def card_in(st, feel):
    dd = DUR[feel]*(0.5 if st == 'Dissolve' else 1)
    if st == 'Dissolve': return dict(op=keys(0, 0.16, lambda p: p))
    return dict(op=keys(0, dd*0.7, smooth), py=keys(0, dd, lambda p: -80*(1-ease_out4(p))))
def card_out(st, feel):
    dd = DUR[feel]*0.7; t0 = END-dd-0.01
    return dict(op=[(0, 1), (t0, 1)] + keys(t0, dd, lambda q: 1-smooth(q))[1:])

# ---------- background + grid
bgs = ''; BG = {}
for i, (nm, hi, mid, edge) in enumerate(PRESETS):
    g1, a = d.rect(f'{nm} Glow', 3000, 1900, hi, rnd=950, feather=1200)
    g2, m = d.rect(f'{nm} Mid', 4300, 3000, mid, rnd=1500, feather=1200)
    g3, b = d.rect(f'{nm} Edge', FW+2*OV, FH+2*OV, edge)
    gg = d.new()
    _, x = d.group(f'{nm} Background', gg, children=a+m+b, op=1 if i == 0 else 0,
                   beh=d.rig(f'Rig {nm}', gg, 'GRP', './1/200/202', W_PRE, [(j+1, 1 if j == i else 0) for j in range(len(PRESETS))], pname='Opacity'))
    bgs += x; BG[nm] = (g1, g2, g3)
_, bgs = d.group('Backgrounds', children=bgs)
GRIDC = hexc('aacdeb'); STEP = 240; gl = ''
for k in range(-8, 9):
    _, r = d.rect(f'Grid V{k}', 3, FH+400, GRIDC, px=k*STEP); gl += r
for k in range(-4, 5):
    _, r = d.rect(f'Grid H{k}', FW+400, 3, GRIDC, py=k*STEP); gl += r
GRID = d.new()
_, grid = d.group('Grid', GRID, children=gl, op=0.07)
GSH = d.new(); _, grid = d.group('Grid Show', GSH, children=grid, beh=d.rig('Rig Grid', GSH, 'GRP', './1/200/202', W_GRID, [(1, 0), (2, 1)], pname='Opacity'))
vb = ''
for nm, w, h, x, y in (('Top', FW+1600, 900, 0, FH/2+150), ('Bottom', FW+1600, 900, 0, -FH/2-150),
                       ('Left', 900, FH+1600, -FW/2-150, 0), ('Right', 900, FH+1600, FW/2+150, 0)):
    _, r = d.rect(f'Vignette {nm}', w, h, (0, 0, 0), px=x, py=y, feather=750); vb += r
VIG, vig = d.group('Vignette', children=vb, op=0.35)
c.media['Media/Grain.png'] = os.path.join(SRC, 'Grain.png')
GR, _, grain = d.image('Grain', 'Grain', 'Media/Grain.png', 1920, 1080, dropzone=False, s=2.05, op=0.10)

# ---------- question: typed word by word; three speeds, only the chosen one is active
SEQS = []
def q_beh(tid, sub):
    x = ''
    for i, (nm, dur) in enumerate(SPEEDS):
        bid, b = d.seq_words(f'Type {nm}', sub, T0, T0+dur, dy=0, spread=1, op0=0)
        SEQS.append((bid, b)); x += b
    return x
Q, QS, q = d.text('Question', 'আপনার টাকা আসলে কোথায় নিরাপদ?', 128, WHITE, beh_fn=q_beh)
# cursor: sits at the right edge of the text, appears when typing is done, blinks
CUR, cur = d.rect('Cursor', 9, 150, WHITE, py=45)
CB = d.new()
_, cur = d.group('Cursor Blink', CB, children=cur, op=0.5, beh=d.osc(CB, 'Blink', './1/200/202', 0.5, 55.0, phase=1.57)[1])
_, q = d.group('Question Hold', children=q, op=[(0, 0), (T0-0.01, 0), (T0, 1), (END, 1)])
src = c.drv_group('Cursor After Typing', dict(op=[(0, 0), (T0+SPEEDS[0][1], 0), (T0+SPEEDS[0][1]+0.04, 1), (END, 1)]))
CH_ = d.new()
lid, lx = d.link('Cursor Timing', CH_, 'GRP', './1/200/202', src, CH['op'][2], mix=1)
_, cur = d.group('Cursor Timing', CH_, children=cur, beh=lx)
CSH = d.new()
al_id, al = d.align_to(Q, 3, ox=30, oy=0)
_, cursor = d.group('Cursor', CSH, children=cur, beh=al + d.rig('Rig Cursor', CSH, 'GRP', './1/200/202', W_CUR, [(1, 0), (2, 1)], pname='Opacity'))
# bar behind the text: grows from the centre while the words type on
BAR, bar = d.rect('Bar', 2300, 230, hexc('6ea0c8'), py=45, rnd=26, op=0.13, outline=(hexc('aacdeb'), 3))
BARG = d.new()
def bar_drv(feel):
    return dict(sx=[(0, 0.04), (T0-0.12, 0.04)] + keys(T0-0.12, SPEEDS[0][1]+0.1, ease_io)[1:])
_, bar = d.group('Bar Grow', BARG, children=bar, beh=c.feel_links(BARG, bar_drv), sy=1)
BSH = d.new(); _, bar = d.group('Bar Show', BSH, children=bar, beh=d.rig('Rig Bar', BSH, 'GRP', './1/200/202', W_BAR, [(1, 0), (2, 1)], pname='Opacity'))
QP, qline = c.place('Question Position', cursor + q + bar, 0, -40)

P(Q, './2/369', 'Question'); P(QS, './14/16', 'Text Colour')
P(W_PRE, './2/100', 'Background')
P(BG['Custom'][0], './2/353/113/111', 'Custom Light'); P(BG['Custom'][1], './2/353/113/111', 'Custom Mid'); P(BG['Custom'][2], './2/353/113/111', 'Custom Edge')
P(W_BAR, './2/100', 'Show Bar'); P(BAR, './2/353/113/111', 'Bar Colour'); P(BAR, './1/200/202', 'Bar Opacity'); P(BAR, './2/353/160/1', 'Bar Width')
P(W_CUR, './2/100', 'Show Cursor')
P(W_GRID, './2/100', 'Show Grid'); P(GRID, './1/200/202', 'Grid Strength')
P(W_ENT, './2/100', 'Entrance'); P(W_EXT, './2/100', 'Exit'); P(c.W_FEEL, './2/100', 'Motion Feel')
P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')
ico = c.icon_block(px=0, py=520, size=0.8, show=False, t0=0.2)
P(QP, './1/100/101', 'Question Position'); P(c.W_RESET, './2/100', 'Reset Layout')

CONT = d.new(); _, content = d.group('Content', CONT, children=ico + qline)
CO = d.new(); CI = d.new()
_, card = d.group('Card Out', CO, children=grain + vig + content + grid + bgs, beh=c.style_links(CO, EXIT, W_EXT, 0, card_out))
_, card = d.group('Card In', CI, children=card, beh=c.style_links(CI, ENTR, W_ENT, 1, card_in))
path, s = c.save(card, OUTDIR, markers=(T0 + 0.2, END-0.6), thumb=SCR + 'chk_3.png')
print('wrote', path, len(s))
