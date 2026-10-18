# common.py - pieces shared by all KhanFT section cards
import os, shutil
from kft import *

SRC = os.path.dirname(os.path.abspath(__file__))
FEELS = ['Smooth', 'Snappy', 'Gentle Bounce']
DUR = {'Smooth': 0.5, 'Snappy': 0.28, 'Gentle Bounce': 0.7}
ICONS = ['Savings', 'Bank', 'Gold', 'Stocks', 'Crypto', 'Loan']
CH = {'px': ('Pos X', './1/100/101', [('1', './1/100/101/1')], 1),
      'py': ('Pos Y', './1/100/101', [('2', './1/100/101/2')], 0.5625),
      'sx': ('Scale', './1/100/105', [('1', './1/100/105/1'), ('2', './1/100/105/2')], 1),
      'rz': ('Rotate', './1/100/109', [('3', './1/100/109/3')], 1),
      'op': ('Fade', './1/200/202', [('202', './1/200/202')], 1)}


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

    def pub_extras(self, label):
        for o, c, n in self.extras_pub.pop(label, []): self.d.publish(o, c, n)

    # ---- drivers
    def drv_group(self, name, kk):
        d = self.d
        gid, x = d.group(name, px=kk.get('px', 0), py=kk.get('py', 0), sx=kk.get('sx', 1), sy=kk.get('sx', 1),
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

    def style_links(self, target, styles, w_style, default, drv_fn):
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
    def float_links(self, label, target, src, w_on, w_amt, on):
        # ids: the target links/rigs keep the exact ids of the earlier build (so clips already in a timeline keep
        # their settings); everything new is allocated from a separate high range.
        d = self.d
        def hi(fn):
            keep = d.nid[0]; d.nid[0] = getattr(self, 'hi_id', 80000)
            try: return fn()
            finally: self.hi_id = d.nid[0]; d.nid[0] = keep
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
                    pad=(60, 34), rnd=26, border=None, shadow=(0.25, 40, 14), box_wrap=None):
        """returns xml: Float group > [text, edge markers, box]. Publishes '<label> …' controls."""
        d = self.d; P = d.publish
        K, KY = 4.0, 2.25
        W_BOX = d.w_check(f'{label} Box', box_on)
        W_PX = d.w_slider(f'{label} Box Padding X', round(pad[0]/300, 4), 0, 300)
        W_PY = d.w_slider(f'{label} Box Padding Y', round(pad[1]/200, 4), 0, 200)
        W_FL = d.w_check(f'{label} Float', float_on)
        W_FA = d.w_slider(f'{label} Float Amount', 0.3, 0, 100)
        W_FS = d.w_slider(f'{label} Float Speed', 0.3, 0, 100)
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
        def L(nm, chan, src, sc, tgt, scale, mode=0):
            return d.link(nm, BX, 'SHP', chan, src, [(tgt, sc)], mode=mode, scale=scale)[1]
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
        BS = d.new()
        _, box = d.group(f'{label} Box Show', BS, children=box, op=1 if box_on else 0,
                         beh=d.rig(f'Rig {label} Box', BS, 'GRP', './1/200/202', W_BOX, [(1, 0), (2, 1)], pname='Opacity'))
        if box_wrap: box = box_wrap(box)
        # float
        FS = d.new()
        o1, x1 = d.osc(FS, 'Float Y', './1/100/101/2', 30, 11.0, phase=round(sum(map(ord, label)) % 628 / 100, 2))
        o2, x2 = d.osc(FS, 'Float Tilt', './1/100/109/3', 0.012, 7.0, phase=1.3)
        sp = d.rig('Rig Float Y Speed', o1, 'OSC', './202', W_FS, [(1, 2), (2, 32)], pname='Speed', rng='100')
        sp += d.rig('Rig Float Tilt Speed', o2, 'OSC', './202', W_FS, [(1, 1.5), (2, 21)], pname='Speed', rng='100')
        _, fsrc = d.group(f'{label} Float Source', FS, beh=x1 + x2 + sp); self.drivers += fsrc
        FG = d.new()
        fb = self.float_links(label, FG, FS, W_FL, W_FA, float_on)
        _, g = d.group(f'{label} Float', FG, children=text_xml + mk + box, beh=fb)
        P = lambda o, c, n: self.extras_pub.setdefault(label, []).append((o, c, n))
        P(W_FL, './2/100', f'{label} Float'); P(W_FA, './2/100', f'{label} Float Amount'); P(W_FS, './2/100', f'{label} Float Speed')
        P(W_BOX, './2/100', f'{label} Box'); P(BX, './2/353/113/111', f'{label} Box Colour'); P(BX, './1/200/202', f'{label} Box Opacity')
        P(BX, './2/353/144', f'{label} Box Roundness'); P(W_PX, './2/100', f'{label} Box Padding X'); P(W_PY, './2/100', f'{label} Box Padding Y')
        P(BX, './2/353/108/105', f'{label} Box Border'); P(BX, './2/353/108/107', f'{label} Box Border Colour')
        P(BX, './1/208/211', f'{label} Box Shadow'); P(BX, './1/208/213', f'{label} Box Shadow Softness'); P(BX, './1/208/212', f'{label} Box Shadow Distance')
        return g

    # ---- optional floating icon: built-in finance icons or your own image, soft shadow, float
    def icon_block(self, px=0, py=600, size=0.9, show=False, shadow=(0.35, 40, 26, 4.7124), t0=0.12, publish=True):
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
        IPA = d.new(); _, g = d.group('Icon Pop', IPA, children=g, beh=self.feel_links(IPA, pop))
        ISH = d.new()
        _, g = d.group('Icon Show', ISH, children=g, op=1 if show else 0, sx=size, sy=size,
                       beh=d.rig('Rig Show Icon', ISH, 'GRP', './1/200/202', W_ICON, [(1, 0), (2, 1)], pname='Opacity'))
        ICOP, g = self.place('Icon Position', g, px, py)
        if publish:
            P = d.publish
            P(W_ICON, './2/100', 'Show Icon'); P(W_SRC, './2/100', 'Icon'); P(DZ, './1/324/300', 'Custom Icon Image')
            P(ICOP, './1/100/101', 'Icon Position'); P(ISH, './1/100/105', 'Icon Size')
            P(W_FL, './2/100', 'Icon Float'); P(W_FAMT, './2/100', 'Float Amount'); P(W_FSPD, './2/100', 'Float Speed')
            P(DZ, './1/208/211', 'Shadow Opacity'); P(DZ, './1/208/213', 'Shadow Softness'); P(DZ, './1/208/212', 'Shadow Distance')
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
