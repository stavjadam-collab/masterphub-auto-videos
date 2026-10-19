import json, re, sys, difflib, wave

lang = sys.argv[1]
W = json.load(open(f'/home/claude/mv/{lang}-words.json'))
LINES = [l.strip() for l in open(f'/home/claude/mv/lyrics_{lang}.txt', encoding='utf-8') if l.strip()]
w = wave.open(f'/home/claude/mv/{lang}.wav'); DUR = w.getnframes() / w.getframerate()
FPS = 24

def norm(s):
    s = re.sub(r'[^\w֐-׿ ]', ' ', s.lower())
    s = re.sub(r'[֑-ׇ]', '', s)
    return ' '.join(s.split())

words = [(a, b, norm(x)) for a, b, x in W if norm(x)]
ptr = 0
starts = []
for li, line in enumerate(LINES):
    lw = norm(line).split()
    key = ' '.join(lw[:3])
    best, bi = -1, ptr
    for j in range(ptr, min(len(words), ptr + 30)):
        cand = ' '.join(x for _, _, x in words[j:j + 3])
        r = difflib.SequenceMatcher(None, key, cand).ratio() - 0.004 * (j - ptr)
        if r > best:
            best, bi = r, j
    starts.append(words[bi][0])
    ptr = bi + max(1, len(lw) - 1)

# lines must be increasing
for i in range(1, len(starts)):
    if starts[i] <= starts[i - 1] + 0.8:
        starts[i] = starts[i - 1] + 0.8
ends = []
for i, s in enumerate(starts):
    n = len(LINES[i].split())
    est = s + 1.2 + n * 0.55
    nxt = starts[i + 1] - 0.15 if i + 1 < len(starts) else DUR - 3
    ends.append(min(max(est, s + 2.0), nxt, s + 7.5))

SEC = {'V1': (0, 3), 'V2': (4, 6), 'CH1': (7, 10), 'V3': (11, 14), 'V4': (15, 18), 'CH2': (19, 22), 'OUT': (23, 26)}
def st(i): return starts[i]
def en(i): return ends[i]

# scene cut points
cuts = [
    ('s00', 0),
    ('s01', st(0) - 0.4),
    ('s02', st(2) - 0.4),
    ('s03', st(4) - 0.4),
    ('s04', st(7) - 0.4),
    ('s11', st(9) - 0.4),
    ('s05', en(10) + 0.8),
    ('s06', st(11) - 0.4),
    ('s07', st(15) - 0.4),
    ('s08', st(17) - 0.4),
    ('s04b', st(19) - 0.4),
    ('s11b', st(21) - 0.4),
    ('s09', en(22) + 0.8),
    ('s10', st(23) - 0.4),
]
scenes = []
for i, (name, t) in enumerate(cuts):
    t1 = cuts[i + 1][1] if i + 1 < len(cuts) else DUR
    scenes.append((name, max(0, t), t1))

TRANS = ['fade', 'lightwipe', 'linear', 'pageturn', 'iris', 'fade', 'lightwipe', 'linear', 'fade', 'pageturn', 'lightwipe', 'iris', 'linear', 'fade']
TD = 1.4  # transition length

js = []
A = js.append
A('var p=app.project;')
A(f'var c=p.items.addComp("ML",1920,1080,1,{DUR:.3f},{FPS});')
A('function imp(f){return p.importFile(new ImportOptions(new File(f)));}')
A('function fx(L,name){return L.property("Effects").addProperty(name);}')
A('function k(prop,arr){for(var i=0;i<arr.length;i++){prop.setValueAtTime(arr[i][0],arr[i][1]);}}')

# audio
A(f'var au=imp("/home/claude/mv/{lang}.mp3"); c.layers.add(au);')
A('var bg=c.layers.addSolid([0.95,0.91,0.83],"paper",1920,1080,1);')

