# KhanFT Section Type 3 - Colour Field
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTDIR = os.environ.get('OUTDIR', '/home/claude/kft/out')
c = Card('KhanFT Section Type 3 – Colour Field'); d = c.d
FW, FH, OV = 3840, 2160, 500
EDGE = 1800   # card colour extends this far past the frame so its soft glows never show a trailing haze while it moves
NAVY = hexc('0f1a2c')
PRESETS = [('Amber', hexc('ffd35a'), hexc('f0a21e'), hexc('b86006')),
           ('Teal', hexc('7be6d2'), hexc('22a493'), hexc('0a5a53')),
           ('Coral', hexc('ffad90'), hexc('f0664b'), hexc('9e3121')),
           ('Indigo', hexc('7c89ff'), hexc('3a47cf'), hexc('171c63')),
           ('Sky', hexc('a6dcff'), hexc('3f9fe3'), hexc('114f87')),
           ('Rose', hexc('ffb7c9'), hexc('ea6f92'), hexc('8a2445')),
           ('Sage', hexc('d6e9b8'), hexc('97b46b'), hexc('4a6330')),
           ('Sand', hexc('f8e4ba'), hexc('dcb877'), hexc('8a6830')),
           ('Lilac', hexc('dccbff'), hexc('9c7ee6'), hexc('4c3492')),
           ('Custom', hexc('a8ec86'), hexc('4fae3c'), hexc('235c20'))]
ENTR = ['Cut', 'Fade', 'Zoom'] + DROP_IN + ['Fade Up', 'Rise In', 'Slide from Left', 'Slide from Right']
EXIT = ['Cut', 'Fade', 'Zoom Out'] + DROP_DOWN + DROP_OUT + ['Fade Down', 'Slide to Left', 'Slide to Right']
ENT0, EXT0 = ENTR.index('Drop In – Stretch'), EXIT.index('Drop Down – Stretch')   # defaults
T_IN, T_OUT = 1.0, END - 0.6

W_PRE = d.w_popup('Colour Preset', [p[0] for p in PRESETS], 0)
W_SHC = d.w_check('Show Counter', True)
W_PIPS = d.w_popup('Progress Pips', ['Off', '3', '4', '5', '6'], 2)
W_CUR = d.w_popup('Current Pip', ['1', '2', '3', '4', '5', '6'], 0)
W_ENT = d.w_popup('Entrance', ENTR, ENT0)
W_EXT = d.w_popup('Exit', EXIT, EXT0)
W_BLUR = c.hi(lambda: d.w_slider('Drop Blur Amount', 0.5, 0, 100), 'drop_id', 95000)
W_ESPD = c.hi(lambda: d.w_popup('Entrance Speed', SPEEDS, 1), 'drop_id', 95000)
W_XSPD = c.hi(lambda: d.w_popup('Exit Speed', SPEEDS, 1), 'drop_id', 95000)
c.W_FEEL = d.w_popup('Motion Feel', FEELS, 0)
W_PUSH = d.w_check('Slow Push-in', True)
c.W_RESET = d.w_check('Reset Layout', False)
P = d.publish

card_in, card_out = card_motion('in', 5800, 4100), card_motion('out', 5800, 4100)
def rise(delay, dist):
    def f(feel):
        dd = DUR[feel]
        if feel == 'Gentle Bounce':
            return dict(sx=[(0, 0.86), (delay, 0.86)] + keys(delay, dd, lambda p: 0.86+0.14*spring(p, ov=0.08))[1:],
                        op=[(0, 0), (delay, 0)] + keys(delay, dd*0.3, smooth)[1:])
        dist2 = dist*(0.6 if feel == 'Snappy' else 1)
        return dict(py=[(0, -dist2), (delay, -dist2)] + keys(delay, dd, lambda p: -dist2*(1-ease_out4(p)))[1:],
                    op=[(0, 0), (delay, 0)] + keys(delay, dd*0.6, smooth)[1:])
    return f

