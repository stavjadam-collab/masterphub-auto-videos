"""Render 12s vertical videos (720x1280, 30fps) with music.

Pack teaser (particles form the name, then the cover + masterphub.io):
  python3 render.py <cover.jpg> "<LINE 1>" "<LINE 2>" "<hook>" <music.mp3> <out.mp4>
Book trailer (a line from the book word by word, then the cover + call to action, Hebrew or English):
  python3 render.py book <cover.jpg> "<line>" "<key word>" "<cta>" <music.mp3> <out.mp4>
"""
import asyncio, base64, json, os, shutil, subprocess, sys, tempfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
if args[0] == 'book':
    page = 'book.html'
    cover, line, key, cta, music, out = args[1:7]
    cfg = {'line': line, 'key': key, 'cta': cta, 'cover': 'cover.jpg'}
else:
    if args[0] == 'teaser':
        args = args[1:]
    page = 'teaser.html'
    cover, l1, l2, hook, music, out = args[:6]
    cfg = {'l1': l1, 'l2': l2, 'hook': hook, 'cover': 'cover.jpg'}
FPS, DUR = 30, 12

async def main():
    tmp = tempfile.mkdtemp()
    for f in (page, 'Poppins-Bold.ttf', 'Rubik-Bold.ttf'):
        shutil.copy(os.path.join(HERE, f), tmp)
    shutil.copy(cover, os.path.join(tmp, 'cover.jpg'))
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await b.new_page(viewport={'width': 720, 'height': 1280})
        await pg.add_init_script(f'window.RENDER=1;window.CFG={json.dumps(cfg)};')
        await pg.goto('file://' + os.path.join(tmp, page))
        await pg.evaluate('boot()')
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-',
                               '-i', music, '-t', str(DUR), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22',
                               '-c:a', 'aac', '-b:a', '128k', '-af', f'afade=t=out:st={DUR-1.5}:d=1.5',
                               '-movflags', '+faststart', out], stdin=subprocess.PIPE)
        for i in range(FPS * DUR):
            data = await pg.evaluate(f"(frame({i / FPS}), document.getElementById('c').toDataURL('image/jpeg', .92))")
            ff.stdin.write(base64.b64decode(data.split(',')[1]))
        ff.stdin.close(); ff.wait()
        await b.close()
    shutil.rmtree(tmp)

asyncio.run(main())
