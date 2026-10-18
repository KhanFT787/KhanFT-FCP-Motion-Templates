import re,os,math
SRC=os.path.expanduser('~/bak/cards_skeleton3.moti')
OUT=os.path.expanduser('~/mnt/Titles.localized--KhanFT/KhanFT Cards Type 1/KhanFT Cards Type 1.moti')
s=open(SRC).read()
GRP='44da0700f6ab11d68c24000393670732'
SHP='712462a4323911d78f8400039389b702'
OSC='1a262447ab7011d7bb4600039366fb58'
LNK='68fba2c1aa094655bf4b81587efec626'
need={'Link':LNK,'Rig':'402246385249454b90e08b2ee1b6bf06','Rig Behavior':'dd0036f96c9e4bfdadb82f71fbf5c9d8',
      'Widget':'e35c74f01d5042f6b468eb530169bfb7','Oscillate':OSC,'Channel':'11615b89cbc0483fb92e95eb0c80e59c','FontChannel':'8eafb077e84c45e1996a83033a3a2c49','Average':'d6bd636a8c7311d79cc900039366fb58'}
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
def group(name,gid,children='',px=0,py=0,sx=1,sy=1,op=1,beh='',extra_props='',pos_keys=None,sc_keys=None,op_keys=None):
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
# ---------- design constants
N_MAX=7; N_DEF=5
W,H,RND=380,420,60; PITCH=440; ROW_Y=-760
SPEEDS={'in':[(0.6,0.06),(0.9,0.09),(1.3,0.14)],'out':[(0.3,0.06),(0.5,0.09),(0.85,0.14)]}
def ease_out_back(p,s=1.5):
    p-=1; return p*p*((s+1)*p+s)+1
def ease_in_back(p,s=1.3): return p*p*((s+1)*p-s)
def ease_in_cubic(p): return p*p*p
def smooth(p): return p*p*(3-2*p)
def spring(p,pk=0.35,ov=0.12,half=0.2,a=4.9):
    if p<pk:
        q=p/pk; return (1+ov)*(1-(1-q)**2)
    t=p-pk; w=math.pi/half
    return 1+ov*math.exp(-a*t)*(math.cos(w*t)+(a/w)*math.sin(w*t))*(1 if p<0.999 else 0)
IN_DROP=800; OUT_DROP=900
def keys_in(t0,d):
    n=max(8,int(d*60)); P=[];S=[];O=[]
    for k in range(n+1):
        p=k/n; t=t0+p*d; e=spring(p)
        P.append((t,-IN_DROP*(1-e))); S.append((t,0.75+0.25*e)); O.append((t,smooth(min(1,p/0.25))))
    return P,S,O
def keys_out(t0,d):
    n=max(4,int(d*30)); P=[];S=[];O=[]
    for k in range(n+1):
        q=k/n; t=t0+q*d
        P.append((t,-OUT_DROP*ease_in_back(q))); S.append((t,1-0.2*ease_in_cubic(q))); O.append((t,1-smooth(max(0,(q-0.3)/0.7))))
    return P,S,O
# ---------- ids
W_N,W_IS,W_ED,W_OS,W_FL,W_FS=[new() for _ in range(6)]
IMG_U='66fc0d6af6a911d6a7a7000393670732'
ICONS=['Stocks','Bank','Savings','Crypto','Gold','Loan']
ICON_REL='file:///Users/mehedihasankhan/Movies/Motion%20Templates.localized/Titles.localized/KhanFT/KhanFT%20Cards%20Type%201/Media/'
DEF_ICON=[0,1,2,3,4,5,0]
DEF_TEXT=['INVESTING\nIN STOCKS','CHOOSING\nA SAFE BANK','BUILDING\nSAVINGS','BUYING\nCRYPTO','INVESTING\nIN GOLD','TAKING\nA LOAN','PLANNING\nAHEAD']
W_IC=[new() for _ in range(N_MAX)]
ICLIP={}
for nm in ICONS:
    cid0=new(); ICLIP[nm]=cid0

