"""Generic Pandata reel builder.

Usage: python3 reelkit.py spec.json
Spec keys:
  audio, out                      paths
  intro_clip, outro_clip          Pandata clips (mouth closed), shown at start/end only
  intro_lines, outro_lines        how many narration lines play over the intro / outro clip
  lines: [{text, heading?, visual?}]   one entry per narration sentence, in order
     visual types: steps{labels,active,icons?} table{title,cols,rows,styles?}
                   code{lines:[[text,ok]]} chips{items:[[icon,name]]} card{lines}
  end_card: [lines]               text shown over the outro clip
"""
import sys, json, re, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from titles import style_b, font, text_img, shadow, pad, TEAL, TEAL2, DARK, CREAM
from captions import speech, chunks

W, H = 720, 1280
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
SYMF = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
RED = (220, 60, 60); GREEN = (46, 170, 90)


def title(t):
    im = style_b(t)
    if im.width > W - 20: im = im.resize((W - 20, int(im.height * (W - 20) / im.width)), Image.LANCZOS)
    return im


def fit(im, maxw=W - 30):
    return im if im.width <= maxw else im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)


# ---------- visuals ----------
def v_steps(labels, active=None, icons=None):
    icons = icons or ['⛁'] * len(labels)
    S = 190; gap = 34
    w = len(labels) * S + (len(labels) - 1) * gap; h = S + 70
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sf = ImageFont.truetype(SYMF, 92)
    x = w
    for i, (lab, ic) in enumerate(zip(labels, icons)):
        x0 = x - S; on = active is None or i == active; done = active is not None and i < active
        fill = TEAL if on else ((200, 230, 225) if done else (235, 235, 232))
        d.rounded_rectangle([x0, 0, x, S], 34, fill=fill + (255,), outline=TEAL + (255,), width=4)
        bb = d.textbbox((0, 0), ic, font=sf)
        d.text((x0 + S / 2 - (bb[2] - bb[0]) / 2 - bb[0], S / 2 - (bb[3] - bb[1]) / 2 - bb[1]), ic, font=sf,
               fill=(255, 255, 255) if on else DARK)
        t = text_img(lab, font(40, 'Bold'), DARK + (255,))
        if t.width > S + 30: t = t.resize((S + 30, int(t.height * (S + 30) / t.width)))
        im.alpha_composite(t, (int(x0 + S / 2 - t.width / 2), S + 12))
        if i < len(labels) - 1:  # arrow pointing left (RTL flow)
            ax = x0 - gap / 2; ay = S / 2
            d.polygon([(ax - 18, ay), (ax + 8, ay - 20), (ax + 8, ay + 20)], fill=TEAL2 + (255,))
        x = x0 - gap
    return shadow(pad(im, 20), 8, (0, 5), 90)


