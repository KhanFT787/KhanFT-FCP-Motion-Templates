import re,os,math
SRC=os.path.expanduser('~/bak/cards_skeleton3.moti')
OUT='/sessions/rcw-01s7kgwhknhlhxkjotg1kyml/mnt/Titles.localized--KhanFT/KhanFT Words Type 1/KhanFT Words Type 1.moti'
s=open(SRC).read()
GRP='44da0700f6ab11d68c24000393670732'
SHP='712462a4323911d78f8400039389b702'
OSC='1a262447ab7011d7bb4600039366fb58'
LNK='68fba2c1aa094655bf4b81587efec626'
need={'Link':LNK,'Rig':'402246385249454b90e08b2ee1b6bf06','Rig Behavior':'dd0036f96c9e4bfdadb82f71fbf5c9d8',
      'Widget':'e35c74f01d5042f6b468eb530169bfb7','Oscillate':OSC,'Channel':'11615b89cbc0483fb92e95eb0c80e59c','FontChannel':'8eafb077e84c45e1996a83033a3a2c49','Average':'d6bd636a8c7311d79cc900039366fb58','Align To':'eecb322ed23242d8ae51f33765574dbd','Sequence Text':'9279a0e120d64a82b26b4cf79391ff47','Basic Ch':'03ce4d4f0ea74b3b9af072a0e4a61ab7','Substance Ch':'f4c2c6ef713f4a18ae987242c8b7f619'}
facs={u:i for i,u in re.findall(r'<factory id="(\d+)" uuid="([^"]*)">',s)}
nf=max(int(i) for i in facs.values())+1; add=''
for d,u in need.items():
    if u not in facs:
        facs[u]=str(nf); add+=f'<factory id="{nf}" uuid="{u}">\n\t<description>{d}</description>\n\t<manufacturer>Apple</manufacturer>\n\t<version>1</version>\n</factory>\n'; nf+=1
s=s.replace('<build>',add+'<build>',1)
F_LNK=facs[LNK]; F_RIG=facs[need['Rig']]; F_RB=facs[need['Rig Behavior']]; F_W=facs[need['Widget']]; F_OSC=facs[OSC]
F_CW=facs['11615b89cbc0483fb92e95eb0c80e59c']; F_C=facs['fdc1944b229111d7b1c300039389b702']
nid=[20000]
def new():
    nid[0]+=1; return str(nid[0])
TB=120000; FR=2002  # 59.94 fps frame ticks
def T(sec): return f'{int(round(sec*TB/FR))*FR} {TB} 1 0'
TIMING='<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>'
END=1199198/TB
# ---------- generic builders
def curve(name,pid,default,keys):
    x=f'<parameter name="{name}" id="{pid}" flags="8606711824"><curve type="1" default="{default}" value="{keys[0][1]:.5f}"><numberOfKeypoints>{len(keys)}</numberOfKeypoints>'
    for t,v in keys: x+=f'<keypoint interpolation="1" flags="0"><time>{T(t)}</time><value>{v:.5f}</value></keypoint>'
    return x+'</curve></parameter>'
def scal(name,pid,default,v): return f'<parameter name="{name}" id="{pid}" flags="8606711824" default="{default}" value="{v}"/>'
def group(name,gid,children='',px=0,py=0,sx=1,sy=1,op=1,beh='',extra_props='',pos_keys=None,sc_keys=None,op_keys=None,rz=None):
    posY = curve('Y','2',0,pos_keys) if pos_keys else scal('Y','2',0,py)
    scX = curve('X','1',1,sc_keys) if sc_keys else scal('X','1',1,sx)
    scY = curve('Y','2',1,sc_keys) if sc_keys else scal('Y','2',1,sy)
    opx = curve('Opacity','202',1,op_keys) if op_keys else f'<parameter name="Opacity" id="202" flags="8606711824" default="1" value="{op}"/>'
    return f'''<group name="{name}" id="{gid}">
{children}<aspectRatio>1</aspectRatio>
<flags>0</flags>
{TIMING}
<foldFlags>0</foldFlags>
<baseFlags>524304</baseFlags>
<parameter name="Properties" id="1" flags="8589938704">
<parameter name="Transform" id="100" flags="8589938704">
<parameter name="Position" id="101" flags="8589938704"><foldFlags>11</foldFlags>{scal('X','1',0,px)}{posY}</parameter>
{'' if rz is None else '<parameter name="Rotation" id="109" flags="8589938704"><foldFlags>15</foldFlags>'+scal('Z','3',0,rz)+'</parameter>'}
<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags>{scX}{scY}</parameter>
</parameter>
<parameter name="Blending" id="200" flags="8589938704">{opx}</parameter>
{extra_props}</parameter>
{beh}</group>
'''
def link(name,aff,afffac,chan,src,chans,mode=2,mix=1,scale=None):
    if scale is None: scale=0.5625 if any(sc=='./1/100/101/2' for t,sc in chans) else 1
    lid=new(); ds=[(new(),new(),new(),t,sc) for t,sc in chans]
    x=f'<behavior name="{name}" id="{lid}" factoryID="{F_LNK}">\n'
    for o,mn,mx,t,sc in ds: x+=f'<dynamicChannelIDSet offsetChannelID="{o}" rangeMinChannelID="{mn}" rangeMaxChannelID="{mx}"/>\n'
    x+=f'<channelBehavior affectingFactory="{afffac}" affectingChannel="{chan}" sliderRange="3.4028234663852886e+38"/>\n{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
    x+=f'<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{aff}"/>\n'
    x+=f'<parameter name="Source Object" id="201" flags="77326254096" default="0" value="{src}"/>\n'
    x+=f'<parameter name="Apply Mode" id="200" flags="8606777360" default="2" value="{mode}"/>\n'
    x+=f'<parameter name="Scale" id="204" flags="8606711824" default="1" value="{scale}"/>\n'
    x+='<parameter name="Mix Time Range" id="206" flags="8606711826" default="10" value="10"/>\n'
    x+=f'<parameter name="Custom Mix" id="207" flags="8606711824" default="1" value="{mix}"/>\n'
    x+='<parameter name="Clamp Source Value Within Range" id="209" flags="8606711826" default="1" value="0"/>\n'
    for o,mn,mx,t,sc in ds:
        x+=f'<parameter name="Value offset" id="{o}" flags="16777232" default="0" value="0"/>\n'
        x+=f'<parameter name="Value min" id="{mn}" flags="16777234" default="-100" value="-100"/>\n<parameter name="Value max" id="{mx}" flags="16777234" default="100" value="100"/>\n'
    parent=chans[0][1] if len(chans)==1 else chans[0][1].rsplit('/',1)[0]
    x+=f'<sourceParentChannelRef>{parent}</sourceParentChannelRef>\n'
    for o,mn,mx,t,sc in ds: x+=f'<expressionChannels><sourceChannelRef>{sc}</sourceChannelRef><targetChannelID>{t}</targetChannelID><offsetChannelRef>./{o}</offsetChannelRef><minChannelRef>./{mn}</minChannelRef><maxChannelRef>./{mx}</maxChannelRef></expressionChannels>\n'
    return lid,x+'</behavior>\n'
