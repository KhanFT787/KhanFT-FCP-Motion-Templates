import re
# common.py - pieces shared by all KhanFT section cards
import os, shutil, math
from kft import *

SRC = os.path.dirname(os.path.abspath(__file__))
FEELS = ['Smooth', 'Snappy', 'Gentle Bounce']
DUR = {'Smooth': 0.5, 'Snappy': 0.28, 'Gentle Bounce': 0.7}
ICONS = ['Savings', 'Bank', 'Gold', 'Stocks', 'Crypto', 'Loan']
CH = {'px': ('Pos X', './1/100/101', [('1', './1/100/101/1')], 1),
      'py': ('Pos Y', './1/100/101', [('2', './1/100/101/2')], 0.5625),
      'sx': ('Scale', './1/100/105', [('1', './1/100/105/1'), ('2', './1/100/105/2')], 1),
      'rz': ('Rotate', './1/100/109', [('3', './1/100/109/3')], 1),
      'op': ('Fade', './1/200/202', [('202', './1/200/202')], 1),
      'sy': ('Scale Y', './1/100/105', [('2', './1/100/105/2')], 1),
      'bl': ('Blur', './1/100/101', [('3', './1/100/101/3')], 1)}   # blur amount rides on a driver's Position Z


class Card:
    """Holds the Doc, the shared widgets (Motion Feel, Reset Layout) and the hidden driver groups."""
    def __init__(self, name, kind='title', motion_blur=False):
        self.name = name; self.kind = kind
        self.d = Doc(kind=kind, motion_blur=motion_blur)
        self.drivers = ''
        self.W_FEEL = None
        self.W_RESET = None
        self.media = {}            # relative path -> source file
        self.post_rigs = []        # (behaviour name regex, xml-fn) applied after save
        self.extras_pub = {}
        self.seq_norm = {}         # Sequence Text id -> reveal time at Normal word speed (behaviour spans the Slow time)
        self.speed_w = {}          # text label -> (word speed widget, published name)
        self.seq_out = {}          # word-by-word exit Sequence Text id -> its time at Normal out speed
        self.out_w = {}            # text label -> [(widget, published name)] for Text Out / Out Speed

    def pub_extras(self, label):
        w = getattr(self, 'text_in_w', {}).pop(label, None)
        if w: self.d.publish(w, './2/100', f'{label} Text In')
        sw = self.speed_w.pop(label, None)
        if sw: self.d.publish(sw[0], './2/100', sw[1])
        for w2, nm in self.out_w.pop(label, []): self.d.publish(w2, './2/100', nm)
        for o, c, n in self.extras_pub.pop(label, []): self.d.publish(o, c, n)

    # ---- per-text entrance ("<label> Text In" menu)
    def burn(self, fn):
        """run an old builder only to consume the same ids as before (keeps older clips' settings), discard its output"""
        keep = self.drivers; fn(); self.drivers = keep

    def text_anim(self, label, gid, delay, dist, seq=None, default='Rise', rename=None, speed_name='Word Speed'):
        """behaviours for the text's Anim group: every TEXT_IN style x Motion Feel, picked by '<label> Text In'.
        seq: the text's Sequence Text behaviour (word-by-word reveal) - its start opacity is switched by the menu."""
        d = self.d; band = ('text_id', 96000)
        di = TEXT_IN.index(default)
        W = self.hi(lambda: d.w_popup(f'{label} Text In', [(rename or {}).get(t, t) for t in TEXT_IN], di), *band)
        self.text_in_w = getattr(self, 'text_in_w', {}); self.text_in_w[label] = W
        beh = self.hi(lambda: self.style_links_basic(gid, TEXT_IN, W, di, text_motion(delay, dist)), *band)
        if seq:
            # base value must equal the default entry's snapshot, or FCP shows the base at the default
            self.seq_base = getattr(self, 'seq_base', {}); self.seq_base[seq] = 0 if default == 'Word by Word' else 1
            beh += self.hi(lambda: d.rig(f'Rig {label} Words', seq, 'SEQ', './1000/1044', W,
                                         [(j+1, 0 if s == 'Word by Word' else 1) for j, s in enumerate(TEXT_IN)], pname='Opacity'), *band)
            # word speed: the Sequence Text spans the Slow time; End Offset (frames) ends it earlier for Normal / Fast
            nd = self.seq_norm[seq]; slow = nd*WORD_MUL['Slow']
            offs = [round((slow - nd*WORD_MUL[sp])*FPS, 3) for sp in WORD_SPEEDS]
            sband = ('speed_id', 97000)
            W2 = self.hi(lambda: d.w_popup(f'{label} {speed_name}', WORD_SPEEDS, 1), *sband)
            self.speed_w[label] = (W2, f'{label} {speed_name}')
            self.seq_end = getattr(self, 'seq_end', {}); self.seq_end[seq] = offs[1]
            beh += self.hi(lambda: d.rig(f'Rig {label} Word Speed', seq, 'SEQ', './201/213', W2,
                                         [(j+1, o) for j, o in enumerate(offs)], pname='End Offset'), *sband)
        return beh

    def follow_out(self, name, children, label, lead):
        """wrap `children` so they leave with <label>'s Text Out / Out Speed (no words: Word by Word = Fade)"""
        d = self.d; W, WS, di = self.out_info[label]; band = ('follow_id', 140000)
        gid = self.hi(d.new, *band)
        beh = self.hi(lambda: self.style_links(gid, TEXT_OUT, W, di, text_out_motion(30, 0.6, lead, words=False), w_speed=WS), *band)
        return d.group(name, gid, children=children, beh=beh)[1]

    def word_seq(self, name, delay, nwords):
        """beh_fn for d.text(): a word-by-word Sequence Text (ids from the text band). Returns (fn, holder) - holder[0] = behaviour id."""
        holder = []
        def fn(tid, sub):
            def mk():
                nd = max(0.6, 0.2*nwords)
                bid, x = self.d.seq_words(name, sub, delay, delay + nd*WORD_MUL['Slow'], dy=0, spread=0, op0=0)
                self.seq_norm[bid] = nd; holder.append(bid)
                ob, ox = self.out_seq(name.replace('Words', 'Words Out'), sub, nd)
                holder.append(ob); return x + ox
            return self.hi(mk, 'text_id', 96000)
        return fn, holder

    def out_seq(self, name, sub, nd, spread=0):
        """word-by-word exit: Sequence Text 'To' opacity 0, from OUT_T0 to the clip end (ids from the out band).
        Its End Offset finishes it earlier for Normal / Fast out speed; holder of the text out menu switches it on."""
        def mk():
            bid, x = self.d.seq_words(name, sub, OUT_T0, END, dy=0, spread=spread, op0=0)
            old = '<parameter name="Sequencing" id="202" flags="8606777360" default="1" value="1"/>'
            assert x.count(old) == 1
            x = x.replace(old, old.replace('value="1"/>', 'value="0"/>'))
            self.seq_out[bid] = nd; return bid, x
        return self.hi(mk, 'out_id', 98000)

    def text_out(self, label, gid, dist, seq=None, rename=None, default='None', lead=0.35):
        """exit for one text: '<label> Text Out' (the Text In looks, reversed; default None = leaves with the card)
        and '<label> Out Speed'. Behaviours go on a wrapper group gid around the text's Anim group."""
        d = self.d; band = ('out_id', 98000)
        di = TEXT_OUT.index(default)
        W = self.hi(lambda: d.w_popup(f'{label} Text Out', [(rename or {}).get(t, t) for t in TEXT_OUT], di), *band)
        WS = self.hi(lambda: d.w_popup(f'{label} Out Speed', SPEEDS, 1), *band)
        self.out_w[label] = [(W, f'{label} Text Out'), (WS, f'{label} Out Speed')]
        self.out_info = getattr(self, 'out_info', {}); self.out_info[label] = (W, WS, di)
        nd = self.seq_out.get(seq, 0.6)
        beh = self.hi(lambda: self.style_links(gid, TEXT_OUT, W, di, text_out_motion(dist, nd, lead), w_speed=WS), *band)
        if seq:
            self.seq_base = getattr(self, 'seq_base', {}); self.seq_base[seq] = 1     # off at the default (None)
            offs = [round((END - (OUT_T0 + nd*SPD[sp]))*FPS, 3) for sp in SPEEDS]
            self.seq_end = getattr(self, 'seq_end', {}); self.seq_end[seq] = offs[1]
            beh += self.hi(lambda: d.rig(f'Rig {label} Words Out', seq, 'SEQ', './1000/1044', W,
                                         [(j+1, 0 if s == 'Word by Word' else 1) for j, s in enumerate(TEXT_OUT)], pname='Opacity'), *band)
            beh += self.hi(lambda: d.rig(f'Rig {label} Out Speed', seq, 'SEQ', './201/213', WS,
                                         [(j+1, o) for j, o in enumerate(offs)], pname='End Offset'), *band)
        return beh

    # ---- drivers
    def drv_group(self, name, kk):
        d = self.d
        gid, x = d.group(name, px=kk.get('px', 0), py=kk.get('py', 0), sx=kk.get('sx', 1), sy=kk.get('sy', kk.get('sx', 1)),
                         rz=kk.get('rz', 0), op=kk.get('op', 1))
        self.drivers += x
        return gid

    def feel_links(self, target, drv_fn):
        d = self.d; beh = ''
        for fi, feel in enumerate(FEELS):
            kk = drv_fn(feel)
            vid = self.drv_group(f'{target} {feel}', kk)
            for k in kk:
                nm, chan, cc, sc = CH[k]
                lid, lx = d.link(f'{feel} {nm}', target, 'GRP', chan, vid, cc, mix=1 if fi == 0 else 0, scale=sc)
                beh += lx + d.rig(f'Rig {feel} {nm}', lid, 'LNK', './207', self.W_FEEL, [(j+1, 1 if j == fi else 0) for j in range(3)], pname='Custom Mix')
        return beh

    def style_links_basic(self, target, styles, w_style, default, drv_fn):
        d = self.d; beh = ''
        for si, st in enumerate(styles):
            if st in ('Cut', 'None'): continue
            sel = d.new(); kinds = list(drv_fn(st, FEELS[0]).keys())
            sb = ''
            for fi, feel in enumerate(FEELS):
                vid = self.drv_group(f'{st} {feel}', drv_fn(st, feel))
                for k in kinds:
                    nm, chan, cc, sc = CH[k]
                    lid, lx = d.link(f'{feel} {nm}', sel, 'GRP', chan, vid, cc, mix=1 if fi == 0 else 0, scale=sc)
                    sb += lx + d.rig(f'Rig {feel} {nm}', lid, 'LNK', './207', self.W_FEEL, [(j+1, 1 if j == fi else 0) for j in range(3)], pname='Custom Mix')
            _, x = d.group(f'Selector {st}', sel, beh=sb); self.drivers += x
            for k in kinds:
                nm, chan, cc, sc = CH[k]
                lid, lx = d.link(f'{st} {nm}', target, 'GRP', chan, sel, cc, mix=1 if si == default else 0, scale=sc)
                beh += lx + d.rig(f'Rig {st} {nm}', lid, 'LNK', './207', w_style, [(j+1, 1 if j == si else 0) for j in range(len(styles))], pname='Custom Mix')
        return beh

    def style_links(self, target, styles, w_style, default, drv_fn, w_speed=None):
        """styles x Motion Feel x Speed. Chain per style: (feel drivers) -> speed selector (Motion Feel rig)
        -> style selector (Speed rig) -> target (style menu rig). One rig per link.
        Without w_speed (the transition) drv_fn(st, feel) and the older two-stage chain are used."""
        if w_speed is None: return self.style_links_basic(target, styles, w_style, default, drv_fn)
        d = self.d; beh = ''
        for si, st in enumerate(styles):
            if st in ('Cut', 'None'): continue
            kinds = [k for k in drv_fn(st, FEELS[0], 'Normal').keys() if k != 'bl']
            sel = d.new(); selb = ''
            for pi, sp in enumerate(SPEEDS):
                ss = d.new(); sb = ''
                for fi, feel in enumerate(FEELS):
                    kk = {k: v for k, v in drv_fn(st, feel, sp).items() if k != 'bl'}
                    vid = self.drv_group(f'{st} {sp} {feel}', kk)
                    for k in kinds:
                        nm, chan, cc, sc = CH[k]
                        lid, lx = d.link(f'{feel} {nm}', ss, 'GRP', chan, vid, cc, mix=1 if fi == 0 else 0, scale=sc)
                        sb += lx + d.rig(f'Rig {feel} {nm}', lid, 'LNK', './207', self.W_FEEL, [(j+1, 1 if j == fi else 0) for j in range(3)], pname='Custom Mix')
                _, x = d.group(f'Selector {st} {sp}', ss, beh=sb); self.drivers += x
                for k in kinds:
                    nm, chan, cc, sc = CH[k]
                    lid, lx = d.link(f'{sp} {nm}', sel, 'GRP', chan, ss, cc, mix=1 if sp == 'Normal' else 0, scale=sc)
                    selb += lx + d.rig(f'Rig {sp} {nm}', lid, 'LNK', './207', w_speed, [(j+1, 1 if j == pi else 0) for j in range(3)], pname='Custom Mix')
            _, x = d.group(f'Selector {st}', sel, beh=selb); self.drivers += x
            snaps = [(j+1, 1 if j == si else 0) for j in range(len(styles))]
            for k in kinds:
                nm, chan, cc, sc = CH[k]
                lid, lx = d.link(f'{st} {nm}', target, 'GRP', chan, sel, cc, mix=1 if si == default else 0, scale=sc)
                beh += lx + d.rig(f'Rig {st} {nm}', lid, 'LNK', './207', w_style, snaps, pname='Custom Mix')
        return beh

    # ---- a draggable/positionable group that snaps back when "Reset Layout" is ticked
    def place(self, name, children, px, py, extra_beh=''):
        d = self.d; gid = d.new()
        src = self.drv_group(f'{name} Default', dict(px=px, py=py))
        beh = extra_beh
        for k in ('px', 'py'):
            nm, chan, cc, sc = CH[k]
            lid, lx = d.link(f'Reset {nm}', gid, 'GRP', chan, src, cc, mode=2, mix=0, scale=sc)
            beh += lx + d.rig(f'Rig Reset {nm}', lid, 'LNK', './207', self.W_RESET, [(1, 0), (2, 1)], pname='Custom Mix')
        _, x = d.group(name, gid, children=children, px=px, py=py, beh=beh)
        return gid, x

    # ---- float wiring. Motion honours only ONE rig per object, so amount and on/off live on separate links:
    #      source (oscillators) -> '<label> Float Amount' driver (link Scale rigged by Amount) -> target (link Custom Mix rigged by On)
    def hi(self, fn, band='hi_id', start=80000):
        """allocate ids from a separate high range so ids of earlier builds stay put (clips keep their settings).
        Each later feature gets its own band so adding one never shifts another's ids."""
        d = self.d; keep = d.nid[0]; d.nid[0] = getattr(self, band, start)
        try: return fn()
        finally: setattr(self, band, d.nid[0]); d.nid[0] = keep

    def drop_blur(self, styles, w_style, w_speed, w_amt, dy, prefix):
        """Directional Blur per blur look, keyframed from the drop speed. Blur look: Amount follows the Speed menu
        (animated rig), Mix is switched on by the Entrance/Exit menu. Adjustable look: Amount follows the slider."""
        d = self.d; x = ''
        for st in styles:
            if not (st.endswith('– Blur') or st.endswith('– Blur (Adjustable)')): continue
            gate = [(j+1, 1 if s2 == st else 0) for j, s2 in enumerate(styles)]
            profs = {sp: drop_style(st, 'Smooth', dy, sp)['bl'] for sp in SPEEDS}
            def mk():
                fid, fx = d.dir_blur(f'{prefix} {st}', amount=0)
                r = d.rig(f'Rig {st} On', fid, 'FILT', './10001', w_style, gate, pname='Mix')
                if st.endswith('(Adjustable)'):
                    pr = profs['Normal']
                    r += d.rig(f'Rig {st} Amount', fid, 'FILT', './1', w_amt, [(1, [(t, 0) for t, _ in pr]), (2, [(t, 2*v) for t, v in pr])], pname='Amount', rng=B)
                else:
                    r += d.rig(f'Rig {st} Speed', fid, 'FILT', './1', w_speed, [(j+1, profs[sp]) for j, sp in enumerate(SPEEDS)], pname='Amount', rng=B)
                return fx + r
            x += self.hi(mk, 'drop_id', 95000)
        return x

    def float_links(self, label, target, src, w_on, w_amt, on):
        # ids: the target links/rigs keep the exact ids of the earlier build (so clips already in a timeline keep
        # their settings); everything new is allocated from a separate high range.
        d = self.d; hi = self.hi
        AMT = hi(d.new); ab = ''; fb = ''
        for nm, chan, chs, sc in (('Float Y', './1/100/101', [('2', './1/100/101/2')], 0.5625), ('Float Tilt', './1/100/109', [('3', './1/100/109/3')], 1.0)):
            lid, lx = d.link(nm, target, 'GRP', chan, AMT, chs, mode=0, mix=1 if on else 0, scale=sc)
            fb += lx + d.rig(f'Rig {nm} On', lid, 'LNK', './207', w_on, [(1, 0), (2, 1)], pname='Custom Mix')
            d.new()   # id formerly used by the amount rig
            def amt():
                alid, alx = d.link(f'{nm} Amount', AMT, 'GRP', chan, src, chs, mode=0, scale=0.9*sc)
                return alx + d.rig(f'Rig {nm} Amount', alid, 'LNK', './204', w_amt, [(1, 0), (2, 3*sc)], pname='Scale', rng=B)
            ab += hi(amt)
        _, x = d.group(f'{label} Float Amount', AMT, beh=ab); self.drivers += x
        return fb

    # ---- per-text extras: a box that fits the text (live bounds via Align To markers) + its own float
    def text_extras(self, label, tid, text_xml, box_on=False, float_on=False, box_col=(1, 1, 1), box_op=0.9,
                    pad=(60, 34), rnd=26, border=None, shadow=(0.25, 40, 14), box_wrap=None, float_speed=0.3,
                    offset_x=None, shadow_layer=False, box_dy=None):
        """returns xml: Float group > [text, edge markers, box]. Publishes '<label> …' controls."""
        d = self.d; P = d.publish
        K, KY = 4.0, 2.25
        W_BOX = d.w_check(f'{label} Box', box_on)
        W_PX = d.w_slider(f'{label} Box Padding X', round(pad[0]/300, 4), 0, 300)
        W_PY = d.w_slider(f'{label} Box Padding Y', round(pad[1]/200, 4), 0, 200)
        W_FL = d.w_check(f'{label} Float', float_on)
        W_FA = d.w_slider(f'{label} Float Amount', 0.3, 0, 100)
        W_FS = d.w_slider(f'{label} Float Speed', float_speed, 0, 100)
        # padded edge markers (invisible 2x2 shapes aligned to the text's edges)
        M = {}; mk = ''
        for nm, code, axis, wid, mx, chan in (('L', 2, -1, W_PX, 300, './203/1'), ('R', 3, 1, W_PX, 300, './203/1'),
                                             ('T', 4, 1, W_PY, 200, './203/2'), ('B', 5, -1, W_PY, 200, './203/2')):
            mid, m = d.rect(f'{label} Edge {nm}', 2, 2, (1, 0, 0), op=0)
            ox = axis*pad[0] if nm in 'LR' else 0; oy = axis*pad[1] if nm in 'TB' else 0
            aid, ax = d.align_to(tid, code, ox=ox, oy=oy)
            ax += d.rig(f'Rig Pad {nm}', aid, 'ALIGN', chan, wid, [(1, 0), (2, axis*mx)], pname='X' if nm in 'LR' else 'Y', rng=B)
            M[nm] = mid; mk += m.replace('</scenenode>', ax + '</scenenode>')
        X_, Y_ = './1/100/101/1', './1/100/101/2'
        def L(nm, chan, src, sc, tgt, scale, mode=0, target=None):
            return d.link(nm, target or BX, 'SHP', chan, src, [(tgt, sc)], mode=mode, scale=scale)[1]
        def fit_links(t=None):
            return (L('W minus L', './2/353/160/1', M['L'], X_, '1', -K, target=t) + L('W from R', './2/353/160/1', M['R'], X_, '1', K, mode=2, target=t) +
                    L('H minus B', './2/353/160/2', M['B'], Y_, '2', -KY, target=t) + L('H from T', './2/353/160/2', M['T'], Y_, '2', KY, mode=2, target=t) +
                    L('X from L', './1/100/101', M['L'], X_, '1', 0.5, target=t) + L('X from R', './1/100/101', M['R'], X_, '1', 0.5, mode=2, target=t) +
                    L('Y from B', './1/100/101', M['B'], Y_, '2', 0.5, target=t) + L('Y from T', './1/100/101', M['T'], Y_, '2', 0.5, mode=2, target=t))
        BX = d.new()
        fit = (L('W minus L', './2/353/160/1', M['L'], X_, '1', -K) + L('W from R', './2/353/160/1', M['R'], X_, '1', K, mode=2) +
               L('H minus B', './2/353/160/2', M['B'], Y_, '2', -KY) + L('H from T', './2/353/160/2', M['T'], Y_, '2', KY, mode=2) +
               L('X from L', './1/100/101', M['L'], X_, '1', 0.5) + L('X from R', './1/100/101', M['R'], X_, '1', 0.5, mode=2) +
               L('Y from B', './1/100/101', M['B'], Y_, '2', 0.5) + L('Y from T', './1/100/101', M['T'], Y_, '2', 0.5, mode=2))
        _, box = d.rect(f'{label} Box', 600, 200, box_col, op=box_op, rnd=rnd, outline=border or ((1, 1, 1), 0))
        box = re.sub(r'<scenenode name="[^"]*" id="\d+"', f'<scenenode name="{label} Box" id="{BX}"', box, 1)
        so, sb, sd = shadow
        box = box.replace('<parameter name="Lighting" id="230"',
                          '<parameter name="Drop Shadow" id="208" flags="8589940752"><foldFlags>131083</foldFlags>'
                          f'<parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="{so}"/>'
                          f'<parameter name="Blur" id="213" flags="8606711824" default="5" value="{sb}"/>'
                          f'<parameter name="Distance" id="212" flags="8606711824" default="5" value="{sd}"/>'
                          '<parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="4.7123889803846897"/></parameter>\n'
                          '<parameter name="Lighting" id="230"', 1)
        box = box.replace('</scenenode>', fit + '</scenenode>')
        if shadow_layer:   # a separate soft shadow under the box: stays visible however see-through the box is
            def mk_shadow():
                SHX = d.new()
                _, sh = d.rect(f'{label} Box Shadow Shape', 600, 200, (0, 0, 0), rnd=rnd, feather=80)
                sh = re.sub(r'<scenenode name="[^"]*" id="\d+"', f'<scenenode name="{label} Box Shadow Shape" id="{SHX}"', sh, 1)
                sh = sh.replace('<parameter name="Feather" id="102" flags="8606744592"', '<parameter name="Feather" id="102" flags="8606711824"', 1)
                sh = sh.replace('</scenenode>', fit_links(SHX) + '</scenenode>')
                W_SD = d.w_slider(f'{label} Box Shadow Distance', 0.15, 0, 200)
                SD = d.new()
                _, sh = d.group(f'{label} Box Shadow Drop', SD, children=sh, py=-30,
                                beh=d.rig(f'Rig {label} Shadow Distance', SD, 'GRP', './1/100/101/2', W_SD, [(1, 0), (2, -200)], pname='Y', rng=B))
                # cut-out: a copy of the box shape (Silhouette Alpha) so the shadow only shows outside the see-through box
                CUT = d.new()
                _, cut = d.rect(f'{label} Box Shadow Cutout', 600, 200, (1, 1, 1), rnd=rnd)
                cut = re.sub(r'<scenenode name="[^"]*" id="\d+"', f'<scenenode name="{label} Box Shadow Cutout" id="{CUT}"', cut, 1)
                cut = cut.replace('</scenenode>', fit_links(CUT) + '</scenenode>')
                o = re.search(r'<parameter name="Opacity" id="202"[^>]*/>', cut).group(0)
                cut = cut.replace(o, o + '<parameter name="Blend Mode" id="203" flags="8606777360" default="0" value="27"/>', 1)
                SG = d.new()
                _, sh = d.group(f'{label} Box Shadow', SG, children=cut + sh, op=0)
                o = '<parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/>'
                assert o in sh
                sh = sh.replace(o, o + '<parameter name="Blend Mode" id="203" flags="8606779408" default="34" value="0"/>', 1)
                return SHX, SG, W_SD, sh
            SHX, SG, W_SD, sh = self.hi(mk_shadow, 'tq_id', 160000)
            box += sh
        # vertical offset: Bangla fonts reserve a deep descender, so the measured text bounds sit low on the
        # visible letters. Default lift scales with the font size; adjustable per clip (-300..300 px).
        dy = round(0.38 * d.text_sizes.get(tid, 120)) if box_dy is None else box_dy
        def offset_grp():
            W_OY = d.w_slider(f'{label} Box Offset Y', round((dy + 300) / 600, 4), -300, 300)
            OG = d.new()
            _, x = d.group(f'{label} Box Offset', OG, children=box, py=dy,
                           beh=d.rig(f'Rig {label} Box Offset', OG, 'GRP', './1/100/101/2', W_OY, [(1, -300), (2, 300)], pname='Y', rng=B))
            return W_OY, x
        W_OY, box = self.hi(offset_grp)
        W_OX = None
        if offset_x is not None:
            def offset_x_grp():
                W = d.w_slider(f'{label} Box Offset X', round((offset_x + 300) / 600, 4), -300, 300)
                OX = d.new()
                _, x = d.group(f'{label} Box Offset X', OX, children=box, px=offset_x,
                               beh=d.rig(f'Rig {label} Box Offset X', OX, 'GRP', './1/100/101/1', W, [(1, -300), (2, 300)], pname='X', rng=B))
                return W, x
            W_OX, box = self.hi(offset_x_grp, 'tq_id', 160000)
        BS = d.new()
        _, box = d.group(f'{label} Box Show', BS, children=box, op=1 if box_on else 0,
                         beh=d.rig(f'Rig {label} Box', BS, 'GRP', './1/200/202', W_BOX, [(1, 0), (2, 1)], pname='Opacity'))
        if box_wrap: box = box_wrap(box)
        # float
        FS = d.new()
        o1, x1 = d.osc(FS, 'Float Y', './1/100/101/2', 30, 11.0 if float_speed == 0.3 else round(2 + 30*float_speed, 4), phase=round(sum(map(ord, label)) % 628 / 100, 2))
        o2, x2 = d.osc(FS, 'Float Tilt', './1/100/109/3', 0.012, 7.0 if float_speed == 0.3 else round(1.5 + 19.5*float_speed, 4), phase=1.3)
        sp = d.rig('Rig Float Y Speed', o1, 'OSC', './202', W_FS, [(1, 2), (2, 32)], pname='Speed', rng='100')
        sp += d.rig('Rig Float Tilt Speed', o2, 'OSC', './202', W_FS, [(1, 1.5), (2, 21)], pname='Speed', rng='100')
        _, fsrc = d.group(f'{label} Float Source', FS, beh=x1 + x2 + sp); self.drivers += fsrc
        FG = d.new()
        fb = self.float_links(label, FG, FS, W_FL, W_FA, float_on)
        _, g = d.group(f'{label} Float', FG, children=text_xml + mk + box, beh=fb)
        P = lambda o, c, n: self.extras_pub.setdefault(label, []).append((o, c, n))
        P(W_FL, './2/100', f'{label} Float'); P(W_FA, './2/100', f'{label} Float Amount'); P(W_FS, './2/100', f'{label} Float Speed')
        P(W_BOX, './2/100', f'{label} Box'); P(BX, './2/353/113/111', f'{label} Box Colour'); P(BX, './1/200/202', f'{label} Box Opacity')
        P(BX, './2/353/144', f'{label} Box Roundness'); P(W_PX, './2/100', f'{label} Box Padding X'); P(W_PY, './2/100', f'{label} Box Padding Y'); P(W_OY, './2/100', f'{label} Box Vertical Offset')
        if W_OX: P(W_OX, './2/100', f'{label} Box Horizontal Offset')
        P(BX, './2/353/108/105', f'{label} Box Border'); P(BX, './2/353/108/107', f'{label} Box Border Colour')
        if shadow_layer:
            P(SG, './1/200/202', f'{label} Box Shadow'); P(SHX, './2/353/102', f'{label} Box Shadow Softness'); P(W_SD, './2/100', f'{label} Box Shadow Distance')
        else:
            P(BX, './1/208/211', f'{label} Box Shadow'); P(BX, './1/208/213', f'{label} Box Shadow Softness'); P(BX, './1/208/212', f'{label} Box Shadow Distance')
        return g

    # ---- optional floating icon: built-in finance icons or your own image, soft shadow, float
    def icon_block(self, px=0, py=600, size=0.9, show=False, shadow=(0.35, 40, 26, 4.7124), t0=0.12, publish=True, icon_out='None', icon_lead=0.25):
        d = self.d
        W_ICON = d.w_check('Show Icon', show)
        W_SRC = d.w_popup('Icon', ICONS + ['Custom Image'], 0)
        W_FL = d.w_check('Icon Float', True)
        W_FAMT = d.w_slider('Float Amount', 0.35, 0, 100)
        W_FSPD = d.w_slider('Float Speed', 0.3, 0, 100)
        imgs = ''; SHADOWED = []
        for i, nm in enumerate(ICONS):
            rel = f'Media/Icon {nm}.png'; self.media[rel] = os.path.join(SRC, 'icons', f'Icon {nm}.png')
            iid, _, x = d.image(f'Icon {nm}', f'Icon {nm}', rel.replace(' ', '%20'), 512, 512, dropzone=False, shadow=shadow, op=1 if i == 0 else 0)
            x = x.replace('</scenenode>', d.rig(f'Rig Icon {nm}', iid, 'IMG', './1/200/202', W_SRC, [(j+1, 1 if j == i else 0) for j in range(len(ICONS)+1)], pname='Opacity') + '</scenenode>')
            imgs += x; SHADOWED.append(iid)
        DZ, _, dz = d.image('Custom Icon', 'Custom Icon', None, 600, 600, dropzone=True, shadow=shadow, op=0)
        dz = dz.replace('</scenenode>', d.rig('Rig Custom Icon', DZ, 'IMG', './1/200/202', W_SRC, [(j+1, 1 if j == len(ICONS) else 0) for j in range(len(ICONS)+1)], pname='Opacity') + '</scenenode>')
        # one set of shadow controls drives every icon layer through links from a hidden shadow source
        inner = dz + imgs
        # float
        FSRC = d.new()
        o1id, o1 = d.osc(FSRC, 'Float Y', './1/100/101/2', 40, 12.0, phase=0.65)
        o2id, o2 = d.osc(FSRC, 'Float Tilt', './1/100/109/3', 0.035, 8.0, phase=3.7)
        sp = d.rig('Rig Float Y Speed', o1id, 'OSC', './202', W_FSPD, [(1, 2), (2, 35)], pname='Speed', rng='100')
        sp += d.rig('Rig Float Tilt Speed', o2id, 'OSC', './202', W_FSPD, [(1, 1.5), (2, 23)], pname='Speed', rng='100')
        _, fsrc = d.group('Float Source', FSRC, beh=o1 + o2 + sp); self.drivers += fsrc
        FLG = d.new()
        fb = self.float_links('Icon', FLG, FSRC, W_FL, W_FAMT, True)
        _, g = d.group('Icon Float', FLG, children=inner, beh=fb)
        def pop(feel):
            dd = DUR[feel] + 0.15
            f = (lambda p: max(0, spring(p, ov=0.14))) if feel != 'Snappy' else ease_out4
            return dict(sx=[(0, 0), (t0, 0)] + keys(t0, dd, f)[1:], op=[(0, 0), (t0, 0)] + keys(t0, dd*0.3, smooth)[1:])
        IPA = d.new(); self.burn(lambda: self.feel_links(IPA, pop))     # old fixed pop: ids kept, replaced by the menus
        band = ('icon_id', 130000)   # own range: the text-out band (98000+) runs past 99000 on cards with several texts
        W_IIN = self.hi(lambda: d.w_popup('Icon In', ICON_IN, 0), *band)
        W_IINS = self.hi(lambda: d.w_popup('Icon In Speed', SPEEDS, 1), *band)
        W_IOUT = self.hi(lambda: d.w_popup('Icon Out', ICON_OUT, ICON_OUT.index(icon_out)), *band)
        W_IOUTS = self.hi(lambda: d.w_popup('Icon Out Speed', SPEEDS, 1), *band)
        beh = self.hi(lambda: self.style_links(IPA, ICON_IN, W_IIN, 0, icon_in_motion(t0), w_speed=W_IINS), *band)
        _, g = d.group('Icon Pop', IPA, children=g, beh=beh)
        IOU = self.hi(d.new, *band)
        beh = self.hi(lambda: self.style_links(IOU, ICON_OUT, W_IOUT, ICON_OUT.index(icon_out), icon_out_motion(lead=icon_lead), w_speed=W_IOUTS), *band)
        _, g = d.group('Icon Out', IOU, children=g, beh=beh)
        ISH = d.new()
        _, g = d.group('Icon Show', ISH, children=g, op=1 if show else 0, sx=size, sy=size,
                       beh=d.rig('Rig Show Icon', ISH, 'GRP', './1/200/202', W_ICON, [(1, 0), (2, 1)], pname='Opacity'))
        ICOP, g = self.place('Icon Position', g, px, py)
        if publish:   # deferred: the build places the icon block with c.pub_extras('Icon')
            P = lambda o, ch, n: self.extras_pub.setdefault('Icon', []).append((o, ch, n))
            P(W_ICON, './2/100', 'Show Icon'); P(W_SRC, './2/100', 'Icon'); P(DZ, './1/324/300', 'Custom Icon Image')
            P(ICOP, './1/100/101', 'Icon Position'); P(ISH, './1/100/105', 'Icon Size')
            P(W_IIN, './2/100', 'Icon In'); P(W_IINS, './2/100', 'Icon In Speed'); P(W_IOUT, './2/100', 'Icon Out'); P(W_IOUTS, './2/100', 'Icon Out Speed')
            P(W_FL, './2/100', 'Icon Float'); P(W_FAMT, './2/100', 'Icon Float Amount'); P(W_FSPD, './2/100', 'Icon Float Speed')
            P(DZ, './1/208/211', 'Icon Shadow Opacity'); P(DZ, './1/208/213', 'Icon Shadow Softness'); P(DZ, './1/208/212', 'Icon Shadow Distance')
        # icon layers copy the custom drop zone's shadow settings
        self.post_links = getattr(self, 'post_links', []) + [(iid, DZ) for iid in SHADOWED]
        return g

    def finish_shadow_links(self, s):
        """link each built-in icon's drop shadow to the custom drop zone's (published) shadow values"""
        d = self.d
        for iid, dz in getattr(self, 'post_links', []):
            x = ''
            for nm, pid in (('Opacity', '211'), ('Blur', '213'), ('Distance', '212')):
                lid, lx = d.link(f'Shadow {nm}', iid, 'IMG', f'./1/208/{pid}', dz, [(pid, f'./1/208/{pid}')], mode=2, mix=1, scale=1)
                x += lx
            k = s.find(f'<scenenode name="Icon ', 0)
            a = s.find(f'id="{iid}" factoryID')
            a = s.rfind('<scenenode', 0, a); e = span(s, a)
            s = s[:e-len('</scenenode>')] + x + s[e-len('</scenenode>'):]
        return s

    def save(self, root, outdir, markers=None, thumb=None):
        d = self.d
        assert not self.extras_pub, f'unpublished text extras: {list(self.extras_pub)}'
        _, drv = d.group('Drivers', children=self.drivers, op=0)
        path = os.path.join(outdir, self.name, self.name + ('.moti' if self.kind == 'title' else '.motr'))
        s = d.save(path, root + drv, markers=(markers or (1.0, END - 0.6)) if self.kind == 'title' else None)
        s = self.finish_shadow_links(s)
        import collections
        dup = [i for i, n in collections.Counter(re.findall(r'<(?:scenenode|behavior|layer|group|text|clip)\b[^>]* id="(\d+)"', s)).items() if n > 1]
        assert not dup, f'duplicate object ids: {dup[:10]}'
        for bid, v in getattr(self, 'seq_base', {}).items():
            i = s.index(f' id="{bid}" factoryID="'); j = s.index('</behavior>', i)
            blk = s[i:j]; old = '<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="0"/>'
            assert blk.count(old) == 1, bid
            blk = blk.replace(old, old.replace('value="0"', f'value="{v}"'))
            if bid in getattr(self, 'seq_end', {}):
                blk, n = re.subn(r'(<parameter name="End Offset" id="213" flags="8606711824" default="0" value=")[^"]*"', rf'\g<1>{self.seq_end[bid]}"', blk)
                assert n == 1, bid
            s = s[:i] + blk + s[j:]
            # the menu rigs must live on the text that owns the Sequence Text (next to it), not on the Anim group
            pat = (r'<behavior name="Rig [^"]*" id="\d+" factoryID="\d+">\n<channelBehavior affectingFactory="[0-9a-f]+" affectingChannel="\./(?:1000/1044|201/213)"[^>]*/>\n'
                   r'(?:(?!</behavior>).)*?"Affecting Object \(Hidden\)" id="199"[^>]*value="' + str(bid) + r'"/>.*?</behavior>\n')
            rigs = []
            while True:
                m = re.search(pat, s, re.S)
                if not m: break
                rigs.append(m.group(0)); s = s[:m.start()] + s[m.end():]
            assert rigs, bid
            j = s.index('</behavior>', s.index(f' id="{bid}" factoryID="')) + len('</behavior>')
            s = s[:j] + '\n' + ''.join(rigs).rstrip('\n') + s[j:]
        open(path, 'w').write(s)
        md = os.path.join(outdir, self.name, 'Media'); os.makedirs(md, exist_ok=True)
        for rel, src in self.media.items():
            shutil.copy(src, os.path.join(outdir, self.name, rel))
        if thumb:
            from PIL import Image
            im = Image.open(thumb).convert('RGB')
            im.resize((400, 225), Image.LANCZOS).save(os.path.join(outdir, self.name, 'large.png'))
            im.resize((160, 90), Image.LANCZOS).save(os.path.join(outdir, self.name, 'small.png'))
        return path, s

