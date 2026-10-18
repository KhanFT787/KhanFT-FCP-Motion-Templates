import os
P=os.path.expanduser('~/work/cards/build_cards.py')
s=open(P).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
BIG='3.4028234663852886e+38'
CH=[('Pos',"./1/100/101",[('2','./1/100/101/2')]),('Scale',"./1/100/105",[('1','./1/100/105/1'),('2','./1/100/105/2')]),('Fade',"./1/200/202",[('202','./1/200/202')])]

# 1. ids + arc helpers + control groups + per-card arc selectors
rep("DRV=group('Drivers',new(),children=drivers)",
r'''W_LY,W_AH,W_TL=new(),new(),new()
CHS=%r
def arc_c(n): return (n+1)/2
def arc_d(i,n): return int(abs(i-arc_c(n))) if i<=n else 0
def arc_u(i,n):
    if i>n or n<2: return 0.0
    return (i-arc_c(n))/(arc_c(n)-1)
# controls: Arc Ctrl Y = height (slider), Arc Amt = Ctrl * layout flag; same for tilt via X
ACT,AAM,TCT,TAM=new(),new(),new(),new()
drivers+=group('Arc Ctrl',ACT,beh=rig('Rig Arc Height',ACT,GRP,'./1/100/101/2',W_AH,[(1,0),(2,1000)],pname='Y',rng='%s'))
lid,lx=link('Arc Amount',AAM,GRP,'./1/100/101',ACT,[('2','./1/100/101/2')])
drivers+=group('Arc Amt',AAM,beh=lx+rig('Rig Arc On',lid,LNK,'./204',W_LY,[(1,0),(2,1)],pname='Scale',rng='%s'))
drivers+=group('Tilt Ctrl',TCT,beh=rig('Rig Tilt',TCT,GRP,'./1/100/101/1',W_TL,[(1,0),(2,0.5236)],pname='X',rng='%s'))
lid,lx=link('Tilt Amount',TAM,GRP,'./1/100/101',TCT,[('1','./1/100/101/1')])
drivers+=group('Tilt Amt',TAM,beh=lx+rig('Rig Tilt On',lid,LNK,'./204',W_LY,[(1,0),(2,1)],pname='Scale',rng='%s'))
arcsel={}
for dirn in ('in','out'):
    for i in range(1,N_MAX+1):
        gid=new(); beh=''
        slots=sorted({arc_d(i,n) for n in range(1,N_MAX+1)})
        for d in slots:
            k = d if dirn=='in' else (N_MAX-1-d)
            for nm,chan,chs in CHS:
                lid,lx=link(f'{nm} d{d}',gid,GRP,chan,sel[(dirn,k)],chs,mix=0)
                beh+=lx+rig(f'Rig {nm} d{d}',lid,LNK,'./207',W_N,[(n,1 if arc_d(i,n)==d else 0) for n in range(1,N_MAX+1)],pname='Custom Mix')
        drivers+=group(f'Arc {dirn.title()} {i}',gid,beh=beh)
        arcsel[(dirn,i)]=gid
DRV=group('Drivers',new(),children=drivers)''' % (CH,BIG,BIG,BIG,BIG))

# 2. card In: add arc links gated by Layout
rep("    gI=group(f'Card {i} In',in_id,children=gF,beh=bi)",
"""    for nm,chan,chs in CHS:
        lid,x=link(f'Arc In {nm}',in_id,GRP,chan,arcsel[('in',i)],chs,mix=0); bi+=x
        bi+=rig(f'Rig Arc In {nm}',lid,LNK,'./207',W_LY,[(1,0),(2,1)],pname='Custom Mix')
    gI=group(f'Card {i} In',in_id,children=gF,beh=bi)""")
# 3. card Out: add arc links gated by Layout (after L/R links)
rep("    gO=group(f'Card {i} Out',out_id,children=gI,beh=bo)",
"""    for nm,chan,chs in CHS:
        lid,x=link(f'Arc Out {nm}',out_id,GRP,chan,arcsel[('out',i)],chs,mix=0); bo+=x
        bo+=rig(f'Rig Arc Out {nm}',lid,LNK,'./207',W_LY,[(1,0),(2,1)],pname='Custom Mix')
    gO=group(f'Card {i} Out',out_id,children=gI,beh=bo)
    arc_id=new(); ba=''
    lid,x=link('Arc Lift',arc_id,GRP,'./1/100/101',AAM,[('2','./1/100/101/2')]); ba+=x
    ba+=rig('Rig Arc Lift',lid,LNK,'./204',W_N,[(n,-(arc_u(i,n)**2) if i<=n else 0) for n in range(1,N_MAX+1)],pname='Scale',rng='%s')
    lid,x=link('Arc Tilt',arc_id,GRP,'./1/100/109',TAM,[('3','./1/100/101/1')]); ba+=x
    ba+=rig('Rig Arc Tilt',lid,LNK,'./204',W_N,[(n,-arc_u(i,n)) for n in range(1,N_MAX+1)],pname='Scale',rng='%s')
    gO=group(f'Card {i} Arc',arc_id,children=gO,beh=ba)""" % (BIG,BIG))
# 4. widgets
rep("rigx+=widget_popup('Entrance Speed',W_IS,SPN,1)",
"""rigx+=widget_popup('Layout',W_LY,['Straight','Arc'],0)
rigx+=widget_slider('Arc Height',W_AH,0.25)
rigx+=widget_slider('Arc Tilt',W_TL,0.4)
rigx+=widget_popup('Entrance Speed',W_IS,SPN,1)""")
rep("pub=[(W_N,'./2/100','Number of Cards'),",
    "pub=[(W_N,'./2/100','Number of Cards'),(W_LY,'./2/100','Layout'),(W_AH,'./2/100','Arc Height'),(W_TL,'./2/100','Arc Tilt'),")
open(P.replace('.py','_arc.py'),'w').write(s); print('patched')
