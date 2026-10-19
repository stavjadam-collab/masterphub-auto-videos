#!/usr/bin/env python3
"""Build a vertical (1080x1920) explainer video from a JSON spec:
AI voiceover (edge-tts) + animated branded scenes (Pillow) + captions, joined with ffmpeg.
Usage: python make_video.py spec.json out.mp4
"""
import json, math, os, subprocess, sys, tempfile, shutil, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

W, H, FPS = 1080, 1920, 30
CACHE = os.path.expanduser('~/.cache/explainer-video')
FONT_URLS = {
    'heebo': 'https://github.com/google/fonts/raw/main/ofl/heebo/Heebo%5Bwght%5D.ttf',
    'anton': 'https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf',
    'caveat': 'https://github.com/google/fonts/raw/main/ofl/caveat/Caveat%5Bwght%5D.ttf',
    'inter': 'https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf',
}
VOICES = {'he': 'he-IL-HilaNeural', 'en': 'en-US-AvaNeural'}

def font_path(name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name + '.ttf')
    if not os.path.exists(p):
        try: urllib.request.urlretrieve(FONT_URLS[name], p)
        except Exception: return None
    return p

def load_font(name, size, wght=None):
    p = font_path(name)
    if not p: return ImageFont.truetype('DejaVuSans-Bold.ttf', size)
    f = ImageFont.truetype(p, size)
    if wght:
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([wght if any(k in str(a.get('name')).lower() for k in ('weight', 'wght')) else min(max(32, a['minimum']), a['maximum']) for a in axes])
        except Exception:
            try: f.set_variation_by_axes([wght])
            except Exception: pass
    return f

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]))

