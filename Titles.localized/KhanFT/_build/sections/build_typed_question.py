# KhanFT Section Type 4 - Typed Question
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
SCR = '/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/'
FW, FH, OV = 3840, 2160, 500
EDGE = 1800   # card colour extends this far past the frame so its soft glows never show a trailing haze while it moves
WHITE = hexc('f4f6fa')
c = Card('KhanFT Section Type 4 – Typed Question'); d = c.d
PRESETS = [('Navy', hexc('24395a'), hexc('18263c'), hexc('0e1726')),
           ('Charcoal', hexc('34363c'), hexc('222428'), hexc('141517')),
           ('Forest', hexc('25453a'), hexc('183028'), hexc('0d1c17')),
           ('Plum', hexc('45284a'), hexc('2e1a33'), hexc('1b0f1e')),
           ('Custom', hexc('24395a'), hexc('18263c'), hexc('0e1726'))]
ENTR = ['Cut', 'Dissolve', 'Fade Up'] + DROP_IN + ['Fade', 'Zoom', 'Rise In', 'Slide from Left', 'Slide from Right']
EXIT = ['Cut', 'Fade'] + DROP_DOWN + DROP_OUT + ['Fade Down', 'Zoom Out', 'Slide to Left', 'Slide to Right']
ENT0, EXT0 = ENTR.index('Drop In – Stretch'), EXIT.index('Drop Down – Stretch')   # defaults
TYPE_SPEEDS = [('Normal', 1.9)]
T0 = 0.9
W_PRE = d.w_popup('Background', [p[0] for p in PRESETS], 0)
W_CUR = d.w_check('Show Cursor', True)
W_GRID = d.w_check('Show Grid', True)
W_ENT = d.w_popup('Entrance', ENTR, ENT0)
W_EXT = d.w_popup('Exit', EXIT, EXT0)
W_BLUR = c.hi(lambda: d.w_slider('Drop Blur Amount', 0.5, 0, 100), 'drop_id', 95000)
W_ESPD = c.hi(lambda: d.w_popup('Entrance Speed', SPEEDS, 1), 'drop_id', 95000)
W_XSPD = c.hi(lambda: d.w_popup('Exit Speed', SPEEDS, 1), 'drop_id', 95000)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
c.W_RESET = d.w_check('Reset Layout', False)
P = d.publish

card_in, card_out = card_motion('in', 5800, 4100), card_motion('out', 5800, 4100)
# ---------- background + grid
bgs = ''; BG = {}
for i, (nm, hi, mid, edge) in enumerate(PRESETS):
    g1, a = d.rect(f'{nm} Glow', 3000, 1900, hi, rnd=950, feather=1200)
    g2, m = d.rect(f'{nm} Mid', 4300, 3000, mid, rnd=1500, feather=1200)
    g3, b = d.rect(f'{nm} Edge', FW+2*EDGE, FH+2*EDGE, edge)
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
SEQS = []; OSEQ = []
def q_beh(tid, sub):
    x = ''
    for i, (nm, dur) in enumerate(TYPE_SPEEDS):
        bid, b = d.seq_words(f'Type {nm}', sub, T0, T0 + dur*WORD_MUL['Slow'], dy=0, spread=1, op0=0)
        c.seq_norm[bid] = dur; SEQS.append((bid, b)); x += b
        ob, ox = c.out_seq(f'Untype {nm}', sub, dur*0.6, spread=1); OSEQ.append(ob); x += ox
    return x
Q, QS, q = d.text('Question', 'আপনার টাকা আসলে কোথায় নিরাপদ?', 128, WHITE, beh_fn=q_beh)
# cursor: sits at the right edge of the text, appears when typing is done, blinks
CUR, cur = d.rect('Cursor', 9, 150, WHITE, py=45)
CB = d.new()
_, cur = d.group('Cursor Blink', CB, children=cur, op=0.5, beh=d.osc(CB, 'Blink', './1/200/202', 0.5, 55.0, phase=1.57)[1])
_, q = d.group('Question Hold', children=q, op=[(0, 0), (T0-0.01, 0), (T0, 1), (END, 1)])
QA = c.hi(d.new, 'text_id', 96000)
_, q = d.group('Question Anim', QA, children=q, beh=c.text_anim('Question', QA, T0, 30, seq=SEQS[0][0], default='Word by Word', rename={'Word by Word': 'Typewriter'}, speed_name='Typing Speed'))
W_TSPD = c.speed_w['Question'][0]
TYPE_END = {sp: TYPE_SPEEDS[0][1]*WORD_MUL[sp] for sp in WORD_SPEEDS}   # typing time per Typing Speed
src = c.drv_group('Cursor After Typing', dict(op=1))   # timing moved to 'Cursor Type Wait' (follows Typing Speed)
CH_ = d.new()
lid, lx = d.link('Cursor Timing', CH_, 'GRP', './1/200/202', src, CH['op'][2], mix=1)
_, cur = d.group('Cursor Timing', CH_, children=cur, beh=lx)
def cur_wait(sp): t = T0 + TYPE_END[sp]; return [(0, 0), (t, 0), (t + 0.04, 1), (END, 1)]
CW = c.hi(d.new, 'speed_id', 97000)
_, cur = d.group('Cursor Type Wait', CW, children=cur, op=cur_wait('Normal'),
                 beh=c.hi(lambda: d.rig('Rig Cursor Type Wait', CW, 'GRP', './1/200/202', W_TSPD, [(j+1, cur_wait(sp)) for j, sp in enumerate(WORD_SPEEDS)], pname='Opacity'), 'speed_id', 97000))