# ---- shared entrance / exit library (every card offers all of these; cards may override some with their own look)
ENTR_ALL = ['Cut', 'Fade', 'Fade Up', 'Zoom', 'Drop In', 'Rise In', 'Slide from Left', 'Slide from Right']
EXIT_ALL = ['Cut', 'Fade', 'Fade Down', 'Zoom Out', 'Drop Out', 'Rise Out', 'Slide to Left', 'Slide to Right']
def merge_styles(own, full):
    """keep a card's existing menu order (clips store the menu position), then append the missing styles"""
    return own + [s for s in full if s not in own]
# ---- motion library: every entrance/exit = look x Motion Feel (curve) x Speed (duration)
SPEEDS = ['Slow', 'Normal', 'Fast']
SPD = {'Slow': 1.45, 'Normal': 1.0, 'Fast': 0.7}
BASE = {'Smooth': 0.8, 'Snappy': 0.65, 'Gentle Bounce': 0.9}      # Normal-speed move time per feel (s)
def sine_io(p): return (1 - math.cos(math.pi*p))/2
def quad_io(p): return 2*p*p if p < 0.5 else 1 - 2*(1-p)**2

def arrive(feel, amp=0.06):
    """progress 0->1 for a move INTO place. Even, eased motion so the eye can follow a full-screen card."""
    if feel == 'Snappy': return quad_io
    if feel == 'Gentle Bounce':
        def g(p):
            if p < 0.6: return 1 - math.cos(math.pi/2 * p/0.6)                      # falls in, gathering speed
            t = (p-0.6)/0.4; return 1 + amp*math.sin(math.pi*2.5*t)*math.exp(-4*t)   # small settling bounce
        return g
    return sine_io

