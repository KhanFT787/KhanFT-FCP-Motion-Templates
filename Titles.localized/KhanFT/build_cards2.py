import re,os,math
SRC=os.path.expanduser('~/bak/cards_skeleton3.moti')
OUT=os.path.expanduser('~/mnt/Titles.localized--KhanFT/KhanFT Cards Type 2/KhanFT Cards Type 2.moti')
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
# ---------- design constants
# ================= KhanFT Cards Type 2 (burst from centre) =================
B='3.4028234663852886e+38'
TXF='babfc7777f4711d7aaa7000393833f6a'
N_MAX=10; N_DEF=6
W,H,RND=380,420,60
END=1199198/TB
SPEEDS={'in':[(0.6,0.07),(0.9,0.1),(1.3,0.15)],'out':[(0.4,0.04),(0.55,0.06),(0.85,0.09)]}
SPN=['Snap','Normal','Slow']
def smooth(p): return p*p*(3-2*p)
def ease_in_back(p,s=1.6): return p*p*((s+1)*p-s)
def spring(p,pk=0.35,ov=0.14,half=0.2,a=4.9):
    if p<pk:
        q=p/pk; return (1+ov)*(1-(1-q)**2)
    t=p-pk; w=math.pi/half
    return 1+ov*math.exp(-a*t)*(math.cos(w*t)+(a/w)*math.sin(w*t))*(1 if p<0.999 else 0)
def keys_in(t0,d):
    n=max(8,int(d*60)); S=[];O=[]
    for k in range(n+1):
        p=k/n; t=t0+p*d
        S.append((t,max(0.0,spring(p)))); O.append((t,smooth(min(1,p/0.15))))
    return S,O
def keys_out(t0,d):
    n=max(8,int(d*60)); S=[];O=[]
    for k in range(n+1):
        q=k/n; t=t0+q*d
        S.append((t,max(0.0,1-ease_in_back(q)))); O.append((t,1 if q<0.8 else 1-smooth((q-0.8)/0.2)))
    return S,O
F_AVG=facs['d6bd636a8c7311d79cc900039366fb58']; F_FCH=facs['8eafb077e84c45e1996a83033a3a2c49']
IMG_U='66fc0d6af6a911d6a7a7000393670732'
ICONS=['Stocks','Bank','Savings','Crypto','Gold','Loan']
# index 0 = centre card, 1..10 = cards
DEF_ICON=[2,0,1,2,3,4,5,0,1,3,4]
DEF_TEXT=['MONEY BASICS','INVESTING\nIN STOCKS','CHOOSING\nA SAFE BANK','BUILDING\nSAVINGS','BUYING\nCRYPTO','INVESTING\nIN GOLD','TAKING\nA LOAN','PLANNING\nAHEAD','PAYING\nTAXES','INSURANCE','RETIREMENT']
FONTS=[('Kohinoor Bold','KohinoorBangla-Bold'),('Kohinoor Semibold','KohinoorBangla-Semibold'),('Kohinoor Medium','KohinoorBangla-Medium'),('Kohinoor Regular','KohinoorBangla-Regular'),('Bangla Sangam Bold','BanglaSangamMN-Bold'),('Bangla MN Bold','BanglaMN-Bold')]
FLOAT=[(10,17,0.004,13),(13,21,0.005,16),(9,15,0.003,19),(12,19,0.006,14),(11,23,0.004,17),(14,16,0.005,21),(10,20,0.003,15),(12,18,0.004,17),(9,22,0.005,14),(13,15,0.004,20),(11,19,0.003,16)]
PHASES=[37,212,148,301,263,95,11,176,329,58,124,247,199,22,83,310,276,141,5,233,167,52]
# ---------- widgets
W_N,W_HUB,W_ORD,W_IS,W_OS,W_FL,W_FS,W_SPR,W_FONT=[new() for _ in range(9)]
HN=[60000]
def swap(): pass  # ids follow first hub build (FCP clips saved against it)
swap(); W_CSH=new(); CSCALE=new(); swap()
CSHAPES=[('Circle',440,440,40),('Square',440,440,40),('Card',380,420,60)]  # Circle uses a true circle shape; rect hidden then
HN2=[70000]
def swap2(): nid[0],HN2[0]=HN2[0],nid[0]
W_ANG=[None]+[new() for _ in range(N_MAX)]; W_DST=[None]+[new() for _ in range(N_MAX)]; W_LINES=new()
DIST_MAX=2000; DIST_DEF=800
LINE1=[None]
def auto_ang(i,n):
    if i>n: return 0.0
    if n==1: return 0.0
    start=180 if n==2 else 90
    return math.radians(start-(i-1)*360.0/n)
W_IC=[new() for _ in range(N_MAX+1)]
W_H=[None]+[new() for _ in range(N_MAX)]
ICLIP={nm:new() for nm in ICONS}
GLOW_STR,UNHL,HLCARD_SRC,HLTEXT_SRC,SIZE_CTRL=[new() for _ in range(5)]
SPR_S=[0.5,0.75,1.0,1.25,1.5]
def widget_slider_n(name,wid,vals,val,rmin,rmax):
    n=len(vals)
    x=f'<scenenode name="{name}" id="{wid}" factoryID="{F_W}" version="5">\n<affecting>3</affecting>'+''.join(f'<snapshot>{k+1}</snapshot>' for k in range(n))
    x+=f'<flags>0</flags><timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/><foldFlags>0</foldFlags><baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704">\n'
    x+=f'<parameter name="Options" id="103" flags="8589938688"><parameter name="Range Minimum" id="104" flags="77326188560" default="0" value="{rmin}"/><parameter name="Range Maximum" id="105" flags="77326188560" default="100" value="{rmax}"/></parameter>\n'
    x+='<parameter name="Hidden" id="102" flags="8606711824" default="0" value="1"/>\n<parameter name="Snapshots" id="101" flags="8589938706">\n'
    for k in range(n): x+=f'<parameter name="Snapshots" id="{k+1}" flags="8589938704"><parameter name="Value" id="1" flags="8589934608" default="0" value="{k/(n-1)}"/><parameter name="Interpolation" id="2" flags="8590000144" default="1" value="1"/></parameter>\n'
    return x+f'</parameter>\n<parameter name="{name}" id="100" flags="8606712080" default="0" value="{val}"/></parameter></scenenode>\n'
