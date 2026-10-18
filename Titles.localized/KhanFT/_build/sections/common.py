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
        FLG = d.new(); fb = ''
        for nm, chan, chs, sc in (('Float Y', './1/100/101', [('2', './1/100/101/2')], 0.5625), ('Float Tilt', './1/100/109', [('3', './1/100/109/3')], 1.0)):
            lid, lx = d.link(nm, FLG, 'GRP', chan, FSRC, chs, mode=0, scale=sc)
            fb += lx + d.rig(f'Rig {nm} On', lid, 'LNK', './207', W_FL, [(1, 0), (2, 1)], pname='Custom Mix')
            fb += d.rig(f'Rig {nm} Amount', lid, 'LNK', './204', W_FAMT, [(1, 0), (2, 3*sc)], pname='Scale', rng=B)
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