def v_table(title_, cols, rows, styles=None):
    rh = 64; n = len(cols); cw = [int(650 / n)] * n
    Wt = sum(cw) + 30; Ht = 62 + rh * (len(rows) + 1) + 14
    im = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, Wt - 1, Ht - 1], 20, fill=(255, 255, 255, 245), outline=TEAL + (255,), width=4)
    t = text_img(title_, font(36, 'Bold'), TEAL + (255,)); im.alpha_composite(t, (Wt - 18 - t.width, 12))
    y = 62

    def row(cells, st, y, head=False):
        x = Wt - 15
        for c, w in zip(cells, cw):
            x0 = x - w
            fill = (235, 244, 242) if head else {'strike': (252, 228, 228), 'good': (214, 245, 224), 'dim': (245, 245, 245)}.get(st, (255, 255, 255))
            d.rectangle([x0, y, x, y + rh], fill=fill, outline=(205, 218, 215), width=2)
            colr = {'strike': (200, 120, 120), 'good': (30, 140, 70), 'dim': (185, 185, 185)}.get(st, DARK)
            tx = text_img(str(c), font(32, 'Bold' if head else 'SemiBold'), colr + (255,))
            if tx.width > w - 10: tx = tx.resize((w - 10, int(tx.height * (w - 10) / tx.width)))
            im.alpha_composite(tx, (x0 + (w - tx.width) // 2, y + (rh - tx.height) // 2))
            if st == 'strike': d.line([x0 + 8, y + rh // 2, x - 8, y + rh // 2], fill=RED + (255,), width=3)
            x = x0
    row(cols, None, y, True); y += rh
    for i, r in enumerate(rows):
        row(r, (styles or [None] * len(rows))[i], y); y += rh
    return shadow(pad(im, 16), 8, (0, 5), 90)


def v_code(lines):
    dd = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    sz = 34
    while sz > 16 and max(dd.textlength(t, font=ImageFont.truetype(MONO, sz)) for t, _ in lines) > 620: sz -= 1
    f = ImageFont.truetype(MONO, sz); lh = int(sz * 1.8)
    w = int(max(dd.textlength(t, font=f) for t, _ in lines) + 60)
    h = 46 + lh * len(lines) + 16
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=(24, 40, 38, 245))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): d.ellipse([18 + i * 24, 14, 32 + i * 24, 28], fill=c)
    y = 44
    for t, ok in lines:
        col = (140, 230, 160) if ok is True else ((255, 120, 110) if ok is False else (235, 245, 243))
        d.text((30, y + 8), t, font=f, fill=col); y += lh
    return shadow(pad(im, 20), 10, (0, 6), 120)


def v_chips(items):
    sf = ImageFont.truetype(SYMF, 38); cs = []
    for ic, name in items:
        t = text_img(name, font(42, 'Bold'), DARK + (255,)); hh = t.height + 30
        dd = ImageDraw.Draw(Image.new('RGB', (1, 1))); bb = dd.textbbox((0, 0), ic, font=sf); iw = bb[2] - bb[0]
        w = t.width + hh + 34
        c = Image.new('RGBA', (w, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rounded_rectangle([0, 0, w - 1, hh - 1], hh // 2, fill=(255, 255, 255, 245), outline=TEAL + (255,), width=3)
        r = hh - 14; d.ellipse([w - 7 - r, 7, w - 7, 7 + r], fill=TEAL + (255,))
        d.text((w - 7 - r / 2 - iw / 2 - bb[0], 7 + r / 2 - (bb[3] - bb[1]) / 2 - bb[1]), ic, font=sf, fill=(255, 255, 255))
        c.alpha_composite(t, (18, (hh - t.height) // 2)); cs.append(c)
    gap = 14; w = sum(c.width for c in cs) + gap * (len(cs) - 1); hh = max(c.height for c in cs)
    o = Image.new('RGBA', (w, hh), (0, 0, 0, 0)); x = w
    for c in cs: x -= c.width; o.alpha_composite(c, (x, 0)); x -= gap
    return shadow(pad(fit(o, 660), 20), 8, (0, 6), 110)


def v_card(lines):
    ims = [text_img(l, font(46, 'Bold' if i == 0 else 'Medium'), DARK + (255,)) for i, l in enumerate(lines)]
    w = min(660, max(i.width for i in ims) + 70); h = sum(i.height + 14 for i in ims) + 50
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(255, 255, 255, 245), outline=TEAL + (255,), width=5)
    y = 25
    for i in ims:
        i = fit(i, w - 40); c.alpha_composite(i, ((w - i.width) // 2, y)); y += i.height + 14
    return shadow(pad(c, 24), 10, (0, 8), 110)


def visual(v):
    t = v['type']
    if t == 'steps': return v_steps(v['labels'], v.get('active'), v.get('icons'))
    if t == 'table': return v_table(v.get('title', ''), v['cols'], v['rows'], v.get('styles'))
    if t == 'code': return v_code(v['lines'])
    if t == 'chips': return v_chips(v['items'])
    if t == 'card': return v_card(v['lines'])
    raise ValueError(t)


# ---------- timing ----------
def timed_lines(texts, audio):
    sp, dur = speech(audio)
    L = [len(t.replace(' ', '')) + 1 for t in texts]; tot = sum(b - a for a, b in sp); r = sum(L) / tot
    n, m = len(texts), len(sp); INF = 1e18
    dp = [[INF] * (m + 1) for _ in range(n + 1)]; bk = [[None] * (m + 1) for _ in range(n + 1)]; dp[0][0] = 0
    for i in range(n + 1):
        for k in range(m + 1):
            if dp[i][k] >= INF: continue
            for b in range(1, 6):
                if i + 1 > n or k + b > m: continue
                c = L[i] / r; d = sum(e - s for s, e in sp[k:k + b])
                cost = dp[i][k] + (c - d) ** 2 / (d + 0.5) + 0.1 * (b - 1)
                if cost < dp[i + 1][k + b]: dp[i + 1][k + b] = cost; bk[i + 1][k + b] = b
    if dp[n][m] >= INF:  # fewer pauses than lines: fall back to proportional split
        out = []; cum = 0
        for l in L: s = cum / sum(L) * dur; cum += l; out.append((s, cum / sum(L) * dur))
        spans = out
    else:
        i, k = n, m; blocks = []
        while i > 0: b = bk[i][k]; blocks.append((k - b, k)); i -= 1; k -= b
        blocks.reverse(); spans = [(sp[a][0], sp[b - 1][1]) for a, b in blocks]
    res = []
    for idx, (t, (s, e)) in enumerate(zip(texts, spans)):
        s0 = 0 if idx == 0 else max(0, s - 0.08)
        e0 = spans[idx + 1][0] - 0.08 if idx + 1 < len(spans) else dur
        cs = chunks(t); cl = [len(c.replace(' ', '')) + 1 for c in cs]; ct = sum(cl); cum = 0; caps = []
        for c, l in zip(cs, cl):
            a = s + (e - s) * cum / ct; cum += l; caps.append([round(max(s0, a - 0.05), 2), 0, c])
        for q in range(len(caps) - 1): caps[q][1] = caps[q + 1][0]
        caps[-1][1] = round(e0, 2); caps[0][0] = round(s0, 2)
        res.append((round(s0, 2), round(e0, 2), caps))
    return res, dur


# ---------- build ----------
def build(spec):
    work = spec['out'] + '_work'; os.makedirs(work, exist_ok=True)
    lines = spec['lines']; texts = [re.sub(r'\[[^\]]+\]\s*', '', l['text']) for l in lines]
    spans, dur = timed_lines(texts, spec['audio'])
    ni, no = spec.get('intro_lines', 1), spec.get('outro_lines', 1)
    T0 = spans[ni][0] if ni < len(spans) else 3.0
    T1 = spans[len(spans) - no][0]; END = dur + 0.3
    ov = []
    def C(im, y): return ((W - im.width) // 2, y)
    cur_h = None; cur_v = None; cur_v2 = None
    mid = [(i, spans[i]) for i in range(ni, len(spans) - no)]
    for j, (i, (s, e, caps)) in enumerate(mid):
        l = lines[i]
        if l.get('heading'): cur_h = title(l['heading'])
        if l.get('visual'): cur_v = visual(l['visual'])
        if 'visual2' in l: cur_v2 = visual(l['visual2']) if l['visual2'] else None
        e2 = mid[j + 1][1][0] if j + 1 < len(mid) else T1
        if cur_h is not None: ov.append((cur_h, s, e2, C(cur_h, 40)))
        top = 170 if cur_h is not None else 60; bot = 1070
        stack = [v for v in (cur_v, cur_v2) if v is not None]
        tot = sum(v.height for v in stack) + 30 * (len(stack) - 1)
        vy = top + max(0, (bot - top - tot) // 2)
        for v in stack: ov.append((v, s, e2, C(v, vy))); vy += v.height + 30
    for i, (s, e, caps) in enumerate(spans):
        for cs, ce, c in caps:
            im = title(c); y = 1090 if T0 <= cs < T1 else 900
            ov.append((im, cs, ce, C(im, y)))
    if spec.get('end_card'):
        parts = [text_img(t, font(46, 'ExtraBold'), (255, 255, 255, 255), 7, DARK + (255,)) for t in spec['end_card']]
        w = max(p.width for p in parts); fin = Image.new('RGBA', (w, sum(p.height + 10 for p in parts)), (0, 0, 0, 0)); yy = 0
        for p in parts: fin.alpha_composite(p, ((w - p.width) // 2, yy)); yy += p.height + 10
        fin = fit(shadow(pad(fin, 20), 8, (0, 5), 140)); ov.append((fin, T1, END, C(fin, 80)))
    Sf = "fps=24,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
    Image.new('RGB', (W, H), CREAM).save(f'{work}/bg.png')
    run = lambda c: subprocess.run(c, shell=True, check=True)
    run(f"ffmpeg -v error -y -i '{spec['intro_clip']}' -vf '{Sf},tpad=stop_mode=clone:stop_duration=20,trim=0:{T0:.3f},setpts=PTS-STARTPTS' -an {work}/p1.mp4")
    run(f"ffmpeg -v error -y -loop 1 -framerate 24 -t {T1 - T0:.3f} -i {work}/bg.png -vf 'format=yuv420p' {work}/p2.mp4")
    run(f"ffmpeg -v error -y -i '{spec['outro_clip']}' -vf '{Sf},tpad=stop_mode=clone:stop_duration=20,trim=0:{END - T1:.3f},setpts=PTS-STARTPTS' -an {work}/p3.mp4")
    open(f'{work}/l.txt', 'w').write("file 'p1.mp4'\nfile 'p2.mp4'\nfile 'p3.mp4'\n")
    run(f"ffmpeg -v error -y -f concat -safe 0 -i {work}/l.txt -c:v libx264 -preset veryfast -crf 19 {work}/base.mp4")
    ins = ['-i', f'{work}/base.mp4', '-i', spec['audio']]; fc = []; prev = '0:v'
    for j, (im, s, e, (x, y)) in enumerate(ov):
        fn = f'{work}/o{j}.png'; im.save(fn); ins += ['-i', fn]
        fc.append(f"[{prev}][{2 + j}:v]overlay={x}:{y}:enable='between(t,{s},{e - 0.01})'[o{j}]"); prev = f'o{j}'
    open(f'{work}/fc.txt', 'w').write(';'.join(fc))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex_script', f'{work}/fc.txt', '-map', f'[{prev}]', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-af', 'apad', '-t', f'{END}',
                    '-movflags', '+faststart', spec['out']], check=True)
    json.dump({'T0': T0, 'T1': T1, 'END': END, 'spans': spans}, open(f'{work}/timing.json', 'w'), ensure_ascii=False, indent=1)
    return END


def add_cover(video, cover, out):
    """Append the cover as a 0.2 s last frame; returns thumbnailOffset in ms for Buffer."""
    subprocess.run(f"ffmpeg -y -v error -i '{video}' -loop 1 -framerate 24 -t 0.2 -i '{cover}' -f lavfi -t 0.2 -i anullsrc=r=44100:cl=stereo "
                   f"-filter_complex \"[1:v]scale=720:1280,setsar=1,format=yuv420p[cv];[0:v]setsar=1,format=yuv420p[v0];[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];[v0][a0][cv][2:a]concat=n=2:v=1:a=1[v][a]\" "
                   f"-map '[v]' -map '[a]' -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 160k -movflags +faststart '{out}'", shell=True, check=True)
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out]))
    return int(d * 1000) - 120


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    print('END', build(spec))
