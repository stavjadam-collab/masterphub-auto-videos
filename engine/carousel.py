#!/usr/bin/env python3
"""Masterphub auto carousels: turn a job (github_daily / blog) into 1080x1350 branded slides.
Usage (test): python carousel.py job.json outdir
"""
import html, json, os, re, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
BG, GOLD, GOLD2 = (14, 12, 10), (245, 180, 40), (255, 210, 110)
WHITE, GREY, CARD = (245, 240, 230), (170, 160, 145), (32, 27, 20)
M = 70  # side margin
CACHE = os.path.expanduser('~/.cache/explainer-video')
INTER = 'https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf'
LOGO = 'https://masterphub.io/masterphub-logo-transparent.png'

def _font_file():
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, 'inter.ttf')
    if not os.path.exists(p):
        try: urllib.request.urlretrieve(INTER, p)
        except Exception: return None
    return p

_FF = None
def font(size, wght=400):
    global _FF
    if _FF is None: _FF = _font_file() or ''
    if not _FF:
        for p in (['/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'] if wght >= 700 else ['/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'] if wght >= 600 else ['/usr/share/fonts/opentype/inter/Inter-Regular.otf']):
            if os.path.exists(p): return ImageFont.truetype(p, size)
        return ImageFont.truetype('DejaVuSans-Bold.ttf' if wght >= 600 else 'DejaVuSans.ttf', size)
    f = ImageFont.truetype(_FF, size)
    try:
        axes = f.get_variation_axes()
        f.set_variation_by_axes([wght if 'eight' in str(a.get('name')) or 'wght' in str(a.get('name')) else min(max(32, a['minimum']), a['maximum']) for a in axes])
    except Exception:
        pass
    return f

def fetch(url, path):
    if url and not os.path.exists(path):
        try: urllib.request.urlretrieve(url, path)
        except Exception: return None
    return path if url and os.path.exists(path) else None