def leave(feel):
    """progress 0->1 for a move OUT of place."""
    if feel == 'Snappy': return quad_io
    if feel == 'Gentle Bounce':
        def g(p):
            if p < 0.25: return -0.04*math.sin(math.pi*p/0.25)                     # little lift first
            return 1 - math.cos(math.pi/2 * (p-0.25)/0.75)
        return g
    return sine_io

def dur(feel, speed): return BASE[feel] * SPD[speed]

def std_in(st, feel, speed='Normal', dx=5800, dy=4100):
    dd = dur(feel, speed); f = arrive(feel); r = lambda p: 1 - f(p)
    if st == 'Dissolve': return dict(op=keys(0.0, dd*0.35, lambda p: p))
    if st == 'Fade': return dict(op=keys(0.0, dd*0.7, smooth))
    if st == 'Fade Up': return dict(op=keys(0.0, dd*0.7, smooth), py=keys(0.0, dd, lambda p: -140*r(p)))
    if st == 'Zoom': return dict(sx=keys(0.0, dd, lambda p: 1 + 0.07*r(p)), op=keys(0.0, dd*0.5, smooth))
    if st == 'Rise In': return dict(py=keys(0.0, dd, lambda p: -dy*r(p)))
    if st == 'Slide from Left': return dict(px=keys(0.0, dd, lambda p: -dx*r(p)))
    if st == 'Slide from Right': return dict(px=keys(0.0, dd, lambda p: dx*r(p)))
    raise ValueError(st)

