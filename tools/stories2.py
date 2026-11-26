import sys; sys.path.insert(0,'/home/claude')
from titles import font, text_img, shadow, pad, TEAL, TEAL2, DARK
from ig import title_img, kicker
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920
MONO=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',40)
def mono(t,col):
    d=ImageDraw.Draw(Image.new('RGB',(1,1))); b=d.textbbox((0,0),t,font=MONO)
    im=Image.new('RGBA',(b[2]+4,b[3]+8),(0,0,0,0)); ImageDraw.Draw(im).text((0,0),t,font=MONO,fill=col); return im
def panel(lines, code, foot, dark):
    bg=(16,38,42,235) if dark else (255,255,255,240); fg=(240,246,245,255) if dark else DARK+(255,)
    acc=TEAL2+(255,) if dark else TEAL+(255,)
    ims=[text_img(l,font(46,'Medium'),fg) for l in lines]
    cims=[]
    for t,ok in code: cims.append(mono(t,(120,220,160,255) if ok else (255,120,110,255)))
    f=text_img(foot,font(42,'Bold'),acc)
    inner=max([i.width for i in ims]+[c.width+60 for c in cims]+[f.width])
    w=min(960,inner+90)
    h=40+sum(i.height+14 for i in ims)+(sum(c.height+12 for c in cims)+50 if cims else 0)+f.height+80
    c=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(c)
    d.rounded_rectangle([0,0,w-1,h-1],36,fill=bg,outline=acc,width=4)
    d.rectangle([w-14,40,w-4,h-40],fill=acc)  # right accent bar (RTL start)
    y=40
    for i in ims:
        if i.width>w-80: i=i.resize((w-80,int(i.height*(w-80)/i.width)))
        c.alpha_composite(i,((w-i.width)//2,y)); y+=i.height+14
    if cims:
        y+=10; ch=sum(x.height+12 for x in cims)+24
        d.rounded_rectangle([40,y,w-40,y+ch],18,fill=(8,20,24,255))
        yy=y+14
        for x in cims: c.alpha_composite(x,(70,yy)); yy+=x.height+12
        y+=ch+16
    d.line([w//2-90,y+10,w//2+90,y+10],fill=acc,width=4)
    c.alpha_composite(f,((w-f.width)//2,y+30))
    return shadow(pad(c,30),12,(0,10),130)
def make(src,out,tag,ttl,lines,code,foot,dark,crop_top=0):
    s=Image.open(src).convert('RGBA'); s=s.resize((W,int(s.height*W/s.width)))
    c=Image.new('RGBA',(W,H),s.getpixel((10,10))); c.alpha_composite(s,(0,H-s.height))
    k=kicker(tag); c.alpha_composite(k,((W-k.width)//2,220))
    t=title_img(ttl,84)
    if t.width>W-30: t=t.resize((W-30,int(t.height*(W-30)/t.width)))
    c.alpha_composite(t,((W-t.width)//2,330)); y=330+t.height-10
    p=panel(lines,code,foot,dark); c.alpha_composite(p,((W-p.width)//2,y))
    c.convert('RGB').save(out,quality=92); return y+p.height

SYM=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
LAT=ImageFont.truetype('/home/claude/rubik.ttf',38) if False else None
def chip(icon,name):
    t=text_img(name,font(36,'Bold'),DARK+(255,))
    d0=ImageDraw.Draw(Image.new('RGB',(1,1))); bb=d0.textbbox((0,0),icon,font=SYM)
    iw=bb[2]-bb[0]
    h=t.height+28; w=t.width+iw+86
    c=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(c)
    d.rounded_rectangle([0,0,w-1,h-1],h//2,fill=(255,255,255,245),outline=TEAL+(255,),width=3)
    r=h-16; d.ellipse([w-8-r,8,w-8,8+r],fill=TEAL+(255,))
    d.text((w-8-r/2-iw/2-bb[0],8+r/2-(bb[3]-bb[1])/2-bb[1]),icon,font=SYM,fill=(255,255,255))
    c.alpha_composite(t,(22,(h-t.height)//2))
    return c
def chips_row(items):
    cs=[chip(i,n) for i,n in items]; gap=18
    w=sum(c.width for c in cs)+gap*(len(cs)-1); h=max(c.height for c in cs)
    o=Image.new('RGBA',(w,h),(0,0,0,0)); x=w
    for c in cs: x-=c.width; o.alpha_composite(c,(x,0)); x-=gap
    return shadow(pad(o,20),8,(0,6),110)
def make2(src,out,tag,ttl,lines,code,foot,dark,chips):
    y=make(src,out,tag,ttl,lines,code,foot,dark)
    c=Image.open(out).convert('RGBA'); r=chips_row(chips)
    if r.width>W-20: r=r.resize((W-20,int(r.height*(W-20)/r.width)))
    c.alpha_composite(r,((W-r.width)//2,y-14)); c.convert('RGB').save(out,quality=92); return y+r.height
