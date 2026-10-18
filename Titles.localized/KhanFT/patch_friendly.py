import os,sys
P=os.path.expanduser('~/work/cards/build_cards.py')
s=open(P).read()
REL=sys.argv[1] if len(sys.argv)>1 else 'file:./Media/'
def rep(a,b,count=1):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b,count)

# 1. constants + image factory + icon widgets
rep("W_N,W_IS,W_ED,W_OS,W_FL,W_FS=[new() for _ in range(6)]",
"""W_N,W_IS,W_ED,W_OS,W_FL,W_FS=[new() for _ in range(6)]
IMG_U='66fc0d6af6a911d6a7a7000393670732'
ICONS=['Stocks','Bank','Savings','Crypto','Gold','Loan']
ICON_REL=%r
DEF_ICON=[0,1,2,3,4,5,0]
DEF_TEXT=['INVESTING\\nIN STOCKS','CHOOSING\\nA SAFE BANK','BUILDING\\nSAVINGS','BUYING\\nCRYPTO','INVESTING\\nIN GOLD','TAKING\\nA LOAN','PLANNING\\nAHEAD']
W_IC=[new() for _ in range(N_MAX)]
ICLIP={}
for nm in ICONS:
    cid0=new(); ICLIP[nm]=cid0
""" % REL)
# icon clips built after CLIP defined -> do it right before the cards loop
rep("cards=''; clips=''",
"""cards=''; clips=''
for nm in ICONS:
    c=CLIP.replace('name="Drop Zone" id="10267"',f'name="Icon {nm}" id="{ICLIP[nm]}"').replace('<pathURL>Drop Zone.tiff</pathURL>',f'<pathURL>{ICON_REL}Icon%20{nm}.png</pathURL>')
    c=c.replace('<missingWidth>1200</missingWidth>','<missingWidth>512</missingWidth>').replace('<missingHeight>1200</missingHeight>','<missingHeight>512</missingHeight>')
    c=c.replace('default="1200" value="1200"','default="512" value="512"')
    clips+=c+'\\n'
def icon_img(i,k,nm):
    iid=new()
    x=DZ.replace('name="Drop Zone" id="10268"',f'name="Card {i} {nm}" id="{iid}"',1)
    x=re.sub(r'\\s*<parameter name="Crop" id="216".*?</parameter>\\s*</parameter>','',x,count=1,flags=re.S)
    x=re.sub(r'\\s*<parameter name="Fit Factor" id="318".*?</parameter>\\s*</parameter>','',x,count=1,flags=re.S)
    x=x.replace('default="10267" value="10267"',f'default="{ICLIP[nm]}" value="{ICLIP[nm]}"')
    x=x.replace('<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="1"/>','<parameter name="Drop Zone" id="311" flags="8589934738" default="0" value="0"/>')
    x=re.sub(r'\\s*<parameter name="Width" id="313"[^>]*/>\\s*<parameter name="Height" id="314"[^>]*/>','',x)
    on=1 if DEF_ICON[i-1]==k else 0
    x=x.replace('<parameter name="Properties" id="1" flags="8589938704">',f'<parameter name="Properties" id="1" flags="8589938704"><parameter name="Transform" id="100" flags="8589938704"><parameter name="Position" id="101" flags="8589938704"><foldFlags>15</foldFlags><parameter name="Y" id="2" flags="8606711824" default="0" value="85"/></parameter><parameter name="Scale" id="105" flags="8589938704"><foldFlags>15</foldFlags><parameter name="X" id="1" flags="8606711824" default="1" value="0.371"/><parameter name="Y" id="2" flags="8606711824" default="1" value="0.371"/></parameter></parameter><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="{on}"/></parameter>',1)
    rg=rig(f'Rig Card {i} {nm}',iid,IMG_U,'./1/200/202',W_IC[i-1],[(j+1,1 if j==k else 0) for j in range(len(ICONS)+1)],pname='Opacity')
    e=x.rfind('</scenenode>'); return x[:e]+rg+x[e:]
""")
# 2. per-card default text
rep("t=t.replace('<text>Type Text Here</text>','<text>CARD TITLE\\nGOES HERE</text>').replace('length=\"14\"','length=\"19\"')",
    "t=t.replace('<text>Type Text Here</text>','<text>%s</text>'%DEF_TEXT[i-1]).replace('length=\"14\"','length=\"%d\"'%len(DEF_TEXT[i-1]))")
# 3. drop zone visible only for Custom Image; add icon images
rep("    content=t+'\\n'+dz+'\\n'+r+'\\n'",
"""    dz=dz.replace('<parameter name="Properties" id="1" flags="8589938704">','<parameter name="Properties" id="1" flags="8589938704"><parameter name="Blending" id="200" flags="8589938704"><parameter name="Opacity" id="202" flags="8606711824" default="1" value="0"/></parameter>',1)
    e=dz.rfind('</scenenode>'); dz=dz[:e]+rig(f'Rig Card {i} Custom',did,IMG_U,'./1/200/202',W_IC[i-1],[(j+1,1 if j==len(ICONS) else 0) for j in range(len(ICONS)+1)],pname='Opacity')+dz[e:]
    imgs=''.join(icon_img(i,k,nm) for k,nm in enumerate(ICONS))
    TXTID[i]=tid
    content=t+'\\n'+imgs+dz+'\\n'+r+'\\n'""")
rep("bg1=None","bg1=None; TXTID={}")
# 4. widgets + publish
rep("rigx+=widget_slider('Float Speed',W_FS,0.5)",
"""rigx+=widget_slider('Float Speed',W_FS,0.5)
for i in range(1,N_MAX+1): rigx+=widget_popup(f'Card {i} Icon',W_IC[i-1],ICONS+['Custom Image'],DEF_ICON[i-1])""")
rep("(bg1,'./2/353/113/111','Card Color'),(bg1,'./2/353/144','Card Roundness'),(bg1,'./1/208/211','Shadow Opacity')]",
"(bg1,'./2/353/113/111','Card Color'),(bg1,'./2/353/144','Card Roundness'),(bg1,'./1/208/211','Shadow Opacity')]\nfor i in range(1,N_MAX+1): pub+=[(TXTID[i],'./2/369',f'Card {i} Text'),(W_IC[i-1],'./2/100',f'Card {i} Icon')]")
open(P.replace('.py','_v2.py'),'w').write(s); print('patched')
