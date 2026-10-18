from PIL import Image, ImageDraw, ImageFilter, ImageChops
import math, random
S=1200; OUT=600
def radial(size, cx, cy, r, stops):
    """stops: list of (t, (r,g,b)) ; returns RGB image"""
    im=Image.new('RGB',(size,size)); px=im.load()
    for y in range(size):
        for x in range(size):
            t=min(1, math.hypot(x-cx,y-cy)/r)
            for k in range(len(stops)-1):
                t0,c0=stops[k]; t1,c1=stops[k+1]
                if t<=t1:
                    u=(t-t0)/(t1-t0) if t1>t0 else 0
                    px[x,y]=tuple(int(c0[i]+(c1[i]-c0[i])*u) for i in range(3)); break
            else: px[x,y]=stops[-1][1]
    return im
def blob_mask(kind, seed):
    m=Image.new('L',(S,S),0); d=ImageDraw.Draw(m); random.seed(seed)
    cx=cy=S/2
    if kind=='coin':
        d.ellipse([S*0.12,S*0.12,S*0.88,S*0.88],fill=255)
    else:
        pts=[]; n=180
        rx,ry=(S*0.40,S*0.33) if kind=='jade' else (S*0.33,S*0.40)
        ph=[random.uniform(0,6.28) for _ in range(4)]; am=[0.06,0.05,0.03,0.02]
        for i in range(n):
            a=2*math.pi*i/n
            k=1+sum(am[j]*math.sin((j+2)*a+ph[j]) for j in range(4))
            pts.append((cx+rx*k*math.cos(a), cy+ry*k*math.sin(a)))
        d.polygon(pts,fill=255)
    return m.filter(ImageFilter.GaussianBlur(2))
def make(name, kind, cols, seed=1, rim=False):
    base=radial(S//4, S//8*0.8, S//8*0.7, S//4*0.75, cols).resize((S,S),Image.BICUBIC)
    mask=blob_mask(kind, seed)
    # edge darkening (ambient occlusion)
    inner=mask.filter(ImageFilter.GaussianBlur(60))
    shade=ImageChops.multiply(base, Image.merge('RGB',[inner.point(lambda v: int(150+105*v/255))]*3))
    # specular highlight
    spec=Image.new('L',(S,S),0); d=ImageDraw.Draw(spec)
    d.ellipse([S*0.28,S*0.22,S*0.48,S*0.36],fill=210); spec=spec.filter(ImageFilter.GaussianBlur(28))
    shade=Image.composite(Image.new('RGB',(S,S),(255,255,255)), shade, spec)
    if rim:
        d2=ImageDraw.Draw(shade)
        for r,w,c in ((0.30,10,(0,0,0)),(0.27,6,(255,255,255))):
            ov=Image.new('L',(S,S),0); dd=ImageDraw.Draw(ov)
            dd.ellipse([S*(0.5-r),S*(0.5-r),S*(0.5+r),S*(0.5+r)],outline=60 if c==(0,0,0) else 45,width=w)
            ov=ov.filter(ImageFilter.GaussianBlur(3))
            shade=Image.composite(Image.new('RGB',(S,S),c), shade, ov)
    out=shade.convert('RGBA'); out.putalpha(mask)
    out.resize((OUT,OUT),Image.LANCZOS).save(name)
make('Gold Coin.png','coin',[(0,(255,244,200)),(0.35,(243,184,71)),(0.75,(181,116,26)),(1,(110,66,11))],rim=True)
make('Silver Coin.png','coin',[(0,(255,255,255)),(0.35,(214,218,226)),(0.75,(138,144,156)),(1,(70,74,82))],rim=True)
make('Bronze Coin.png','coin',[(0,(255,226,200)),(0.35,(214,140,90)),(0.75,(140,80,40)),(1,(80,42,18))],rim=True)
make('Jade Stone.png','jade',[(0,(214,245,232)),(0.36,(95,194,160)),(0.76,(31,125,99)),(1,(14,70,55))],seed=3)
make('Grey Stone.png','stone',[(0,(245,243,238)),(0.38,(196,192,184)),(0.78,(124,120,113)),(1,(69,66,62))],seed=7)
# ring
R=Image.new('L',(2800,1800),0); d=ImageDraw.Draw(R); d.ellipse([20,20,2780,1780],outline=255,width=6)
ring=Image.new('RGBA',R.size,(255,255,255,0)); ring.putalpha(R.filter(ImageFilter.GaussianBlur(1.2)))
ring.resize((1400,900),Image.LANCZOS).save('Ring.png')
# vertical line texture
L=Image.new('RGBA',(1920,1080),(255,255,255,0)); px=L.load()
for x in range(0,1920,3):
    for y in range(1080): px[x,y]=(255,255,255,255)
L.save('Lines.png')
print('done')