# ---------- backgrounds
bgs = ''; BG = {}
NEW_PRESETS = ('Sky', 'Rose', 'Sage', 'Sand', 'Lilac')   # added later: ids from the high range so older clips keep their settings
for i, (nm, hi, mid, edge) in enumerate(PRESETS):
    def make():
        g1, a = d.rect(f'{nm} Glow', 3000, 1900, hi, py=40, rnd=950, feather=1100)
        g2, m = d.rect(f'{nm} Mid', 4300, 3000, mid, rnd=1500, feather=1300)
        g3, b = d.rect(f'{nm} Edge', FW+2*EDGE, FH+2*EDGE, edge)
        gg = d.new()
        _, x = d.group(f'{nm} Background', gg, children=a+m+b, op=1 if i == 0 else 0,
                       beh=d.rig(f'Rig {nm}', gg, 'GRP', './1/200/202', W_PRE, [(j+1, 1 if j == i else 0) for j in range(len(PRESETS))], pname='Opacity'))
        return x, (g1, g2, g3)
    if nm in NEW_PRESETS:
        x, BG[nm] = c.hi(make, 'preset_hi', 90000)
    else:
        x, BG[nm] = make()
    bgs += x
_, backgrounds = d.group('Backgrounds', children=bgs)
vb = ''
for nm, w, h, x, y in (('Top', FW+1600, 900, 0, FH/2+150), ('Bottom', FW+1600, 900, 0, -FH/2-150),
                       ('Left', 900, FH+1600, -FW/2-150, 0), ('Right', 900, FH+1600, FW/2+150, 0)):
    _, r = d.rect(f'Vignette {nm}', w, h, (0, 0, 0), px=x, py=y, feather=750); vb += r
VIG, vig = d.group('Vignette', children=vb, op=0.25)
c.media['Media/Grain.png'] = os.path.join(SRC, 'Grain.png')
GR, _, grain = d.image('Grain', 'Grain', 'Media/Grain.png', 1920, 1080, dropzone=False, s=2.05, op=0.07)

# ---------- counter
CNT_SEQ = []
def cnt_beh(tid, sub):
    bid, x = d.seq_words('Counter Words', sub, 0.75, 0.75 + 0.6*WORD_MUL['Slow'], dy=0, spread=0, op0=0); CNT_SEQ.append(bid); c.seq_norm[bid] = 0.6
    ob, ox = c.out_seq('Counter Words Out', sub, 0.6); CNT_SEQ.append(ob); return x + ox
CNT, CNT_STY, cnt = d.text('Counter', 'অধ্যায় ১ / ৪', 104, NAVY, beh_fn=cnt_beh)
cnt = c.text_extras('Counter', CNT, cnt, pad=(50, 26))
CNTA = d.new(); c.burn(lambda: c.feel_links(CNTA, rise(0.0, 30)))
_, cnt = d.group('Counter Anim', CNTA, children=cnt, beh=c.text_anim('Counter', CNTA, 0.75, 30, seq=CNT_SEQ[0], default='Word by Word'))
CNTO = c.hi(d.new, 'out_id', 98000); cnt = d.group('Counter Out', CNTO, children=cnt, beh=c.text_out('Counter', CNTO, 30, seq=CNT_SEQ[1], lead=0.3))[1]
CNTS = d.new(); _, cnt = d.group('Counter Show', CNTS, children=cnt, beh=d.rig('Rig Show Counter', CNTS, 'GRP', './1/200/202', W_SHC, [(1, 0), (2, 1)], pname='Opacity'))
CNTP, cnt = c.place('Counter Position', cnt, 0, 235)
# ---------- title
TTL_FN, TTL_SEQ = c.word_seq('Title Words', 0.85, 2)
TTL, TTL_STY, ttl = d.text('Title', 'টাকার মনস্তত্ত্ব', 290, NAVY, beh_fn=TTL_FN)
ttl = c.text_extras('Title', TTL, ttl, pad=(90, 50))
TTLA = d.new(); c.burn(lambda: c.feel_links(TTLA, rise(0.06, 45)))
_, ttl = d.group('Title Anim', TTLA, children=ttl, beh=c.text_anim('Title', TTLA, 0.85, 45, seq=TTL_SEQ[0]))
TTLO = c.hi(d.new, 'out_id', 98000); ttl = d.group('Title Out', TTLO, children=ttl, beh=c.text_out('Title', TTLO, 45, seq=TTL_SEQ[1], lead=0.4))[1]
TTLP, ttl = c.place('Title Position', ttl, 0, -95)
# ---------- pips
PW, PH, PG = 130, 22, 32; PITCH = PW + PG; PIP_N = [0, 3, 4, 5, 6]
pips = ''
for i in range(1, 7):
    pid_, p = d.rect(f'Pip {i}', PW, PH, NAVY, px=(i-1)*PITCH, rnd=11, op=0.25 if i <= 4 else 0)
    p = p.replace('</scenenode>', d.rig(f'Rig Pip {i}', pid_, 'SHP', './1/200/202', W_PIPS, [(j+1, 0.25 if (n and i <= n) else 0) for j, n in enumerate(PIP_N)], pname='Opacity') + '</scenenode>')
    pips = p + pips
