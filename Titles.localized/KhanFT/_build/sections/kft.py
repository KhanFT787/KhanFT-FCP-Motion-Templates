# kft.py - shared builder for KhanFT Motion titles (.moti)
# Starts from a Motion-saved Final Cut Title skeleton and adds layers, behaviours,
# rig widgets and published parameters. Patterns are the ones proven in the earlier
# KhanFT builds (Section/Text/Words/Cards Type 1).
import re, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
B = '3.4028234663852886e+38'
TB = 120000; FR = 2002                      # 59.94 fps
END = 1199198 / TB                          # 10 s title
TIMING = '<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>'

U = dict(GRP='44da0700f6ab11d68c24000393670732', SHP='712462a4323911d78f8400039389b702',
         IMG='66fc0d6af6a911d6a7a7000393670732', TXT='babfc7777f4711d7aaa7000393833f6a',
         OSC='1a262447ab7011d7bb4600039366fb58', LNK='68fba2c1aa094655bf4b81587efec626',
         RIG='402246385249454b90e08b2ee1b6bf06', RB='dd0036f96c9e4bfdadb82f71fbf5c9d8',
         W='e35c74f01d5042f6b468eb530169bfb7', CW='11615b89cbc0483fb92e95eb0c80e59c',
         C='fdc1944b229111d7b1c300039389b702', SEQ='9279a0e120d64a82b26b4cf79391ff47',
         BASIC='03ce4d4f0ea74b3b9af072a0e4a61ab7', SUBST='f4c2c6ef713f4a18ae987242c8b7f619',
         STYLE='044beba5ad3211d7ac9b000393833f6a', ALIGN='eecb322ed23242d8ae51f33765574dbd', RATE='742cb47d503411d891e9000a95b0025a',
         FILT='deca4859b16011d7a12d0003936f6f92')
DESC = dict(GRP='Group', SHP='Shape', IMG='Image', TXT='Text', OSC='Oscillate', LNK='Link', RIG='Rig',
            RB='Rig Behavior', W='Widget', CW='Channel', C='Channel', SEQ='Sequence Text',
            BASIC='Basic Ch', SUBST='Substance Ch', STYLE='Style', ALIGN='Align To', RATE='Rate', FILT='ProPlugin Filter')

def T(sec): return f'{int(round(sec*TB/FR))*FR} {TB} 1 0'

def span(text, start, tag='scenenode'):
    depth = 0
    for mm in re.finditer(r'<(/?)%s\b[^>]*?(/?)>' % tag, text[start:]):
        if mm.group(2): continue
        depth += -1 if mm.group(1) else 1
        if depth == 0: return start + mm.end()

def node_from(src, name):
    a = src.find('<scenenode name="%s"' % name); return src[a:span(src, a)]

def facmap(src):
    return {i: u for i, u in re.findall(r'<factory id="(\d+)" uuid="([0-9a-f]+)">', src)}

# ---------- easing
def smooth(p): return p*p*(3-2*p)
def ease_out(p): return 1-(1-p)**3
def ease_out4(p): return 1-(1-p)**4
def ease_in(p): return p**3
def ease_io(p): return 4*p**3 if p < 0.5 else 1-(-2*p+2)**3/2
def back_out(p, s=1.9): p -= 1; return 1 + (s+1)*p**3 + s*p**2
def spring(p, ov=0.10, a=6.0, half=0.22):
    pk = 0.38
    if p < pk:
        q = p/pk; return (1+ov)*(1-(1-q)**2)
    t = p-pk; w = math.pi/half
    return 1+ov*math.exp(-a*t)*(math.cos(w*t)+(a/w)*math.sin(w*t))*(1 if p < 0.999 else 0)
def keys(t0, d, f, n=None):
    n = n or max(8, int(d*60)); return [(t0+d*k/n, f(k/n)) for k in range(n+1)]

def colp(col):
    return ('<parameter name="Red" id="1" flags="8606711824" default="1" value="%s"/>'
            '<parameter name="Green" id="2" flags="8606711824" default="1" value="%s"/>'
            '<parameter name="Blue" id="3" flags="8606711824" default="1" value="%s"/>') % tuple(col)

def hexc(h):
    h = h.lstrip('#'); return tuple(round(int(h[i:i+2], 16)/255, 4) for i in (0, 2, 4))