def std_out(st, feel, speed='Normal', dx=5800, dy=4100):
    dd = dur(feel, speed)*0.9; t0 = END - dd - 0.02; g = leave(feel)
    hold = lambda v: [(0, v), (t0, v)]
    seg = lambda fn: keys(t0, dd, fn)[1:]
    if st == 'Fade': return dict(op=hold(1) + seg(lambda q: 1-smooth(q)))
    if st == 'Fade Down': return dict(op=hold(1) + seg(lambda q: 1-smooth(q)), py=hold(0) + seg(lambda q: -140*smooth(q)))
    if st == 'Zoom Out': return dict(sx=hold(1) + seg(lambda q: 1+0.05*smooth(q)), op=hold(1) + seg(lambda q: 1-smooth(q)))
    if st == 'Rise Out': return dict(py=hold(0) + seg(lambda q: dy*g(q)))
    if st == 'Slide to Left': return dict(px=hold(0) + seg(lambda q: -dx*g(q)))
    if st == 'Slide to Right': return dict(px=hold(0) + seg(lambda q: dx*g(q)))
    raise ValueError(st)

# ---- drop family: Drop In (from above), Drop Out (back up), Drop Down (falls off the bottom), six looks each
DROP_LOOKS = ['Blur', 'Blur (Adjustable)', 'Sleek', 'Bounce', 'Stretch', 'Swing']
DROP_IN = [f'Drop In – {v}' for v in DROP_LOOKS]
DROP_DOWN = [f'Drop Down – {v}' for v in DROP_LOOKS]
DROP_OUT = [f'Drop Out – {v}' for v in DROP_LOOKS]
ADJ_BLUR = {'Drop In – Blur (Adjustable)', 'Drop Down – Blur (Adjustable)', 'Drop Out – Blur (Adjustable)'}
SHUTTER = 1/120          # 180-degree shutter at 59.94 fps: blur length = speed x 1/120 s