def tts(text, voice, rate, out):
    cmd = ['edge-tts', '--voice', voice, f'--rate={rate}', '--text', text, '--write-media', out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('edge-tts failed (pip install edge-tts; behind a TLS proxy append the system CA bundle to certifi):\n' + r.stderr[-400:])

class R:
    def __init__(s, spec):
        s.rtl = spec.get('lang', 'en') == 'he' and features.check('raqm')
        b = spec.get('brand', {})
        s.name = b.get('name', 'MASTERPHUB'); s.sig = b.get('signature', '')
        s.acc = hexrgb(b.get('accent', '#FFC107')); s.bg = hexrgb(b.get('background', '#121212')); s.fg = hexrgb(b.get('text', '#F0F0F0'))
        s.card = hexrgb(b.get('card', '#1c1c1c'))
        s.bgi = s._bg(); s.host = b.get('host'); s.logo = b.get('logo')
        fam = 'heebo' if s.rtl or b.get('font', 'inter') == 'heebo' else 'inter'
        s.big = lambda n: load_font(fam, n, 800); s.mid = lambda n: load_font(fam, n, 600)
        s.disp = lambda n: load_font('anton', n); s.sigf = load_font('caveat', 78, 700)
        s.cache = {}
    def _bg(s):
        im = Image.new('RGB', (W, H), s.bg); d = ImageDraw.Draw(im); r = 60
        line = tuple(min(255, c + 22) for c in s.bg)
        for row in range(-1, int(H / (r * 1.5)) + 2):
            for col in range(-1, int(W / (r * 1.73)) + 2):
                cx = col * r * 1.732 + (r * 0.866 if row % 2 else 0); cy = row * r * 1.5
                d.polygon([(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)], outline=line)
        g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((-200, 300, W + 200, 1500), fill=90); g = g.filter(ImageFilter.GaussianBlur(200))
        glow = tuple(int(c * 0.3) for c in s.acc); im.paste(Image.new('RGB', (W, H), glow), (0, 0), g); return im
    def img_rgba(s, p):
        k = 'rgba:' + p
        if k not in s.cache:
            im = Image.open(p).convert('RGBA'); bb = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
            s.cache[k] = im.crop(bb) if bb else im
        return s.cache[k]
    def img(s, p):
        if p not in s.cache: s.cache[p] = Image.open(p).convert('RGB')
        return s.cache[p]
    def tl(s, d, t, f): return d.textlength(t, font=f, direction='rtl') if s.rtl else d.textlength(t, font=f)
    def wrap(s, d, txt, f, maxw):
        words = txt.split(' '); lines = []; cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if s.tl(d, t, f) <= maxw: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur); return lines
    def text(s, d, y, txt, f, fill, maxw=940, gap=12):
        for ln in s.wrap(d, txt, f, maxw):
            w = s.tl(d, ln, f)
            kw = {'direction': 'rtl'} if s.rtl else {}
            d.text(((W - w) / 2, y), ln, font=f, fill=fill, **kw); y += f.size + gap
        return y
    def photo(s, im, path, box, t, zoom=0.06, anchor='center'):
        x0, y0, x1, y1 = [int(v) for v in box]; bw, bh = x1 - x0, y1 - y0; src = s.img(path)
        z = 1 + zoom * min(1, t / 4); sc = max(bw / src.width, bh / src.height) * z
        r = src.resize((int(src.width * sc), int(src.height * sc))); cx = (r.width - bw) // 2; cy = 0 if anchor == 'top' else (r.height - bh) // 2
        r = r.crop((cx, cy, cx + bw, cy + bh)); m = Image.new('L', (bw, bh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, bw, bh), 36, fill=255)
        im.paste(r, (x0, y0), m); ImageDraw.Draw(im).rounded_rectangle((x0, y0, x1, y1), 36, outline=s.acc, width=6)

    def frame(s, sc, t):
        im = s.bgi.copy(); d = ImageDraw.Draw(im)
        kind = sc.get('type', 'text')
        if s.logo and kind != 'logo':
            lg = s.img_rgba(s.logo); lh = 130; lw = int(lg.width * lh / lg.height)
            im.paste(lg.resize((lw, lh)), (60, 45), lg.resize((lw, lh)))
        elif not s.logo:
            d.text((70, 90), s.name, font=s.disp(56), fill=s.acc)
        if s.host and kind not in ('host', 'logo') and not sc.get('image') == s.host:
            src = s.img(s.host); sz = 150; sc_ = sz / src.width
            a = src.resize((sz, int(src.height * sc_))).crop((0, 0, sz, sz))
            m = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz, sz), fill=255)
            bob = int(math.sin(t * 2.5) * 5); im.paste(a, (W - sz - 60, 55 + bob), m)
            d.ellipse((W - sz - 60, 55 + bob, W - 60, 55 + bob + sz), outline=s.acc, width=5); pop = 1 - (1 - min(1, t / 0.35)) ** 3
        title, sub = sc.get('title', ''), sc.get('subtitle', '')
        if kind == 'logo':  # brand sting: big logo + tagline
            lg = s.img_rgba(s.logo); e = 1 - (1 - min(1, t / 0.6)) ** 3; lw = int(620 * (0.85 + 0.15 * e)); lh = int(lg.height * lw / lg.width)
            x, y = (W - lw) // 2, 520 - (lh - 660) // 2
            glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((W / 2 - 420, y + lh / 2 - 420, W / 2 + 420, y + lh / 2 + 420), fill=int(110 * e)); glow = glow.filter(ImageFilter.GaussianBlur(120))
            im.paste(Image.new('RGB', (W, H), s.acc), (0, 0), glow); a = lg.resize((lw, lh)); im.paste(a, (x, y), a); d = ImageDraw.Draw(im)
            if title: s.text(d, y + lh + 70, title, s.big(64), s.fg)
        elif kind == 'host':  # the brand host, big, head and shoulders
            s.photo(im, s.host, (240, 260, 840, 860), t, 0.05, 'top'); d = ImageDraw.Draw(im)
            y = s.text(d, 930, title, s.big(96), s.acc); y = s.text(d, y + 10, sub, s.mid(60), s.fg)
            if sc.get('button'):
                d.rounded_rectangle((150, y + 30, 930, y + 150), 60, fill=s.acc); s.text(d, y + 48, sc['button'], s.big(60), s.bg, 760)
        elif kind == 'banner':  # wide image (e.g. 16:9) shown whole, full width
            src = s.img(sc['image']); bw = 1000; bh = min(int(bw * src.height / src.width), 760); y0 = 300
            s.photo(im, sc['image'], (40, y0, 40 + bw, y0 + bh), t, 0.04); d = ImageDraw.Draw(im)
            tf = s.big(96 if len(title) <= 24 else 72 if len(title) <= 48 else 56)
            y = s.text(d, y0 + bh + 60, title, tf, s.acc); s.text(d, y + 10, sub, s.mid(56), s.fg)
        elif kind == 'hero':
            if sc.get('image'): s.photo(im, sc['image'], (190, 190, 890, 1090), t); d = ImageDraw.Draw(im)
            y = s.text(d, 1130, title, s.big(100), s.acc); s.text(d, y + 10, sub, s.mid(64), s.fg)
        elif kind == 'step':
            d.ellipse((W / 2 - 80, 230, W / 2 + 80, 390), fill=s.acc)
            n = str(sc.get('step', '')); d.text(((W - d.textlength(n, font=s.disp(110))) / 2, 245), n, font=s.disp(110), fill=s.bg)
            s.text(d, 430, title, s.big(92), s.fg)
            if sc.get('image'):
                s.photo(im, sc['image'], (260, 620, 820, 1370), t); d = ImageDraw.Draw(im)
                if sub: s.text(d, 1395, sub, s.mid(46), s.acc)
            elif sc.get('card'):
                c = sc['card']; d.rounded_rectangle((90, 680, W - 90, 1120), 30, fill=s.card, outline=s.acc, width=4)
                y = s.text(d, 720, c.get('title', ''), s.big(56), s.acc, 800); s.text(d, y + 20, c.get('body', ''), s.mid(38), s.fg, 800)
                if c.get('button') and t > 1.2:
                    d.rounded_rectangle((330, 1170, 750, 1280), 50, fill=s.acc); s.text(d, 1185, c['button'], s.big(56), s.bg, 400)
            elif sub: s.text(d, 800, sub, s.mid(56), s.acc)
        elif kind == 'compare':
            s.text(d, 430, title, s.big(92), s.fg)
            L, Rr = (70, 640, 500, 1240), (580, 640, 1010, 1240)
            before, after = (Rr, L) if s.rtl else (L, Rr)
            s.photo(im, sc['before'], before, t, 0.03); s.photo(im, sc['after'], after, t, 0.03); d = ImageDraw.Draw(im)
            if s.rtl: d.polygon([(565, 915), (515, 940), (565, 965)], fill=s.acc)
            else: d.polygon([(515, 915), (565, 940), (515, 965)], fill=s.acc)
            labs = sc.get('labels', ['לפני', 'אחרי'] if s.rtl else ['BEFORE', 'AFTER'])
            for box, lab in ((before, labs[0]), (after, labs[1])):
                f = s.big(56); w = s.tl(d, lab, f); kw = {'direction': 'rtl'} if s.rtl else {}
                d.text(((box[0] + box[2]) / 2 - w / 2, 1260), lab, font=f, fill=s.acc, **kw)
        elif kind == 'stat':
            y = 300
            for row in sc.get('rows', []):
                d.text(((W - d.textlength(row['big'], font=s.disp(230))) / 2, y), row['big'], font=s.disp(230), fill=s.acc); y += 280
                y = s.text(d, y, row.get('label', ''), s.big(80), s.fg) + 30
            if sc.get('button'):
                d.rounded_rectangle((150, y + 20, 930, y + 140), 60, fill=s.acc); s.text(d, y + 38, sc['button'], s.big(60), s.bg, 760)
        else:  # text / cta / thanks
            y = 330
            if sc.get('image'): s.photo(im, sc['image'], (290, 260, 790, 920), t); d = ImageDraw.Draw(im); y = 990
            y = s.text(d, y, title, s.big(110), s.fg); y = s.text(d, y + 10, sc.get('highlight', ''), s.big(150), s.acc); s.text(d, y + 10, sub, s.mid(56), s.fg)
            if sc.get('button'):
                d.rounded_rectangle((150, 1300, 930, 1420), 60, fill=s.acc); s.text(d, 1318, sc['button'], s.big(60), s.bg, 760)
        cap = sc.get('caption', sc.get('say', ''))
        if cap:
            for fs in (46, 40, 34):
                f = s.mid(fs); lines = s.wrap(d, cap, f, 900)
                if len(lines) <= 3: break
            bh = len(lines) * (fs + 14) + 40
            d.rounded_rectangle((60, 1520, W - 60, 1520 + bh), 24, fill=(0, 0, 0)); s.text(d, 1540, cap, f, 'white', 900, 14)
        if s.sig: d.text((W - 60 - d.textlength(s.sig, font=s.sigf), H - 150), s.sig, font=s.sigf, fill=s.fg)
        return im

