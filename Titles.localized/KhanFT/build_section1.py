import re,os,math
SRC=os.path.expanduser('~/bak/cards_skeleton3.moti')
OUT=os.path.expanduser('~/mnt/Titles.localized--KhanFT/KhanFT Section Type 1/KhanFT Section Type 1.moti')
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
# ================= KhanFT Section Type 1 — background =================
B='3.4028234663852886e+38'
IMG_U='66fc0d6af6a911d6a7a7000393670732'
NAVY=(0.118,0.161,0.231); NAVY2=(0.20,0.27,0.40); GOLD=(0.984,0.749,0.141)
FW,FH=3840,2160; OV=500          # backgrounds overhang the frame so soft edges stay off-screen
def ins(xml,beh):
    k=xml.rfind('</scenenode>'); return xml[:k]+beh+xml[k:]
def colp(col): return '<parameter name="Red" id="1" flags="8606711824" default="1" value="%s"/><parameter name="Green" id="2" flags="8606711824" default="1" value="%s"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="%s"/>'%col
def rect(name,w,h,col,op=1,px=0,py=0,feather=0,fill=True,outline=None):
    bid=new()
    r=RECT.replace('name="Rectangle" id="10244"',f'name="{name}" id="{bid}"',1)
    r=re.sub(r'<parameter name="X" id="1" flags="8606711824" default="0" value="-493[^"]*"/>',f'<parameter name="X" id="1" flags="8606711824" default="0" value="{px}"/>',r)
    r=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-251[^"]*"/>',f'<parameter name="Y" id="2" flags="8606711824" default="0" value="{py}"/>',r)
    r=r.replace('<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>','<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>\n<parameter name="Feather" id="102" flags="8606744592" default="0" value="%s"/>'%feather)
    r=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)',r'\1'+colp(col),r)
    if not fill: r=r.replace('<parameter name="Fill" id="113" flags="8589938704">','<parameter name="Fill" id="113" flags="8589971472">',1)
    r=re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Width" id="1" flags="12901679120" default="{w}" value="{w}"/>',r)
    r=re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Height" id="2" flags="12901679120" default="{h}" value="{h}"/>',r)
    r=r.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="%s"/></parameter>'%op,1)
    if outline:
        col,wd=outline
        r=r.replace('<parameter name="Outline" id="108" flags="8589971472">','<parameter name="Outline" id="108" flags="8589938704"><parameter name="Brush Color" id="107" flags="8589938704"><foldFlags>11</foldFlags>%s</parameter><parameter name="Brush Opacity" id="142" flags="8606711824" default="1" value="1"/><parameter name="Width" id="105" flags="8606711824" default="2" value="%s"/>'%(colp(col),wd),1)
    return bid,r
def dgroup(name,gid,children='',px=None,py=None,sx=None,sy=None,op=None,beh=''):
    def ch(nm,pid,dflt,keys): return curve(nm,pid,dflt,keys) if keys else scal(nm,pid,dflt,dflt)
    return f'''<group name="{name}" id="{gid}">
{children}<aspectRatio>1</aspectRatio><flags>0</flags>
{TIMING}
<foldFlags>0</foldFlags><baseFlags>524304</baseFlags>
<parameter name="Properties" id="1" flags="8589938704">
<parameter name="Transform" id="100" flags="8589938704">
<parameter name="Position" id="101" flags="8589938704"><foldFlags>11</foldFlags>{ch('X','1',0,px)}{ch('Y','2',0,py)}</parameter>
<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags>{ch('X','1',1,sx)}{ch('Y','2',1,sy)}</parameter>
</parameter>
<parameter name="Blending" id="200" flags="8589938704">{ch('Opacity','202',1,op)}</parameter>
</parameter>
{beh}</group>
'''
def widget_slider_n(name,wid,vals,val,rmin,rmax):
    n=len(vals)
    x=f'<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">\n<affecting>3</affecting>'+''.join(f'<snapshot>{k+1}</snapshot>' for k in range(n))
    x+=f'<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
    x+=f'<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="{rmin}"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="{rmax}"/></parameter>\n'
    x+='<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
    for k in range(n): x+=f'<parameter name="Snapshots" id="{k+1}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{k/(n-1)}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
    return x+f'</parameter>\n<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>\n'