def _blur_from(kk, ch='py'):
    pts = kk[ch]; out = []
    for i, (t, v) in enumerate(pts):
        a, b = pts[max(i-1, 0)], pts[min(i+1, len(pts)-1)]
        vel = (b[1]-a[1])/(b[0]-a[0]) if b[0] > a[0] else 0
        out.append((t, round(min(abs(vel)*SHUTTER, 400), 2)))
    return out

def _look_timing(look, feel, speed):
    """Blur looks keep the Smooth feel (their blur is keyframed); the Adjustable one also stays at Normal speed
    (one Directional Blur can't follow the menu, the speed and the slider at once)."""
    if look in ('Blur', 'Blur (Adjustable)'): feel = 'Smooth'
    if look == 'Blur (Adjustable)': speed = 'Normal'
    if look == 'Bounce': feel = 'Gentle Bounce'
    return feel, speed

def drop_in(look, feel, dy, speed='Normal'):
    feel, speed = _look_timing(look, feel, speed)
    dd = dur(feel, speed)
    f = arrive(feel, amp=0.09 if look == 'Bounce' else 0.06)
    kk = dict(py=keys(0.0, dd, lambda p: dy*(1-f(p))))
    if look in ('Blur', 'Blur (Adjustable)'):
        kk['bl'] = _blur_from(kk)
    elif look == 'Stretch':
        bl = _blur_from(kk); vmax = max(v for _, v in bl) or 1
        kk['sy'] = [(t, 1 + 0.14*v/vmax) for t, v in bl][:-1] + keys(dd, 0.22, lambda p: 1 - 0.05*math.sin(math.pi*p))
    elif look == 'Swing':
        kk['rz'] = keys(0.0, dd*1.3, lambda p: 0.075*math.exp(-3.2*p)*math.cos(8.5*p))
    return kk