def main(spec_path, out):
    spec = json.load(open(spec_path)); base = os.path.dirname(os.path.abspath(spec_path))
    for sc in spec['scenes']:
        for bk in ('host', 'logo'):
            if spec.get('brand', {}).get(bk) and not os.path.isabs(spec['brand'][bk]): spec['brand'][bk] = os.path.join(base, spec['brand'][bk])
        for k in ('image', 'before', 'after'):
            if sc.get(k) and not os.path.isabs(sc[k]): sc[k] = os.path.join(base, sc[k])
    voice = spec.get('voice') or VOICES.get(spec.get('lang', 'en'), VOICES['en']); rate = spec.get('rate', '+5%')
    r = R(spec); tmp = tempfile.mkdtemp(); os.makedirs(f'{tmp}/f')
    n = 0; wavs = []
    for i, sc in enumerate(spec['scenes']):
        wav = f'{tmp}/p{i}.wav'
        if sc.get('say'):
            a = f'{tmp}/a{i}.mp3'; tts(sc['say'], voice, rate, a); dur = duration(a) + 0.35
            subprocess.run(['ffmpeg', '-y', '-v', 'quiet', '-i', a, '-af', 'apad', '-t', str(dur), '-ar', '44100', '-ac', '2', wav], check=True)
        else:
            dur = float(sc.get('hold', 1.5))
            subprocess.run(['ffmpeg', '-y', '-v', 'quiet', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', str(dur), wav], check=True)
        wavs.append(wav)
        for k in range(int(dur * FPS)):
            r.frame(sc, k / FPS).save(f'{tmp}/f/{n:05d}.jpg', quality=88); n += 1
        print(f'scene {i + 1}/{len(spec["scenes"])} done ({dur:.1f}s)', flush=True)
    open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{w}'\n" for w in wavs))
    subprocess.run(['ffmpeg', '-y', '-v', 'quiet', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', f'{tmp}/all.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'quiet', '-framerate', str(FPS), '-i', f'{tmp}/f/%05d.jpg', '-i', f'{tmp}/all.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], check=True)
    shutil.rmtree(tmp); print('saved', out, f'{n / FPS:.1f}s')

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