class Doc:
    def __init__(self, kind='title', motion_blur=False):
        self.kind = kind
        self.s = open(os.path.join(HERE, 'skel.moti' if kind == 'title' else 'tskel.motr')).read()
        if motion_blur:
            self.s = self.s.replace('<showMotionBlur>0</showMotionBlur>', '<showMotionBlur>1</showMotionBlur>')
        self.AB = {}
        if kind == 'transition':
            for nm in ('Transition A', 'Transition B'):
                n = node_from(self.s, nm)
                self.AB[nm] = n
        self.sec1 = open(os.path.join(HERE, 'sec1.moti')).read()
        self.words1 = open(os.path.join(HERE, 'words1.moti')).read()
        self.facs = {u: i for i, u in re.findall(r'<factory id="(\d+)" uuid="([0-9a-f]+)">', self.s)}
        self.add_fac = ''
        for k in U: self.F(k)
        self.nid = [30000]
        self.widgets = ''; self.clips = ''; self.pub = []
        # templates
        self.TXT = self._text_template()
        self.RECT = self._rect_template()
        sk = open(os.path.join(HERE, 'skel.moti')).read()
        self.DZ = node_from(sk, 'Drop Zone')
        self.DZ = re.sub(r'factoryID="\d+"', f'factoryID="{self.F("IMG")}"', self.DZ, 1)
        a = sk.find('<clip name="Drop Zone"'); self.CLIP = sk[a:sk.find('</clip>', a)+7]

    # ---- factories / ids
    def F(self, key):
        u = U.get(key, key)
        if u not in self.facs:
            nf = str(max(int(v) for v in self.facs.values())+1); self.facs[u] = nf
            self.add_fac += (f'<factory id="{nf}" uuid="{u}">\n\t<description>{DESC.get(key, key)}</description>\n'
                             f'\t<manufacturer>Apple</manufacturer>\n\t<version>1</version>\n</factory>\n')
        return self.facs[u]
    def new(self):
        self.nid[0] += 1; return str(self.nid[0])
    def remap(self, xml, src):
        sm = facmap(src)
        return re.sub(r'factoryID="(\d+)"', lambda m: 'factoryID="%s"' % self.F(sm[m.group(1)]) if m.group(1) in sm and m.group(1) != '0' else m.group(0), xml)

    # ---- templates
    def _text_template(self):
        t = node_from(self.words1, 'Title')
        t = re.sub(r'<behavior .*?</behavior>\s*', '', t, flags=re.S)
        return self.remap(t, self.words1)
    def _rect_template(self):
        r = node_from(self.sec1, 'Gradient')
        r = re.sub(r'<behavior .*?</behavior>\s*', '', r, flags=re.S)
        return self.remap(r, self.sec1)

    # ---- curves / params
    @staticmethod
    def curve(name, pid, default, ks):
        x = (f'<parameter name="{name}" id="{pid}" flags="8606711824"><curve type="1" default="{default}" value="{ks[0][1]:.5f}">'
             f'<numberOfKeypoints>{len(ks)}</numberOfKeypoints>')
        for t, v in ks: x += f'<keypoint interpolation="1" flags="0"><time>{T(t)}</time><value>{v:.5f}</value></keypoint>'
        return x + '</curve></parameter>'
    @staticmethod
    def scal(name, pid, default, v):
        return f'<parameter name="{name}" id="{pid}" flags="8606711824" default="{default}" value="{v}"/>'

    def group(self, name, gid=None, children='', px=0, py=0, sx=1, sy=1, rz=0, op=1, beh='', ax=0, ay=0, pz=None, crop=None, rx=0):
        """px/py/sx/sy/op may be numbers or keyframe lists [(t,v),...]"""
        gid = gid or self.new()
        def ch(nm, pid, dflt, v): return self.curve(nm, pid, dflt, v) if isinstance(v, list) else self.scal(nm, pid, dflt, v)
        anchor = ''
        if ax or ay:
            anchor = f'<parameter name="Anchor Point" id="107" flags="8589938704"><foldFlags>15</foldFlags>{self.scal("X","1",0,ax)}{self.scal("Y","2",0,ay)}</parameter>'
        fixed = ''
        if crop:   # Fixed Resolution: the group renders only this centred area (clips soft glows that spill past a card's edge)
            fixed = ('<parameter name="Object" id="2" flags="8589938704"><parameter name="Fixed Resolution" id="301" flags="8589936658" default="0" value="1"/>'
                     f'<parameter name="Fixed Width" id="302" flags="12884901910" default="3840" value="{crop[0]}"/>'
                     f'<parameter name="Fixed Height" id="303" flags="12884901910" default="2160" value="{crop[1]}"/></parameter>\n')
        x = f'''<group name="{name}" id="{gid}">
{children}<aspectRatio>1</aspectRatio>
<flags>0</flags>
{TIMING}
<foldFlags>0</foldFlags>
<baseFlags>524304</baseFlags>
<parameter name="Properties" id="1" flags="8589938704">
<parameter name="Transform" id="100" flags="8589938704">
<parameter name="Position" id="101" flags="8589938704"><foldFlags>11</foldFlags>{ch('X','1',0,px)}{ch('Y','2',0,py)}{ch('Z','3',0,pz) if pz is not None else ''}</parameter>
<parameter name="Rotation" id="109" flags="8589938704"><foldFlags>15</foldFlags>{ch('X','1',0,rx) if rx else ''}{ch('Z','3',0,rz)}</parameter>
<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags>{ch('X','1',1,sx)}{ch('Y','2',1,sy)}</parameter>
{anchor}</parameter>
<parameter name="Blending" id="200" flags="8589938704">{ch('Opacity','202',1,op)}</parameter>
</parameter>
{fixed}{beh}</group>
'''
        return gid, x

    def rect(self, name, w, h, col, op=1, px=0, py=0, rnd=0, feather=0, beh='', fill=True, outline=None):
        bid = self.new()
        r = re.sub(r'<scenenode name="Gradient" id="\d+"', f'<scenenode name="{name}" id="{bid}"', self.RECT, 1)
        r = re.sub(r'(<parameter name="Position" id="101" flags="8589938704">\s*<foldFlags>15</foldFlags>\s*)<parameter name="X"[^>]*/>\s*<parameter name="Y"[^>]*/>',
                   lambda m: m.group(1)+self.scal('X', '1', 0, px)+self.scal('Y', '2', 0, py), r, 1)
        r = re.sub(r'<parameter name="Opacity" id="202" flags="8606711824" default="1" value="[^"]*"/>',
                   self.scal('Opacity', '202', 1, op), r, 1)
        r = re.sub(r'<parameter name="Feather" id="102" flags="8606744592" default="0" value="[^"]*"/>',
                   f'<parameter name="Feather" id="102" flags="8606744592" default="0" value="{feather}"/>\n'
                   f'<parameter name="Roundness" id="144" flags="8606711824" default="0" value="{rnd}"/>', r, 1)
        r = re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>).*?(\s*</parameter>)',
                   lambda m: m.group(1)+colp(col)+m.group(2), r, 1, flags=re.S)
        r = re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>',
                   f'<parameter name="Width" id="1" flags="12901679120" default="{w}" value="{w}"/>', r, 1)
        r = re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>',
                   f'<parameter name="Height" id="2" flags="12901679120" default="{h}" value="{h}"/>', r, 1)
        if not fill:
            r = r.replace('<parameter name="Fill" id="113" flags="8589938704">', '<parameter name="Fill" id="113" flags="8589971472">', 1)
        if outline:
            ocol, ow = outline
            r = r.replace('<parameter name="Outline" id="108" flags="8589971472">',
                          '<parameter name="Outline" id="108" flags="8589938704"><parameter name="Brush Color" id="107" flags="8589938704"><foldFlags>11</foldFlags>%s</parameter>'
                          '<parameter name="Brush Opacity" id="142" flags="8606711824" default="1" value="1"/><parameter name="Width" id="105" flags="8606711824" default="2" value="%s"/>' % (colp(ocol), ow), 1)
        if beh:
            k = r.rfind('</scenenode>'); r = r[:k]+beh+r[k:]
        return bid, r

    def text(self, name, txt, size, col=(1, 1, 1), px=0, py=0, op=1, align=1, font='KohinoorBangla-Bold',
             tracking=None, beh_fn=None):
        """beh_fn(tid, subid) -> behaviour xml (e.g. sequence text) appended inside the text node"""
        tid, pid, sid, sub = self.new(), self.new(), self.new(), self.new()
        t = self.TXT
        t = re.sub(r'<scenenode name="Title" id="\d+"', f'<scenenode name="{name}" id="{tid}"', t, 1)
        t = re.sub(r'<text>.*?</text>', '<text>%s</text>' % txt, t, 1, flags=re.S)
        o_p = re.search(r'<paragraphStyle id="(\d+)">', t).group(1)
        o_s = re.search(r'<style name="Style" id="(\d+)"', t).group(1)
        o_sub = re.search(r'<parameter name="Substance" id="(\d+)"', t).group(1)
        t = t.replace(f'<paragraphStyle id="{o_p}">', f'<paragraphStyle id="{pid}">').replace(f'<parameter name="Paragraph" id="{o_p}"', f'<parameter name="Paragraph" id="{pid}"')
        t = t.replace(f'<style name="Style" id="{o_s}"', f'<style name="Style" id="{sid}"').replace(f'style="{o_s}"', f'style="{sid}"')
        t = t.replace(f'<parameter name="Substance" id="{o_sub}"', f'<parameter name="Substance" id="{sub}"')
        t = re.sub(r'<styleRun style="(\d+)" offset="0" length="\d+"/>', f'<styleRun style="{sid}" offset="0" length="{len(txt)}"/>', t, 1)
        t = t.replace('value="120"/>', f'value="{size}"/>', 1)
        self.text_sizes = getattr(self, 'text_sizes', {}); self.text_sizes[tid] = size
        t = t.replace('<font>KohinoorBangla-Bold</font>', f'<font>{font}</font>', 1)
        t = re.sub(r'<parameter name="Alignment" id="401" flags="8606777360" default="0" value="\d"/>',
                   f'<parameter name="Alignment" id="401" flags="8606777360" default="0" value="{align}"/>', t)
        face = ('<parameter name="Face" id="14" flags="8589938704">\n<foldFlags>131072</foldFlags>\n'
                f'<parameter name="Color" id="16" flags="8589938704"><foldFlags>11</foldFlags>{colp(col)}</parameter>\n')
        t = re.sub(r'<parameter name="Face" id="14" flags="\d+">\s*<foldFlags>131072</foldFlags>', lambda m: face, t, 1)
        assert f'id="16"' in t, 'face colour'
        if tracking is not None:
            t = t.replace(f'value="{size}"/>', f'value="{size}"/>\n<parameter name="Tracking" id="5" flags="8606711824" default="0" value="{tracking}"/>', 1)
        # position + opacity
        t = t.replace('<parameter name="Transform" id="100" flags="8589938704">',
                      '<parameter name="Transform" id="100" flags="8589938704">'
                      f'<parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags>{self.scal("X","1",0,px)}{self.scal("Y","2",0,py)}</parameter>', 1)
        t = t.replace('<parameter name="Properties" id="1" flags="8589938704">',
                      '<parameter name="Properties" id="1" flags="8589938704">'
                      f'<parameter name="Blending" id="200" flags="8589938704">{self.scal("Opacity","202",1,op)}</parameter>', 1)
        if beh_fn:
            b = beh_fn(tid, sub); k = t.rfind('</scenenode>'); t = t[:k]+b+t[k:]
        return tid, sid, t

    def image(self, name, clip_name, rel, w, h, dropzone=True, px=0, py=0, s=1.0, op=1, shadow=None):
        cid, iid = self.new(), self.new()
        c = self.CLIP.replace(re.search(r'<clip name="Drop Zone" id="\d+">', self.CLIP).group(0), f'<clip name="{clip_name}" id="{cid}">')
        if rel: c = c.replace('<pathURL>Drop Zone.tiff</pathURL>', f'<relativeURL>{rel}</relativeURL>')
        c = c.replace('<missingWidth>1200</missingWidth>', f'<missingWidth>{w}</missingWidth>').replace('<missingHeight>1200</missingHeight>', f'<missingHeight>{h}</missingHeight>')
        c = c.replace('default="1200" value="1200"', f'default="{w}" value="{w}"', 1).replace('default="1200" value="1200"', f'default="{h}" value="{h}"', 1)
        c = c.replace('<parameter name="Object" id="2" flags="8589938704">', '<parameter name="Object" id="2" flags="8589938704"><parameter name="Alpha Type" id="100" flags="8589938704"><parameter name="Alpha Type" id="101" flags="8606777344" default="0" value="1"/></parameter>', 1)
        c = c.replace('<timing in="0 1 1 0" out="0 120000 1 0" offset="0 1 1 0"/>', TIMING, 1)
        self.clips += c + '\n'
        x = re.sub(r'<scenenode name="Drop Zone" id="\d+"', f'<scenenode name="{name}" id="{iid}"', self.DZ, 1)
        x = re.sub(r'\s*<parameter name="Crop" id="216" flags="\d+">\s*<foldFlags>\d+</foldFlags>(\s*<parameter [^>]*/>)*\s*</parameter>', '', x, count=1)
        x = re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>', '', x, count=1, flags=re.S)
        x = re.sub(r'(<parameter name="Source Media" id="300" flags="\d+") default="\d+" value="\d+"/>', rf'\1 default="{cid}" value="{cid}"/>', x, 1)
        if not dropzone:
            x = x.replace('<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="1"/>', '<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="0"/>')
        x = re.sub(r'<parameter name="Width" id="313" flags="(\d+)" default="1" value="\d+"/>', rf'<parameter name="Width" id="313" flags="\1" default="1" value="{w}"/>', x, 1)
        x = re.sub(r'<parameter name="Height" id="314" flags="(\d+)" default="1" value="\d+"/>', rf'<parameter name="Height" id="314" flags="\1" default="1" value="{h}"/>', x, 1)
        x = x.replace('<parameter name="Fit" id="317" flags="8606777360" default="0" value="0"/>', '<parameter name="Fit" id="317" flags="8606777360" default="0" value="0"/>', 1)
        props = ('<parameter name="Properties" id="1" flags="8589938704">'
                 '<parameter name="Transform" id="100" flags="8589938704">'
                 f'<parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags>{self.scal("X","1",0,px)}{self.scal("Y","2",0,py)}</parameter>'
                 f'<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags>{self.scal("X","1",1,s)}{self.scal("Y","2",1,s)}</parameter></parameter>'
                 f'<parameter name="Blending" id="200" flags="8589938704">{self.scal("Opacity","202",1,op)}</parameter>')
        if shadow:
            o, bl, d, ang = shadow
            props += ('<parameter name="Drop Shadow" id="208" flags="8589938704"><foldFlags>131083</foldFlags>'
                      f'<parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="{o}"/>'
                      f'<parameter name="Blur" id="213" flags="8606711824" default="5" value="{bl}"/>'
                      f'<parameter name="Distance" id="212" flags="8606711824" default="5" value="{d}"/>'
                      f'<parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="{ang}"/></parameter>')
        x = x.replace('<parameter name="Properties" id="1" flags="8589938704">', props, 1)
        return iid, cid, x

    # ---- behaviours
    def link(self, name, aff, afffac, chan, src, chans, mode=2, mix=1, scale=1):
        lid = self.new(); ds = [(self.new(), self.new(), self.new(), t, sc) for t, sc in chans]
        x = f'<behavior name="{name}" id="{lid}" factoryID="{self.F("LNK")}">\n'
        for o, mn, mx, t, sc in ds: x += f'<dynamicChannelIDSet offsetChannelID="{o}" rangeMinChannelID="{mn}" rangeMaxChannelID="{mx}"/>\n'
        x += f'<channelBehavior affectingFactory="{U[afffac]}" affectingChannel="{chan}" sliderRange="{B}"/>\n{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
        x += f'<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{aff}"/>\n'
        x += f'<parameter name="Source Object" id="201" flags="77326254096" default="0" value="{src}"/>\n'
        x += f'<parameter name="Apply Mode" id="200" flags="8606777360" default="2" value="{mode}"/>\n'
        x += f'<parameter name="Scale" id="204" flags="8606711824" default="1" value="{scale}"/>\n'
        x += '<parameter name="Mix Time Range" id="206" flags="8606711826" default="10" value="10"/>\n'
        x += f'<parameter name="Custom Mix" id="207" flags="8606711824" default="1" value="{mix}"/>\n'
        x += '<parameter name="Clamp Source Value Within Range" id="209" flags="8606711826" default="1" value="0"/>\n'
        for o, mn, mx, t, sc in ds:
            x += f'<parameter name="Value offset" id="{o}" flags="16777232" default="0" value="0"/>\n'
            x += f'<parameter name="Value min" id="{mn}" flags="16777234" default="-100" value="-100"/>\n<parameter name="Value max" id="{mx}" flags="16777234" default="100" value="100"/>\n'
        parent = chans[0][1] if len(chans) == 1 else chans[0][1].rsplit('/', 1)[0]
        x += f'<sourceParentChannelRef>{parent}</sourceParentChannelRef>\n'
        for o, mn, mx, t, sc in ds:
            x += f'<expressionChannels><sourceChannelRef>{sc}</sourceChannelRef><targetChannelID>{t}</targetChannelID><offsetChannelRef>./{o}</offsetChannelRef><minChannelRef>./{mn}</minChannelRef><maxChannelRef>./{mx}</maxChannelRef></expressionChannels>\n'
        return lid, x + '</behavior>\n'

    def rig(self, name, target, afffac, chan, widget, snaps, pname='Value', rng='1', vec=None):
        rid = self.new()
        x = f'<behavior name="{name}" id="{rid}" factoryID="{self.F("RB")}">\n<channelBehavior affectingFactory="{U[afffac]}" affectingChannel="{chan}" sliderRange="{rng}"/>\n'
        x += '<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<baseFlags>8589934610</baseFlags>\n'
        x += f'<parameter name="Affecting Object (Hidden)" id="199" flags="77309476882" default="0" value="{target}"/>\n'
        x += f'<parameter name="Widget" id="200" flags="77309476880" default="0" value="{widget}"/>\n'
        x += '<parameter name="Snapshots" id="202" flags="8590004242">\n<flags>8590004242</flags>\n'
        for sid, v in snaps:
            if vec:
                x += f'<parameter name="{pname}" id="{sid}" factoryID="{self.F("CW")}"><flags>8589938704</flags><foldFlags>11</foldFlags>'
                for k, (cn, cv) in enumerate(zip(vec, v)):
                    x += f'<parameter name="{cn}" id="{k+1}" factoryID="{self.F("C")}"><flags>8606711824</flags><curve type="1" default="0" value="{cv}"/></parameter>'
                x += '</parameter>\n'
            else:
                if isinstance(v, list):   # animated snapshot: the rig blends between whole animation curves
                    cv = self.curve(pname, sid, 1, v)
                    cv = cv.replace(f'<parameter name="{pname}" id="{sid}" flags="8606711824">', f'<parameter name="{pname}" id="{sid}" factoryID="{self.F("C")}"><flags>8606711824</flags>', 1)
                    x += cv + '\n'
                else:
                    x += f'<parameter name="{pname}" id="{sid}" factoryID="{self.F("C")}"><flags>8606711824</flags><curve type="1" default="1" value="{v}"/></parameter>\n'
        return x + '</parameter>\n</behavior>\n'

    def osc(self, target, name, chan, amp, speed, phase=0, afffac='GRP'):
        oid = self.new()
        x = f'<behavior name="{name}" id="{oid}" factoryID="{self.F("OSC")}">\n<channelBehavior affectingFactory="{U[afffac]}" affectingChannel="{chan}" sliderRange="{B}"/>\n{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
        x += f'<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{target}"/>\n<parameter name="Phase" id="200" flags="8606711824" default="0" value="{phase}"/>\n'
        x += f'<parameter name="Amplitude" id="201" flags="8606711824" default="100" value="{amp}"/>\n<parameter name="Speed" id="202" flags="8606711824" default="10" value="{speed}"/>\n</behavior>\n'
        return oid, x

    def rate(self, target, name, chan, r, afffac='GRP'):
        bid = self.new()
        x = (f'<behavior name="{name}" id="{bid}" factoryID="{self.F("RATE")}">\n<channelBehavior affectingFactory="{U[afffac]}" affectingChannel="{chan}" sliderRange="{B}"/>\n{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
             f'<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{target}"/>\n<parameter name="Rate" id="200" flags="8606711824" default="0" value="{r}"/>\n</behavior>\n')
        return bid, x

    def seq_words(self, name, sub, t_in, t_out, dy=-40, dx=0, spread=60, op0=0, scale=None):
        """Sequence Text by word (from the proven Words Type 1 behaviour). sub = the text's Substance id."""
        a = self.words1.find('<behavior name="Words in"'); b = self.words1.find('</behavior>', a)+11
        x = self.remap(self.words1[a:b], self.words1)
        o_sub = re.search(r'<parameter name="Substance" id="(\d+)"', x).group(1)
        x = x.replace(f'id="{o_sub}"', f'id="{sub}"')
        bid = self.new()
        x = re.sub(r'<behavior name="Words in" id="\d+"', f'<behavior name="{name}" id="{bid}"', x, 1)
        x = re.sub(r'<timing in="[^"]*" out="[^"]*" offset="0 1 1 0"/>', f'<timing in="{T(t_in)}" out="{T(t_out)}" offset="0 1 1 0"/>', x, 1)
        x = x.replace('<parameter name="X" id="1" flags="8606711824" default="0" value="0"/><parameter name="Y" id="2" flags="8606711824" default="0" value="-40"/>',
                      f'<parameter name="X" id="1" flags="8606711824" default="0" value="{dx}"/><parameter name="Y" id="2" flags="8606711824" default="0" value="{dy}"/>', 1)
        x = x.replace('<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="0"/>',
                      f'<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="{op0}"/>', 1)
        if scale is not None:
            x = x.replace('<parameter name="Opacity" id="1044"',
                          f'<parameter name="Scale" id="1002" flags="8589938688"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="{scale}"/><parameter name="Y" id="2" flags="8606711824" default="1" value="{scale}"/></parameter>\n<parameter name="Opacity" id="1044"', 1)
        x = x.replace('<parameter name="End Offset" id="213" flags="8606711824" default="0" value="60"/>',
                      f'<parameter name="End Offset" id="213" flags="8606711824" default="0" value="{spread}"/>', 1)
        return bid, x

    def align_to(self, target, code, ox=0, oy=0):
        bid = self.new()
        return bid, (f'<behavior name="Align" id="{bid}" factoryID="{self.F("ALIGN")}">\n{TIMING}\n<baseFlags>8589934609</baseFlags>\n'
                     f'<parameter name="Object" id="200" flags="77326254096" default="0" value="{target}"/>\n<parameter name="Align" id="201" flags="8606777360" default="0" value="0"/>\n'
                     f'<parameter name="To" id="202" flags="8606777360" default="0" value="{code}"/>\n'
                     f'<parameter name="Offset" id="203" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="0" value="{ox}"/><parameter name="Y" id="2" flags="8606711824" default="0" value="{oy}"/></parameter>\n</behavior>\n')

    # ---- widgets
    def w_popup(self, name, entries, default_idx):
        wid = self.new(); sids = list(range(1, len(entries)+1))
        x = f'<scenenode name="{name}" id="{wid}" factoryID="{self.F("W")}" version="5">\n<affecting>2</affecting>\n' + ''.join(f'<snapshot>{i}</snapshot>\n' for i in sids)
        x += '<flags>0</flags>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<foldFlags>0</foldFlags>\n<baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
        x += '<parameter name="Options" id="103" flags="8589938688"><parameter name="Initial Value" id="106" flags="77326254096" default="0" value="0"/></parameter>\n'
        x += f'<parameter name="Hidden" id="102" flags="8606711824" default="0" value="{sids[default_idx]}"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
        for i, sid in enumerate(sids):
            x += f'<parameter name="Snapshots" id="{sid}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{i}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
        x += f'</parameter>\n<parameter name="{name}" id="100" flags="8606777360" default="0" value="{default_idx}">\n' + ''.join(f'<entry name="{e}" tag="{i}"/>\n' for i, e in enumerate(entries))
        self.widgets += x + '</parameter>\n</parameter>\n</scenenode>\n'
        return wid

    def w_check(self, name, on):
        wid = self.new()
        self.widgets += f'''<scenenode name="{name}" id="{wid}" factoryID="{self.F("W")}" version="5">
<affecting>1</affecting><snapshot>1</snapshot><snapshot>2</snapshot>
<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>
<parameter name="Properties" id="1" flags="8589938704"/>
<parameter name="Object" id="2" flags="8589938704"><parameter name="Options" id="103" flags="8589938688"/>
<parameter name="Hidden" id="102" flags="8606711824" default="0" value="{2 if on else 1}"/>
<parameter name="Snapshots" id="101" flags="8589938706">
<parameter name="Snapshots" id="1" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="0"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
<parameter name="Snapshots" id="2" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="1"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
</parameter>
<parameter name="{name}" id="100" flags="8606711824" default="0" value="{1 if on else 0}"/></parameter></scenenode>
'''
        return wid

    def w_slider(self, name, val, rmin=0, rmax=100):
        """two snapshots: 0 -> value at rmin, 1 -> value at rmax ; val in [0,1]"""
        wid = self.new(); self.sliders = getattr(self, 'sliders', set()) | {wid}
        self.widgets += f'''<scenenode name="{name}" id="{wid}" factoryID="{self.F("W")}" version="5">
<affecting>3</affecting><snapshot>1</snapshot><snapshot>2</snapshot>
<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>
<parameter name="Properties" id="1" flags="8589938704"/>
<parameter name="Object" id="2" flags="8589938704">
<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="{rmin}"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="{rmax}"/></parameter>
<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>
<parameter name="Snapshots" id="101" flags="8589938706">
<parameter name="Snapshots" id="1" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="0"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
<parameter name="Snapshots" id="2" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="1"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
</parameter>
<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>
'''
        return wid

    def dir_blur(self, name, angle=1.5707963267948966, amount=0):
        """Directional Blur filter (amount 0, no crop so the blur can spill past the card edge). Returns (fid, xml)."""
        fid = self.new()
        x = (f'<filter name="{name}" id="{fid}" factoryID="{self.F("FILT")}" pluginUUID="2E7B1340-5D4F-4015-8AA0-53BEB9F2CA52" pluginVersion="1" pluginName="Directional Blur" pluginDynamicParams="0">\n'
             f'{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
             + (f'<parameter name="Amount" id="1" flags="12901679120" default="7" value="{amount}"/>\n' if not isinstance(amount, list) else
                self.curve('Amount', '1', 7, amount).replace('flags="8606711824"', 'flags="12901679120"', 1) + '\n') +
             f'<parameter name="Angle" id="2" flags="12901679120" default="0" value="{angle}"/>\n'
             '<parameter name="Crop" id="3" flags="12901679104" default="0" value="0"/>\n'
             '<parameter name="OSC Center" id="4" flags="12889165856"><foldFlags>15</foldFlags></parameter>\n'
             '<parameter name="Mix" id="10001" flags="12901679104" default="1" value="1"/>\n'
             '<parameter name="Flip" id="10002" flags="12905938976" default="0" value="0"/>\n'
             '<parameter name="Input Points" id="10003" flags="12905938976" default="1" value="1"/>\n'
             '<parameter name="Publish OSC" id="10005" flags="12901679104" default="0" value="0"/>\n</filter>\n')
        return fid, x

    def publish(self, obj, chan, name): self.pub.append((obj, chan, name))

    # ---- assemble
    def slider_bases(self, s):
        """Final Cut renders a published slider set to exactly 0 with the rigged parameter's stored (base) value,
        so every slider-rigged parameter gets the value of the slider's 0-snapshot as its base value."""
        sl = getattr(self, 'sliders', set()); n = 0
        pat = re.compile(r'<behavior name="[^"]*" id="\d+" factoryID="\d+">\s*<channelBehavior affectingFactory="[^"]*" affectingChannel="([^"]*)"[^>]*/>'
                         r'\s*<timing[^>]*/>\s*<baseFlags>\d+</baseFlags>\s*<parameter name="Affecting Object \(Hidden\)" id="199" flags="\d+" default="0" value="(\d+)"/>'
                         r'\s*<parameter name="Widget" id="200" flags="\d+" default="0" value="(\d+)"/>\s*<parameter name="Snapshots" id="202"[^>]*>\s*<flags>\d+</flags>'
                         r'\s*<parameter name="[^"]*" id="1" factoryID="\d+"><flags>\d+</flags><curve type="1" default="1" value="([^"]*)"/>')
        for m in list(pat.finditer(s)):
            chan, tgt, wid, v0 = m.groups()
            if wid not in sl: continue
            mt = re.search(rf'<(behavior|scenenode|layer|group) name="[^"]*" id="{tgt}"', s); a = mt.start()
            if mt.group(1) == 'behavior': e = s.find('</behavior>', a)
            cur = a
            if mt.group(1) != 'behavior':
                e = span(s, a, mt.group(1)); cur = s.rfind('<aspectRatio>', a, e); assert cur > 0
            for pid in chan[2:].split('/'):
                mm = re.compile(rf'<parameter name="[^"]*" id="{pid}"[^>]*?(/?)>').search(s, cur, e)
                assert mm, (tgt, chan)
                cur = mm.start()
            tag_end = s.find('>', cur)
            tag = s[cur:tag_end]
            assert ' value="' in tag, (tgt, chan, tag)
            s = s[:cur] + re.sub(r' value="[^"]*"', f' value="{v0}"', tag, 1) + s[tag_end:]; n += 1
        self.slider_base_count = n
        return s

    def save(self, path, root_xml, markers=(1.0, END-0.6)):
        s = self.s
        a = s.find('<layer name="Group"'); b = s.find('>', a)+1
        if self.kind == 'title':
            c = s.find('<scenenode name="Title Background"', b)
        else:
            c = s.find('<aspectRatio>1</aspectRatio>', b)
        s = s[:b] + '\n' + root_xml + s[c:]
        # title background drop zone stays (disabled) - FCP expects it
        k = s.find('<clip name="Drop Zone"'); s = s[:k] + self.clips + s[k:]
        pa = s.find('<scenenode name="Project"'); pe = span(s, pa)
        rig = (f'<scenenode name="Rig" id="{self.new()}" factoryID="{self.F("RIG")}" version="5">\n' + self.widgets +
               '<flags>0</flags>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<foldFlags>0</foldFlags>\n<baseFlags>16</baseFlags>\n'
               '<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704"/>\n</scenenode>\n')
        s = s[:pe] + '\n' + rig + s[pe:]
        pubx = ''.join(f'\t\t<target object="{o}" channel="{c}" name="{n}"/>\n' for o, c, n in self.pub)
        s = re.sub(r'<publishSettings>\s*<version>2</version>\s*(<target object="\d+" channel="./1/324/300" name="Drop Zone"/>\s*)?',
                   lambda m: '<publishSettings>\n\t\t<version>2</version>\n' + pubx, s, 1)
        if markers: s = s.replace('<timemarkerset/>', f'<timemarkerset><timemarker><inpoint>{T(markers[0])}</inpoint><color>1</color><type>4</type></timemarker>'
                      f'<timemarker><inpoint>{T(markers[1])}</inpoint><color>1</color><type>6</type></timemarker></timemarkerset>', 1)
        s = self.slider_bases(s)
        self.F('RIG')
        s = s.replace('<build>', self.add_fac + '<build>', 1)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').write(s)
        return s