def smooth(p): return p*p*(3-2*p)
def ease_out(p): return 1-(1-p)**4
def ease_in(p): return p**3
def ease_io(p): return 4*p**3 if p<0.5 else 1-(-2*p+2)**3/2
def keys(t0,d,f,n=None):
    n=n or max(10,int(d*60)); return [(t0+d*k/n,f(k/n)) for k in range(n+1)]
# ---------- options
W_FILL,W_IN,W_SIN,W_OUT,W_SOUT,W_ACC,W_THK=[new() for _ in range(7)]
SPN=['Snap','Normal','Slow']
DUR={'in':[0.5,0.85,1.4],'out':[0.4,0.65,1.0]}
INS=['From Top','From Bottom','From Left','From Right','Centre Out']
OUTS=['To Top','To Bottom','To Left','To Right','Shrink to Centre','Fade','None']
IN_DEF,OUT_DEF=0,1
YD,XD=FH+OV*2+200,FW+OV*2+200
ACCS=[('None',0,3840,0),('Top Edge',1000,3840,1),('Bottom Edge',-1000,3840,1),('Centre',-260,700,1)]
ACC_DEF=0; THK_MAX=40; THK=10
def drv(dirn,style,d):
    if dirn=='in':
        t0=0.0; f=lambda g:keys(t0,d,g)
        return {'From Top':dict(py=f(lambda p:YD*(1-ease_io(p)))),'From Bottom':dict(py=f(lambda p:-YD*(1-ease_io(p)))),
                'From Left':dict(px=f(lambda p:-XD*(1-ease_io(p)))),'From Right':dict(px=f(lambda p:XD*(1-ease_io(p)))),
                'Centre Out':dict(sx=f(lambda p:ease_io(p)),sy=f(lambda p:ease_io(p)))}[style]
    t0=END-d-0.02; f=lambda g:keys(t0,d,g)
    return {'To Top':dict(py=f(lambda q:YD*ease_io(q))),'To Bottom':dict(py=f(lambda q:-YD*ease_io(q))),
            'To Left':dict(px=f(lambda q:-XD*ease_io(q))),'To Right':dict(px=f(lambda q:XD*ease_io(q))),
            'Shrink to Centre':dict(sx=f(lambda q:1-ease_io(q)),sy=f(lambda q:1-ease_io(q))),'Fade':dict(op=f(lambda q:1-smooth(q)))}[style]
CHS={'px':('Pos X','./1/100/101',[('1','./1/100/101/1')]),'py':('Pos Y','./1/100/101',[('2','./1/100/101/2')]),
     'sx':('Scale','./1/100/105',[('1','./1/100/105/1'),('2','./1/100/105/2')]),'op':('Fade','./1/200/202',[('202','./1/200/202')])}
drivers=''; SEL={}
for dirn,names,wsp in (('in',INS,W_SIN),('out',OUTS,W_SOUT)):
    for st in names:
        if st=='None': continue
        selid=new(); beh=''; kinds=None
        for si,d in enumerate(DUR[dirn]):
            kk=drv(dirn,st,d); vid=new(); kinds=[k for k in kk if k!='sy']
            drivers+=dgroup(f'{dirn} {st} {SPN[si]}',vid,px=kk.get('px'),py=kk.get('py'),sx=kk.get('sx'),sy=kk.get('sy'),op=kk.get('op'))
            for k in kinds:
                nm,chan,cc=CHS[k]
                lid,lx=link(f'{nm} {SPN[si]}',selid,GRP,chan,vid,cc,mix=1 if si==1 else 0,scale=0.5625 if k=='py' else 1)
                beh+=lx+rig(f'Rig {nm} {SPN[si]}',lid,LNK,'./207',wsp,[(j+1,1 if j==si else 0) for j in range(3)],pname='Custom Mix')
        drivers+=dgroup(f'{dirn} {st}',selid,beh=beh); SEL[(dirn,st)]=(selid,kinds)
