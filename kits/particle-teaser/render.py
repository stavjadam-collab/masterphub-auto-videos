"""Render a Masterphub pack teaser (12s, 720x1280, 30fps) with music.
Usage: python3 render.py <cover.jpg> "<line1>" "<line2>" "<hook>" <music.mp3> <out.mp4>
"""
import asyncio, base64, json, os, shutil, subprocess, sys, tempfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
cover, l1, l2, hook, music, out = sys.argv[1:7]
FPS, DUR = 30, 12

async def main():
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(HERE, 'teaser.html'), tmp)
    shutil.copy(os.path.join(HERE, 'Poppins-Bold.ttf'), tmp)
    shutil.copy(cover, os.path.join(tmp, 'cover.jpg'))
    cfg = json.dumps({'l1': l1, 'l2': l2, 'hook': hook, 'cover': 'cover.jpg'})
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = await b.new_page(viewport={'width': 720, 'height': 1280})
        await pg.add_init_script(f'window.RENDER=1;window.CFG={cfg};')
        await pg.goto('file://' + os.path.join(tmp, 'teaser.html'))
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