# scenes added last-first so the earlier scene sits on top and wipes away
for idx in range(len(scenes) - 1, -1, -1):
    name, t0, t1 = scenes[idx]
    img = name.rstrip('b') if name.endswith('b') and name not in ('s11b',) else name
    if name == 's11b': img = 's11'
    if name == 's04b': img = 's04'
    a = max(0, t0 - (TD if idx > 0 else 0))
    b = min(DUR, t1 + (TD / 2 if idx < len(scenes) - 1 else 0))
    if idx > 0: a = max(0, t0 - TD / 2)
    d = b - a
    A(f'var L=c.layers.add(imp("/home/claude/mv/img/{img}.png")); L.name="{name}"; L.startTime=0; L.inPoint={a:.3f}; L.outPoint={b:.3f};')
    # Ken Burns: alternate zoom in / out and drift
    zin = idx % 2 == 0
    s0, s1 = (101, 111) if zin else (111, 101)
    dx = [40, -40, 30, -30, 0, 50, -50][idx % 7]
    dy = [15, -10, 0, 20, -15, 10, -20][idx % 7]
    A(f'k(L.property("Scale"),[[{a:.3f},[{s0},{s0}]],[{b:.3f},[{s1},{s1}]]]);')
    A(f'k(L.property("Position"),[[{a:.3f},[{960-dx},{540-dy}]],[{b:.3f},[{960+dx},{540+dy}]]]);')
    # per-scene life
    if img == 's00':
        A('var r=fx(L,"CC Rainfall"); r.property("Drops").setValue(4000); r.property("Opacity").setValue(55); r.property("Size").setValue(2);')
        A(f'var g=fx(L,"Glow"); k(g.property("Glow Intensity"),[[{a:.3f},0.4],[{b:.3f},1.2]]);')
    if img == 's01':
        A('L.property("Rotation").expression="wiggle(3,0.6)";')
    if img == 's02':
        A(f'var sw=fx(L,"CC Light Sweep"); sw.property("Width").setValue(120); sw.property("Sweep Intensity").setValue(35); k(sw.property("Center"),[[{a:.3f},[-200,540]],[{b:.3f},[2100,540]]]);')
    if img == 's03':
        A(f'var lw=fx(L,"Linear Wipe"); lw.property("Wipe Angle").setValue(270); lw.property("Feather").setValue(220); k(lw.property("Transition Completion"),[[{t0:.3f},100],[{t0+4:.3f},0]]);')
    if img == 's04':
        A('var sn=fx(L,"CC Snowfall"); sn.property("Flakes").setValue(500); sn.property("Size").setValue(5); sn.property("Speed").setValue(25); sn.property("Wind").setValue(70); sn.property("Opacity").setValue(70); sn.property("Color").setValue([1,0.85,0.45]);')
        A(f'var lf=fx(L,"Lens Flare"); k(lf.property("Flare Brightness"),[[{a:.3f},40],[{b:.3f},90]]); lf.property("Flare Center").setValue([1150,330]);')
    if img == 's05':
        A(f'var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); k(g.property("Glow Intensity"),[[{a:.3f},0.5],[{(a+b)/2:.3f},1.4],[{b:.3f},0.6]]);')
        A('var dd=fx(L,"CC Snowfall"); dd.property("Flakes").setValue(250); dd.property("Size").setValue(3); dd.property("Speed").setValue(15); dd.property("Wind").setValue(-40); dd.property("Opacity").setValue(55); dd.property("Color").setValue([1,0.9,0.6]);')
    if img == 's06':
        A(f'var hs=fx(L,"Hue/Saturation"); k(hs.property("Master Saturation"),[[{t0:.3f},-100],[{t0+3.5:.3f},0]]);')
        A(f'var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); k(g.property("Glow Intensity"),[[{t0+2:.3f},0.3],[{t0+4:.3f},1.3],[{b:.3f},0.6]]);')
    if img in ('s07', 's08'):
        A('var st=fx(L,"CC Snowfall"); st.property("Flakes").setValue(300); st.property("Size").setValue(2); st.property("Speed").setValue(8); st.property("Wind").setValue(10); st.property("Opacity").setValue(45); st.property("Color").setValue([0.8,0.88,1]);')
        A('var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); g.property("Glow Intensity").setValue(0.7);')
    if img == 's08':
        A('L.property("Rotation").expression="Math.sin(time*0.7)*0.6";')
    if img == 's09':
        A('L.property("Rotation").expression="Math.sin(time*1.1)*1.4";')
        A('var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); g.property("Glow Intensity").setValue(0.9);')
    if img == 's10':
        A(f'var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); k(g.property("Glow Intensity"),[[{a:.3f},0.5],[{b-4:.3f},1.5]]);')
        A('var sn=fx(L,"CC Snowfall"); sn.property("Flakes").setValue(200); sn.property("Size").setValue(4); sn.property("Speed").setValue(12); sn.property("Wind").setValue(40); sn.property("Opacity").setValue(55); sn.property("Color").setValue([1,0.8,0.5]);')
        A(f'k(L.property("Opacity"),[[{DUR-4:.3f},100],[{DUR-0.2:.3f},0]]);')
    if img == 's11':
        A(f'var rw=fx(L,"Radial Wipe"); k(rw.property("Transition Completion"),[[{t0:.3f},100],[{t0+2.5:.3f},0]]);')
        A(f'var g=fx(L,"Glow"); g.property("Glow Radius").setValue(12); k(g.property("Glow Intensity"),[[{t0+1:.3f},0.3],[{t0+3:.3f},1.2],[{b:.3f},0.5]]);')
    # outgoing transition on this (upper) layer
    if idx < len(scenes) - 1:
        tr = TRANS[idx % len(TRANS)]
        x0, x1 = t1 - TD / 2, t1 + TD / 2
        if tr == 'fade':
            A(f'k(L.property("Opacity"),[[{x0:.3f},100],[{x1:.3f},0]]);')
        elif tr == 'lightwipe':
            A(f'var tw=fx(L,"CC Light Wipe"); k(tw.property("Completion"),[[{x0:.3f},0],[{x1:.3f},100]]);')
        elif tr == 'linear':
            A(f'var tw=fx(L,"Linear Wipe"); tw.property("Feather").setValue(300); k(tw.property("Transition Completion"),[[{x0:.3f},0],[{x1:.3f},100]]);')
        elif tr == 'iris':
            A(f'var tw=fx(L,"Iris Wipe"); tw.property("Feather").setValue(200); k(tw.property("Outer Radius"),[[{x0:.3f},0],[{x1:.3f},1300]]); tw.property("Use Inner Radius").setValue(0);')
            # iris opens a hole; we want old layer to vanish from centre: use opacity fallback too
            A(f'k(L.property("Opacity"),[[{x0:.3f},100],[{x1:.3f},100]]);')
        elif tr == 'pageturn':
            A(f'var tw=fx(L,"CC Page Turn"); k(tw.property("Fold Position"),[[{x0:.3f},[1950,1100]],[{x1:.3f},[-900,-500]]]); tw.property("Paper Color").setValue([0.96,0.92,0.84]);')