def anim_links(target,dirn):
    names=INS if dirn=='in' else OUTS; w=W_IN if dirn=='in' else W_OUT; dflt=IN_DEF if dirn=='in' else OUT_DEF; x=''
    for k,st in enumerate(names):
        if (dirn,st) not in SEL: continue
        selid,kinds=SEL[(dirn,st)]
        for kd in kinds:
            nm,chan,cc=CHS[kd]
            lid,lx=link(f'{st} {nm}',target,GRP,chan,selid,cc,mix=1 if k==dflt else 0,scale=0.5625 if kd=='py' else 1)
            x+=lx+rig(f'Rig {st} {nm}',lid,LNK,'./207',w,[(j+1,1 if j==k else 0) for j in range(len(names))],pname='Custom Mix')
    return x
# ---------- background layers
BGW,BGH=FW+2*OV,FH+2*OV
BASE,base=rect('Background',BGW,BGH,NAVY)
GRAD,grad=rect('Gradient',BGW,BGH*0.7,NAVY2,op=0,py=-(BGH*0.3)/2-150,feather=900)
grad=ins(grad,rig('Rig Fill',GRAD,SHP,'./1/200/202',W_FILL,[(1,0),(2,1)],pname='Opacity'))
# vignette: four soft black bands sitting half off each edge
vb=''
for nm,w,h,x,y in (('Top',FW+1600,900,0,FH/2+150),('Bottom',FW+1600,900,0,-FH/2-150),('Left',900,FH+1600,-FW/2-150,0),('Right',900,FH+1600,FW/2+150,0)):
    _,r=rect(f'Vignette {nm}',w,h,(0,0,0),px=x,py=y,feather=700); vb+=r
VIG=new(); vig=group('Vignette',VIG,children=vb,op=0.35)
# texture: a still image of fine grain, laid over the background at low opacity
TCLIP,TEX=new(),new()
clip=CLIP.replace('name="Drop Zone" id="10267"',f'name="Grain" id="{TCLIP}"').replace('<pathURL>Drop Zone.tiff</pathURL>','<relativeURL>Media/Grain.png</relativeURL>')
clip=clip.replace('<missingWidth>1200</missingWidth>','<missingWidth>1920</missingWidth>').replace('<missingHeight>1200</missingHeight>','<missingHeight>1080</missingHeight>')
clip=clip.replace('default="1200" value="1200"','default="1920" value="1920"',1).replace('default="1200" value="1200"','default="1080" value="1080"',1)
clip=clip.replace('<parameter name="Object" id="2" flags="8589938704">','<parameter name="Object" id="2" flags="8589938704"><parameter name="Alpha Type" id="100" flags="8589938704"><parameter name="Alpha Type" id="101" flags="8606777344" default="0" value="1"/></parameter>',1)
clip=clip.replace('<timing in="0 1 1 0" out="0 120000 1 0" offset="0 1 1 0"/>','<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>',1)
tex=DZ.replace('name="Drop Zone" id="10268"',f'name="Texture" id="{TEX}"',1)
tex=re.sub(r'\s*<parameter name="Crop" id="216".*?</parameter>','',tex,count=1,flags=re.S)
tex=re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>','',tex,count=1,flags=re.S)
tex=tex.replace('default="10267" value="10267"',f'default="{TCLIP}" value="{TCLIP}"')
tex=tex.replace('<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="1"/>','<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="0"/>')
oa=tex.find('<parameter name="Object" id="2"'); ob=tex.rfind('</parameter>')
tex=tex[:oa]+'<parameter name="Object" id="2" flags="8589938704"><parameter name="Width" id="313" flags="8589934610" default="1" value="1920"/><parameter name="Height" id="314" flags="8589934610" default="1" value="1080"/></parameter>'+tex[ob+12:]
tex=tex.replace('id="300" flags="12901744656"','id="300" flags="81621221392"')
tex=tex.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="2.5208"/><parameter name="Y" id="2" flags="8606711824" default="1" value="2.9259"/></parameter></parameter><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
# accent line
ACC,acc=rect('Accent Line',ACCS[ACC_DEF][2],THK,GOLD,op=ACCS[ACC_DEF][3],py=ACCS[ACC_DEF][1])
acc=ins(acc,rig('Rig Accent Y',ACC,SHP,'./1/100/101/2',W_ACC,[(k+1,a[1]) for k,a in enumerate(ACCS)],pname='Y',rng=B)
          +rig('Rig Accent Width',ACC,SHP,'./2/353/160/1',W_ACC,[(k+1,a[2]) for k,a in enumerate(ACCS)],pname='Width',rng=B)
          +rig('Rig Accent On',ACC,SHP,'./1/200/202',W_ACC,[(k+1,a[3]) for k,a in enumerate(ACCS)],pname='Opacity')
          +rig('Rig Accent Thickness',ACC,SHP,'./2/353/160/2',W_THK,[(1,0),(2,THK_MAX)],pname='Height',rng=B))