def font_rig(target,sid):
    rid=new()
    x=f'<behavior name="Rig Font" id="{rid}" factoryID="{F_RB}">\n<channelBehavior affectingFactory="{TXF}" affectingChannel="./5/{sid}/83" sliderRange="0"/>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<baseFlags>8589934610</baseFlags>\n'
    x+=f'<parameter name="Affecting Object (Hidden)" id="199" flags="77309476882" default="0" value="{target}"/>\n<parameter name="Widget" id="200" flags="77309476880" default="0" value="{W_FONT}"/>\n<parameter name="Snapshots" id="202" flags="8590004242">\n<flags>8590004242</flags>\n'
    for k,(lab,ps) in enumerate(FONTS): x+=f'<parameter name="Font" id="{k+1}" factoryID="{F_FCH}"><font>{ps}</font><defaultFont>Helvetica</defaultFont></parameter>\n'
    return x+'</parameter>\n</behavior>\n'
def osc(target,nm,chan,a,sp,ph):
    oid=new()
    x=f'''<behavior name="{nm}" id="{oid}" factoryID="{F_OSC}">
<channelBehavior affectingFactory="{GRP}" affectingChannel="{chan}" sliderRange="{B}"/>
{TIMING}
<baseFlags>8589934608</baseFlags>
<parameter name="Affecting Object (Hidden)" id="199" flags="77326254098" default="0" value="{target}"/>
<parameter name="Phase" id="200" flags="8606711824" default="0" value="{ph}"/>
<parameter name="Amplitude" id="201" flags="8606711824" default="100" value="{a}"/>
<parameter name="Speed" id="202" flags="8606711824" default="10" value="{sp}"/>
</behavior>
'''
    x+=rig(f'Rig {nm} On',oid,OSC,'./201',W_FL,[(1,0),(2,a)],pname='Amplitude',rng='100')
    x+=rig(f'Rig {nm} Speed',oid,OSC,'./202',W_FS,[(1,0),(2,sp*2)],pname='Speed',rng='100')
    return x
def scale_rig(name,target,widget,snaps):
    return rig(name+' X',target,GRP,'./1/100/105/1',widget,snaps,pname='X',rng=B)+rig(name+' Y',target,GRP,'./1/100/105/2',widget,snaps,pname='Y',rng=B)