def clean(t):
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))
    t = re.sub(r'[*_#`>]+', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def sentences(text, n=3, lo=6, hi=34):
    out = []
    for s in re.split(r'(?<=[.!?])\s+', clean(text)):
        w = len(s.split())
        if lo <= w <= hi and '|' not in s and not s.endswith('...') and not re.match(r'(However|But|This|That|These|Those|It|They|And|So|Also|Below|Here|TL;DR|Note)\b', s) and ':' not in s[:25]:
            out.append(s)
        if len(out) == n: break
    return out

def kfmt(n):
    try: n = int(n)
    except Exception: return ''
    return f'{n / 1000:.0f}K' if n >= 1000 else str(n)

class Deck:
    def __init__(self, logo_path):
        lg = Image.open(logo_path).convert('RGBA') if logo_path else None
        if lg:
            lg = lg.crop(lg.getbbox()); lg.thumbnail((150, 150))
        self.logo = lg
        glow = Image.new('RGB', (W, H), BG)
        g = ImageDraw.Draw(glow)
        g.ellipse((W - 520, -320, W + 320, 480), fill=(90, 60, 10))
        g.ellipse((-400, H - 380, 360, H + 380), fill=(55, 38, 8))
        self.bg = Image.blend(Image.new('RGB', (W, H), BG), glow.filter(ImageFilter.GaussianBlur(160)), 0.9)

    def base(self, i, n):
        im = self.bg.copy(); d = ImageDraw.Draw(im)
        lh = 150
        if self.logo:
            im.paste(self.logo, (M, 60), self.logo); lh = self.logo.height
            d.text((M + self.logo.width + 20, 60 + lh // 2), 'Masterphub', font=font(40, 800), fill=WHITE, anchor='lm')
        d.text((W - M, 60 + lh // 2), f'{i}/{n}', font=font(34, 600), fill=GREY, anchor='rm')
        d.rounded_rectangle((M, H - 90, W - M, H - 82), 4, fill=(45, 38, 28))
        d.rounded_rectangle((M, H - 90, M + (W - 2 * M) * i // n, H - 82), 4, fill=GOLD)
        d.text((M, H - 130), 'masterphub.io', font=font(30, 600), fill=GREY, anchor='ls')
        if i < n: d.text((W - M, H - 130), 'Swipe  →', font=font(30, 600), fill=GOLD, anchor='rs')
        return im, d

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split('\n'):
        cur = ''
        for w in para.split(' '):
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=f) <= maxw or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def fit(d, text, maxw, maxh, start, stop, wght, gap=1.18):
    """Largest font size (start..stop) whose wrapped text fits in maxw x maxh."""
    for s in range(start, stop - 1, -4):
        f = font(s, wght); ls = wrap(d, text, f, maxw)
        if len(ls) * s * gap <= maxh and not (len(ls) > 1 and len(ls[-1].split()) == 1 and s > stop): return f, ls
    f = font(stop, wght); return f, wrap(d, text, f, maxw)

def draw_lines(d, y, lines, f, color, gap=1.18):
    for ln in lines:
        d.text((M, y), ln, font=f, fill=color); y += int(f.size * gap)
    return y

def tag(d, y, text):
    f = font(30, 600); w = d.textlength(text, font=f)
    d.rounded_rectangle((M, y, M + w + 44, y + 58), 29, outline=GOLD, width=3)
    d.text((M + 22, y + 29), text, font=f, fill=GOLD, anchor='lm')
    return y + 100

def paste_photo(im, path, y, maxh):
    try: ph = Image.open(path).convert('RGB')
    except Exception: return y
    pw = W - 2 * M
    ph = ph.resize((pw, max(1, int(ph.height * pw / ph.width))))
    if ph.height > maxh:
        top = (ph.height - maxh) // 2; ph = ph.crop((0, top, pw, top + maxh))
    mk = Image.new('L', ph.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, ph.width, ph.height), 28, fill=255)
    im.paste(ph, (M, y), mk)
    return y + ph.height

BOTTOM = H - 170  # content must end above the footer

def slide_text(deck, i, n, label, head, body='', accent='', photo=None):
    im, d = deck.base(i, n)
    if not photo:
        # measure, then center the block between header and footer
        hf, hl = fit(d, head, W - 2 * M, 520, 80, 48, 800)
        h = 100 + len(hl) * int(hf.size * 1.18)
        bf = bl = None
        if body:
            bf, bl = fit(d, body, W - 2 * M, BOTTOM - 260 - h - 40, 46, 32, 400, 1.3)
            h += 40 + len(bl) * int(bf.size * 1.3)
        y = max(260, 230 + (BOTTOM - 230 - h) // 2)
        y = tag(d, y, label)
        y = draw_lines(d, y, hl, hf, WHITE)
        d.rounded_rectangle((M, y + 14, M + 90, y + 22), 4, fill=GOLD)
        if bl: draw_lines(d, y + 50, bl, bf, GREY, 1.3)
        return im
    y = tag(d, 260, label)
    room = BOTTOM - y
    ph_h = 0
    if photo: ph_h = 420 if body else 520
    hf, hl = fit(d, head, W - 2 * M, min(360, room - ph_h - 40), 92, 52, 800)
    y = draw_lines(d, y, hl, hf, WHITE)
    if accent:
        af, al = fit(d, accent, W - 2 * M, 200, 92, 52, 800)
        y = draw_lines(d, y, al, af, GOLD)
    if body:
        y += 30
        bf, bl = fit(d, body, W - 2 * M, max(120, BOTTOM - y - ph_h - (40 if photo else 0)), 44, 30, 400, 1.3)
        y = draw_lines(d, y, bl, bf, GREY, 1.3)
    if photo:
        y += 40; paste_photo(im, photo, y, min(ph_h, BOTTOM - y))
    return im

def slide_cta(deck, i, n, label, head, sub, button, photo=None):
    im, d = deck.base(i, n)
    y = tag(d, 260, label)
    hf, hl = fit(d, head, W - 2 * M, 260, 84, 52, 800)
    y = draw_lines(d, y, hl, hf, WHITE) + 10
    sf, sl = fit(d, sub, W - 2 * M, 130, 42, 30, 400, 1.3)
    y = draw_lines(d, y, sl, sf, GREY, 1.3) + 40
    btn_y = BOTTOM - 130
    if photo: paste_photo(im, photo, y, max(0, btn_y - 30 - y))
    bf = font(50, 800)
    while d.textlength(button, font=bf) > W - 2 * M - 80 and bf.size > 30: bf = font(bf.size - 4, 800)
    d.rounded_rectangle((M, btn_y, W - M, btn_y + 120), 60, fill=GOLD)
    d.text((W // 2, btn_y + 60), button, font=bf, fill=BG, anchor='mm')
    return im

def plan_github(src):
    name = src['repo'].split('/')[-1]; stars = kfmt(src.get('stars'))
    what = (sentences(src.get('what'), 2, 4, 40) or [clean(src.get('what'))])
    why = (sentences(src.get('why'), 2, 4, 40) or [clean(src.get('why'))])
    how = (sentences(src.get('how'), 2, 3, 40) or [clean(src.get('how'))])
    s = [('text', 'GITHUB REPO OF THE DAY', name, (f'{stars} stars on GitHub. ' if stars else '') + src['repo'], '', 'image'),
         ('text', 'WHAT IT IS', what[0], ' '.join(what[1:2]), '', None),
         ('text', 'WHY IT MATTERS', why[0], ' '.join(why[1:2]), '', None),
         ('text', 'HOW TO USE IT', how[0], ' '.join(how[1:2]), '', None),
         ('cta', 'GET IT FREE', 'Full review + skill download', 'Free on Masterphub, every day a new repo.', 'masterphub.io/github', 'image')]
    return s

def plan_blog(src):
    body = sentences(src.get('content') or src.get('excerpt'), 6)
    ex = (sentences(src.get('excerpt'), 1, 5, 40) or [''])[0]
    s = [('text', 'NEW ON THE BLOG', src['title'], ex, '', 'image')]
    pairs = [body[k:k + 2] for k in range(0, min(len(body), 6), 2)]
    for lab, b in zip(['THE IDEA', 'WHY IT WORKS', 'TRY THIS'], pairs):
        s.append(('text', lab, b[0], ' '.join(b[1:]), '', None))
    s.append(('cta', 'READ THE FULL GUIDE', 'Free on Masterphub', src['title'], 'masterphub.io/blog', 'image'))
    return s

def build(job, outdir='.'):
    kind, src = job['type'], job['src']
    os.makedirs(outdir, exist_ok=True)
    deck = Deck(fetch(LOGO, os.path.join(outdir, '_logo.png')))
    img = None
    if src.get('image'):
        img = fetch(src['image'], os.path.join(outdir, '_cover' + os.path.splitext(src['image'].split('?')[0])[1][:5]))
    plan = plan_github(src) if kind == 'github_daily' else plan_blog(src)
    plan = [p for p in plan if p[0] == 'cta' or p[2]]
    n = len(plan); paths = []
    for i, (t, lab, head, body, accent, ph) in enumerate(plan, 1):
        photo = img if ph == 'image' else None
        im = slide_cta(deck, i, n, lab, head, body, accent, photo) if t == 'cta' else slide_text(deck, i, n, lab, head, body, accent, photo)
        p = os.path.join(outdir, f"{job.get('job_id', 'test')}-{i}.png")
        im.save(p, optimize=True); paths.append(p)
    return paths

if __name__ == '__main__':
    print(build(json.load(open(sys.argv[1])), sys.argv[2] if len(sys.argv) > 2 else 'out'))