accg=dgroup('Accent Grow',new(),children=acc,sx=[(0,0),(0.45,0)]+keys(0.45,0.6,lambda p:ease_out(p))[1:],sy=[(0,1)])
# ---------- assemble
bgc=accg+vig+tex+grad+base
BI,BO=new(),new()
root=dgroup('Background In',BI,children=bgc,beh=anim_links(BI,'in'))
root=dgroup('Background Out',BO,children=root,beh=anim_links(BO,'out'))
root+=group('Drivers',new(),children=drivers,op=0)
a=s.find('<layer name="Group" id="10206">'); b=s.find('>',a)+1
c=s.find('<scenenode name="Title Background"',b)
s=s[:b]+'\n'+root+s[c:]
s=s.replace('<clip name="Drop Zone" id="10267">',clip+'\n<clip name="Drop Zone" id="10267">',1)
w=widget_popup('Fill',W_FILL,['Solid','Gradient'],0)
w+=widget_popup('Entrance',W_IN,INS,IN_DEF)+widget_popup('In Speed',W_SIN,SPN,1)
w+=widget_popup('Exit',W_OUT,OUTS,OUT_DEF)+widget_popup('Out Speed',W_SOUT,SPN,1)
w+=widget_popup('Accent Line',W_ACC,[a[0] for a in ACCS],ACC_DEF)+widget_slider_n('Accent Thickness',W_THK,[0,1],THK/THK_MAX,0,THK_MAX)
pa=s.find('<scenenode name="Project"'); pe=span(s,pa)
s=s[:pe]+'\n'+w+s[pe:]
pub=[(W_FILL,'./2/100','Fill'),(BASE,'./2/353/113/111','Color 1'),(GRAD,'./2/353/113/111','Color 2'),
     (W_IN,'./2/100','Entrance'),(W_SIN,'./2/100','In Speed'),(W_OUT,'./2/100','Exit'),(W_SOUT,'./2/100','Out Speed'),
     (VIG,'./1/200/202','Vignette'),(TEX,'./1/200/202','Texture'),
     (W_ACC,'./2/100','Accent Line'),(ACC,'./2/353/113/111','Accent Color'),(W_THK,'./2/100','Accent Thickness')]
pubx=''.join(f'\t\t<target object="{o}" channel="{c}" name="{n}"/>\n' for o,c,n in pub)
s=s.replace('<publishSettings>\n\t\t<version>2</version>\n','<publishSettings>\n\t\t<version>2</version>\n'+pubx,1)
s=re.sub(r'\s*<target object="10268"[^>]*/>','',s)
s=s.replace('<timemarkerset/>',f'<timemarkerset><timemarker><inpoint>{T(1.5)}</inpoint><color>1</color><type>4</type></timemarker><timemarker><inpoint>{T(8.6)}</inpoint><color>1</color><type>6</type></timemarker></timemarkerset>',1)
open(OUT,'w').write(s); print('ok',len(s),nid[0])