SPN=['Snap','Normal','Slow']
# ---------- drivers
drivers=''
sel={}
for dirn in ('in','out'):
    for k in range(N_MAX):
        selid=new(); beh=''
        for si,(d,stg) in enumerate(SPEEDS[dirn]):
            vid=new()
            if dirn=='in': P,S,O=keys_in(0.05+k*stg,d)
            else:
                start=END-d-(N_MAX-1-k)*stg-0.02; P,S,O=keys_out(start,d)
            drivers+=group(f'{dirn.title()} {k+1} {SPN[si]}',vid,pos_keys=P,sc_keys=S,op_keys=O)
            wdg=W_IS if dirn=='in' else W_OS
            for nm,chan,chs in (('Pos',"./1/100/101",[('2','./1/100/101/2')]),('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])):
                lid,lx=link(f'{nm} {SPN[si]}',selid,GRP,chan,vid,chs,mix=1 if si==1 else 0)
                beh+=lx+rig(f'Rig {nm} {SPN[si]}',lid,LNK,'./207',wdg,[(j+1,1 if j==si else 0) for j in range(3)],pname='Custom Mix')
        drivers+=group(f'{dirn.title()} {k+1}',selid,beh=beh)
        sel[(dirn,k)]=selid
W_LY,W_AH,W_TL=new(),new(),new()
HI=[40000]
def hi(f):
    sv=nid[0]; nid[0]=HI[0]; r=f(); HI[0]=nid[0]; nid[0]=sv; return r
W_DIR=hi(new)
FONTS=[('Kohinoor Bold','KohinoorBangla-Bold'),('Kohinoor Semibold','KohinoorBangla-Semibold'),('Kohinoor Medium','KohinoorBangla-Medium'),('Kohinoor Regular','KohinoorBangla-Regular'),('Bangla Sangam Bold','BanglaSangamMN-Bold'),('Bangla MN Bold','BanglaMN-Bold')]
W_FONT=hi(new)
W_HL=hi(new)
W_H=[hi(new) for _ in range(N_MAX)]
GLOW_STR=hi(new)
HLCARD_SRC=hi(new); HLTEXT_SRC=hi(new)
SINK=[hi(new) for _ in range(N_MAX)]
UNHL=hi(new)
GLOW1=[None]
F_AVG=facs['d6bd636a8c7311d79cc900039366fb58']
def avg(target,chan,n=4):
    x=''
    for k in range(n):
        x+=f'<behavior name="Smooth {k+1}" id="{new()}" factoryID="{F_AVG}">\n<channelBehavior affectingFactory="{GRP}" affectingChannel="{chan}" sliderRange="1"/>\n{TIMING}\n<baseFlags>8589934609</baseFlags>\n<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{target}"/>\n</behavior>\n'
    return x
F_FCH=facs['8eafb077e84c45e1996a83033a3a2c49']
def font_rig(target,sid):
    rid=new()
    x=f'<behavior name="Rig Font" id="{rid}" factoryID="{F_RB}">\n<channelBehavior affectingFactory="babfc7777f4711d7aaa7000393833f6a" affectingChannel="./5/{sid}/83" sliderRange="0"/>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<baseFlags>8589934610</baseFlags>\n'
    x+=f'<parameter name="Affecting Object (Hidden)" id="199" flags="77309476882" default="0" value="{target}"/>\n<parameter name="Widget" id="200" flags="77309476880" default="0" value="{W_FONT}"/>\n<parameter name="Snapshots" id="202" flags="8590004242">\n<flags>8590004242</flags>\n'
    for k,(lab,ps) in enumerate(FONTS): x+=f'<parameter name="Font" id="{k+1}" factoryID="{F_FCH}"><font>{ps}</font><defaultFont>Helvetica</defaultFont></parameter>\n'
    return x+'</parameter>\n</behavior>\n'
DIRS=[(1,0.5625),(2,-0.5625),(3,0.5625),(4,0.5625)]
HP=math.pi/2
CHS=[('Pos', './1/100/101', [('2', './1/100/101/2')]), ('Scale', './1/100/105', [('1', './1/100/105/1'), ('2', './1/100/105/2')]), ('Fade', './1/200/202', [('202', './1/200/202')])]
def arc_c(n): return (n+1)/2
def arc_d(i,n): return int(abs(i-arc_c(n))) if i<=n else 0
def arc_u(i,n):
    if i>n or n<2: return 0.0
    return (i-arc_c(n))/(arc_c(n)-1)
# controls: Arc Ctrl Y = height (slider), Arc Amt = Ctrl * layout flag; same for tilt via X
ACT,AAM,TCT,TAM=new(),new(),new(),new()
drivers+=group('Arc Ctrl',ACT,py=250,beh=rig('Rig Arc Height',ACT,GRP,'./1/100/101/2',W_AH,[(1,0),(2,1000)],pname='Y',rng='3.4028234663852886e+38'))
ADR,TDR=hi(new),hi(new)
def _mk():
    l1,x1=link('Arc Direction',ADR,GRP,'./1/100/101',ACT,[('2','./1/100/101/2')],scale=0.5625)
    g=group('Arc Dir',ADR,beh=x1+rig('Rig Arc Dir',l1,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38'))
    l2,x2=link('Tilt Direction',TDR,GRP,'./1/100/109',TCT,[('3','./1/100/109/3')],scale=1)
    g+=group('Tilt Dir',TDR,beh=x2+rig('Rig Tilt Dir',l2,LNK,'./204',W_DIR,[(1,1),(2,-1),(3,1),(4,1)],pname='Scale',rng='3.4028234663852886e+38'))
    return g
drivers+=hi(_mk)
lid,lx=link('Arc Amount',AAM,GRP,'./1/100/101',ADR,[('2','./1/100/101/2')],scale=0)
drivers+=group('Arc Amt',AAM,beh=lx+rig('Rig Arc On',lid,LNK,'./204',W_LY,[(1,0),(2,0.5625)],pname='Scale',rng='3.4028234663852886e+38'))
drivers+=group('Tilt Ctrl',TCT,beh=rig('Rig Tilt',TCT,GRP,'./1/100/109/3',W_TL,[(1,0),(2,0.5236)],pname='Z',rng='3.4028234663852886e+38'))
lid,lx=link('Tilt Amount',TAM,GRP,'./1/100/109',TDR,[('3','./1/100/109/3')],scale=0)
drivers+=group('Tilt Amt',TAM,beh=lx+rig('Rig Tilt On',lid,LNK,'./204',W_LY,[(1,0),(2,1)],pname='Scale',rng='3.4028234663852886e+38'))
arcsel={}
for dirn in ('in','out'):
    for i in range(1,N_MAX+1):
        gid=new(); beh=''
        slots=sorted({arc_d(i,n) for n in range(1,N_MAX+1)})
        for d in slots:
            k = d if dirn=='in' else (N_MAX-1-d)
            for nm,chan,chs in CHS:
                lid,lx=link(f'{nm} d{d}',gid,GRP,chan,sel[(dirn,k)],chs,mix=1 if arc_d(i,N_DEF)==d else 0)
                beh+=lx+rig(f'Rig {nm} d{d}',lid,LNK,'./207',W_N,[(n,1 if arc_d(i,n)==d else 0) for n in range(1,N_MAX+1)],pname='Custom Mix')
        drivers+=group(f'Arc {dirn.title()} {i}',gid,beh=beh)
        arcsel[(dirn,i)]=gid
DRV=group('Drivers',new(),children=drivers)
# ---------- cards
def xpos(i,n): return (i-(n+1)/2)*PITCH
cards=''; clips=''; FDRV=[]
PHASES=[37,212,148,301,263,95,11,176,329,58,124,247,199,22]
for nm in ICONS:
    c=CLIP.replace('name="Drop Zone" id="10267"',f'name="Icon {nm}" id="{ICLIP[nm]}"').replace('<pathURL>Drop Zone.tiff</pathURL>',f'<relativeURL>Media/Icon%20{nm}.png</relativeURL>')
    c=c.replace('<missingWidth>1200</missingWidth>','<missingWidth>512</missingWidth>').replace('<missingHeight>1200</missingHeight>','<missingHeight>512</missingHeight>')
    c=c.replace('default="1200" value="1200"','default="512" value="512"')
    c=c.replace('<parameter name="Object" id="2" flags="8589938704">','<parameter name="Object" id="2" flags="8589938704"><parameter name="Alpha Type" id="100" flags="8589938704"><parameter name="Alpha Type" id="101" flags="8606777344" default="0" value="1"/></parameter>',1)
    c=c.replace('<timing in="0 1 1 0" out="0 120000 1 0" offset="0 1 1 0"/>','<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>',1)
    clips+=c+'\n'
def icon_img(i,k,nm):
    iid=new()
    x=DZ.replace('name="Drop Zone" id="10268"',f'name="Card {i} {nm}" id="{iid}"',1)
    x=re.sub(r'\s*<parameter name="Crop" id="216".*?</parameter>','',x,count=1,flags=re.S)
    x=re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>','',x,count=1,flags=re.S)
    x=x.replace('default="10267" value="10267"',f'default="{ICLIP[nm]}" value="{ICLIP[nm]}"')
    x=x.replace('<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="1"/>','<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="0"/>')
    oa=x.find('<parameter name="Object" id="2"'); ob=x.rfind('</parameter>')
    x=x[:oa]+'<parameter name="Object" id="2" flags="8589938704"><parameter name="Width" id="313" flags="8589934610" default="1" value="512"/><parameter name="Height" id="314" flags="8589934610" default="1" value="512"/></parameter>'+x[ob+12:]
    x=x.replace('id="300" flags="12901744656"','id="300" flags="81621221392"')
    on=1 if DEF_ICON[i-1]==k else 0
    x=x.replace('<parameter name="Properties" id="1" flags="8589938704">',f'<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags><parameter name="Y" id="2" flags="8606711824" default="0" value="85"/></parameter><parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="0.371"/><parameter name="Y" id="2" flags="8606711824" default="1" value="0.371"/></parameter></parameter><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="{on}"/></parameter>',1)
    rg=rig(f'Rig Card {i} {nm}',iid,IMG_U,'./1/200/202',W_IC[i-1],[(j+1,1 if j==k else 0) for j in range(len(ICONS)+1)],pname='Opacity')
    e=x.rfind('</scenenode>'); return x[:e]+rg+x[e:]

bg1=None; TXTID={}; DZID={}
FLOAT=[(10,17,0.004,13),(13,21,0.005,16),(9,15,0.003,19),(12,19,0.006,14),(11,23,0.004,17),(14,16,0.005,21),(10,20,0.003,15)]
for i in range(1,N_MAX+1):
    tid,did,bid,cid=new(),new(),new(),new()
    t=TXT.replace('name="Type Text Here" id="10210"',f'name="Card {i} Text" id="{tid}"',1)
    t=t.replace('<text>Type Text Here</text>','<text>%s</text>'%DEF_TEXT[i-1]).replace('length="14"','length="%d"'%len(DEF_TEXT[i-1]))
    pid=new()
    t=t.replace('<paragraphStyle id="10239">','<paragraphStyle id="%s">'%pid).replace('<parameter name="Paragraph" id="10239"','<parameter name="Paragraph" id="%s"'%pid)
    sid=new(); t=t.replace('id="10241" factoryID','id="%s" factoryID'%sid).replace('style="10241"','style="%s"'%sid)
    _fr=hi(lambda: font_rig(tid,sid)); _k=t.rfind('</scenenode>'); t=t[:_k]+_fr+t[_k:]
    if i==1: STY1,TXT1=sid,tid
    else:
        def _tl():
            x=link('Text Size',tid,'babfc7777f4711d7aaa7000393833f6a',f'./5/{sid}/3',TXT1,[('3',f'./5/{STY1}/3')])[1]
            x+=link('Text Color',tid,'babfc7777f4711d7aaa7000393833f6a',f'./5/{sid}/14/16',TXT1,[('1',f'./5/{STY1}/14/16/1'),('2',f'./5/{STY1}/14/16/2'),('3',f'./5/{STY1}/14/16/3')])[1]
            return x
        _x=hi(_tl); _k=t.rfind('</scenenode>'); t=t[:_k]+_x+t[_k:]
    t=t.replace('<parameter name="Substance" id="10229"','<parameter name="Substance" id="%s"'%new())
    t=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-921[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="-75"/>',t)
    t=t.replace('<parameter name="Anchor Point" id="107"','<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="0.82"/><parameter name="Y" id="2" flags="8606711824" default="1" value="0.82"/></parameter><parameter name="Anchor Point" id="107"',1)
    t=t.replace('<parameter name="X" id="1" flags="8606711824" default="0" value="1728"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="0"/>').replace('<parameter name="Y" id="2" flags="8606711824" default="0" value="50"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>')
    dz=DZ.replace('name="Drop Zone" id="10268"',f'name="Card {i} Icon" id="{did}"',1)
    dz=re.sub(r'\s*<parameter name="Crop" id="216".*?</parameter>','',dz,count=1,flags=re.S)
    dz=dz.replace('default="10267" value="10267"',f'default="{cid}" value="{cid}"')
    dz=re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>','',dz,count=1,flags=re.S)
    dz=dz.replace('<parameter name="Width" id="313" flags="8589934610" default="1" value="3840"/>','<parameter name="Width" id="313" flags="8589934610" default="1" value="190"/>')
    dz=dz.replace('<parameter name="Height" id="314" flags="8589934610" default="1" value="3840"/>','<parameter name="Height" id="314" flags="8589934610" default="1" value="190"/>')
    dz=dz.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags><parameter name="Y" id="2" flags="8606711824" default="0" value="85"/></parameter></parameter>',1)
    clips+=CLIP.replace('name="Drop Zone" id="10267"',f'name="Card {i} Icon" id="{cid}"')+'\n'
    r=RECT.replace('name="Rectangle" id="10244"',f'name="Card {i} Card" id="{bid}"',1)
    r=re.sub(r'<parameter name="X" id="1" flags="8606711824" default="0" value="-493[^"]*"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="0"/>',r)
    r=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-251[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>',r)
    r=r.replace('<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>','<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>\n<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%d"/>'%RND)
    r=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)',r'\1<parameter name="Red" id="1" flags="8606711824" default="1" value="1"/><parameter name="Green" id="2" flags="8606711824" default="1" value="1"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="1"/>',r)
    r=re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Width" id="1" flags="12901679120" default="{W}" value="{W}"/>',r)
    r=re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Height" id="2" flags="12901679120" default="{H}" value="{H}"/>',r)
    r=r.replace('<parameter name="Lighting" id="230"','<parameter name="Drop Shadow" id="208" flags="8589940752"><foldFlags>131083</foldFlags><parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="0.28"/><parameter name="Blur" id="213" flags="8606711824" default="5" value="40"/><parameter name="Distance" id="212" flags="8606711824" default="5" value="16"/><parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="4.7123889803846897"/></parameter>\n<parameter name="Lighting" id="230"',1)
    r=r.replace('<parameter name="Outline" id="108" flags="8589971472">','<parameter name="Outline" id="108" flags="8589938704"><parameter name="Brush Color" id="107" flags="8589938704"><foldFlags>11</foldFlags><parameter name="Red" id="1" flags="8606711824" default="1" value="0.118"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.161"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.231"/></parameter><parameter name="Brush Opacity" id="142" flags="8606711824" default="1" value="1"/><parameter name="Width" id="105" flags="8606711824" default="2" value="0"/>',1)
    if i==1: bg1=bid
    else:
        lb=''
        _,x=link('Card Color',bid,SHP,'./2/353/113/111',bg1,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')]); lb+=x
        _,x=link('Card Roundness',bid,SHP,'./2/353/144',bg1,[('144','./2/353/144')]); lb+=x
        _,x=link('Card Shadow',bid,SHP,'./1/208/211',bg1,[('211','./1/208/211')]); lb+=x
        lb+=hi(lambda: link('Border Color',bid,SHP,'./2/353/108/107',bg1,[('1','./2/353/108/107/1'),('2','./2/353/108/107/2'),('3','./2/353/108/107/3')])[1]+link('Border Width',bid,SHP,'./2/353/108/105',bg1,[('105','./2/353/108/105')])[1]+link('Border Opacity',bid,SHP,'./2/353/108/142',bg1,[('142','./2/353/108/142')])[1])
        k=r.rfind('</scenenode>'); r=r[:k]+lb+r[k:]
    dz=dz.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
    e=dz.rfind('</scenenode>'); dz=dz[:e]+rig(f'Rig Card {i} Custom',did,IMG_U,'./1/200/202',W_IC[i-1],[(j+1,1 if j==len(ICONS) else 0) for j in range(len(ICONS)+1)],pname='Opacity')+dz[e:]
    imgs=''.join(icon_img(i,k,nm) for k,nm in enumerate(ICONS))
    TXTID[i]=tid; DZID[i]=did
    def _glow():
        gsid=new(); gid=new()
        g=re.sub(r'<behavior .*?</behavior>\s*','',r,flags=re.S)
        g=g.replace(f'name="Card {i} Card" id="{bid}"',f'name="Card {i} Glow" id="{gsid}"',1)
        g=g.replace('<parameter name="Drop Shadow" id="208" flags="8589940752">','<parameter name="Drop Shadow" id="208" flags="8589971472">',1)
        g=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)<parameter name="Red" id="1" flags="8606711824" default="1" value="1"/><parameter name="Green" id="2" flags="8606711824" default="1" value="1"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="1"/>',r'\1<parameter name="Red" id="1" flags="8606711824" default="1" value="0.984"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.749"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.141"/>',g,count=1)
        g=g.replace('<parameter name="Roundness" id="144"','<parameter name="Feather" id="102" flags="8606744592" default="0" value="70"/>\n<parameter name="Roundness" id="144"',1)
        b=rig('Rig Glow',gsid,SHP,'./1/200/202',W_H[i-1],[(1,0),(2,1)],pname='Opacity')
        if GLOW1[0] is None: GLOW1[0]=gsid
        else:
            b+=link('Glow Color',gsid,SHP,'./2/353/113/111',GLOW1[0],[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
        k=g.rfind('</scenenode>'); g=g[:k]+b+g[k:]
        g=g.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
        lb=link('Glow Strength',gid,GRP,'./1/200/202',GLOW_STR,[('202','./1/200/202')],scale=1)[1]
        return group(f'Card {i} Glow Group',gid,children=g,py=-14,sx=1.1,sy=1.1,beh=lb)
    glow=hi(_glow)
    def _hlcol():
        global r,t
        if i==1:
            for nm,sid_,col in (('Highlight Card Color Source',HLCARD_SRC,(1,1,1)),('Highlight Text Color Source',HLTEXT_SRC,(0.13,0.13,0.15))):
                g=re.sub(r'<behavior .*?</behavior>\s*','',r,flags=re.S)
                g=re.sub(r'<behavior .*?</behavior>\s*','',g,flags=re.S)
                g=g.replace(f'name="Card {i} Card" id="{bid}"',f'name="{nm}" id="{sid_}"',1)
                g=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)<parameter name="Red" id="1" flags="8606711824" default="1" value="1"/><parameter name="Green" id="2" flags="8606711824" default="1" value="1"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="1"/>',r'\1<parameter name="Red" id="1" flags="8606711824" default="1" value="%s"/><parameter name="Green" id="2" flags="8606711824" default="1" value="%s"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="%s"/>'%col,g,count=1)
                g=g.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
                FDRV.append(g)
        x=link('Highlight Card Color',bid,SHP,'./2/353/113/111',HLCARD_SRC,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')],mix=0)
        xb=x[1]+rig('Rig Highlight Card Color',x[0],LNK,'./207',W_H[i-1],[(1,0),(2,1)],pname='Custom Mix')
        k=r.find('<behavior '); k=r.rfind('</scenenode>') if k<0 else k
        r=r[:k]+xb+r[k:]
        y=link('Highlight Text Color',tid,'babfc7777f4711d7aaa7000393833f6a',f'./5/{sid}/14/16',HLTEXT_SRC,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')],mix=0)
        yb=y[1]+rig('Rig Highlight Text Color',y[0],LNK,'./207',W_H[i-1],[(1,0),(2,1)],pname='Custom Mix')
        k=t.find('<behavior name="Text Color"'); k=t.rfind('</scenenode>') if k<0 else k
        t=t[:k]+yb+t[k:]
    hi(_hlcol)
    def _shadow():
        return rig('Rig Shadow Dist',bid,SHP,'./1/208/212',W_H[i-1],[(1,16),(2,44)],pname='Distance',rng='3.4028234663852886e+38')+rig('Rig Shadow Blur',bid,SHP,'./1/208/213',W_H[i-1],[(1,40),(2,80)],pname='Blur',rng='3.4028234663852886e+38')
    _k=r.rfind('</scenenode>'); r=r[:_k]+hi(_shadow)+r[_k:]
    content=t+'\n'+imgs+dz+'\n'+r+'\n'+glow+'\n'
    fl_id=new(); amp,spd,ramp,rspd=FLOAT[i-1]
    t_in=0
    fbeh=''
    for nm,chan,a,sp in (('Float Y','./1/100/101/2',amp,spd),('Float Tilt','./1/100/109/3',ramp,rspd)):
        oid=new()
        fbeh+=f'''<behavior name="{nm}" id="{oid}" factoryID="{F_OSC}">
<channelBehavior affectingFactory="{GRP}" affectingChannel="{chan}" sliderRange="3.4028234663852886e+38"/>
<timing in="{T(t_in)}" out="1199198 120000 1 0" offset="0 1 1 0"/>
<baseFlags>8589934608</baseFlags>
<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{fl_id}"/>
<parameter name="Phase" id="200" flags="8606711824" default="0" value="{PHASES[(i-1)*2+(0 if nm=='Float Y' else 1)]}"/>
<parameter name="Amplitude" id="201" flags="8606711824" default="100" value="{a}"/>
<parameter name="Speed" id="202" flags="8606711824" default="10" value="{sp}"/>
</behavior>
'''
        fbeh+=rig(f'Rig {nm} On',oid,OSC,'./201',W_FL,[(1,0),(2,a)],pname='Amplitude',rng='100')
        fbeh+=rig(f'Rig {nm} Speed',oid,OSC,'./202',W_FS,[(1,0),(2,sp*2)],pname='Speed',rng='100')
    _save=nid[0]; nid[0]=HI[0]
    fs_id,fa_id=new(),new()
    fsb=fbeh.replace(f'name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{fl_id}"',f'name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{fs_id}"')
    fab=''
    for nm,chan,a,sp in (('Float Y','./1/100/101/2',amp,spd),('Float Tilt','./1/100/109/3',ramp,rspd)):
        oid=new()
        fab+=f'''<behavior name="{nm}" id="{oid}" factoryID="{F_OSC}">
<channelBehavior affectingFactory="{GRP}" affectingChannel="{chan}" sliderRange="3.4028234663852886e+38"/>
<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>
<baseFlags>8589934608</baseFlags>
<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{fa_id}"/>
<parameter name="Phase" id="200" flags="8606711824" default="0" value="{PHASES[(i-1)*2+(0 if nm=='Float Y' else 1)]}"/>
<parameter name="Amplitude" id="201" flags="8606711824" default="100" value="{a}"/>
<parameter name="Speed" id="202" flags="8606711824" default="10" value="{sp}"/>
</behavior>
'''
        fab+=rig(f'Rig {nm} On',oid,OSC,'./201',W_FL,[(1,0),(2,a)],pname='Amplitude',rng='100')
        fab+=rig(f'Rig {nm} Speed',oid,OSC,'./202',W_FS,[(1,0),(2,sp*2)],pname='Speed',rng='100')
    FDRV.append(group(f'Float Straight {i}',fs_id,beh=fsb)+group(f'Float Arc {i}',fa_id,beh=fab))
    YC=('Y','./1/100/101',[('2','./1/100/101/2')]); TC=('Tilt','./1/100/109',[('3','./1/100/109/3')])
    mix_id=new(); mb=''
    for src,mixr in ((fa_id,True),(fs_id,False)):
        for nm,chan,chs in (YC,TC):
            lid,x=link(f'Float {nm}'+(' Arc' if mixr else ''),mix_id,GRP,chan,src,chs,mix=0 if mixr else 1); mb+=x
            if mixr: mb+=rig(f'Rig Float {nm} Arc',lid,LNK,'./207',W_LY,[(1,0),(2,1)],pname='Custom Mix')
    FDRV.append(group(f'Float Mix {i}',mix_id,beh=mb))
    prev=mix_id
    for j in range(1,N_MAX+1):
        if j==i: continue
        hid=new(); hb=''
        for nm,chan,chs in (YC,TC):
            base=0.5625 if nm=='Y' else 1
            lid,x=link(f'Calm {nm}',hid,GRP,chan,prev,chs,scale=base); hb+=x
            hb+=rig(f'Rig Calm {nm} {j}',lid,LNK,'./204',W_H[j-1],[(1,base),(2,base*0.25)],pname='Scale',rng='3.4028234663852886e+38')
        FDRV.append(group(f'Float Calm {i} by {j}',hid,beh=hb))
        prev=hid
    hid=new(); hb=''
    for nm,chan,chs in (YC,TC):
        base=0.5625 if nm=='Y' else 1
        lid,x=link(f'Boost {nm}',hid,GRP,chan,prev,chs,scale=base); hb+=x
        hb+=rig(f'Rig Boost {nm}',lid,LNK,'./204',W_H[i-1],[(1,base),(2,base*1.8)],pname='Scale',rng='3.4028234663852886e+38')
    FDRV.append(group(f'Float Boost {i}',hid,beh=hb))
    prev=hid
    fl=''
    for nm,chan,chs in (YC,TC):
        fl+=link(f'Float {nm}',fl_id,GRP,chan,prev,chs)[1]
    HI[0]=nid[0]; nid[0]=_save
    gF=group(f'Card {i} Float',fl_id,children=content,beh=fl)
    in_id=new(); bi=''
    for nm,chan,chs in (('Pos',"./1/100/101",[('2','./1/100/101/2')]),('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])):
        lid,x=link(f'In {nm}',in_id,GRP,chan,sel[('in',i-1)],chs); bi+=x+(hi(lambda: rig('Rig Dir In',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')) if nm=='Pos' else '')
    for nm,chan,chs in CHS:
        lid,x=link(f'Arc In {nm}',in_id,GRP,chan,arcsel[('in',i)],chs,mix=0); ab=x+(hi(lambda: rig('Rig Dir Arc In',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')) if nm=='Pos' else '')
        ab+=rig(f'Rig Arc In {nm}',lid,LNK,'./207',W_LY,[(1,0),(2,1)],pname='Custom Mix'); bi=ab+bi
    def _up():
        uid=new()
        b=rig('Rig Upright Rot',uid,GRP,'./1/100/109/3',W_DIR,[(1,0),(2,0),(3,HP),(4,HP)],pname='Z',rng='3.4028234663852886e+38')
        b+=rig('Rig Upright Flip',uid,GRP,'./1/100/105/1',W_DIR,[(1,1),(2,1),(3,0.88),(4,-0.88)],pname='X',rng='3.4028234663852886e+38')
        b+=rig('Rig Upright Size',uid,GRP,'./1/100/105/2',W_DIR,[(1,1),(2,1),(3,0.88),(4,0.88)],pname='Y',rng='3.4028234663852886e+38')
        return group(f'Card {i} Upright',uid,children=gF,beh=b)
    gF=hi(_up)
    gI=group(f'Card {i} In',in_id,children=gF,beh=bi)
    out_id=new(); bo=''
    for nm,chan,chs in (('Pos',"./1/100/101",[('2','./1/100/101/2')]),('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])):
        lid,x=link(f'Out R {nm}',out_id,GRP,chan,sel[('out',N_MAX-i)],chs,mix=0); bo+=x+(hi(lambda: rig('Rig Dir Out R',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')) if nm=='Pos' else '')
        bo+=rig(f'Rig Out R {nm}',lid,LNK,'./207',W_ED,[(1,0),(2,1)],pname='Custom Mix')
        lid,x=link(f'Out L {nm}',out_id,GRP,chan,sel[('out',i-1)],chs); bo+=x+(hi(lambda: rig('Rig Dir Out L',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')) if nm=='Pos' else '')
    for nm,chan,chs in CHS:
        lid,x=link(f'Arc Out {nm}',out_id,GRP,chan,arcsel[('out',i)],chs,mix=0); ab=x+(hi(lambda: rig('Rig Dir Arc Out',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')) if nm=='Pos' else '')
        ab+=rig(f'Rig Arc Out {nm}',lid,LNK,'./207',W_LY,[(1,0),(2,1)],pname='Custom Mix'); bo=ab+bo
    gO=group(f'Card {i} Out',out_id,children=gI,beh=bo)
    arc_id=new(); ba=''
    lid,x=link('Arc Lift',arc_id,GRP,'./1/100/101',AAM,[('2','./1/100/101/2')],scale=((1-arc_u(i,N_DEF)**2)*0.5625 if N_DEF>1 else 0)); ba+=x
    ba+=rig('Rig Arc Lift',lid,LNK,'./204',W_N,[(n,(1-arc_u(i,n)**2)*0.5625 if (i<=n and n>1) else 0) for n in range(1,N_MAX+1)],pname='Scale',rng='3.4028234663852886e+38')
    lid,x=link('Arc Tilt',arc_id,GRP,'./1/100/109',TAM,[('3','./1/100/109/3')],scale=-arc_u(i,N_DEF)); ba+=x
    ba+=rig('Rig Arc Tilt',lid,LNK,'./204',W_N,[(n,-arc_u(i,n)) for n in range(1,N_MAX+1)],pname='Scale',rng='3.4028234663852886e+38')
    def _focus():
        inner=gO
        for j in range(1,N_MAX+1):
            if j==i: continue
            did_=new()
            dl,dx=link(f'Dim by {j}',did_,GRP,'./1/200/202',UNHL,[('202','./1/200/202')],mix=0)
            bb=dx+rig(f'Rig Dim {j}',dl,LNK,'./207',W_H[j-1],[(1,0),(2,1)],pname='Custom Mix')
            bb+=rig(f'Rig Shrink X {j}',did_,GRP,'./1/100/105/1',W_H[j-1],[(1,1),(2,0.94)],pname='X',rng='3.4028234663852886e+38')
            bb+=rig(f'Rig Shrink Y {j}',did_,GRP,'./1/100/105/2',W_H[j-1],[(1,1),(2,0.94)],pname='Y',rng='3.4028234663852886e+38')
            if i==1 and j==2 or (i>1 and j==1):
                pass
            sl,sx=link(f'Sink by {j}',did_,GRP,'./1/100/101',SINK[j-1],[('2','./1/100/101/2')])
            bb=sx+rig(f'Rig Sink Dir {j}',sl,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')+bb
            inner=group(f'Card {i} Dim by {j}',did_,children=inner,beh=bb)
        fid=new()
        bb=rig('Rig Grow X',fid,GRP,'./1/100/105/1',W_H[i-1],[(1,1),(2,1.12)],pname='X',rng='3.4028234663852886e+38')
        bb+=rig('Rig Grow Y',fid,GRP,'./1/100/105/2',W_H[i-1],[(1,1),(2,1.12)],pname='Y',rng='3.4028234663852886e+38')
        lsrc=new()
        FDRV.append(group(f'Lift Source {i}',lsrc,beh=rig('Rig Lift',lsrc,GRP,'./1/100/101/2',W_H[i-1],[(1,0),(2,50)],pname='Y',rng='3.4028234663852886e+38')))
        lid,lx=link('Highlight Lift',fid,GRP,'./1/100/101',lsrc,[('2','./1/100/101/2')])
        bb=lx+rig('Rig Lift Dir',lid,LNK,'./204',W_DIR,DIRS,pname='Scale',rng='3.4028234663852886e+38')+bb
        return group(f'Card {i} Highlight',fid,children=inner,beh=bb)
    gO=hi(_focus)
    gO=group(f'Card {i} Arc',arc_id,children=gO,beh=ba)
    cid_=new()
    cb=rig(f'Rig Card {i} X',cid_,GRP,'./1/100/101',W_N,[(n,(xpos(i,n) if i<=n else 0,0,0)) for n in range(1,8)],pname='Position',rng='3.4028234663852886e+38',vec=('X','Y','Z'))
    cb+=rig(f'Rig Card {i} Show',cid_,GRP,'./1/200/202',W_N,[(n,1 if i<=n else 0) for n in range(1,8)],pname='Opacity')
    cards+=group(f'Card {i}',cid_,children=gO,px=xpos(i,N_DEF) if i<=N_DEF else 0,op=1 if i<=N_DEF else 0,beh=cb)
ROW=new()
shadow='''<parameter name="Drop Shadow" id="208" flags="8589938704"><foldFlags>131083</foldFlags>
<parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="0.3"/>
<parameter name="Blur" id="213" flags="8606711824" default="5" value="30"/>
<parameter name="Distance" id="212" flags="8606711824" default="5" value="10"/></parameter>'''
def colscale(n): return min(1.0,1920.0/((n-1)*PITCH+H))
def _fit():
    src,fit=new(),new()
    b=rig('Rig Fit X',src,GRP,'./1/100/105/1',W_N,[(n,colscale(n)) for n in range(1,N_MAX+1)],pname='X',rng='3.4028234663852886e+38')
    b+=rig('Rig Fit Y',src,GRP,'./1/100/105/2',W_N,[(n,colscale(n)) for n in range(1,N_MAX+1)],pname='Y',rng='3.4028234663852886e+38')
    FDRV.append(group('Glow Strength',GLOW_STR,op=0.7))
    FDRV.append(group('Unhighlighted Opacity',UNHL,op=1))
    for _j in range(N_MAX):
        FDRV.append(group(f'Sink Source {_j+1}',SINK[_j],beh=rig('Rig Sink',SINK[_j],GRP,'./1/100/101/2',W_H[_j],[(1,0),(2,-25)],pname='Y',rng='3.4028234663852886e+38')))
    FDRV.append(group('Column Fit Source',src,sx=colscale(N_DEF),sy=colscale(N_DEF),beh=b))
    lid,x=link('Column Fit',fit,GRP,'./1/100/105',src,[('1','./1/100/105/1'),('2','./1/100/105/2')],mix=0)
    x+=rig('Rig Column Fit',lid,LNK,'./207',W_DIR,[(1,0),(2,0),(3,1),(4,1)],pname='Custom Mix')
    return group('Column Fit',fit,children=cards,beh=x)
cards=hi(_fit)
ROWG=group('Cards',ROW,children=cards,py=ROW_Y)
RDI=hi(new)
ROWG=group('Row Direction',RDI,children=ROWG,beh=hi(lambda: rig('Rig Row Dir',RDI,GRP,'./1/100/101/2',W_DIR,[(1,0),(2,-2*ROW_Y),(3,-740),(4,-740)],pname='Y',rng='3.4028234663852886e+38')))
a=s.find('<layer name="Group" id="10206">'); b=s.find('>',a)+1
c=s.find('<scenenode name="Title Background"',b)
def _wrap():
    rid,mid,fdid=new(),new(),new()
    g=group('Row Rotate',rid,children=ROWG,beh=rig('Rig Row Rotate',rid,GRP,'./1/100/109/3',W_DIR,[(1,0),(2,0),(3,-HP),(4,-HP)],pname='Z',rng='3.4028234663852886e+38'))
    g=group('Row Mirror',mid,children=g,beh=rig('Rig Row Mirror',mid,GRP,'./1/100/105/1',W_DIR,[(1,1),(2,1),(3,1),(4,-1)],pname='X',rng='3.4028234663852886e+38'))
    return g+DRV+group('Float Drivers',fdid,children=''.join(FDRV))
s=s[:b]+'\n'+hi(_wrap)+s[c:]
print('HI',HI[0])
s=s.replace('<clip name="Drop Zone" id="10267">',clips+'<clip name="Drop Zone" id="10267">',1)
rigx=f'<scenenode name="Rig" id="{new()}" factoryID="{F_RIG}" version="5">\n'
rigx+=widget_popup('Number of Cards',W_N,[str(n) for n in range(1,8)],N_DEF-1)
rigx+=widget_popup('Layout',W_LY,['Straight','Arc'],0)
def widget_slider_n(name,wid,n,val,rmax):
    x=f'<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">\n<affecting>3</affecting>'+''.join(f'<snapshot>{k+1}</snapshot>' for k in range(n))
    x+=f'<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
    x+=f'<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="0"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="{rmax}"/></parameter>\n'
    x+='<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
    for k in range(n): x+=f'<parameter name="Snapshots" id="{k+1}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{k/(n-1)}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
    return x+f'</parameter>\n<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>\n'
for k in range(N_MAX): rigx+=widget_slider(f'Card {k+1} Highlight',W_H[k],0)
rigx+=widget_popup('Font',W_FONT,[f[0] for f in FONTS],0)
rigx+=widget_popup('Entrance From',W_DIR,['Bottom','Top','Left','Right'],0)
rigx+=widget_slider('Arc Height',W_AH,0.25)
rigx+=widget_slider('Arc Tilt',W_TL,0.4)
rigx+=widget_popup('Entrance Speed',W_IS,SPN,1)
rigx+=widget_popup('Exit Order',W_ED,['Left to Right','Right to Left'],0)
rigx+=widget_popup('Exit Speed',W_OS,SPN,1)
rigx+=widget_check('Float',W_FL,True)
rigx+=widget_slider('Float Speed',W_FS,0.5)
for i in range(1,N_MAX+1): rigx+=widget_popup(f'Card {i} Icon',W_IC[i-1],ICONS+['Custom Image'],DEF_ICON[i-1])
rigx+='<flags>0</flags>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<foldFlags>0</foldFlags>\n<baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704"/>\n</scenenode>\n'
pa=s.find('<scenenode name="Project"'); pe=span(s,pa)
s=s[:pe]+'\n'+rigx+s[pe:]
pub=[(W_N,'./2/100','Number of Cards'),(W_LY,'./2/100','Layout'),(W_DIR,'./2/100','Entrance From'),(W_AH,'./2/100','Arc Height'),(W_TL,'./2/100','Arc Tilt'),(W_IS,'./2/100','Entrance Speed'),(W_ED,'./2/100','Exit Order'),(W_OS,'./2/100','Exit Speed'),
     (W_FL,'./2/100','Float'),(W_FS,'./2/100','Float Speed'),
     (ROW,'./1/100/101','Row Position'),(ROW,'./1/100/105','Card Size'),
     (bg1,'./2/353/113/111','Card Color'),(bg1,'./2/353/144','Card Roundness'),(bg1,'./1/208/211','Shadow Opacity'),(bg1,'./2/353/108/105','Border Width'),(bg1,'./2/353/108/107','Border Color'),(bg1,'./2/353/108/142','Border Opacity'),(HLCARD_SRC,'./2/353/113/111','Highlight Card Color'),(HLTEXT_SRC,'./2/353/113/111','Highlight Text Color'),(GLOW1[0],'./2/353/113/111','Highlight Color'),(GLOW_STR,'./1/200/202','Highlight Glow'),(UNHL,'./1/200/202','Unhighlighted Opacity')]
pub+=[(W_FONT,'./2/100','Font'),(STY1,'./3','Text Size'),(STY1,'./14/16','Text Color')]
for i in range(1,N_MAX+1): pub+=[(TXTID[i],'./2/369',f'Card {i} Text'),(W_IC[i-1],'./2/100',f'Card {i} Icon'),(DZID[i],'./1/324/300',f'Card {i} Custom Image'),(W_H[i-1],'./2/100',f'Card {i} Highlight')]
pubx=''.join(f'\t\t<target object="{o}" channel="{c}" name="{n}"/>\n' for o,c,n in pub)
s=s.replace('<publishSettings>\n\t\t<version>2</version>\n','<publishSettings>\n\t\t<version>2</version>\n'+pubx,1)
s=s.replace('<timemarkerset/>',f'<timemarkerset><timemarker><inpoint>{T(2.2)}</inpoint><color>1</color><type>4</type></timemarker><timemarker><inpoint>{T(7.9)}</inpoint><color>1</color><type>6</type></timemarker></timemarkerset>',1)
s=re.sub(r'\s*<target object="10268"[^>]*/>','',s)
open(OUT,'w').write(s); print('ok',len(s),nid[0])