def rig(name,target,afffac,chan,widget,snaps,pname='Value',rng='1',vec=None):
    rid=new()
    x=f'<behavior name="{name}" id="{rid}" factoryID="{F_RB}">\n<channelBehavior affectingFactory="{afffac}" affectingChannel="{chan}" sliderRange="{rng}"/>\n'
    x+='<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<baseFlags>8589934610</baseFlags>\n'
    x+=f'<parameter name="Affecting Object (Hidden)" id="199" flags="77309476882" default="0" value="{target}"/>\n'
    x+=f'<parameter name="Widget" id="200" flags="77309476880" default="0" value="{widget}"/>\n'
    x+='<parameter name="Snapshots" id="202" flags="8590004242">\n<flags>8590004242</flags>\n'
    for sid,v in snaps:
        if vec:
            x+=f'<parameter name="{pname}" id="{sid}" factoryID="{F_CW}"><flags>8589938704</flags><foldFlags>11</foldFlags>'
            for k,(cn,cv) in enumerate(zip(vec,v)): x+=f'<parameter name="{cn}" id="{k+1}" factoryID="{F_C}"><flags>8606711824</flags><curve type="1" default="0" value="{cv}"/></parameter>'
            x+='</parameter>\n'
        else:
            x+=f'<parameter name="{pname}" id="{sid}" factoryID="{F_C}"><flags>8606711824</flags><curve type="1" default="1" value="{v}"/></parameter>\n'
    return x+'</parameter>\n</behavior>\n'
def widget_popup(name,wid,entries,default_idx):
    sids=list(range(1,len(entries)+1))
    x=f'<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">\n<affecting>2</affecting>\n'+''.join(f'<snapshot>{i}</snapshot>\n' for i in sids)
    x+='<flags>0</flags>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<foldFlags>0</foldFlags>\n<baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
    x+='<parameter name="Options" id="103" flags="8589938688"><parameter name="Initial Value" id="106" flags="77326254096" default="0" value="0"/></parameter>\n'
    x+=f'<parameter name="Hidden" id="102" flags="8606711824" default="0" value="{sids[default_idx]}"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
    for i,sid in enumerate(sids): x+=f'<parameter name="Snapshots" id="{sid}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{i}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
    x+=f'</parameter>\n<parameter name="{name}" id="100" flags="8606777360" default="0" value="{default_idx}">\n'+''.join(f'<entry name="{e}" tag="{i}"/>\n' for i,e in enumerate(entries))
    return x+'</parameter>\n</parameter>\n</scenenode>\n'
def widget_check(name,wid,on):
    return f'''<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">
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
def widget_slider(name,wid,val):
    return f'''<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">
<affecting>3</affecting><snapshot>1</snapshot><snapshot>2</snapshot>
<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>
<parameter name="Properties" id="1" flags="8589938704"/>
<parameter name="Object" id="2" flags="8589938704">
<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="0"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="100"/></parameter>
<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>
<parameter name="Snapshots" id="101" flags="8589938706">
<parameter name="Snapshots" id="1" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="0"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
<parameter name="Snapshots" id="2" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="1"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>
</parameter>
<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>
'''
# ---------- templates from skeleton
def span(text,start,tag='scenenode'):
    depth=0
    for mm in re.finditer(r'<(/?)%s\b[^>]*?(/?)>'%tag,text[start:]):
        if mm.group(2): continue
        depth+= -1 if mm.group(1) else 1
        if depth==0: return start+mm.end()
def node(name):
    a=s.find('<scenenode name="%s"'%name); return s[a:span(s,a)]
TXT=node('Type Text Here'); DZ=node('Drop Zone'); RECT=node('Rectangle')
clipA=s.find('<clip name="Drop Zone"'); CLIP=s[clipA:s.find('</clip>',clipA)+7]
# ================= KhanFT Text Type 1 =================
B='3.4028234663852886e+38'
TXF='babfc7777f4711d7aaa7000393833f6a'
F_AL=facs['eecb322ed23242d8ae51f33765574dbd']
K=4.0      # position X -> shape size (a link reads 1/4)
KY=2.25    # position Y -> shape size
NAVY=(0.118,0.161,0.231); GOLD=(0.984,0.749,0.141)
DEF_TEXT='আর্থিক স্বাধীনতা'
def ins(xml,beh):
    k=xml.rfind('</scenenode>'); return xml[:k]+beh+xml[k:]
def align_to(target,code,ox=0,oy=0,bid=None,rigs=''):
    return (f'<behavior name="Align" id="{bid or new()}" factoryID="{F_AL}">\n{TIMING}\n<baseFlags>8589934609</baseFlags>\n<parameter name="Object" id="200" flags="77326254096" default="0" value="{target}"/>\n<parameter name="Align" id="201" flags="8606777360" default="0" value="0"/>\n<parameter name="To" id="202" flags="8606777360" default="0" value="{code}"/>\n'
            f'<parameter name="Offset" id="203" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="0" value="{ox}"/><parameter name="Y" id="2" flags="8606711824" default="0" value="{oy}"/></parameter>\n</behavior>\n')
def colp(col): return '<parameter name="Red" id="1" flags="8606711824" default="1" value="%s"/><parameter name="Green" id="2" flags="8606711824" default="1" value="%s"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="%s"/>'%col
def rect(name,w,h,col,rnd=0,op=1,px=0,py=0,shadow=False,border=None):
    bid=new()
    r=RECT.replace('name="Rectangle" id="10244"',f'name="{name}" id="{bid}"',1)
    r=re.sub(r'<parameter name="X" id="1" flags="8606711824" default="0" value="-493[^"]*"/>',f'<parameter name="X" id="1" flags="8606711824" default="0" value="{px}"/>',r)
    r=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-251[^"]*"/>',f'<parameter name="Y" id="2" flags="8606711824" default="0" value="{py}"/>',r)
    r=r.replace('<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>','<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>\n<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%s"/>'%rnd)
    r=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)',r'\1'+colp(col),r)
    r=re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Width" id="1" flags="12901679120" default="{w}" value="{w}"/>',r)
    r=re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Height" id="2" flags="12901679120" default="{h}" value="{h}"/>',r)
    r=r.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="%s"/></parameter>'%op,1)
    if shadow:
        r=r.replace('<parameter name="Lighting" id="230"','<parameter name="Drop Shadow" id="208" flags="8589940752"><foldFlags>131083</foldFlags><parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="0.3"/><parameter name="Blur" id="213" flags="8606711824" default="5" value="40"/><parameter name="Distance" id="212" flags="8606711824" default="5" value="14"/><parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="4.7123889803846897"/></parameter>\n<parameter name="Lighting" id="230"',1)
    if border:
        r=r.replace('<parameter name="Outline" id="108" flags="8589971472">','<parameter name="Outline" id="108" flags="8589938704"><parameter name="Brush Color" id="107" flags="8589938704"><foldFlags>11</foldFlags>%s</parameter><parameter name="Brush Opacity" id="142" flags="8606711824" default="1" value="1"/><parameter name="Width" id="105" flags="8606711824" default="2" value="0"/>'%colp(border),1)
    return bid,r
def dgroup(name,gid,px=None,py=None,sx=None,sy=None,op=None):
    def ch(nm,pid,dflt,keys): return curve(nm,pid,dflt,keys) if keys else scal(nm,pid,dflt,dflt)
    return f'''<group name="{name}" id="{gid}">