# title
title = 'אהובתי' if lang == 'he' else 'My Love'
A(f'var T=c.layers.addText("{title}"); var d=T.property("Source Text").value; d.font="AmaticSC-Bold"; d.fontSize=230; d.fillColor=[1,0.97,0.9]; d.applyStroke=true; d.strokeColor=[0.25,0.15,0.08]; d.strokeWidth=6; d.strokeOverFill=false; d.justification=ParagraphJustification.CENTER_JUSTIFY; T.property("Source Text").setValue(d);')
A('T.inPoint=1.5; T.outPoint=Math.min(12,' + f'{starts[0]-0.5:.3f}' + '); T.property("Position").setValue([960,470]);')
A('k(T.property("Opacity"),[[1.5,0],[3,100],[T.outPoint-1.5,100],[T.outPoint,0]]); k(T.property("Scale"),[[1.5,[90,90]],[T.outPoint,[104,104]]]);')
A('var tg=fx(T,"Glow"); tg.property("Glow Radius").setValue(12);')

# captions
for i, line in enumerate(LINES):
    s, e = starts[i], ends[i]
    txt = line.replace('"', '\\"')
    A(f'var C=c.layers.addText("{txt}"); var d=C.property("Source Text").value; d.font="Heebo"; d.fauxBold=true; d.fontSize=62; d.fillColor=[1,1,1]; d.applyStroke=true; d.strokeColor=[0.12,0.09,0.06]; d.strokeWidth=5; d.strokeOverFill=false; d.justification=ParagraphJustification.CENTER_JUSTIFY; C.property("Source Text").setValue(d);')
    A(f'C.inPoint={s:.3f}; C.outPoint={e:.3f}; C.property("Position").setValue([960,1000]);')
    A(f'k(C.property("Opacity"),[[{s:.3f},0],[{s+0.3:.3f},100],[{e-0.3:.3f},100],[{e:.3f},0]]);')
    A(f'k(C.property("Position"),[[{s:.3f},[960,1015]],[{s+0.4:.3f},[960,1000]]]);')

# signature
A('var S=c.layers.addText("stavjadam"); var d=S.property("Source Text").value; d.font="HomemadeApple-Regular"; d.fontSize=40; d.fillColor=[1,1,1]; d.applyStroke=true; d.strokeColor=[0.1,0.08,0.05]; d.strokeWidth=2; d.strokeOverFill=false; S.property("Source Text").setValue(d); S.property("Position").setValue([190,1045]); S.property("Opacity").setValue(85);')

# finishing adjustment layer: vignette + grain
A('var adj=c.layers.addSolid([0,0,0],"look",1920,1080,1); adj.adjustmentLayer=true; adj.moveToBeginning();')
A('var v=fx(adj,"CC Vignette"); v.property("Amount").setValue(35);')
A('')
A(f'p.save(new File("/home/claude/mv/ml-{lang}.ecproj")); writeLn("saved");')

open(f'/home/claude/mv/ml-{lang}.jsx', 'w', encoding='utf-8').write('\n'.join(js))
json.dump({'starts': starts, 'ends': ends, 'scenes': scenes, 'dur': DUR}, open(f'/home/claude/mv/plan-{lang}.json', 'w'), ensure_ascii=False, indent=1)
for i, l in enumerate(LINES): print(f'{starts[i]:6.1f}-{ends[i]:6.1f} {l}')
for sc in scenes: print(sc)