CSH = d.new()
al_id, al = d.align_to(Q, 3, ox=30, oy=0)
_, cursor = d.group('Cursor', CSH, children=cur, beh=al + d.rig('Rig Cursor', CSH, 'GRP', './1/200/202', W_CUR, [(1, 0), (2, 1)], pname='Opacity'))
# text box (was the "bar"): fits the question, grows from the centre while the words type on
BARG = d.new()
def bar_drv(feel):
    return dict(sx=1)   # the grow moved to 'Box Type Grow' (follows Typing Speed)
def bar_grow(sp):
    return [(0, 0.04), (T0-0.12, 0.04)] + keys(T0-0.12, TYPE_END[sp]+0.1, ease_io)[1:]
def grow(box):
    g = d.group('Box Grow', BARG, children=box, beh=c.feel_links(BARG, bar_drv), sy=1)[1]
    BW = c.hi(d.new, 'speed_id', 97000)
    return d.group('Box Type Grow', BW, children=g, sx=bar_grow('Normal'), sy=1,
                   beh=c.hi(lambda: d.rig('Rig Box Type Grow', BW, 'GRP', './1/100/105/1', W_TSPD, [(j+1, bar_grow(sp)) for j, sp in enumerate(WORD_SPEEDS)], pname='X'), 'speed_id', 97000))[1]
qx = c.text_extras('Question', Q, cursor + q, box_on=True, box_col=hexc('6ea0c8'), box_op=0.13, pad=(70, 40),
                   border=(hexc('aacdeb'), 3), shadow=(0, 40, 14), box_wrap=grow)
QO = c.hi(d.new, 'out_id', 98000); qx = d.group('Question Out', QO, children=qx, beh=c.text_out('Question', QO, 30, seq=OSEQ[0], lead=0.35, rename={'Word by Word': 'Typewriter'}))[1]
QP, qline = c.place('Question Position', qx, 0, -40)

ico = c.icon_block(px=0, py=520, size=0.8, show=False, t0=0.75, icon_lead=0.25)
P(W_ENT, './2/100', 'Entrance'); P(W_ESPD, './2/100', 'Entrance Speed'); P(W_EXT, './2/100', 'Exit'); P(W_XSPD, './2/100', 'Exit Speed'); P(W_BLUR, './2/100', 'Drop Blur Amount'); P(c.W_FEEL, './2/100', 'Motion Feel')
P(W_PRE, './2/100', 'Background')
P(BG['Custom'][0], './2/353/113/111', 'Custom Light'); P(BG['Custom'][1], './2/353/113/111', 'Custom Mid'); P(BG['Custom'][2], './2/353/113/111', 'Custom Edge')
P(W_GRID, './2/100', 'Show Grid'); P(GRID, './1/200/202', 'Grid Strength'); P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')
c.pub_extras('Icon')
P(Q, './2/369', 'Question'); P(QS, './14/16', 'Text Colour'); P(W_CUR, './2/100', 'Show Cursor')
c.pub_extras('Question'); P(QP, './1/100/101', 'Question Position')
P(c.W_RESET, './2/100', 'Reset Layout')

CONT = d.new(); _, content = d.group('Content', CONT, children=ico + qline)
CO = d.new(); CI = d.new()
_, card = d.group('Card Out', CO, children=grain + vig + content + grid + bgs, beh=c.drop_blur(EXIT, W_EXT, W_XSPD, W_BLUR, 4100, 'Exit') + c.style_links(CO, EXIT, W_EXT, EXT0, card_out, W_XSPD))
_, card = d.group('Card In', CI, children=card, beh=c.drop_blur(ENTR, W_ENT, W_ESPD, W_BLUR, 4100, 'Entrance') + c.style_links(CI, ENTR, W_ENT, ENT0, card_in, W_ESPD))
path, s = c.save(card, OUTDIR, markers=(3.9, END-2.0), thumb=SCR + 'chk_3.png')
print('wrote', path, len(s))