def drop_exit(look, feel, dy, up, speed='Normal'):
    """Drop Down (falls, up=False) or Drop Out (lifts away, up=True), ending at the clip's end."""
    sgn = 1 if up else -1
    feel, speed = _look_timing(look, feel, speed)
    dd = dur(feel, speed)*0.9; t0 = END - dd - 0.02; g = leave(feel)
    if look == 'Bounce':
        g0 = g; g = lambda q: (-0.07*math.sin(math.pi*q/0.25) if q < 0.25 else g0(q))
    kk = dict(py=[(0, 0), (t0, 0)] + keys(t0, dd, lambda q: sgn*dy*g(q))[1:])
    if look in ('Blur', 'Blur (Adjustable)'):
        kk['bl'] = _blur_from(kk)
    elif look == 'Stretch':
        bl = _blur_from(kk); vmax = max(v for _, v in bl) or 1
        kk['sy'] = [(t, 1 + 0.14*v/vmax) for t, v in bl]
    elif look == 'Swing':
        kk['rz'] = [(0, 0), (t0, 0)] + keys(t0, dd, lambda q: -sgn*0.09*smooth(q))[1:]
    return kk

def drop_style(st, feel, dy, speed='Normal'):
    """returns driver dict for any Drop In / Drop Out / Drop Down style name, else None"""
    for fam, f in (('Drop In – ', lambda lk: drop_in(lk, feel, dy, speed)), ('Drop Down – ', lambda lk: drop_exit(lk, feel, dy, False, speed)),
                   ('Drop Out – ', lambda lk: drop_exit(lk, feel, dy, True, speed))):
        if st.startswith(fam): return f(st[len(fam):])
    return None

