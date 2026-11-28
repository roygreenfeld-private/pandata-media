from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = '/home/claude/rubik.ttf'
TEAL = (31, 140, 128); TEAL2 = (43, 179, 163); DARK = (20, 60, 56); CREAM = (243, 237, 226)

def font(size, w='Bold'):
    f = ImageFont.truetype(FONT, size); f.set_variation_by_name(w); return f

def measure(t, f, stroke=0):
    d = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    b = d.textbbox((0, 0), t, font=f, direction='rtl', stroke_width=stroke)
    return b

def split(t):
    if '=' in t:
        a, b = t.split('=', 1); return a.strip(), b.strip()
    return None, t

def shadow(im, r=10, off=(0, 6), a=110):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    alpha = im.split()[3].point(lambda v: min(a, v))
    sh.putalpha(alpha); sh = Image.composite(Image.new('RGBA', im.size, (0, 0, 0, 255)), sh, alpha)
    sh.putalpha(alpha); sh = sh.filter(ImageFilter.GaussianBlur(r))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh, off); out.alpha_composite(im); return out

def pad(im, p=30):
    o = Image.new('RGBA', (im.width + 2*p, im.height + 2*p), (0, 0, 0, 0)); o.alpha_composite(im, (p, p)); return o

def text_img(t, f, fill, stroke=0, sfill=None):
    x0, y0, x1, y1 = measure(t, f, stroke)
    im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-x0, -y0), t, font=f, fill=fill, direction='rtl', stroke_width=stroke, stroke_fill=sfill)
    return im

# A: dark glass pill, keyword in bright teal chip
def style_a(t):
    k, rest = split(t); f = font(40, 'SemiBold'); fk = font(40, 'Bold')
    body = text_img(rest, f, (255, 255, 255, 255))
    parts = [body]
    if k:
        ki = text_img(k, fk, (255, 255, 255, 255))
        chip = Image.new('RGBA', (ki.width + 36, ki.height + 24), (0, 0, 0, 0))
        ImageDraw.Draw(chip).rounded_rectangle([0, 0, chip.width-1, chip.height-1], 16, fill=TEAL2 + (255,))
        chip.alpha_composite(ki, (18, 12)); parts = [body, chip]  # rtl: chip on the right
    gap = 18; h = max(p.height for p in parts) + 36; w = sum(p.width for p in parts) + gap*(len(parts)-1) + 52
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w-1, h-1], h//2 if not k else 26, fill=DARK + (215,))
    x = 26
    for p in parts:
        im.alpha_composite(p, (x, (h - p.height)//2)); x += p.width + gap
    return shadow(pad(im))

# B: no box, white bold text, dark teal outline + soft shadow
def style_b(t):
    k, rest = split(t); f = font(54, 'ExtraBold')
    if k:
        a = text_img(k, font(44, 'Bold'), TEAL2 + (255,), 6, DARK + (255,))
        b = text_img(rest, f, (255, 255, 255, 255), 7, DARK + (255,))
        w = max(a.width, b.width); im = Image.new('RGBA', (w, a.height + b.height + 10), (0, 0, 0, 0))
        im.alpha_composite(a, ((w-a.width)//2, 0)); im.alpha_composite(b, ((w-b.width)//2, a.height + 10))
    else:
        im = text_img(t, f, (255, 255, 255, 255), 7, DARK + (255,))
    return shadow(pad(im), 8, (0, 5), 140)

# C: yellow sticky note, slight tilt, tape
def style_c(t):
    k, rest = split(t); f = font(44, 'Bold')
    lines = [text_img(k, font(32, 'Medium'), TEAL + (255,)), text_img(rest, f, DARK + (255,))] if k else [text_img(t, f, DARK + (255,))]
    w = max(l.width for l in lines) + 64; h = sum(l.height for l in lines) + 14*(len(lines)-1) + 60
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=(255, 226, 110, 255))
    d.polygon([(w-34, h), (w, h-34), (w, h)], fill=(232, 196, 70, 255))  # folded corner
    y = 30
    for l in lines:
        im.alpha_composite(l, ((w - l.width)//2, y)); y += l.height + 14
    im = pad(im, 40)
    tape = Image.new('RGBA', (110, 34), (255, 255, 255, 150)); im.alpha_composite(tape, ((im.width-110)//2, 24))
    im = im.rotate(-2.5, resample=Image.BICUBIC, expand=True)
    return shadow(im, 9, (4, 8), 120)

# D: lower-third: teal term chip + cream definition bar, right aligned
def style_d(t):
    k, rest = split(t)
    top = text_img(k or rest, font(46, 'Bold'), (255, 255, 255, 255))
    chip = Image.new('RGBA', (top.width + 40, top.height + 26), TEAL + (255,)); chip.alpha_composite(top, (20, 13))
    if not k:
        return shadow(pad(chip), 8, (0, 4), 100)
    bt = text_img(rest, font(54, 'Bold'), DARK + (255,))
    bar = Image.new('RGBA', (bt.width + 44, bt.height + 30), CREAM + (245,)); bar.alpha_composite(bt, (22, 15))
    ImageDraw.Draw(bar).rectangle([bar.width-8, 0, bar.width, bar.height], fill=TEAL2 + (255,))
    w = max(chip.width, bar.width); im = Image.new('RGBA', (w, chip.height + bar.height), (0, 0, 0, 0))
    im.alpha_composite(chip, (w - chip.width, 0)); im.alpha_composite(bar, (w - bar.width, chip.height))
    return shadow(pad(im), 8, (0, 4), 100)

STYLES = {'A': style_a, 'B': style_b, 'C': style_c, 'D': style_d}
# placement (x anchor, y) on a 720x1280 frame; D sits right-aligned around 60% height (clear of IG bottom UI)
def place(style, im, W=720, H=1280):
    if style == 'D': return (max(0, W - 120 - im.width), int(H*0.52))
    return ((W - im.width)//2, 110)