FILL, fill = d.rect('Active Pip', PW, PH, NAVY, rnd=11)
_, fill = d.group('Active Fill', children=fill, sx=[(0, 0), (0.3, 0)] + keys(0.3, 0.55, ease_out4)[1:], sy=1)
ACT = d.new(); _, fill = d.group('Active Pip Slot', ACT, children=fill, beh=d.rig('Rig Current Pip', ACT, 'GRP', './1/100/101/1', W_CUR, [(j+1, j*PITCH) for j in range(6)], pname='X', rng=B))
SH = d.new(); _, prow = d.group('Pips Row', SH, children=fill + pips, px=-1.5*PITCH,
                                 beh=d.rig('Rig Pip Centre', SH, 'GRP', './1/100/101/1', W_PIPS, [(j+1, -(max(n, 1)-1)/2*PITCH) for j, n in enumerate(PIP_N)], pname='X', rng=B))
PSH = d.new(); _, prow = d.group('Pips Show', PSH, children=prow, beh=d.rig('Rig Pips Show', PSH, 'GRP', './1/200/202', W_PIPS, [(j+1, 0 if n == 0 else 1) for j, n in enumerate(PIP_N)], pname='Opacity'))
prow = c.follow_out('Pips Out', prow, 'Title', 0.5)   # pips leave with the title, first
PIPP, prow = c.place('Pips Position', prow, 0, -830)

# ---------- publish (inspector order): colours > icon > counter > title > pips > animation > reset
ico = c.icon_block(px=0, py=640, size=0.85, t0=0.7, icon_lead=0.2)
P(W_ENT, './2/100', 'Entrance'); P(W_ESPD, './2/100', 'Entrance Speed'); P(W_EXT, './2/100', 'Exit'); P(W_XSPD, './2/100', 'Exit Speed'); P(W_BLUR, './2/100', 'Drop Blur Amount'); P(c.W_FEEL, './2/100', 'Motion Feel'); P(W_PUSH, './2/100', 'Slow Push-in')
P(W_PRE, './2/100', 'Colour Preset')
P(BG['Custom'][0], './2/353/113/111', 'Custom Light'); P(BG['Custom'][1], './2/353/113/111', 'Custom Mid'); P(BG['Custom'][2], './2/353/113/111', 'Custom Edge')
P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')
c.pub_extras('Icon')
P(CNT, './2/369', 'Counter Text'); P(W_SHC, './2/100', 'Show Counter'); P(CNT_STY, './14/16', 'Counter Colour')
c.pub_extras('Counter'); P(CNTP, './1/100/101', 'Counter Position')
P(TTL, './2/369', 'Title Text'); P(TTL_STY, './14/16', 'Title Colour')
c.pub_extras('Title'); P(TTLP, './1/100/101', 'Title Position')
P(W_PIPS, './2/100', 'Progress Pips'); P(W_CUR, './2/100', 'Current Pip'); P(FILL, './2/353/113/111', 'Pip Colour'); P(PIPP, './1/100/101', 'Pips Position')
P(c.W_RESET, './2/100', 'Reset Layout')

# ---------- assemble
PD = c.drv_group('Push Driver', dict(sx=[(0, 1), (T_IN, 1)] + keys(T_IN, T_OUT-T_IN, lambda p: 1+0.03*p, n=40)[1:]))
CONT = d.new()
lid, lx = d.link('Push-in', CONT, 'GRP', './1/100/105', PD, CH['sx'][2], mix=1)
_, content = d.group('Content', CONT, children=ico + cnt + ttl + prow, beh=lx + d.rig('Rig Push-in', lid, 'LNK', './207', W_PUSH, [(1, 0), (2, 1)], pname='Custom Mix'))
CO = d.new(); CI = d.new()
_, card = d.group('Card Out', CO, children=grain + vig + content + backgrounds, beh=c.drop_blur(EXIT, W_EXT, W_XSPD, W_BLUR, 4100, 'Exit') + c.style_links(CO, EXIT, W_EXT, EXT0, card_out, W_XSPD))
_, card = d.group('Card In', CI, children=card, beh=c.drop_blur(ENTR, W_ENT, W_ESPD, W_BLUR, 4100, 'Entrance') + c.style_links(CI, ENTR, W_ENT, ENT0, card_in, W_ESPD))
path, s = c.save(card, OUTDIR, markers=(2.4, END-2.0), thumb='/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/chk_2.png')
print('wrote', path, len(s))
