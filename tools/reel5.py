import subprocess, sys, os, json
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude')
from titles import style_b, font, text_img, shadow, pad, TEAL, TEAL2, DARK, CREAM
W, H = 720, 1280
RED = (220, 60, 60); GREEN = (46, 170, 90)
OUT = '/home/claude/r5'; os.makedirs(OUT, exist_ok=True)
U = '/mnt/user-data/uploads/'
AUD = [U+'e151cfeb-ElevenLabs_2026-11-25T11_08_36_Nimrod_-_Warm__Confident_pvc_s50_sim75_v4.mp3',
       U+'48667604-ElevenLabs_2026-11-25T11_22_49_Nimrod_-_Warm__Confident_pvc_s50_sim75_v4.mp3',
       U+'c84885ba-ElevenLabs_2026-11-25T11_24_32_Nimrod_-_Warm__Confident_pvc_s50_sim75_v4.mp3']
VID = sys.argv[1:4]

def icon(kind, s=44):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == 'x':
        d.ellipse([0, 0, s-1, s-1], fill=RED+(255,)); m = s*0.3
        d.line([m, m, s-m, s-m], fill='white', width=6); d.line([m, s-m, s-m, m], fill='white', width=6)
    elif kind == 'v':
        d.ellipse([0, 0, s-1, s-1], fill=GREEN+(255,))
        d.line([s*.27, s*.52, s*.44, s*.7, s*.75, s*.32], fill='white', width=6, joint='curve')
    elif kind == 'arrow':  # pointing left (RTL flow)
        d.polygon([(0, s/2), (s*.55, s*.1), (s*.55, s*.35), (s, s*.35), (s, s*.65), (s*.55, s*.65), (s*.55, s*.9)], fill=TEAL2+(255,))
    return im

def card(rows, w=None, border=TEAL):
    """rows: list of lists of RGBA parts laid out right-to-left"""
    lines = []
    for parts in rows:
        lw = sum(p.width for p in parts) + 14*(len(parts)-1); lh = max(p.height for p in parts)
        l = Image.new('RGBA', (lw, lh), (0, 0, 0, 0)); x = lw
        for p in parts:
            x -= p.width; l.alpha_composite(p, (x, (lh-p.height)//2)); x -= 14
        lines.append(l)
    cw = w or max(l.width for l in lines) + 60; ch = sum(l.height for l in lines) + 22*(len(lines)-1) + 50
    im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, cw-1, ch-1], 26, fill=CREAM+(250,), outline=border+(255,), width=5)
    y = 25
    for l in lines:
        im.alpha_composite(l, (cw - 30 - l.width, y)); y += l.height + 22
    return shadow(pad(im))

def T(t, size=40, w='Bold', c=DARK): return text_img(t, font(size, w), c+(255,))

def stamp(t, c):
    tx = text_img(t, font(64, 'ExtraBold'), c+(255,))
    im = Image.new('RGBA', (tx.width+50, tx.height+36), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width-1, im.height-1], 14, outline=c+(255,), width=7, fill=(255, 255, 255, 200))
    im.alpha_composite(tx, (25, 18)); return shadow(pad(im.rotate(-8, expand=True, resample=Image.BICUBIC)))

def title(t):
    im = style_b(t)
    if im.width > W-20: im = im.resize((W-20, int(im.height*(W-20)/im.width)), Image.LANCZOS)
    return im

