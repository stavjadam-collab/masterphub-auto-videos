#!/usr/bin/env python3
"""Masterphub auto videos: claim a job from Supabase, build a spec, render, upload, then post via the Distribution Hub."""
import json, os, re, subprocess, sys, urllib.request

SB = 'https://izwsmxwjimowaioyplza.supabase.co'
ANON = os.environ.get('SUPABASE_ANON', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6d3NteHdqaW1vd2Fpb3lwbHphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0ODQ1MzQsImV4cCI6MjA5NDA2MDUzNH0.qwvwopCpOycOBvOPNaPzDQqOkvvYkMrQXEoBqUs0ufc')
HUB = os.environ.get('HUB_URL', '')
LOGO = 'https://masterphub.io/masterphub-logo-transparent.png'
HOST = SB + '/storage/v1/object/public/assets/video/claudia.png'
H = {'apikey': ANON, 'Authorization': 'Bearer ' + ANON}

def req(url, data=None, headers=None, method=None, raw=False, auth=True):
    hd = dict(H) if auth else {}; hd.update(headers or {})
    body = data if raw or data is None else json.dumps(data).encode()
    if data is not None and not raw: hd.setdefault('Content-Type', 'application/json')
    r = urllib.request.urlopen(urllib.request.Request(url, data=body, headers=hd, method=method), timeout=120)
    t = r.read().decode() or 'null'
    try: return json.loads(t)
    except Exception: return t

def rpc(name, args=None): return req(f'{SB}/rest/v1/rpc/{name}', args or {})

def fetch(url, path):
    if not os.path.exists(path): urllib.request.urlretrieve(url, path)
    return path

def sentences(text, n=3, lo=8, hi=32):
    text = re.sub(r'\s+', ' ', text or '').strip()
    out = []
    for s in re.split(r'(?<=[.!?])\s+', text):
        w = len(s.split())
        if lo <= w <= hi and not s.endswith('...') and '|' not in s and not re.match(r'(However|But|This|That|These|Those|It|They|And|So|Also)\b', s): out.append(s)
        if len(out) == n: break
    return out

def kfmt(n):
    try: n = int(n)
    except Exception: return ''
    return f'{n / 1000:.0f}K' if n >= 1000 else str(n)

def first(text, key):
    m = re.search(key + r'\s*:?\s*(.+?)(?:\s+(?:Not for|Limitation)\s*:|$)', text or '', re.S)
    return m.group(1).strip().rstrip('.') if m else ''

def spec_github(src):
    name = src['repo'].split('/')[-1]; stars = kfmt(src.get('stars'))
    sc = [{'type': 'logo', 'title': 'GitHub Repo of the Day', 'hold': 1.8}]
    intro = f"Hi, I'm Claudia. Here's the GitHub repo of the day: {name}." + (f' {int(src["stars"]):,} stars.' if stars else '')
    if src.get('image'):
        sc.append({'type': 'banner', 'image': fetch(src['image'], 'banner.jpg'), 'title': 'Repo of the Day', 'subtitle': f'{stars} stars on GitHub' if stars else src['repo'], 'say': intro})
    else:
        sc.append({'type': 'text', 'title': 'Repo of the Day', 'highlight': name, 'say': intro})
    sc.append({'type': 'step', 'step': 1, 'title': 'What it is', 'card': {'title': name, 'body': src.get('what', '')}, 'say': src.get('what', '')})
    sc.append({'type': 'step', 'step': 2, 'title': 'Why it matters', 'subtitle': (sentences(src.get('why'), 1, 3, 40) or [src.get('why', '')])[0], 'say': src.get('why', '')})
    how = src.get('how', '')
    sc.append({'type': 'step', 'step': 3, 'title': 'How to use', 'card': {'title': 'Get started', 'body': how}, 'say': how, 'caption': (sentences(how, 1, 3, 30) or [how])[0]})
    who = first(src.get('verdict', ''), 'For')
    if who: sc.append({'type': 'text', 'title': 'Made for', 'highlight': ' '.join(who.split()[:3]) if len(who.split()) <= 3 else 'builders', 'subtitle': who, 'say': f'Made for {who}.'})
    sc.append({'type': 'host', 'title': 'Get it free', 'subtitle': 'Full review + skill download', 'button': 'masterphub.io/github', 'say': 'Get the full review and the skill, free, on masterphub dot I O. See you tomorrow!', 'caption': 'Full review + free skill at masterphub.io/github. See you tomorrow!'})
    return sc

def spec_blog(src):
    title = src['title']; body = sentences(src.get('content') or src.get('excerpt'), 3)
    sc = [{'type': 'logo', 'title': 'From the Masterphub blog', 'hold': 1.8}]
    hook = f"Hi, I'm Claudia. New on the Masterphub blog: {title}."
    if src.get('image'):
        sc.append({'type': 'banner', 'image': fetch(src['image'], 'cover.jpg'), 'title': title, 'say': hook})
    else:
        sc.append({'type': 'text', 'title': 'New on the blog', 'subtitle': title, 'say': hook})
    labels = ['The idea', 'Why it works', 'Try this']
    for i, s in enumerate(body): sc.append({'type': 'step', 'step': i + 1, 'title': labels[i], 'subtitle': s, 'say': s})
    sc.append({'type': 'host', 'title': 'Read the full guide', 'subtitle': 'Free on Masterphub', 'button': 'masterphub.io/blog', 'say': 'Read the full guide, free, on masterphub dot I O.', 'caption': 'Read the full guide, free, at masterphub.io/blog'})
    return sc

def post_text(kind, src):
    if kind == 'custom': return src['text']
    if kind == 'github_daily':
        return (f"GitHub Repo of the Day: {src['repo']}" + (f" ⭐ {kfmt(src.get('stars'))}" if src.get('stars') else '') +
                f"\n\n{src.get('what', '')}\n\nFull review + free skill download 👉 https://masterphub.io/github\n\n#GitHub #AI #OpenSource #Masterphub")
    ex = (sentences(src.get('excerpt'), 1, 5, 40) or [''])[0]
    return f"{src['title']}\n\n{ex}\n\nRead the full guide 👉 https://masterphub.io/guides.html?slug={src['slug']}\n\n#AI #Masterphub"

def render(job):
    kind, src = job['type'], job['src']
    scenes = spec_github(src) if kind == 'github_daily' else spec_blog(src)
    spec = {'lang': 'en', 'voice': 'en-US-AvaNeural', 'brand': {'logo': fetch(LOGO, 'logo.png'), 'host': fetch(HOST, 'claudia.png'), 'signature': 'stavjadam', 'font': 'inter'}, 'scenes': scenes}
    json.dump(spec, open('spec.json', 'w'))
    out = f"{job['job_id']}.mp4"
    subprocess.run([sys.executable, 'make_video.py', 'spec.json', out], check=True)
    return out

def main():
    dry = os.environ.get('DRY_JOB')
    if dry:  # local test: render a job JSON without touching the database
        print(render(json.load(open(dry)))); return
    for _ in range(int(os.environ.get('MAX_JOBS', '3'))):
        job = rpc('video_claim')
        if not job: break
        try:
            out = render(job)
            req(f"{SB}/storage/v1/object/social-videos/auto/{job['job_id']}.mp4", open(out, 'rb').read(), {'Content-Type': 'video/mp4'}, raw=True)
            print('done', rpc('video_complete', {'p_job': job['job_id']}))
        except Exception as e:
            print('failed', job['job_id'], e); rpc('video_fail', {'p_job': job['job_id'], 'p_err': str(e)})
    p = rpc('video_next_post')
    if p:
        text = post_text(p['type'], p['src'])
        print('hub', req(HUB, {'text': text, 'video_url': p['video_url']}, auth=False))
        rpc('video_posted', {'p_job': p['job_id']}); print('posted', p['job_id'])

if __name__ == '__main__':
    main()
