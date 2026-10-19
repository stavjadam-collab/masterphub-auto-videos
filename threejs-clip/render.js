// node render.js <lang> <start> <end> <out.mp4> [fps]
const { chromium } = require(process.env.PW || '/opt/npm-tools/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const [lang, S, E, out, fpsArg] = process.argv.slice(2);
const FPS = +(fpsArg || 24), start = +S, end = +E;
const root = __dirname;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); });
}).listen(0);
(async () => {
  const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
  p.on('pageerror', e => console.error('pageerror:', e.message));
  await p.goto(`http://127.0.0.1:${port}/index.html?lang=${lang}`);
  await p.waitForFunction('window.READY === true', null, { timeout: 120000 });
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n0 = Math.round(start * FPS), n1 = Math.round(end * FPS);
  const t0 = Date.now();
  for (let n = n0; n < n1; n++) {
    await p.evaluate(t => window.renderAt(t), n / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((n - n0) % 48 === 0) console.log(`frame ${n - n0}/${n1 - n0} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); srv.close();
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
})();
