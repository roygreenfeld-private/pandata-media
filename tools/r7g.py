import sys; sys.path.insert(0,'/home/claude')
from PIL import Image, ImageDraw, ImageFont
from titles import font, text_img, shadow, pad, TEAL, TEAL2, DARK, CREAM
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
RED=(220,60,60); GREEN=(46,170,90)
CODE=[("SELECT customer, SUM(qty) AS total",5),("FROM orders",1),("WHERE product = 'bamboo'",2),("GROUP BY customer",3),("HAVING SUM(qty) > 10",4),("ORDER BY total DESC",6),("LIMIT 3;",7)]
KW=['SELECT','FROM','WHERE','GROUP BY','HAVING','ORDER BY','LIMIT','SUM','AS','DESC']
def code_panel(active=None, done=(), mode='exec'):
    f=ImageFont.truetype(MONO,26); W,lh=680,56; H=40+lh*len(CODE)+20
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,W-1,H-1],22,fill=(24,40,38,245))
    for i,c in enumerate([(255,95,86),(255,189,46),(39,201,63)]): d.ellipse([18+i*24,14,32+i*24,28],fill=c)
    y=40
    for line,n in CODE:
        on = (mode=='exec' and n==active) or (mode=='write' and active=='write')
        if on: d.rounded_rectangle([8,y+2,W-8,y+lh-4],10,fill=(43,179,163,90),outline=TEAL2+(255,),width=2)
        x=70
        col=(150,170,168) if (mode=='exec' and active and n!=active and n not in done) else (235,245,243)
        # keyword coloring
        rest=line
        for kw in sorted(KW,key=len,reverse=True):
            pass
        tokens=line.split(' ')
        for t in tokens:
            c=col
            if t.rstrip(',;').split('(')[0] in ['SELECT','FROM','WHERE','GROUP','BY','HAVING','ORDER','LIMIT','AS','DESC','SUM']: c=(255,200,90) if col!=(150,170,168) else (150,140,110)
            if t.startswith("'"): c=(140,230,150) if col!=(150,170,168) else (110,150,115)
            d.text((x,y+12),t,font=f,fill=c); x+=d.textlength(t+' ',font=f)
        # exec badge
        if mode=='exec' and (n==active or n in done):
            bc=TEAL2 if n==active else (90,120,118)
            d.ellipse([16,y+8,54,y+46],fill=bc); 
            tb=ImageFont.truetype(MONO,24); d.text((35,y+27),str(n),font=tb,fill='white',anchor='mm')
        y+=lh
    return shadow(pad(im,20),10,(0,6),120)
def table(cols, rows, styles=None, title=None, hl_head=False):
    # rows: list of lists; styles: per row None|'strike'|'dim'|'good'
    cw=[200,170,130][:len(cols)] if len(cols)==3 else [260,200]
    rh=36; W=sum(cw)+30; H=(60 if title else 16)+rh*(len(rows)+1)+14
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,W-1,H-1],20,fill=(255,255,255,245),outline=TEAL+(255,),width=4)
    y=14
    if title:
        t=text_img(title,font(30,'Bold'),TEAL+(255,)); im.alpha_composite(t,(W-18-t.width,14)); y=58
    def row(cells,st,y,head=False):
        x=W-15
        for c,w in zip(cells,cw):
            x0=x-w
            fill=(235,244,242) if head else {'dim':(245,245,245),'strike':(252,228,228),'good':(214,245,224)}.get(st,(255,255,255))
            if head and hl_head: fill=(205,240,234)
            d.rectangle([x0,y,x,y+rh],fill=fill,outline=(205,218,215),width=2)
            colr={'dim':(185,185,185),'strike':(200,120,120),'good':(30,140,70)}.get(st,DARK)
            tx=text_img(str(c),font(23,"Bold" if head else "SemiBold"),colr+(255,))
            im.alpha_composite(tx,(x0+(w-tx.width)//2,y+(rh-tx.height)//2))
            if st=='strike': d.line([x0+8,y+rh//2,x-8,y+rh//2],fill=RED+(255,),width=3)
            x=x0
    row(cols,None,y,True); y+=rh
    for i,r in enumerate(rows): row(r,styles[i] if styles else None,y); y+=rh
    return shadow(pad(im,16),8,(0,5),90)
RAW=[['דני','bamboo',8],['מיה','tea',5],['דני','bamboo',6],['נועם','bamboo',4],['מיה','bamboo',12],['רון','bamboo',3],['נועם','tea',7],['שיר','bamboo',11],['אור','bamboo',15],['רון','bamboo',2]]
C3=['לקוח','מוצר','כמות']; C2=['לקוח','סה"כ']
G=[['דני',14],['מיה',12],['נועם',4],['רון',5],['שיר',11],['אור',15]]
def states():
    S={}
    S[1]=table(C3,RAW,None,'orders')
    S[2]=table(C3,RAW,['strike' if r[1]=='tea' else None for r in RAW],'WHERE')
    S[3]=table(C2,G,None,'GROUP BY')
    S[4]=table(C2,G,['strike' if r[1]<=10 else None for r in G],'HAVING')
    H4=[r for r in G if r[1]>10]
    S[5]=table(C2,H4,None,'SELECT',hl_head=True)
    O=sorted(H4,key=lambda r:-r[1])
    S[6]=table(C2,O,None,'ORDER BY')
    S[7]=table(C2,O,['good','good','good','strike'],'LIMIT 3')
    return S
if __name__=='__main__':
    bg=Image.new('RGBA',(720,1280),CREAM+(255,))
    c=code_panel(2,done=(1,)); bg.alpha_composite(c,((720-c.width)//2,170))
    t=states()[2]; bg.alpha_composite(t,((720-t.width)//2,650))
    bg.convert('RGB').resize((360,640)).save('r7/prev.jpg')
