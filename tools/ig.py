import sys; sys.path.insert(0,'/home/claude')
from titles import style_b, font, text_img, shadow, pad, TEAL, TEAL2, DARK, CREAM
from PIL import Image, ImageDraw
W,H=1080,1920
def bgcol(im): return im.convert('RGB').resize((1,1)).getpixel((0,0)) if False else im.convert('RGB').getpixel((20,20))
def title_img(lines, size=96):
    ims=[text_img(l, font(size,'ExtraBold'), (255,255,255,255), 10, DARK+(255,)) for l in lines]
    w=max(i.width for i in ims); h=sum(i.height for i in ims)+20*(len(ims)-1)
    o=Image.new('RGBA',(w,h),(0,0,0,0)); y=0
    for i in ims: o.alpha_composite(i,((w-i.width)//2,y)); y+=i.height+20
    return shadow(pad(o,30),10,(0,8),150)
def kicker(t):
    tx=text_img(t,font(46,'Bold'),(255,255,255,255)); c=Image.new('RGBA',(tx.width+60,tx.height+36),(0,0,0,0))
    ImageDraw.Draw(c).rounded_rectangle([0,0,c.width-1,c.height-1],30,fill=TEAL+(255,)); c.alpha_composite(tx,(30,18)); return shadow(pad(c))
def cover(src, box, lines, num, out, fill=None):
    s=Image.open(src).convert('RGB'); crop=s.crop(box)
    col=fill or s.getpixel((30,30))
    c=Image.new('RGBA',(W,H),col+(255,))
    # panda area: y 820..1660 (inside 3:4 grid crop 240..1680)
    tw=int(crop.width*840/crop.height)
    if tw>W: crop=crop.resize((W,int(crop.height*W/crop.width))); c.paste(crop,(0,1660-crop.height))
    else: crop=crop.resize((tw,840)); c.paste(crop,((W-tw)//2,820))
    k=kicker(f'הידעת · #{num}'); c.alpha_composite(k,((W-k.width)//2,280))
    t=title_img(lines); 
    if t.width>W-40: t=t.resize((W-40,int(t.height*(W-40)/t.width)))
    c.alpha_composite(t,((W-t.width)//2,420))
    c.convert('RGB').save(out,quality=92); return c
if __name__=='__main__':
    covers=[
     ('r1_frame.png',(0,0,720,1280),['פנדה','שמדברת על דאטה?'],1,'ig/cover1_intro.jpg'),
     ('cover_roles_9x16.jpg',(0,1180,1080,1920),['Engineer, Analyst','או Scientist?'],2,'ig/cover2_roles.jpg'),
     ('cover_dashboard_9x16.png',(0,1100,1080,1920),['מה זה','דשבורד?'],3,'ig/cover3_dashboard.jpg'),
     ('cover_database_9x16.png',(0,1080,1080,1920),['מה זה','בסיס נתונים?'],4,'ig/cover4_database.jpg')]
    for src,box,l,n,o in covers: cover(src,box,l,n,o)
    # post A: meet Pandata (1080x1350)
    cs=Image.open('pandata_character_sheet.jpg').convert('RGB')
    p=Image.new('RGBA',(1080,1350),cs.getpixel((10,10))+(255,))
    p.paste(cs.resize((1000,1000)),(40,320))
    t=title_img(['תכירו את פנדאטא'],88); p.alpha_composite(t,((1080-t.width)//2,40))
    s=text_img('פנדה + דאטה. מסביר דאטה כמו לחבר',font(44,'Medium'),DARK+(255,)); p.alpha_composite(s,((1080-s.width)//2,230))
    p.convert('RGB').save('ig/post_meet_pandata.jpg',quality=92)
    # post B: roles cheat sheet
    q=Image.new('RGBA',(1080,1350),CREAM+(255,)); d=ImageDraw.Draw(q)
    t=title_img(['3 תפקידים בדאטה','בשורה אחת'],80); q.alpha_composite(t,((1080-t.width)//2,40))
    rows=[('Data Engineer','בונה את הצינור: אוסף ומעביר את הנתונים'),('Data Analyst','מבין מה קרה: מנתח את העבר'),('Data Scientist','מנחש מה יקרה: מודלים וחיזוי')]
    y=430
    for r,dsc in rows:
        d.rounded_rectangle([60,y,1020,y+230],34,fill=(255,255,255),outline=TEAL,width=6)
        a=text_img(r,font(60,'ExtraBold'),TEAL+(255,)); q.alpha_composite(a,(1020-40-a.width,y+30))
        b=text_img(dsc,font(40,'Medium'),DARK+(255,)); 
        if b.width>880: b=b.resize((880,int(b.height*880/b.width)))
        q.alpha_composite(b,(1020-40-b.width,y+130)); y+=270
    f=text_img('שמרו לפעם הבאה ששואלים אתכם 📌'.replace(' 📌',''),font(42,'Bold'),DARK+(255,)); q.alpha_composite(f,((1080-f.width)//2,1250))
    q.convert('RGB').save('ig/post_roles_cheatsheet.jpg',quality=92)