# ---------- drivers (scale + fade per slot; slot 0 = centre card)
drivers=''; sel={}
for dirn in ('in','out'):
    for k in range(N_MAX+1):
        selid=new(); beh=''
        for si,(d,stg) in enumerate(SPEEDS[dirn]):
            vid=new()
            if dirn=='in': S,O=keys_in(0.05+k*stg,d)
            else: S,O=keys_out(END-d-(N_MAX-k)*stg-0.02,d)
            drivers+=group(f'{dirn.title()} {k} {SPN[si]}',vid,sc_keys=S,op_keys=O)
            wdg=W_IS if dirn=='in' else W_OS
            for nm,chan,chs in (('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])):
                lid,lx=link(f'{nm} {SPN[si]}',selid,GRP,chan,vid,chs,mix=1 if si==1 else 0)
                beh+=lx+rig(f'Rig {nm} {SPN[si]}',lid,LNK,'./207',wdg,[(j+1,1 if j==si else 0) for j in range(3)],pname='Custom Mix')
        drivers+=group(f'{dirn.title()} {k}',selid,beh=beh)
        sel[(dirn,k)]=selid
SC=[('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])]
def frame_links(target,one,together):
    # one-by-one applied first, 'all together' link (listed first) overrides via Pop Order
    x=''
    for nm,chan,chs in SC:
        lid,lx=link(f'Together {nm}',target,GRP,chan,together,chs,mix=0)
        x+=lx+rig(f'Rig Together {nm}',lid,LNK,'./207',W_ORD,[(1,0),(2,1)],pname='Custom Mix')
    for nm,chan,chs in SC:
        x+=link(f'Pop {nm}',target,GRP,chan,one,chs)[1]
    return x
# ---------- layout
RX,RY=1250,700
def slot_pos(i,n):
    if i>n: return (0,0)
    if n==1: return (RX*0.75,0)
    start=180 if n==2 else 90
    phi=math.radians(start-(i-1)*360.0/n)
    return (round(RX*math.cos(phi),1),round(RY*math.sin(phi),1))
# ---------- media clips
clips=''
for nm in ICONS:
    c=CLIP.replace('name="Drop Zone" id="10267"',f'name="Icon {nm}" id="{ICLIP[nm]}"').replace('<pathURL>Drop Zone.tiff</pathURL>',f'<relativeURL>Media/Icon%20{nm}.png</relativeURL>')
    c=c.replace('<missingWidth>1200</missingWidth>','<missingWidth>512</missingWidth>').replace('<missingHeight>1200</missingHeight>','<missingHeight>512</missingHeight>')
    c=c.replace('default="1200" value="1200"','default="512" value="512"')
    c=c.replace('<parameter name="Object" id="2" flags="8589938704">','<parameter name="Object" id="2" flags="8589938704"><parameter name="Alpha Type" id="100" flags="8589938704"><parameter name="Alpha Type" id="101" flags="8606777344" default="0" value="1"/></parameter>',1)
    c=c.replace('<timing in="0 1 1 0" out="0 120000 1 0" offset="0 1 1 0"/>','<timing in="0 1 1 0" out="1199198 120000 1 0" offset="0 1 1 0"/>',1)
    clips+=c+'\n'
def label(i): return 'Center' if i==0 else f'Card {i}'
def icon_img(i,k,nm):
    iid=new()
    x=DZ.replace('name="Drop Zone" id="10268"',f'name="{label(i)} {nm}" id="{iid}"',1)
    x=re.sub(r'\s*<parameter name="Crop" id="216".*?</parameter>','',x,count=1,flags=re.S)
    x=re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>','',x,count=1,flags=re.S)
    x=x.replace('default="10267" value="10267"',f'default="{ICLIP[nm]}" value="{ICLIP[nm]}"')
    x=x.replace('<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="1"/>','<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="0"/>')
    oa=x.find('<parameter name="Object" id="2"'); ob=x.rfind('</parameter>')
    x=x[:oa]+'<parameter name="Object" id="2" flags="8589938704"><parameter name="Width" id="313" flags="8589934610" default="1" value="512"/><parameter name="Height" id="314" flags="8589934610" default="1" value="512"/></parameter>'+x[ob+12:]
    x=x.replace('id="300" flags="12901744656"','id="300" flags="81621221392"')
    on=1 if DEF_ICON[i]==k else 0
    x=x.replace('<parameter name="Properties" id="1" flags="8589938704">',f'<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags><parameter name="Y" id="2" flags="8606711824" default="0" value="85"/></parameter><parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="0.371"/><parameter name="Y" id="2" flags="8606711824" default="1" value="0.371"/></parameter></parameter><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="{on}"/></parameter>',1)
    rg=rig(f'Rig {label(i)} {nm}',iid,IMG_U,'./1/200/202',W_IC[i],[(j+1,1 if j==k else 0) for j in range(len(ICONS)+1)],pname='Opacity')
    e=x.rfind('</scenenode>'); return x[:e]+rg+x[e:]
def ins(xml,beh,first=False):
    if first:
        k=xml.find('<behavior '); k=xml.rfind('</scenenode>') if k<0 else k
    else: k=xml.rfind('</scenenode>')
    return xml[:k]+beh+xml[k:]
WHITE='<parameter name="Red" id="1" flags="8606711824" default="1" value="1"/><parameter name="Green" id="2" flags="8606711824" default="1" value="1"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="1"/>'
def recolor(xml,col):
    return re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)'+re.escape(WHITE),r'\1<parameter name="Red" id="1" flags="8606711824" default="1" value="%s"/><parameter name="Green" id="2" flags="8606711824" default="1" value="%s"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="%s"/>'%col,xml,count=1)
def strip_beh(xml): return re.sub(r'<behavior .*?</behavior>\s*','',xml,flags=re.S)
def add_opacity0(xml): return xml.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
M={}   # master ids from card 1
TXTID={}; DZID={}; FDRV=[]; GLOW1=[None]
def make_content(i):
    tid,did,bid,cid=new(),new(),new(),new()
    txt=DEF_TEXT[i]
    t=TXT.replace('name="Type Text Here" id="10210"',f'name="{label(i)} Text" id="{tid}"',1)
    t=t.replace('<text>Type Text Here</text>','<text>%s</text>'%txt).replace('length="14"','length="%d"'%len(txt))
    pid=new(); t=t.replace('<paragraphStyle id="10239">','<paragraphStyle id="%s">'%pid).replace('<parameter name="Paragraph" id="10239"','<parameter name="Paragraph" id="%s"'%pid)
    sid=new(); t=t.replace('id="10241" factoryID','id="%s" factoryID'%sid).replace('style="10241"','style="%s"'%sid)
    t=ins(t,font_rig(tid,sid))
    t=t.replace('<parameter name="Substance" id="10229"','<parameter name="Substance" id="%s"'%new())
    t=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-921[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="-75"/>',t)
    t=t.replace('<parameter name="Anchor Point" id="107"','<parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="0.82"/><parameter name="Y" id="2" flags="8606711824" default="1" value="0.82"/></parameter><parameter name="Anchor Point" id="107"',1)
    t=t.replace('<parameter name="X" id="1" flags="8606711824" default="0" value="1728"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="0"/>').replace('<parameter name="Y" id="2" flags="8606711824" default="0" value="50"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>')
    dz=DZ.replace('name="Drop Zone" id="10268"',f'name="{label(i)} Icon" id="{did}"',1)
    dz=re.sub(r'\s*<parameter name="Crop" id="216".*?</parameter>','',dz,count=1,flags=re.S)
    dz=dz.replace('default="10267" value="10267"',f'default="{cid}" value="{cid}"')
    dz=re.sub(r'\s*<parameter name="Fit Factor" id="318".*?</parameter>','',dz,count=1,flags=re.S)
    dz=dz.replace('<parameter name="Width" id="313" flags="8589934610" default="1" value="3840"/>','<parameter name="Width" id="313" flags="8589934610" default="1" value="190"/>')
    dz=dz.replace('<parameter name="Height" id="314" flags="8589934610" default="1" value="3840"/>','<parameter name="Height" id="314" flags="8589934610" default="1" value="190"/>')
    dz=dz.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags><parameter name="Y" id="2" flags="8606711824" default="0" value="85"/></parameter></parameter>',1)
    dz=add_opacity0(dz)
    dz=ins(dz,rig(f'Rig {label(i)} Custom',did,IMG_U,'./1/200/202',W_IC[i],[(j+1,1 if j==len(ICONS) else 0) for j in range(len(ICONS)+1)],pname='Opacity'))
    global clips
    clips+=CLIP.replace('name="Drop Zone" id="10267"',f'name="{label(i)} Icon" id="{cid}"')+'\n'
    r=RECT.replace('name="Rectangle" id="10244"',f'name="{label(i)} Card" id="{bid}"',1)
    r=re.sub(r'<parameter name="X" id="1" flags="8606711824" default="0" value="-493[^"]*"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="0"/>',r)
    r=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-251[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>',r)
    r=r.replace('<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>','<parameter name="Closed" id="116" flags="8590000146" default="0" value="1"/>\n<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%d"/>'%RND)
    r=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)',r'\1'+WHITE,r)
    r=re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Width" id="1" flags="12901679120" default="{W}" value="{W}"/>',r)
    r=re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>',f'<parameter name="Height" id="2" flags="12901679120" default="{H}" value="{H}"/>',r)
    r=r.replace('<parameter name="Lighting" id="230"','<parameter name="Drop Shadow" id="208" flags="8589940752"><foldFlags>131083</foldFlags><parameter name="Opacity" id="211" flags="8606711824" default="0.75" value="0.28"/><parameter name="Blur" id="213" flags="8606711824" default="5" value="40"/><parameter name="Distance" id="212" flags="8606711824" default="5" value="16"/><parameter name="Angle" id="214" flags="8606711824" default="5.497787143782138" value="4.7123889803846897"/></parameter>\n<parameter name="Lighting" id="230"',1)
    r=r.replace('<parameter name="Outline" id="108" flags="8589971472">','<parameter name="Outline" id="108" flags="8589938704"><parameter name="Brush Color" id="107" flags="8589938704"><foldFlags>11</foldFlags><parameter name="Red" id="1" flags="8606711824" default="1" value="0.118"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.161"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.231"/></parameter><parameter name="Brush Opacity" id="142" flags="8606711824" default="1" value="1"/><parameter name="Width" id="105" flags="8606711824" default="2" value="0"/>',1)
    if i==1:
        M.update(sty=sid,txt=tid,bg=bid)
        # hidden colour sources for highlight colours
        for nm,sid_,col in (('Highlight Card Color Source',HLCARD_SRC,(1,1,1)),('Highlight Text Color Source',HLTEXT_SRC,(0.13,0.13,0.15))):
            g=strip_beh(r).replace(f'name="{label(i)} Card" id="{bid}"',f'name="{nm}" id="{sid_}"',1)
            FDRV.append(add_opacity0(recolor(g,col)))
    elif i==0:
        M.update(hub_sty=sid,hub_bg=bid); swap()
        t=t.replace('<parameter name="Red" id="1" flags="8606711824" default="1" value="0.13"/>','<parameter name="Red" id="1" flags="8606711824" default="1" value="1"/>',1)
        t=t.replace('<parameter name="Green" id="2" flags="8606711824" default="1" value="0.13"/>','<parameter name="Green" id="2" flags="8606711824" default="1" value="1"/>',1)
        t=t.replace('<parameter name="Blue" id="3" flags="8606711824" default="1" value="0.15000000000000002"/>','<parameter name="Blue" id="3" flags="8606711824" default="1" value="1"/>',1)
        r=recolor(r,(0.118,0.161,0.231))
        nm0,w0,h0,r0=CSHAPES[0]
        r=r.replace(f'<parameter name="Width" id="1" flags="12901679120" default="{W}" value="{W}"/>',f'<parameter name="Width" id="1" flags="12901679120" default="{w0}" value="{w0}"/>',1)
        r=r.replace(f'<parameter name="Height" id="2" flags="12901679120" default="{H}" value="{H}"/>',f'<parameter name="Height" id="2" flags="12901679120" default="{h0}" value="{h0}"/>',1)
        r=r.replace('<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%d"/>'%RND,'<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%d"/>'%r0,1)
        r=r.replace('<parameter name="Red" id="1" flags="8606711824" default="1" value="0.118"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.161"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.231"/></parameter><parameter name="Brush Opacity"','<parameter name="Red" id="1" flags="8606711824" default="1" value="0.984"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.749"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.141"/></parameter><parameter name="Brush Opacity"',1)
        swap2(); cbid=new(); M['hub_c']=cbid
        c=r.replace(f'name="{label(i)} Card" id="{bid}"',f'name="Center Circle" id="{cbid}"',1)
        c=c.replace('<parameter name="Shape Type" id="100" flags="12884967442" default="5" value="5"/>','<parameter name="Shape Type" id="100" flags="12884967442" default="4" value="4"/>',1)
        c=c.replace('<parameter name="Roundness" id="144" flags="8606711824" default="0" value="%d"/>'%r0,'',1)
        c=re.sub(r'<parameter name="Size" id="160" flags="8589938704">\s*<foldFlags>8388623</foldFlags>\s*<parameter name="Width" id="1"[^>]*/>\s*<parameter name="Height" id="2"[^>]*/>',
                 '<parameter name="Curvature" id="159" flags="12901679120" default="1" value="1"/><parameter name="Radius" id="160" flags="8589938704"><foldFlags>8388623</foldFlags><parameter name="X" id="1" flags="12901679120" default="230" value="230"/><parameter name="Y" id="2" flags="12901679120" default="230" value="230"/>',c,count=1)
        assert 'name="Radius" id="160"' in c
        c=add_opacity0(c).replace('<parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/>','<parameter name="Opacity" id="202" flags="8606711824" default="1" value="1"/>',1)
        cb=rig('Rig Circle On',cbid,SHP,'./1/200/202',W_CSH,[(1,1),(2,0),(3,0)],pname='Opacity')
        cb+=link('Card Shadow',cbid,SHP,'./1/208/211',M['bg'],[('211','./1/208/211')])[1]
        cb+=link('Center Color',cbid,SHP,'./2/353/113/111',bid,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
        cb+=link('Center Border Color',cbid,SHP,'./2/353/108/107',bid,[('1','./2/353/108/107/1'),('2','./2/353/108/107/2'),('3','./2/353/108/107/3')])[1]
        cb+=link('Center Border Width',cbid,SHP,'./2/353/108/105',bid,[('105','./2/353/108/105')])[1]
        c=ins(c,cb)
        hb=rig('Rig Center Width',bid,SHP,'./2/353/160/1',W_CSH,[(k+1,x[1]) for k,x in enumerate(CSHAPES)],pname='Width',rng=B)
        hb+=rig('Rig Center Height',bid,SHP,'./2/353/160/2',W_CSH,[(k+1,x[2]) for k,x in enumerate(CSHAPES)],pname='Height',rng=B)
        hb+=rig('Rig Center Roundness',bid,SHP,'./2/353/144',W_CSH,[(k+1,x[3]) for k,x in enumerate(CSHAPES)],pname='Roundness',rng=B)
        hb+=rig('Rig Rect On',bid,SHP,'./1/200/202',W_CSH,[(1,0),(2,1),(3,1)],pname='Opacity')
        hb+=link('Card Shadow',bid,SHP,'./1/208/211',M['bg'],[('211','./1/208/211')])[1]
        r=add_opacity0(r); swap2()
        r=ins(r,hb)+'\n'+c; swap(); nid[0]+=7  # keep later ids = first hub build
    else:
        x=link('Text Size',tid,TXF,f'./5/{sid}/3',M['txt'],[('3',f'./5/{M["sty"]}/3')])[1]
        x+=link('Text Color',tid,TXF,f'./5/{sid}/14/16',M['txt'],[('1',f'./5/{M["sty"]}/14/16/1'),('2',f'./5/{M["sty"]}/14/16/2'),('3',f'./5/{M["sty"]}/14/16/3')])[1]
        t=ins(t,x)
        bg=M['bg']; lb=''
        lb+=link('Card Color',bid,SHP,'./2/353/113/111',bg,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
        lb+=link('Card Roundness',bid,SHP,'./2/353/144',bg,[('144','./2/353/144')])[1]
        lb+=link('Card Shadow',bid,SHP,'./1/208/211',bg,[('211','./1/208/211')])[1]
        lb+=link('Border Color',bid,SHP,'./2/353/108/107',bg,[('1','./2/353/108/107/1'),('2','./2/353/108/107/2'),('3','./2/353/108/107/3')])[1]
        lb+=link('Border Width',bid,SHP,'./2/353/108/105',bg,[('105','./2/353/108/105')])[1]
        lb+=link('Border Opacity',bid,SHP,'./2/353/108/142',bg,[('142','./2/353/108/142')])[1]
        r=ins(r,lb)
    imgs=''.join(icon_img(i,k,nm) for k,nm in enumerate(ICONS))
    TXTID[i]=tid; DZID[i]=did
    glow=''
    if i>=1:
        # glow
        gsid,gid=new(),new()
        g=strip_beh(r).replace(f'name="{label(i)} Card" id="{bid}"',f'name="{label(i)} Glow" id="{gsid}"',1)
        g=g.replace('<parameter name="Drop Shadow" id="208" flags="8589940752">','<parameter name="Drop Shadow" id="208" flags="8589971472">',1)
        g=recolor(g,(0.984,0.749,0.141))
        g=g.replace('<parameter name="Roundness" id="144"','<parameter name="Feather" id="102" flags="8606744592" default="0" value="70"/>\n<parameter name="Roundness" id="144"',1)
        b=rig('Rig Glow',gsid,SHP,'./1/200/202',W_H[i],[(1,0),(2,1)],pname='Opacity')
        if GLOW1[0] is None: GLOW1[0]=gsid
        else: b+=link('Glow Color',gsid,SHP,'./2/353/113/111',GLOW1[0],[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
        g=add_opacity0(ins(g,b))
        glow=group(f'{label(i)} Glow Group',gid,children=g,py=-14,sx=1.1,sy=1.1,beh=link('Glow Strength',gid,GRP,'./1/200/202',GLOW_STR,[('202','./1/200/202')],scale=1)[1])
        # highlight colours
        x=link('Highlight Card Color',bid,SHP,'./2/353/113/111',HLCARD_SRC,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')],mix=0)
        r=ins(r,x[1]+rig('Rig Highlight Card Color',x[0],LNK,'./207',W_H[i],[(1,0),(2,1)],pname='Custom Mix'),first=True)
        y=link('Highlight Text Color',tid,TXF,f'./5/{sid}/14/16',HLTEXT_SRC,[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')],mix=0)
        yb=y[1]+rig('Rig Highlight Text Color',y[0],LNK,'./207',W_H[i],[(1,0),(2,1)],pname='Custom Mix')
        k=t.find('<behavior name="Text Color"'); k=t.rfind('</scenenode>') if k<0 else k
        t=t[:k]+yb+t[k:]
        r=ins(r,rig('Rig Shadow Dist',bid,SHP,'./1/208/212',W_H[i],[(1,16),(2,44)],pname='Distance',rng=B)+rig('Rig Shadow Blur',bid,SHP,'./1/208/213',W_H[i],[(1,40),(2,80)],pname='Blur',rng=B))
    return t+'\n'+imgs+dz+'\n'+r+'\n'+glow+'\n'
def size_group(i,children):
    sg=new()
    return group(f'{label(i)} Size',sg,children=children,beh=link('Card Size',sg,GRP,'./1/100/105',SIZE_CTRL,[('1','./1/100/105/1'),('2','./1/100/105/2')],scale=1)[1])
# ---------- cards
cards=''
for i in range(1,N_MAX+1):
    content=make_content(i)
    amp,spd,ramp,rspd=FLOAT[i]
    # float source + calm/boost chain
    fsrc=new()
    FDRV.append(group(f'Float Source {i}',fsrc,beh=osc(fsrc,'Float Y','./1/100/101/2',amp,spd,PHASES[2*i])+osc(fsrc,'Float Tilt','./1/100/109/3',ramp,rspd,PHASES[2*i+1])))
    YC=('Y','./1/100/101',[('2','./1/100/101/2')]); TC=('Tilt','./1/100/109',[('3','./1/100/109/3')])
    prev=fsrc
    for j in [j for j in range(1,N_MAX+1) if j!=i]+[0]:
        hid=new(); hb=''
        for nm,chan,chs in (YC,TC):
            base=0.5625 if nm=='Y' else 1
            lid,x=link(f'Calm {nm}',hid,GRP,chan,prev,chs,scale=base); hb+=x
            if j: hb+=rig(f'Rig Calm {nm} {j}',lid,LNK,'./204',W_H[j],[(1,base),(2,base*0.25)],pname='Scale',rng=B)
            else: hb+=rig(f'Rig Boost {nm}',lid,LNK,'./204',W_H[i],[(1,base),(2,base*1.8)],pname='Scale',rng=B)
        FDRV.append(group(f'Float {i} '+(f'Calm by {j}' if j else 'Boost'),hid,beh=hb))
        prev=hid
    fl_id=new(); fl=''
    for nm,chan,chs in (YC,TC): fl+=link(f'Float {nm}',fl_id,GRP,chan,prev,chs)[1]
    inner=group(f'{label(i)} Float',fl_id,children=content,beh=fl)
    # dim/shrink by other highlights
    for j in range(1,N_MAX+1):
        if j==i: continue
        did_=new()
        dl,dx=link(f'Dim by {j}',did_,GRP,'./1/200/202',UNHL,[('202','./1/200/202')],mix=0)
        bb=dx+rig(f'Rig Dim {j}',dl,LNK,'./207',W_H[j],[(1,0),(2,1)],pname='Custom Mix')+scale_rig(f'Rig Shrink {j}',did_,W_H[j],[(1,1),(2,0.94)])
        inner=group(f'{label(i)} Dim by {j}',did_,children=inner,beh=bb)
    gid_=new(); inner=group(f'{label(i)} Grow',gid_,children=inner,beh=scale_rig('Rig Grow',gid_,W_H[i],[(1,1),(2,1.12)]))
    inner=size_group(i,inner)
    # counter-scales (undo push/pull/spread on card size)
    for j in range(1,N_MAX+1):
        cid_=new()
        if j==i: inner=group(f'{label(i)} Counter Push',cid_,children=inner,beh=scale_rig('Rig Counter Push',cid_,W_H[i],[(1,1),(2,1/1.1)]))
        else: inner=group(f'{label(i)} Counter Pull {j}',cid_,children=inner,beh=scale_rig(f'Rig Counter Pull {j}',cid_,W_H[j],[(1,1),(2,1/0.93)]))
    cs=new(); inner=group(f'{label(i)} Counter Spread',cs,children=inner,beh=scale_rig('Rig Counter Spread',cs,W_SPR,[(k+1,1/v) for k,v in enumerate(SPR_S)]))
    # counter-rotations keep the card upright
    cr=new(); inner=group(f'{label(i)} Unrotate Angle',cr,children=inner,rz=0,beh=rig('Rig Unrotate Angle',cr,GRP,'./1/100/109/3',W_ANG[i],[(1,math.pi),(2,-math.pi)],pname='Z',rng=B))
    ca=new(); inner=group(f'{label(i)} Unrotate Auto',ca,children=inner,rz=-auto_ang(i,N_DEF),beh=rig('Rig Unrotate Auto',ca,GRP,'./1/100/109/3',W_N,[(n,-auto_ang(i,n)) for n in range(1,N_MAX+1)],pname='Z',rng=B))
    # arm: card sits at (distance, 0) along the aimed direction
    arm=new(); inner=group(f'{label(i)} Arm',arm,children=inner,px=DIST_DEF,beh=rig('Rig Distance',arm,GRP,'./1/100/101/1',W_DST[i],[(1,0),(2,DIST_MAX)],pname='X',rng=B))
    # connector line from the centre to the card
    lid_=new()
    ln=RECT.replace('name="Rectangle" id="10244"',f'name="{label(i)} Line" id="{lid_}"',1)
    ln=re.sub(r'<parameter name="X" id="1" flags="8606711824" default="0" value="-493[^"]*"/>','<parameter name="X" id="1" flags="8606711824" default="0" value="500"/>',ln)
    ln=re.sub(r'<parameter name="Y" id="2" flags="8606711824" default="0" value="-251[^"]*"/>','<parameter name="Y" id="2" flags="8606711824" default="0" value="0"/>',ln)
    ln=re.sub(r'(<parameter name="Fill Color" id="111" flags="12884906000">\s*<foldFlags>15</foldFlags>)',r'\1<parameter name="Red" id="1" flags="8606711824" default="1" value="0.118"/><parameter name="Green" id="2" flags="8606711824" default="1" value="0.161"/><parameter name="Blue" id="3" flags="8606711824" default="1" value="0.231"/>',ln)
    ln=re.sub(r'<parameter name="Width" id="1" flags="12901679120" default="[^"]*" value="[^"]*"/>','<parameter name="Width" id="1" flags="12901679120" default="1000" value="1000"/>',ln)
    ln=re.sub(r'<parameter name="Height" id="2" flags="12901679120" default="[^"]*" value="[^"]*"/>','<parameter name="Height" id="2" flags="12901679120" default="8" value="8"/>',ln)
    ln=ln.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0.6"/></parameter>',1)
    if LINE1[0] is None: LINE1[0]=lid_
    else:
        lb=link('Line Color',lid_,SHP,'./2/353/113/111',LINE1[0],[('1','./2/353/113/111/1'),('2','./2/353/113/111/2'),('3','./2/353/113/111/3')])[1]
        lb+=link('Line Opacity',lid_,SHP,'./1/200/202',LINE1[0],[('202','./1/200/202')])[1]
        lb+=link('Line Thickness',lid_,SHP,'./2/353/160/2',LINE1[0],[('2','./2/353/160/2')])[1]
        ln=ins(ln,lb)
    lg=new()
    lbeh=rig('Rig Line Length',lg,GRP,'./1/100/105/1',W_DST[i],[(1,0),(2,DIST_MAX/1000)],pname='X',rng=B)+rig('Rig Lines On',lg,GRP,'./1/200/202',W_LINES,[(1,0),(2,1)],pname='Opacity')
    line=group(f'{label(i)} Line Group',lg,children=ln,sx=DIST_DEF/1000,beh=lbeh)
    # aim: user angle adjust inside automatic angle (by Number of Cards)
    ad=new(); inner=group(f'{label(i)} Angle',ad,children=inner+line,rz=0,beh=rig('Rig Angle',ad,GRP,'./1/100/109/3',W_ANG[i],[(1,-math.pi),(2,math.pi)],pname='Z',rng=B))
    am=new(); inner=group(f'{label(i)} Aim',am,children=inner,rz=auto_ang(i,N_DEF),beh=rig('Rig Aim',am,GRP,'./1/100/109/3',W_N,[(n,auto_ang(i,n)) for n in range(1,N_MAX+1)],pname='Z',rng=B))
    # push (own highlight) / pull (others) frames about the centre
    for j in range(1,N_MAX+1):
        pf=new()
        if j==i: inner=group(f'{label(i)} Push',pf,children=inner,beh=scale_rig('Rig Push',pf,W_H[i],[(1,1),(2,1.1)]))
        else: inner=group(f'{label(i)} Pull by {j}',pf,children=inner,beh=scale_rig(f'Rig Pull {j}',pf,W_H[j],[(1,1),(2,0.93)]))
    # pop frames
    fo=new(); inner=group(f'{label(i)} Out',fo,children=inner,beh=frame_links(fo,sel[('out',N_MAX-i)],sel[('out',N_MAX-1)]))
    fi=new(); inner=group(f'{label(i)} In',fi,children=inner,beh=frame_links(fi,sel[('in',i)],sel[('in',1)]))
    sh=new()
    sb=rig(f'Rig {label(i)} Show',sh,GRP,'./1/200/202',W_N,[(n,1 if i<=n else 0) for n in range(1,N_MAX+1)],pname='Opacity')
    cards+=group(label(i),sh,children=inner,op=1 if i<=N_DEF else 0,beh=sb)
# ---------- centre card
content=make_content(0)
amp,spd,ramp,rspd=FLOAT[0]
hf=new()
hub=group('Center Float',hf,children=content,beh=osc(hf,'Float Y','./1/100/101/2',amp,spd,PHASES[0])+osc(hf,'Float Tilt','./1/100/109/3',ramp,rspd,PHASES[1]))
hub=size_group(0,hub)
swap(); hub=group('Center Scale',CSCALE,children=hub,sx=1.2,sy=1.2); swap()
cs=new(); hub=group('Center Counter Spread',cs,children=hub,beh=scale_rig('Rig Counter Spread',cs,W_SPR,[(k+1,1/v) for k,v in enumerate(SPR_S)]))
fo=new(); hub=group('Center Out',fo,children=hub,beh=frame_links(fo,sel[('out',N_MAX)],sel[('out',N_MAX)]))
fi=new(); hub=group('Center In',fi,children=hub,beh=frame_links(fi,sel[('in',0)],sel[('in',0)]))
hs=new(); hub=group('Center',hs,children=hub,beh=rig('Rig Center Show',hs,GRP,'./1/200/202',W_HUB,[(1,0),(2,1)],pname='Opacity'))
# ---------- assemble
FDRV.append(group('Glow Strength',GLOW_STR,op=0.7))
FDRV.append(group('Unhighlighted Opacity',UNHL,op=1))
FDRV.append(group('Card Size Control',SIZE_CTRL))
SPREAD=new()
BURST=new()
burst=group('Spread',SPREAD,children=hub+cards,beh=scale_rig('Rig Spread',SPREAD,W_SPR,[(k+1,v) for k,v in enumerate(SPR_S)]))
burst=group('Burst',BURST,children=burst)
DRV=group('Drivers',new(),children=drivers+''.join(FDRV))
a=s.find('<layer name="Group" id="10206">'); b=s.find('>',a)+1
c=s.find('<scenenode name="Title Background"',b)
s=s[:b]+'\n'+burst+DRV+s[c:]
s=s.replace('<clip name="Drop Zone" id="10267">',clips+'<clip name="Drop Zone" id="10267">',1)
rigx=f'<scenenode name="Rig" id="{new()}" factoryID="{F_RIG}" version="5">\n'
rigx+=widget_popup('Number of Cards',W_N,[str(n) for n in range(1,N_MAX+1)],N_DEF-1)
rigx+=widget_check('Center Card',W_HUB,True)
swap(); rigx+=widget_popup('Center Shape',W_CSH,[c[0] for c in CSHAPES],0); swap()
rigx+=widget_popup('Pop Order',W_ORD,['One by One','All Together'],0)
rigx+=widget_popup('Entrance Speed',W_IS,SPN,1)
rigx+=widget_popup('Exit Speed',W_OS,SPN,1)
rigx+=widget_slider_n('Spread',W_SPR,SPR_S,0.5,50,150)
rigx+=widget_check('Lines',W_LINES,True)
rigx+=widget_check('Float',W_FL,True)
rigx+=widget_slider('Float Speed',W_FS,0.5)
rigx+=widget_popup('Font',W_FONT,[f[0] for f in FONTS],0)
for i in range(0,N_MAX+1): rigx+=widget_popup(f'{label(i)} Icon',W_IC[i],ICONS+['Custom Image'],DEF_ICON[i])
for i in range(1,N_MAX+1): rigx+=widget_slider(f'Card {i} Highlight',W_H[i],0)
for i in range(1,N_MAX+1):
    rigx+=widget_slider_n(f'Card {i} Angle',W_ANG[i],[0,1],0.5,-180,180)
    rigx+=widget_slider_n(f'Card {i} Distance',W_DST[i],[0,1],DIST_DEF/DIST_MAX,0,DIST_MAX)
rigx+='<flags>0</flags>\n<timing in="0 1 1 0" out="-4004 120000 1 0" offset="0 1 1 0"/>\n<foldFlags>0</foldFlags>\n<baseFlags>16</baseFlags>\n<parameter name="Properties" id="1" flags="8589938704"/>\n<parameter name="Object" id="2" flags="8589938704"/>\n</scenenode>\n'
pa=s.find('<scenenode name="Project"'); pe=span(s,pa)
s=s[:pe]+'\n'+rigx+s[pe:]
bg=M['bg']
pub=[(W_N,'./2/100','Number of Cards'),(W_HUB,'./2/100','Center Card'),(W_ORD,'./2/100','Pop Order'),(W_IS,'./2/100','Entrance Speed'),(W_OS,'./2/100','Exit Speed'),
     (BURST,'./1/100/101','Center Position'),(W_SPR,'./2/100','Spread'),(SIZE_CTRL,'./1/100/105','Card Size'),
     (W_LINES,'./2/100','Lines'),(LINE1[0],'./2/353/113/111','Line Color'),(LINE1[0],'./1/200/202','Line Opacity'),(LINE1[0],'./2/353/160/2','Line Thickness'),(W_FL,'./2/100','Float'),(W_FS,'./2/100','Float Speed'),
     (bg,'./2/353/113/111','Card Color'),(bg,'./2/353/144','Card Roundness'),(bg,'./1/208/211','Shadow Opacity'),(bg,'./2/353/108/105','Border Width'),(bg,'./2/353/108/107','Border Color'),(bg,'./2/353/108/142','Border Opacity'),
     (HLCARD_SRC,'./2/353/113/111','Highlight Card Color'),(HLTEXT_SRC,'./2/353/113/111','Highlight Text Color'),(GLOW1[0],'./2/353/113/111','Highlight Color'),(GLOW_STR,'./1/200/202','Highlight Glow'),(UNHL,'./1/200/202','Unhighlighted Opacity'),
     (W_FONT,'./2/100','Font'),(M['sty'],'./3','Text Size'),(M['sty'],'./14/16','Text Color'),
     (TXTID[0],'./2/369','Center Text'),(W_CSH,'./2/100','Center Shape'),(CSCALE,'./1/100/105','Center Size'),(M['hub_bg'],'./2/353/113/111','Center Color'),(M['hub_sty'],'./14/16','Center Text Color'),(M['hub_sty'],'./3','Center Text Size'),(M['hub_bg'],'./2/353/108/105','Center Border Width'),(M['hub_bg'],'./2/353/108/107','Center Border Color'),(W_IC[0],'./2/100','Center Icon'),(DZID[0],'./1/324/300','Center Custom Image')]
for i in range(1,N_MAX+1): pub+=[(TXTID[i],'./2/369',f'Card {i} Text'),(W_IC[i],'./2/100',f'Card {i} Icon'),(DZID[i],'./1/324/300',f'Card {i} Custom Image'),(W_ANG[i],'./2/100',f'Card {i} Angle'),(W_DST[i],'./2/100',f'Card {i} Distance'),(W_H[i],'./2/100',f'Card {i} Highlight')]
pubx=''.join(f'\t\t<target object="{o}" channel="{c}" name="{n}"/>\n' for o,c,n in pub)
s=s.replace('<publishSettings>\n\t\t<version>2</version>\n','<publishSettings>\n\t\t<version>2</version>\n'+pubx,1)
s=s.replace('<timemarkerset/>',f'<timemarkerset><timemarker><inpoint>{T(2.4)}</inpoint><color>1</color><type>4</type></timemarker><timemarker><inpoint>{T(7.8)}</inpoint><color>1</color><type>6</type></timemarker></timemarkerset>',1)
s=re.sub(r'\s*<target object="10268"[^>]*/>','',s)
open(OUT,'w').write(s); print('ok',len(s),nid[0])