<aspectRatio>1</aspectRatio><flags>0</flags>
{TIMING}
<foldFlags>0</foldFlags><baseFlags>524304</baseFlags>
<parameter name="Properties" id="1" flags="8589938704">
<parameter name="Transform" id="100" flags="8589938704">
<parameter name="Position" id="101" flags="8589938704"><foldFlags>11</foldFlags>{ch('X','1',0,px)}{ch('Y','2',0,py)}</parameter>
<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags>{ch('X','1',1,sx)}{ch('Y','2',1,sy)}</parameter>
</parameter>
<parameter name="Blending" id="200" flags="8589938704">{ch('Opacity','202',1,op)}</parameter>
</parameter>
</group>
'''
def smooth(p): return p*p*(3-2*p)
def ease_out(p): return 1-(1-p)**3
def ease_in(p): return p**3
def ease_in_back(p,s=1.6): return p*p*((s+1)*p-s)
def spring(p,pk=0.35,ov=0.12,half=0.2,a=5.2):
    if p<pk:
        q=p/pk; return (1+ov)*(1-(1-q)**2)
    t=p-pk; w=math.pi/half
    return 1+ov*math.exp(-a*t)*(math.cos(w*t)+(a/w)*math.sin(w*t))*(1 if p<0.999 else 0)
def keys(t0,d,f,n=None):
    n=n or max(8,int(d*60)); return [(t0+d*k/n,f(k/n)) for k in range(n+1)]
def widget_slider_n(name,wid,vals,val,rmin,rmax):
    n=len(vals)
    x=f'<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">\n<affecting>3</affecting>'+''.join(f'<snapshot>{k+1}</snapshot>' for k in range(n))
    x+=f'<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
    x+=f'<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="{rmin}"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="{rmax}"/></parameter>\n'
    x+='<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
    for k in range(n): x+=f'<parameter name="Snapshots" id="{k+1}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{k/(n-1)}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
    return x+f'</parameter>\n<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>\n'
# ---------- widgets
W_PL,W_BG,W_AIN,W_AOUT,W_SIN,W_SOUT,W_PADX,W_PADY,W_THK=[new() for _ in range(9)]
PLACES=[('Center',0,0,1),('Lower Third Left',-1500,-640,0),('Lower Third Center',0,-640,1),('Lower Third Right',1500,-640,2),
        ('Top Left',-1500,760,0),('Top Center',0,760,1),('Top Right',1500,760,2),('Middle Left',-1500,0,0),('Middle Right',1500,0,2)]
BGS=['None','Box','Box + Accent Bar','Underline','Side Bar','Highlight']
import sys
BG_DEF=int(os.environ.get('BG_DEF','1'))
PL_DEF=int(os.environ.get('PL_DEF','0'))
WORDS=bool(os.environ.get('WORDS'))
WT,WB_=44/120,-93/120; WK=1.0
SEQ=['Box Grow'] if WORDS else []   # Typewriter / Wipe removed; word-by-word only in KhanFT Words
AIN_DEF=int(os.environ.get('AIN_DEF','1'))
if WORDS:
    ANIM_IN=['None','Box Grow','Pop','Fade Up','Slide']
    ANIM_OUT=['None','Box Grow','Pop','Fade Down','Slide']
    DEF_TEXT='টাকা জমানোর সহজ উপায়'
else:
    ANIM_IN=['None','Pop','Fade Up','Slide','Expand']
    ANIM_OUT=['None','Pop','Fade Down','Slide','Collapse']
HS=[80000]
def swapS(): nid[0],HS[0]=HS[0],nid[0]
SEQ_IN_T0=0.35; SEQ_OUT_END=END-0.42
SEQ_DUR={'Typewriter':1.3,'Word by Word':1.0,'Wipe':0.9}
SPN=['Snap','Normal','Slow']
DUR={'in':[0.45,0.7,1.1],'out':[0.35,0.5,0.8]}
PADX_MAX,PADY_MAX,THK_MAX=400,300,60
PADX,PADY,THK=100,50,18
# ---------- text
tid=new()
t=TXT.replace('name="Type Text Here" id="10210"',f'name="Title" id="{tid}"',1)
t=t.replace('<text>Type Text Here</text>','<text>%s</text>'%DEF_TEXT).replace('length="14"','length="%d"'%len(DEF_TEXT))
pid=new(); t=t.replace('<paragraphStyle id="10239">','<paragraphStyle id="%s">'%pid).replace('<parameter name="Paragraph" id="10239"','<parameter name="Paragraph" id="%s"'%pid)
sid=new(); t=t.replace('id="10241" factoryID','id="%s" factoryID'%sid).replace('style="10241"','style="%s"'%sid)
SUBID=new(); t=t.replace('<parameter name="Substance" id="10229"','<parameter name="Substance" id="%s"'%SUBID)
t=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-921[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>',t)
t=t.replace('<parameter name="X" id="1" flags="8606711824" default="0" value="1728"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="0"/>').replace('<parameter name="Y" id="2" flags="8606711824" default="0" value="50"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>')
for c,i in (('Red',1),('Green',2),('Blue',3)):
    t=re.sub(r'<parameter name="%s" id="%d" flags="8606711824" default="1" value="0\.1[35][0-9]*"/>'%(c,i),'<parameter name="%s" id="%d" flags="8606711824" default="1" value="1"/>'%(c,i),t,count=1)
t=t.replace('<parameter name="All Caps" id="12" flags="8606711824" default="0" value="1"/>','<parameter name="All Caps" id="12" flags="8606711824" default="0" value="0"/>\n<parameter name="Size" id="3" flags="8606711824" default="48" value="130"/>',1)
t=t.replace('<parameter name="Alignment" id="401" flags="8606777360" default="0" value="1"/>','<parameter name="Alignment" id="401" flags="8606777360" default="0" value="%d"/>'%PLACES[PL_DEF][3])
assert '<text>%s</text>'%DEF_TEXT in t and 'value="130"' in t
if WORDS:
    SM=open(os.path.expanduser('~/bak/words1_motion.moti')).read()
    smf={i:u for i,u in re.findall(r'<factory id="(\d+)" uuid="([0-9a-f]+)">',SM)}
    smd={u:d for u,d in re.findall(r'uuid="([0-9a-f]+)">\s*<description>([^<]+)',SM)}
    addf=''
    for i,u in smf.items():
        if u not in facs:
            facs[u]=str(max(int(v) for v in facs.values())+1)
            addf+=f'<factory id="{facs[u]}" uuid="{u}">\n\t<description>{smd[u]}</description>\n\t<manufacturer>Apple</manufacturer>\n\t<version>1</version>\n</factory>\n'
    s=s.replace('<build>',addf+'<build>',1)
    def remapf(x): return re.sub(r'factoryID="(\d+)"',lambda m:'factoryID="%s"'%facs[smf[m.group(1)]] if m.group(1) in smf else m.group(0),x)
    a=SM.find('<scenenode name="Type Text Here"'); tn=SM[a:span(SM,a)]
    SEQT=remapf(tn[tn.find('<behavior name="Sequence Text"'):tn.find('</behavior>',tn.find('<behavior name="Sequence Text"'))+11])
    tn=re.sub(r'<behavior name="Sequence Text".*?</behavior>\s*','',tn,flags=re.S)
    tn=remapf(tn)
    o_t=re.search(r'<scenenode name="Type Text Here" id="(\d+)"',tn).group(1)
    o_p=re.search(r'<paragraphStyle id="(\d+)">',tn).group(1)
    o_s=re.search(r'<style name="Style" id="(\d+)"',tn).group(1)
    o_sub=re.search(r'<parameter name="Substance" id="(\d+)"',tn).group(1)
    tn=tn.replace(f'name="Type Text Here" id="{o_t}"',f'name="Title" id="{tid}"',1)
    for o,nw in ((o_p,pid),(o_s,sid),(o_sub,SUBID)): tn=tn.replace(f'id="{o}"',f'id="{nw}"').replace(f'style="{o}"',f'style="{nw}"')
    SEQT=SEQT.replace(f'id="{o_sub}"',f'id="{SUBID}"')
    tn=tn.replace('<parameter name="Alignment" id="401" flags="8606777360" default="0" value="1"/>','<parameter name="Alignment" id="401" flags="8606777360" default="0" value="%d"/>'%PLACES[PL_DEF][3])
    assert DEF_TEXT in tn, 'sample text'
    t=tn
t=ins(t,rig('Rig Alignment',tid,TXF,f'./2/354/{pid}/401',W_PL,[(k+1,p[3]) for k,p in enumerate(PLACES)],pname='Alignment',rng='2'))
# ---------- edge markers (invisible): tight ones on the text bounds, padded ones offset by the padding sliders
F_ALU='eecb322ed23242d8ae51f33765574dbd'
M={}; mk=''
for nm,code,ox,oy,wp,axis in (('L',2,0,0,None,0),('R',3,0,0,None,0),('T',4,0,0,None,0),('B',5,0,0,None,0),
                              ('PL',2,-PADX,0,W_PADX,-1),('PR',3,PADX,0,W_PADX,1),('PT',4,0,PADY,W_PADY,1),('PB',5,0,-PADY,W_PADY,-1)):
    mid,m=rect(f'Edge {nm}',2,2,(1,0,0),op=0)
    abid=new(); rg=''
    if wp:
        ch,mx=('./203/1',PADX_MAX) if nm in ('PL','PR') else ('./203/2',PADY_MAX)
        rg=rig(f'Rig Pad {nm}',abid,F_ALU,ch,wp,[(1,0),(2,axis*mx)],pname='X' if nm in ('PL','PR') else 'Y',rng=B)
    if WORDS and nm in ('T','B','PT','PB'):
        # vertical box edges come from the text size, not the live text bounds,
        # so the per-word rise animation can't push the box around
        if nm in ('T','B'):
            k=(WT if nm=='T' else WB_)*WK
            m=m.replace('<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="%g"/>'%(k*120),1)
            M[nm]=mid; mk+=m; continue   # fixed: matches one line of 120pt Kohinoor Bangla
        sg=1 if nm=='PT' else -1
        m=re.sub(r'(<parameter name="Y" id="2" flags="8606711824" default="0" value=")[^"]*"',r'\g<1>%g"'%(sg*PADY),m,1)
        if 'PADC' not in M:   # hidden control: its Y = padding Y (rigged); markers only use links
            pc,pr=rect('Pad Ctrl',2,2,(1,0,0),op=0,py=PADY)
            M['PADC']=pc; mk+=ins(pr,rig('Rig Pad Ctrl',pc,SHP,'./1/100/101/2',W_PADY,[(1,0),(2,PADY_MAX)],pname='Y',rng=B))
        x=link(f'{nm} add edge',mid,SHP,'./1/100/101',M[nm[1]],[('2','./1/100/101/2')],mode=0)[1]
        x+=link(f'{nm} pad',mid,SHP,'./1/100/101',M['PADC'],[('2','./1/100/101/2')],scale=0.5625*sg)[1]
        M[nm]=mid; mk+=ins(m,x); continue
    M[nm]=mid; mk+=ins(m,align_to(tid,code,ox,oy,bid=abid)+rg)
def L(name,aff,chan,src,sc,tgt,scale,mode=0):
    return link(name,aff,SHP,chan,src,[(tgt,sc)],mode=mode,scale=scale)[1]
X_='./1/100/101/1'; Y_='./1/100/101/2'
# behaviours apply bottom-up: the Replace link is listed LAST so it is applied first, the Add links after it
def fit_w(bid,l,r,frac=1.0):
    return L('W minus L',bid,'./2/353/160/1',M[l],X_,'1',-K*frac)+L('W from R',bid,'./2/353/160/1',M[r],X_,'1',K*frac,mode=2)
def fit_h(bid,t,b,frac=1.0):
    return L('H minus B',bid,'./2/353/160/2',M[b],Y_,'2',-KY*frac)+L('H from T',bid,'./2/353/160/2',M[t],Y_,'2',KY*frac,mode=2)
def cx(bid,l,r,wl=0.5,wr=0.5):
    return L('X from L',bid,'./1/100/101',M[l],X_,'1',wl)+L('X from R',bid,'./1/100/101',M[r],X_,'1',wr,mode=2)
def cy(bid,t,b,wt=0.5,wb=0.5):
    return L('Y from B',bid,'./1/100/101',M[b],Y_,'2',0.5625*wb)+L('Y from T',bid,'./1/100/101',M[t],Y_,'2',0.5625*wt,mode=2)
def bg_op(bid,on):
    return rig('Rig Style',bid,SHP,'./1/200/202',W_BG,[(k+1,1 if k in on else 0) for k in range(len(BGS))],pname='Opacity')
def thick(bid,ch,mult=1):
    return rig('Rig Thickness',bid,SHP,ch,W_THK,[(1,0),(2,THK_MAX*mult)],pname='Width' if ch.endswith('/1') else 'Height',rng=B)
# ---------- background shapes
BOX,box=rect('Box',600,200,NAVY,rnd=28,op=int(BG_DEF in (1,2)),shadow=True,border=GOLD)
box=ins(box,fit_w(BOX,'PL','PR')+fit_h(BOX,'PT','PB')+cx(BOX,'PL','PR')+cy(BOX,'PT','PB')+bg_op(BOX,[1,2]))
# accent bar: a gold copy of the box behind it, shifted left by the thickness, so a strip shows on the left edge
THKM,thkm=rect('Thickness',2,2,(1,0,0),op=0,px=THK)
thkm=ins(thkm,rig('Rig Thickness',THKM,SHP,'./1/100/101/1',W_THK,[(1,0),(2,THK_MAX)],pname='X',rng=B))
mk+=thkm
ACC,acc=rect('Accent Bar',600,200,GOLD,rnd=28,op=int(BG_DEF==2))
acc=ins(acc,fit_w(ACC,'PL','PR')+fit_h(ACC,'PT','PB',frac=0.985)+L('X minus thickness',ACC,'./1/100/101',THKM,X_,'1',-1)+cx(ACC,'PL','PR')+cy(ACC,'PT','PB')
        +link('Accent Roundness',ACC,SHP,'./2/353/144',BOX,[('144','./2/353/144')])[1]+bg_op(ACC,[2]))
def colink(bid): return link('Accent Color',bid,SHP,'./2/353/113/111',ACC,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
UND,und=rect('Underline',600,THK,GOLD,rnd=4,op=int(BG_DEF==3))
und=ins(und,fit_w(UND,'L','R')+cx(UND,'L','R')+cy(UND,'PB','PB')+thick(UND,'./2/353/160/2')+colink(UND)+bg_op(UND,[3]))
SIDE,side=rect('Side Bar',THK,200,GOLD,rnd=4,op=int(BG_DEF==4))
side=ins(side,fit_h(SIDE,'T','B',frac=1.1)+cy(SIDE,'T','B')+cx(SIDE,'PL','PL')+thick(SIDE,'./2/353/160/1')+colink(SIDE)+bg_op(SIDE,[4]))
HIL,hil=rect('Highlight',600,80,GOLD,rnd=8,op=int(BG_DEF==5))
hil=ins(hil,fit_w(HIL,'L','R',frac=1.06)+fit_h(HIL,'T','B',frac=0.55)+cx(HIL,'L','R')+cy(HIL,'T','B',wt=0.22,wb=0.78)+colink(HIL)+bg_op(HIL,[5]))

# ---------- animation drivers
def drv_keys(dirn,style,d):
    if dirn=='in':
        t0=0.05
        if style=='Pop':   return dict(sx=keys(t0,d,lambda p:max(0,spring(p))),sy=keys(t0,d,lambda p:max(0,spring(p))),op=keys(t0,d,lambda p:smooth(min(1,p/0.18))))
        if style=='Fade Up': return dict(py=keys(t0,d,lambda p:-90*(1-ease_out(p))),op=keys(t0,d,lambda p:smooth(min(1,p/0.7))))
        if style=='Slide': return dict(px=keys(t0,d,lambda p:-420*(1-ease_out(p))),op=keys(t0,d,lambda p:smooth(min(1,p/0.5))))
        if style=='Expand': return dict(bsx=keys(t0,d,lambda p:max(0,spring(min(1,p/0.75),pk=0.45,ov=0.05))),top=keys(t0,d,lambda p:smooth(max(0,(p-0.35)/0.45)) if p<0.8 else 1))
    else:
        t0=END-d-0.02
        if style=='Pop':   return dict(sx=keys(t0,d,lambda q:max(0,1-ease_in_back(q))),sy=keys(t0,d,lambda q:max(0,1-ease_in_back(q))),op=keys(t0,d,lambda q:1 if q<0.75 else 1-smooth((q-0.75)/0.25)))
        if style=='Fade Down': return dict(py=keys(t0,d,lambda q:-70*ease_in(q)),op=keys(t0,d,lambda q:1-smooth(q)))
        if style=='Slide': return dict(px=keys(t0,d,lambda q:420*ease_in(q)),op=keys(t0,d,lambda q:1-smooth(q)))
        if style=='Collapse': return dict(top=keys(t0,d,lambda q:1-smooth(min(1,q/0.4))),bsx=keys(t0,d,lambda q:1 if q<0.3 else max(0,1-ease_in_back((q-0.3)/0.7,1.2))))
    if style in SEQ:   # box grows first, text is then revealed by a Sequence Text behaviour
        if dirn=='in': return dict(bsx=keys(0.05,0.5,lambda p:max(0,spring(min(1,p/0.75),pk=0.45,ov=0.05))),top=[(0,0),(SEQ_IN_T0-0.01,0),(SEQ_IN_T0,1)])
        return dict(top=[(0,1),(SEQ_OUT_END,1),(SEQ_OUT_END+0.01,0)],bsx=[(0,1),(SEQ_OUT_END,1)]+keys(SEQ_OUT_END+0.01,0.38,lambda q:max(0,1-ease_in_back(q,1.2)))[1:])
    return {}
CH_ALL=[('Pos','./1/100/101',[('1','./1/100/101/1'),('2','./1/100/101/2')]),('Scale','./1/100/105',[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade','./1/200/202',[('202','./1/200/202')])]
CH_BOX=[('Scale X','./1/100/105',[('1','./1/100/105/1')])]
CH_TXT=[('Fade','./1/200/202',[('202','./1/200/202')])]
drivers=''; SEL={}
for dirn,names,wsp in (('in',ANIM_IN,W_SIN),('out',ANIM_OUT,W_SOUT)):
    for st in names[1:]:
      if st in SEQ: swapS()
      for part,chs in (('all',CH_ALL),('box',CH_BOX),('txt',CH_TXT)):
            if (part!='all') != (st in ('Expand','Collapse')+tuple(SEQ)): continue
            selid=new(); beh=''
            for si,d in enumerate(DUR[dirn]):
                kk=drv_keys(dirn,st,d); vid=new()
                if part=='all': drivers+=dgroup(f'{dirn} {st} {SPN[si]}',vid,px=kk.get('px'),py=kk.get('py'),sx=kk.get('sx'),sy=kk.get('sy'),op=kk.get('op'))
                elif part=='box': drivers+=dgroup(f'{dirn} {st} box {SPN[si]}',vid,sx=kk.get('bsx'))
                else: drivers+=dgroup(f'{dirn} {st} text {SPN[si]}',vid,op=kk.get('top'))
                for nm,chan,cc in chs:
                    lid,lx=link(f'{nm} {SPN[si]}',selid,GRP,chan,vid,cc,mix=1 if si==1 else 0)
                    beh+=lx+rig(f'Rig {nm} {SPN[si]}',lid,LNK,'./207',wsp,[(j+1,1 if j==si else 0) for j in range(3)],pname='Custom Mix')
            drivers+=group(f'{dirn} {st} {part}',selid,beh=beh); SEL[(dirn,st,part)]=selid
      if st in SEQ: swapS()
def anim_links(target,dirn,part,chs):
    names=ANIM_IN if dirn=='in' else ANIM_OUT; w=W_AIN if dirn=='in' else W_AOUT; x=''
    for k,st in enumerate(names):
        if (dirn,st,part) not in SEL: continue
        if st in SEQ: swapS()
        for nm,chan,cc in chs:
            lid,lx=link(f'{st} {nm}',target,GRP,chan,SEL[(dirn,st,part)],cc,mix=1 if ((k==AIN_DEF if dirn=='in' else k==1) and (part=='all') == (names[k] not in ('Expand','Collapse')+tuple(SEQ))) else 0)
            x+=lx+rig(f'Rig {st} {nm}',lid,LNK,'./207',w,[(j+1,1 if j==k else 0) for j in range(len(names))],pname='Custom Mix')
        if st in SEQ: swapS()
    return x

# ---------- float (ids from a high range so existing clips keep their settings)
HN=[60000]
def swap(): nid[0],HN[0]=HN[0],nid[0]
swap()
W_FL,W_FAMT,W_FSPD,FSRC,FLG=[new() for _ in range(5)]
FL_AMP,FL_SPD,FL_TILT=14,15,0.005
def osc_beh(target,nm,chan,a,sp,ph):
    oid=new()
    x=f'<behavior name="{nm}" id="{oid}" factoryID="{F_OSC}">\n<channelBehavior affectingFactory="{GRP}" affectingChannel="{chan}" sliderRange="{B}"/>\n{TIMING}\n<baseFlags>8589934608</baseFlags>\n'
    x+=f'<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{target}"/>\n<parameter name="Phase" id="200" flags="8606711824" default="0" value="{ph}"/>\n'
    x+=f'<parameter name="Amplitude" id="201" flags="8606711824" default="100" value="{a}"/>\n<parameter name="Speed" id="202" flags="8606711824" default="10" value="{sp}"/>\n</behavior>\n'
    return x+rig(f'Rig {nm} Speed',oid,OSC,'./202',W_FSPD,[(1,0),(2,sp*2)],pname='Speed',rng='100')
float_src=group('Float Source',FSRC,beh=osc_beh(FSRC,'Float Y','./1/100/101/2',FL_AMP,FL_SPD,37)+osc_beh(FSRC,'Float Tilt','./1/100/109/3',FL_TILT,FL_SPD*0.7,212))
def float_links():
    x=''
    for nm,chan,chs,sc in (('Float Y','./1/100/101',[('2','./1/100/101/2')],0.5625),('Float Tilt','./1/100/109',[('3','./1/100/109/3')],1.0)):
        lid,lx=link(nm,FLG,GRP,chan,FSRC,chs,mode=0,scale=sc)
        x+=lx+rig(f'Rig {nm} On',lid,LNK,'./207',W_FL,[(1,0),(2,1)],pname='Custom Mix')
        x+=rig(f'Rig {nm} Amount',lid,LNK,'./204',W_FAMT,[(1,0),(2,2*sc)],pname='Scale',rng=B)
    return x
swap()
# ---------- sequence text behaviours (typewriter / word by word / wipe), gated by the animation pop-ups
SEQU='9279a0e120d64a82b26b4cf79391ff47'; F_SEQ=facs[SEQU]; F_BASIC=facs['03ce4d4f0ea74b3b9af072a0e4a61ab7']; F_SUBST=facs['f4c2c6ef713f4a18ae987242c8b7f619']
W_RISE=None; WB={}
FPS=60000/1001
def seq_beh_words(dirn,st):
    names=ANIM_IN if dirn=='in' else ANIM_OUT; w=W_AIN if dirn=='in' else W_AOUT; k=names.index(st)
    spd=W_SIN if dirn=='in' else W_SOUT
    durs=[0.8,1.4,2.4] if dirn=='in' else [0.6,1.0,1.8]; full=durs[-1]
    t_in,t_out=(SEQ_IN_T0,SEQ_IN_T0+full) if dirn=='in' else (SEQ_OUT_END-full,SEQ_OUT_END)
    offs=[round((full-d)*FPS) for d in durs]
    bid=new(); x=SEQT
    x=re.sub(r'<behavior name="Sequence Text" id="\d+"',f'<behavior name="Words {dirn}" id="{bid}"',x,1)
    x=re.sub(r'<timing in="[^"]*" out="[^"]*" offset="[^"]*"/>',f'<timing in="{T(t_in)}" out="{T(t_out)}" offset="0 1 1 0"/>',x,1)
    rise=-40 if dirn=='in' else 30
    x=x.replace('<parameter name="Format" id="1000" flags="8589938704">','<parameter name="Format" id="1000" flags="8589938704"><parameter name="Position" id="1001" flags="8589938688"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="0" value="0"/><parameter name="Y" id="2" flags="8606711824" default="0" value="%d"/></parameter>'%rise,1)
    sel=True
    x=re.sub(r'<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="[^"]*"/>',f'<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="{0 if sel else 1}"/>',x,1)
    ctl='<parameter name="Controls" id="201" flags="8589938704">'
    oid,oname=('213','End Offset') if dirn=='in' else ('235','Start Offset')
    extra=(f'<parameter name="Sequencing" id="202" flags="8606777360" default="1" value="{1 if dirn=="in" else 0}"/>')
    i=x.find(ctl)+len(ctl); x=x[:i]+extra+x[i:]
    j=x.find('</parameter>\n',x.rfind('</parameter>',0,x.find('<parameter name="Basic"')))
    j=x.rfind('</parameter>',0,x.find('<parameter name="Basic"'))
    x=x[:j]+f'<parameter name="{oname}" id="{oid}" flags="8606711824" default="0" value="{offs[1]}"/>'+x[j:]
    beh=x+'\n'; WB[dirn]=bid
    return beh
    n=len(names)
    beh+=rig(f'Rig Words {dirn} On',bid,SEQU,'./1000/1044',w,[(jj+1,0 if jj==k else 1) for jj in range(n)],pname='Opacity')
    beh+=rig(f'Rig Words {dirn} Speed',bid,SEQU,f'./201/{oid}',spd,[(jj+1,offs[jj]) for jj in range(3)],pname=oname,rng=B)
    beh+=rig(f'Rig Words {dirn} Rise',bid,SEQU,'./1000/1001/2',W_RISE,[(1,0),(2,RISE_MAX*(-1 if dirn=='in' else 1))],pname='Y',rng=B)
    return beh
def seq_beh(dirn,st):
    names=ANIM_IN if dirn=='in' else ANIM_OUT; w=W_AIN if dirn=='in' else W_AOUT; k=names.index(st)
    d=SEQ_DUR[st]
    t_in,t_out=(SEQ_IN_T0,SEQ_IN_T0+d) if dirn=='in' else (SEQ_OUT_END-d,SEQ_OUT_END)
    unit={'Typewriter':0,'Word by Word':2,'Wipe':0}[st]
    spread={'Typewriter':1,'Word by Word':2,'Wipe':10}[st]
    speed={'Typewriter':0,'Word by Word':2,'Wipe':0}[st]
    direction=1 if (dirn=='out' and st=='Typewriter') else 0
    rise=(40 if dirn=='in' else 30) if st=='Word by Word' else 0
    bid=new()
    x=f'<behavior name="Seq {dirn} {st}" id="{bid}" factoryID="{F_SEQ}">\n<timing in="{T(t_in)}" out="{T(t_out)}" offset="0 1 1 0"/>\n<baseFlags>8589934609</baseFlags>\n'
    x+='<parameter name="Format" id="1000" flags="8589938704">\n'
    if rise: x+='<parameter name="Position" id="1001" flags="8589938688"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="0" value="0"/><parameter name="Y" id="2" flags="8606711824" default="0" value="0"/></parameter>\n'
    sel=(dirn=='in' and k==AIN_DEF)
    x+=f'<parameter name="Opacity" id="1044" flags="8606711824" default="1" value="{0 if sel else 1}"/>\n</parameter>\n'
    x+='<parameter name="Glow" id="1016" flags="8589971474"/>\n<parameter name="Drop Shadow" id="1020" flags="8589971474"/>\n'
    x+=f'<parameter name="Controls" id="201" flags="8589938704">\n<parameter name="Sequencing" id="202" flags="8606777360" default="1" value="{1 if dirn=="in" else 0}"/>\n'
    x+=f'<parameter name="Animate" id="203" flags="8606777360" default="0" value="{unit}"/>\n<parameter name="Spread" id="204" flags="8606711824" default="1" value="{spread}"/>\n'
    x+=f'<parameter name="Direction" id="205" flags="8606777360" default="0" value="{direction}"/>\n<parameter name="Speed" id="208" flags="8606777360" default="0" value="{speed}"/>\n'
    x+='<parameter name="Start" id="218" flags="8610906114" default="0" value="0"/>\n<parameter name="End" id="219" flags="8610906114" default="0" value="0"/>\n</parameter>\n'
    # the behaviour must carry the text's material (Substance) reference, exactly as Motion writes it
    x+=f'<parameter name="Basic" id="2000" flags="12884938774" factoryID="{F_BASIC}"><parameter name="Substance" id="{SUBID}" flags="12884906002" factoryID="{F_SUBST}"><parameter name="Color" id="1" flags="4295004162"><foldFlags>15</foldFlags></parameter><parameter name="Opacity" id="2" flags="4295000066" default="1" value="1"/></parameter></parameter>\n</behavior>\n'
    n=len(names)
    x+=rig(f'Rig Seq {dirn} {st}',bid,SEQU,'./1000/1044',w,[(j+1,0 if j==k else 1) for j in range(n)],pname='Opacity')
    if rise: x+=rig(f'Rig Seq Rise {dirn} {st}',bid,SEQU,'./1000/1001/2',w,[(j+1,(-rise if dirn=='in' else rise) if j==k else 0) for j in range(n)],pname='Y',rng=B)
    return x
swapS()
t=t.replace('<parameter name="Basic" id="2000" flags="12884938770" factoryID="0">','<parameter name="Basic" id="2000" flags="12884938770" factoryID="%s">'%F_BASIC,1)
t=t.replace('<parameter name="Substance" id="%s" flags="12884906002" factoryID="0">'%SUBID,'<parameter name="Substance" id="%s" flags="12884906002" factoryID="%s">'%(SUBID,F_SUBST),1)
t=ins(t,''.join((seq_beh_words if WORDS else seq_beh)(dn,st) for dn in ('in','out') for st in SEQ))
swapS()
# ---------- assemble
TI,TO=new(),new()
txt=group('Text Out',TO,children=group('Text In',TI,children=t,beh=anim_links(TI,'in','txt',CH_TXT)),beh=anim_links(TO,'out','txt',CH_TXT))
BI,BO=new(),new()
shapes=group('Background Out',BO,children=group('Background In',BI,children=box+acc+und+side+hil,beh=anim_links(BI,'in','box',CH_BOX)),beh=anim_links(BO,'out','box',CH_BOX))
content=txt+shapes+mk
AI,AO,SZ,POS,PLC=new(),new(),new(),new(),new()
swap(); content=group('Float',FLG,children=content,rz=0,beh=float_links()); swap()
root=group('Anim In',AI,children=content,beh=anim_links(AI,'in','all',CH_ALL))
root=group('Anim Out',AO,children=root,beh=anim_links(AO,'out','all',CH_ALL))
root=group('Title Size',SZ,children=root)
root=group('Frame Guard',new(),children=root,op_keys=[(0,0),(0.03,1),(END-0.03,1),(END,0)])
root=group('Position',POS,children=root)
root=group('Placement',PLC,children=root,px=PLACES[PL_DEF][1],py=PLACES[PL_DEF][2],
           beh=rig('Rig Place X',PLC,GRP,'./1/100/101/1',W_PL,[(k+1,p[1]) for k,p in enumerate(PLACES)],pname='X',rng=B)+rig('Rig Place Y',PLC,GRP,'./1/100/101/2',W_PL,[(k+1,p[2]) for k,p in enumerate(PLACES)],pname='Y',rng=B))
root+=group('Drivers',new(),children=drivers+float_src,op=0)
a=s.find('<layer name="Group" id="10206">'); b=s.find('>',a)+1
c=s.find('<scenenode name="Title Background"',b)
s=s[:b]+'\n'+root+s[c:]
# ---------- widgets + publish
w=widget_popup('Placement',W_PL,[p[0] for p in PLACES],PL_DEF)
w+=widget_popup('Background',W_BG,BGS,BG_DEF)
w+=widget_slider_n('Padding X',W_PADX,[0,1],PADX/PADX_MAX,0,PADX_MAX)+widget_slider_n('Padding Y',W_PADY,[0,1],PADY/PADY_MAX,0,PADY_MAX)
w+=widget_slider_n('Accent Thickness',W_THK,[0,1],THK/THK_MAX,0,THK_MAX)
w+=widget_popup('Animation In',W_AIN,ANIM_IN,AIN_DEF)+widget_popup('In Speed',W_SIN,SPN,1)
w+=widget_popup('Animation Out',W_AOUT,ANIM_OUT,1)+widget_popup('Out Speed',W_SOUT,SPN,1)

w+=widget_check('Float',W_FL,True)+widget_slider_n('Float Amount',W_FAMT,[0,1],0.5,0,200)+widget_slider_n('Float Speed',W_FSPD,[0,1],0.5,0,200)
pa=s.find('<scenenode name="Project"'); pe=span(s,pa)
s=s[:pe]+'\n'+w+s[pe:]
pub=[(tid,'./2/369','Text'),]+([(sid,'./14/16','Text Color')] if WORDS else [])+[(W_PL,'./2/100','Placement'),(POS,'./1/100/101','Position'),(SZ,'./1/100/105','Title Size'),
     (W_BG,'./2/100','Background'),(BOX,'./2/353/113/111','Box Color'),(BOX,'./1/200/202','Box Opacity'),(BOX,'./2/353/144','Roundness'),
     (W_PADX,'./2/100','Padding X'),(W_PADY,'./2/100','Padding Y'),(BOX,'./2/353/108/105','Border Width'),(BOX,'./2/353/108/107','Border Color'),(BOX,'./1/208/211','Shadow'),
     (ACC,'./2/353/113/111','Accent Color'),(W_THK,'./2/100','Accent Thickness'),
     (W_AIN,'./2/100','Animation In'),(W_SIN,'./2/100','In Speed'),(W_AOUT,'./2/100','Animation Out'),(W_SOUT,'./2/100','Out Speed'),]+([(WB['in'],'./201/213','Word In Speed'),(WB['in'],'./1000/1001/2','Word Rise'),(WB['out'],'./201/235','Word Out Speed'),(WB['out'],'./1000/1044','Word Exit Opacity')] if WORDS else [])+[(W_FL,'./2/100','Float'),(W_FAMT,'./2/100','Float Amount'),(W_FSPD,'./2/100','Float Speed')]
pubx=''.join(f'\t\t<target object="{o}" channel="{c}" name="{n}"/>\n' for o,c,n in pub)
s=s.replace('<publishSettings>\n\t\t<version>2</version>\n','<publishSettings>\n\t\t<version>2</version>\n'+pubx,1)
s=re.sub(r'\s*<target object="10268"[^>]*/>','',s)
s=s.replace('<timemarkerset/>',f'<timemarkerset><timemarker><inpoint>{T(2.4)}</inpoint><color>1</color><type>4</type></timemarker><timemarker><inpoint>{T(7.8)}</inpoint><color>1</color><type>6</type></timemarker></timemarkerset>',1)
open(OUT,'w').write(s); print('ok',len(s),nid[0])