def card_motion(kind, dx, dy):
    """drv_fn(st, feel, speed) for a card: every style goes through the shared library"""
    def fn(st, feel, speed):
        r = drop_style(st, feel, dy, speed)
        if r: return r
        return std_in(st, feel, speed, dx, dy) if kind == 'in' else std_out(st, feel, speed, dx, dy)
    return fn

# ---- text entrances (per text, follows Motion Feel)
WORD_SPEEDS = ['Slow', 'Normal', 'Fast']          # how fast the words come in (Word by Word / Typewriter)
WORD_MUL = {'Slow': 1.5, 'Normal': 1.0, 'Fast': 0.6}
FPS = 60000/1001
OUT_T0 = END - 1.45                                  # word-by-word exits start here (Sequence Text timing is fixed)
TEXT_OUT = ['Rise', 'Word by Word', 'Fade', 'Slide to Left', 'Slide to Right', 'Drop', 'Pop', 'None']
CARD_T0 = {f: END - BASE[f]*0.9 - 0.02 for f in FEELS}   # when the card's own exit starts (Normal Exit Speed)
FALL = 3000                                          # Drop exit: far enough to leave the frame from anywhere on the card
def _fall(feel):
    """gravity: slow start, then accelerating out of frame (Gentle Bounce: a little hop first)"""
    if feel == 'Snappy': return lambda p: p**3
    if feel == 'Gentle Bounce': return lambda p: -0.025*math.sin(math.pi*p/0.2) if p < 0.2 else ((p - 0.2)/0.8)**2.2
    return lambda p: p**2.2
def _drop_out(feel, speed, lead):
    """a real drop, timed `lead` s before the card's own exit so the elements and the card fall as one stack"""
    dd = {'Smooth': 0.75, 'Snappy': 0.55, 'Gentle Bounce': 0.85}[feel]*SPD[speed]
    t0 = CARD_T0[feel] - lead; g = _fall(feel)
    dd = min(dd, END - 0.03 - t0)   # Slow: still finish inside the clip
    return dict(py=[(0, 0), (t0, 0)] + keys(t0, dd, lambda p: -FALL*g(p), n=max(10, int(dd*30)))[1:],
                op=[(0, 1), (t0, 1)])   # no fade (it falls out of frame); op kept so the links/ids match earlier builds