def ctr(im, y): return ((W-im.width)//2, y)

def chips(words, hi=None):
    ps = []
    for i, wd in enumerate(words):
        tx = T(wd, 38, 'Bold', (255, 255, 255))
        c = Image.new('RGBA', (tx.width+36, tx.height+26), (0, 0, 0, 0))
        ImageDraw.Draw(c).rounded_rectangle([0, 0, c.width-1, c.height-1], 18, fill=(TEAL2 if i == hi else TEAL)+(255,))
        c.alpha_composite(tx, (18, 13)); ps.append(c)
    w = sum(p.width for p in ps) + 16*(len(ps)-1); im = Image.new('RGBA', (w, ps[0].height), (0, 0, 0, 0)); x = w
    for p in ps: x -= p.width; im.alpha_composite(p, (x, 0)); x -= 16
    return shadow(pad(im))

# overlays per segment: (image, start, end, (x,y))
S1, S2, S3 = [], [], []
oc = card([[T('הזמנה חדשה', 34, 'Medium', TEAL)], [T('במבוק × 3', 42)], [T('כתובת:', 42), T('ליד הבית של דני', 42, 'ExtraBold', RED)]])
S1 += [(oc, 0.3, 6.5, (20, 420))]
S1 += [(title('ולידציה = בדיקה לפני שימוש'), 13.1, 22.7, 'top')]
chk1 = card([[icon('x'), T('רחוב', 44)]], w=320); chk2 = card([[icon('x'), T('מספר בית', 44)]], w=320)
S1 += [(chk1, 18.0, 22.7, (W-360, 330)), (chk2, 19.3, 22.7, (W-360, 450))]
S1 += [(stamp('נעצר', RED), 20.6, 22.7, (50, 360))]

S2 += [(card([[icon('v'), T('הכתובת תקינה', 42)]]), 0.2, 3.4, None)]
S2 += [(chips(['אשראי']), 6.8, 12.6, (490, 300)), (chips(['משלוחים']), 7.3, 12.6, (40, 400)), (chips(['מלאי']), 7.8, 12.6, (500, 640))]
S2 += [(title('אינטגרציה = מערכות שמדברות'), 12.8, 21.55, 'top')]
f1 = card([[icon('v'), T('תשלום אושר', 40)]]); f2 = card([[icon('v'), T('משלוח הוזמן', 40)]]); f3 = card([[icon('v'), T('מלאי עודכן', 40)]])
S2 += [(f1, 16.4, 21.55, (W-f1.width-10, 480)), (f2, 18.4, 21.55, (W-f2.width-10, 590)), (f3, 19.5, 21.55, (W-f3.width-10, 700))]

q = text_img('?', font(260, 'ExtraBold'), (255, 255, 255, 255), 12, DARK+(255,)); q = shadow(pad(q))
S3 += [(q, 0.3, 6.4, None)]
S3 += [(title('אוטומציה = רץ לבד'), 7.0, 14.2, 'top')]
rule = card([[T('תנאי:', 38, 'Medium', TEAL), T('נכנסה הזמנה', 40)], [T('פעולה:', 38, 'Medium', TEAL), T('הכל רץ מעצמו', 40)]])
S3 += [(rule, 8.6, 14.2, None)]
for i, t in enumerate(range(11, 20)):
    cnt = card([[T('הזמנות היום:', 38, 'Medium', TEAL), T(str(t), 46, 'ExtraBold')]])
    S3 += [(cnt, 11.2 + i*0.55, 11.2 + (i+1)*0.55 if i < 8 else 14.2, 'cnt')]
S3 += [(chips(['ולידציה', 'אינטגרציה', 'אוטומציה']), 19.0, 22.6, None)]

def build(i, vid, aud, ovs):
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', aud]))
    ins = ['-i', vid, '-i', aud]; fc = [f"[0:v]fps=24,scale={W}:{H},tpad=stop_mode=clone:stop_duration=5,trim=0:{dur:.3f},setpts=PTS-STARTPTS,format=yuv420p[b]"]
    prev = 'b'
    for j, (im, s, e, pos) in enumerate(ovs):
        if pos is None: pos = ctr(im, 330)
        elif pos == 'top': pos = ctr(im, 100)
        fd = 0.01 if (isinstance(pos,tuple) and pos[0] is None) else 0.2
        p = f'{OUT}/s{i}_{j}.png'; im.save(p)
        if pos == 'cnt': pos = ctr(im, 560)
        elif pos == 'low': pos = ctr(im, int(H*0.6))
        elif isinstance(pos,tuple) and pos[0] is None: pos = ctr(im, 900)
        ins += ['-loop', '1', '-framerate', '24', '-t', f'{dur:.3f}', '-i', p]
        fc.append(f"[{2+j}:v]format=rgba,fade=in:st={s}:d={fd}:alpha=1,fade=out:st={max(s, e-fd):.2f}:d={fd}:alpha=1[t{j}]")
        fc.append(f"[{prev}][t{j}]overlay={pos[0]}:{pos[1]}[o{j}]"); prev = f'o{j}'
    out = f'{OUT}/seg{i}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', f'[{prev}]', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', f'{dur:.3f}', out], check=True)
    return out

from captions import timed5
TX=["לקוח הזמין במבוק מהחנות של פנדאטה, ובשדה הכתובת כתב: ליד הבית של דני. אבל השליח לא יודע מי זה דני. ולכן לפני שההזמנה ממשיכה, המערכת בודקת אותה. זו ולידציה: בדיקה שהמידע תקין לפני שמשתמשים בו. חסרים רחוב ומספר בית, ולכן ההזמנה נעצרת עד שהלקוח מתקן.",
"עכשיו הכתובת תקינה, אבל ההזמנה צריכה לעבור בין שלוש מערכות שלא מכירות זו את זו: חברת האשראי, חברת השליחויות, והמלאי של פנדאטה. לכן מחברים ביניהן. זו אינטגרציה: חיבור בין מערכות שונות, כך שיעבירו מידע ויעבדו יחד. ברגע שהתשלום מאושר, המשלוח מוזמן, והמלאי מתעדכן.",
"ומי לוחץ על כל הכפתורים האלה, בכל הזמנה מחדש? אף אחד. זו אוטומציה: משימה שרצה לבד בכל פעם שמתקיים תנאי. כל הזמנה חדשה מפעילה את התהליך מעצמה, ופנדאטה בינתיים פנוי לדבר החשוב באמת: לאכול במבוק. שלוש מילים, הזמנה אחת. שמרו את זה."]
for S,t,a in zip([S1,S2,S3],TX,AUD):
    for st,en,c in timed5(t,a):
        S.append((title(c),st,en,(None,'cap')))
if __name__ == '__main__':
    segs = []
    for i, ovs in enumerate([S1, S2, S3]):
        segs.append(build(i+1, VID[i], AUD[i], ovs))
    lst = f'{OUT}/list.txt'; open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', '/home/claude/pandata_reel05_vai.mp4'], check=True)
    print('done')