def text_out_motion(dist, nd, lead=0.35, words=True):
    """the Text In looks played backwards. Drop is a real fall locked to the card's exit; the others end just as
    the card starts to leave (lead = how far ahead of the card this element goes; lower elements go first)."""
    def fn(st, feel, speed):
        if st == 'Drop': return _drop_out(feel, speed, lead)
        if st == 'Word by Word' and not words: st = 'Fade'
        dd = {'Smooth': 0.5, 'Snappy': 0.35, 'Gentle Bounce': 0.6}[feel]*SPD[speed]
        t0 = OUT_T0 if st == 'Word by Word' else CARD_T0[feel] - lead - dd*0.75
        if feel == 'Gentle Bounce': g = lambda p: p*p*(2.4*p - 1.4)          # small wind-up, then away
        elif feel == 'Snappy': g = lambda p: p**4
        else: g = ease_in
        hold = lambda v: [(0, v), (t0, v)]
        seg = lambda f, d2=dd: keys(t0, d2, f, n=max(8, int(d2*30)))[1:]     # 30 keys/s keeps the files light
        fade = hold(1) + seg(lambda p: 1 - smooth(p), dd*0.8)
        if st == 'Rise': return dict(py=hold(0) + seg(lambda p: dist*g(p)), op=fade)
        if st == 'Word by Word':
            wd = nd*SPD[speed]
            return dict(py=hold(0) + seg(lambda p: dist*0.5*g(p), wd), op=hold(1) + [(t0 + wd - 0.05, 1)] + keys(t0 + wd - 0.05, 0.2, lambda p: 1 - smooth(p), n=8)[1:])   # box fades after the words
        if st == 'Fade': return dict(op=hold(1) + seg(lambda p: 1 - smooth(p)))
        if st == 'Slide to Left': return dict(px=hold(0) + seg(lambda p: -dist*4*g(p)), op=fade)
        if st == 'Slide to Right': return dict(px=hold(0) + seg(lambda p: dist*4*g(p)), op=fade)
        if st == 'Pop': return dict(sx=hold(1) + seg(lambda p: 1 - 0.18*g(p)), op=hold(1) + seg(lambda p: 1 - smooth(p), dd*0.6))
        raise ValueError(st)
    return fn
ICON_IN = ['Pop', 'Rise', 'Fade', 'Slide from Left', 'Slide from Right', 'Drop', 'None']
ICON_OUT = ['Pop', 'Rise', 'Fade', 'Slide to Left', 'Slide to Right', 'Drop', 'None']
def icon_in_motion(t0, dist=80):
    def fn(st, feel, speed):
        if st == 'Pop':      # the original pop, now with a speed
            dd = (DUR[feel] + 0.15)*SPD[speed]
            f = (lambda p: max(0, spring(p, ov=0.14))) if feel != 'Snappy' else ease_out4
            return dict(sx=[(0, 0), (t0, 0)] + keys(t0, dd, f, n=max(10, int(dd*30)))[1:], op=[(0, 0), (t0, 0)] + keys(t0, dd*0.3, smooth, n=8)[1:])
        dd = {'Smooth': 0.6, 'Snappy': 0.4, 'Gentle Bounce': 0.75}[feel]*SPD[speed]
        if feel == 'Gentle Bounce': r = lambda p: 1 - spring(p, ov=0.12)
        elif feel == 'Snappy': r = lambda p: 1 - ease_out4(p)
        else: r = lambda p: 1 - ease_out(p)
        pre = lambda v: [(0, v), (t0, v)]
        seg = lambda f, d2=dd: keys(t0, d2, f, n=max(8, int(d2*30)))[1:]
        fade = pre(0) + seg(smooth, dd*0.6)
        if st == 'Rise': return dict(py=pre(-dist) + seg(lambda p: -dist*r(p)), op=fade)
        if st == 'Fade': return dict(op=pre(0) + seg(smooth))
        if st == 'Slide from Left': return dict(px=pre(-dist*4) + seg(lambda p: -dist*4*r(p)), op=fade)
        if st == 'Slide from Right': return dict(px=pre(dist*4) + seg(lambda p: dist*4*r(p)), op=fade)
        if st == 'Drop': return dict(py=pre(dist) + seg(lambda p: dist*r(p)), op=fade)
        raise ValueError(st)
    return fn
def icon_out_motion(dist=80, lead=0.25):
    def fn(st, feel, speed):
        if st == 'Drop': return _drop_out(feel, speed, lead)
        dd = {'Smooth': 0.5, 'Snappy': 0.35, 'Gentle Bounce': 0.6}[feel]*SPD[speed]
        t0 = CARD_T0[feel] - lead - dd*0.75
        if feel == 'Gentle Bounce': g = lambda p: p*p*(2.4*p - 1.4)
        elif feel == 'Snappy': g = lambda p: p**4
        else: g = ease_in
        hold = lambda v: [(0, v), (t0, v)]
        seg = lambda f, d2=dd: keys(t0, d2, f, n=max(8, int(d2*30)))[1:]
        fade = hold(1) + seg(lambda p: 1 - smooth(p), dd*0.8)
        if st == 'Pop': return dict(sx=hold(1) + seg(lambda p: max(0, 1 - g(p))), op=hold(1) + [(t0 + dd*0.6, 1)] + keys(t0 + dd*0.6, dd*0.4, lambda p: 1 - p, n=8)[1:])
        if st == 'Rise': return dict(py=hold(0) + seg(lambda p: dist*g(p)), op=fade)
        if st == 'Fade': return dict(op=hold(1) + seg(lambda p: 1 - smooth(p)))
        if st == 'Slide to Left': return dict(px=hold(0) + seg(lambda p: -dist*4*g(p)), op=fade)
        if st == 'Slide to Right': return dict(px=hold(0) + seg(lambda p: dist*4*g(p)), op=fade)
        raise ValueError(st)
    return fn
TEXT_IN = ['Rise', 'Word by Word', 'Fade', 'Slide from Left', 'Slide from Right', 'Drop', 'Pop', 'None']
def text_motion(delay, dist):
    def fn(st, feel):
        dd = {'Smooth': 0.6, 'Snappy': 0.4, 'Gentle Bounce': 0.75}[feel]
        if feel == 'Gentle Bounce': r = lambda p: 1 - spring(p, ov=0.12)
        elif feel == 'Snappy': r = lambda p: 1 - ease_out4(p)
        else: r = lambda p: 1 - ease_out(p)
        pre = lambda v: [(0, v), (delay, v)]
        seg = lambda f, d2=dd: keys(delay, d2, f)[1:]
        fade = pre(0) + seg(smooth, dd*0.6)
        if st == 'Rise': return dict(py=pre(-dist) + seg(lambda p: -dist*r(p)), op=fade)
        if st == 'Word by Word': return dict(py=pre(-dist*0.5) + seg(lambda p: -dist*0.5*r(p), dd*1.6), op=pre(0) + [(delay + 0.01, 1)])
        if st == 'Fade': return dict(op=pre(0) + seg(smooth))
        if st == 'Slide from Left': return dict(px=pre(-dist*4) + seg(lambda p: -dist*4*r(p)), op=fade)
        if st == 'Slide from Right': return dict(px=pre(dist*4) + seg(lambda p: dist*4*r(p)), op=fade)
        if st == 'Drop': return dict(py=pre(dist) + seg(lambda p: dist*r(p)), op=fade)
        if st == 'Pop': return dict(sx=pre(0.82) + seg(lambda p: 1 - 0.18*r(p)), op=pre(0) + seg(smooth, dd*0.35))
        raise ValueError(st)
    return fn
