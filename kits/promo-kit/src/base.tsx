// shared parts from the BB promo (Hebrew, 9:16, 30fps, 30s).
// video-shotcraft vocabulary: blur-slide title (hook) · page-cam 2.5D settle + push on real screenshots
// · draw-svg-trace focus ring · paper/brand CTA with digit-roll. Cuts on bars of cat-walk.mp3 (129 BPM, bar≈55.7f).
import React from 'react';
import { AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, staticFile, useCurrentFrame } from 'remotion';

const W = 1080, H = 1920;
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// tokens taken from the tool page (dark #111, card #1b1b1b, honey #f5c518-ish, white text, Heebo)
const BG = '#0f0f0f';
const HONEY = '#f7c31a';
const TEXT = '#f4f1ea';
const DIM = 'rgba(244,241,234,0.62)';
const HEB = 'Heebo, sans-serif';

// animated honeycomb (brand): gold hex cells, a slow light sweep lights cells near it
const HEXR = 64, HH = HEXR * Math.sqrt(3);
const CELLS: { x: number; y: number; k: number }[] = [];
for (let c = -1; c < W / (1.5 * HEXR) + 2; c++) for (let r = -1; r < H / HH + 2; r++) {
  const x = c * 1.5 * HEXR, y = r * HH + (c % 2 ? HH / 2 : 0);
  const sd = Math.sin((c * 12.9898 + r * 78.233)) * 43758.5453; CELLS.push({ x, y, k: sd - Math.floor(sd) });
}
const hexPts = (x: number, y: number, rr: number) => Array.from({ length: 6 }, (_, i) => { const a = (Math.PI / 3) * i; return `${(x + rr * Math.cos(a)).toFixed(1)},${(y + rr * Math.sin(a)).toFixed(1)}`; }).join(' ');
const Glow: React.FC<{ lx?: number; ly?: number }> = ({ lx, ly }) => {
  const f = useCurrentFrame();
  const gx = lx ?? 540 + 380 * Math.sin(f / 70), gy = ly ?? 520 + 300 * Math.cos(f / 95);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(1000px 800px at 50% 28%, rgba(247,195,26,0.13), transparent 70%), ${BG}` }}>
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        {CELLS.map((c, i) => {
          const d = Math.hypot(c.x - gx, c.y - gy);
          const lit = Math.max(0, 1 - d / 420);
          const tw = 0.5 + 0.5 * Math.sin(f / 18 + c.k * 6.28);
          const fillA = lit * lit * 0.16 * (0.6 + 0.4 * tw);
          const strokeA = 0.07 + lit * 0.35;
          return <polygon key={i} points={hexPts(c.x, c.y, HEXR - 3)} fill={`rgba(247,195,26,${fillA.toFixed(3)})`} stroke={`rgba(247,195,26,${strokeA.toFixed(3)})`} strokeWidth={1.6} />;
        })}
      </svg>
      <AbsoluteFill style={{ background: 'radial-gradient(1400px 1200px at 50% 50%, transparent 55%, rgba(0,0,0,0.55))' }} />
    </AbsoluteFill>
  );
};
const Logo: React.FC<{ size: number; style?: React.CSSProperties }> = ({ size, style }) => (
  <Img src={staticFile('logo_c.png')} style={{ width: size, height: size * (845 / 798), ...style }} />
);

type Copy = { dir: 'rtl' | 'ltr'; font: string };
const LangCtx = React.createContext<Copy>({ dir: 'rtl', font: 'Heebo, sans-serif' });
// "a *b c* d" -> words with accent on b,c
const W_ = (txt: string): Word[] => { let on = false; return txt.split(' ').filter(Boolean).map((t) => { const n = (t.match(/\*/g) || []).length; const a = on || n > 0; if (n % 2 === 1) on = !on; return { t: t.replace(/\*/g, ''), a }; }); };

// ---------- blur-slide headline (RTL, word by word) ----------
type Word = { t: string; a?: boolean };
const Headline: React.FC<{ words: Word[]; start?: number; size?: number; top: number }> = ({ words, start = 0, size = 92, top }) => {
  const f = useCurrentFrame();
  const L = React.useContext(LangCtx);
  return (
    <div style={{ position: 'absolute', top, width: '100%', display: 'flex', justifyContent: 'center' }}>
      <div style={{ direction: L.dir, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', columnGap: '0.24em', width: 960,
        fontFamily: L.font, fontWeight: 900, fontSize: size, lineHeight: 1.15, color: TEXT }}>
        {words.map((w, i) => {
          const d = start + i * 3.5;
          const t = interpolate(f, [d, d + 14], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          return <span key={i} style={{ display: 'inline-block', opacity: t, transform: `translateY(${(1 - t) * 40}px)`, filter: `blur(${(1 - t) * 10}px)`, color: w.a ? HONEY : undefined }}>{w.t}</span>;
        })}
      </div>
    </div>
  );
};

// ---------- page-cam shot: real screenshot settles from 2.5D tilt, then pushes to a focus rect ----------
type Rect = [number, number, number, number]; // x0,y0,x1,y1 in screenshot px (958x910)
const SW = 958, SHH = 854, PS = 1000 / 958; // displayed scale
const Shot: React.FC<{ src: string; focus: Rect; words: Word[]; dur: number; push?: number; ringAt?: number }> = ({ src, focus, words, dur, push = 1.32, ringAt = 30 }) => {
  const f = useCurrentFrame();
  const settle = interpolate(f, [0, 26], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const pushT = interpolate(f, [ringAt + 6, dur - 14], [0, 1], { ...clamp, easing: Easing.bezier(0.45, 0, 0.25, 1) });
  const fadeOut = interpolate(f, [dur - 6, dur], [1, 0], clamp);
  const [x0, y0, x1, y1] = focus;
  const cx = ((x0 + x1) / 2) * PS, cy = ((y0 + y1) / 2) * PS;
  const pw = SW * PS, ph = SHH * PS;
  const s = (0.86 + 0.14 * settle) * (1 + (push - 1) * pushT);
  // move focus toward the frame centre while pushing
  const tx = (pw / 2 - cx) * pushT * 0.9, ty = (ph / 2 - cy) * pushT * 0.9;
  const rx = (1 - settle) * 16, ry = (1 - settle) * -12;
  // focus ring draw-on
  const ring = interpolate(f, [ringAt, ringAt + 16], [0, 1], { ...clamp, easing: Easing.bezier(0.3, 0, 0.2, 1) });
  const dim = interpolate(f, [ringAt + 4, ringAt + 18], [0, 0.55], clamp);
  const rw = (x1 - x0) * PS + 24, rh = (y1 - y0) * PS + 24, per = 2 * (rw + rh);
  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <Glow />
      <div style={{ position: 'absolute', left: (W - pw) / 2, top: 640, width: pw, height: ph, perspective: 1600 }}>
        <div style={{ width: pw, height: ph, transformStyle: 'preserve-3d', transformOrigin: '50% 50%',
          transform: `translate(${tx}px, ${ty}px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${s})` }}>
          <div style={{ position: 'absolute', inset: 0, borderRadius: 22, overflow: 'hidden', boxShadow: '0 40px 120px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.08)' }}>
            <Img src={staticFile(src)} style={{ width: pw, height: ph, display: 'block' }} />
            {/* spotlight: dim everything except the focus rect */}
            <div style={{ position: 'absolute', inset: 0, background: `rgba(0,0,0,${dim})`,
              clipPath: `polygon(0 0, 100% 0, 100% 100%, 0 100%, 0 0, ${x0 * PS - 12}px ${y0 * PS - 12}px, ${x0 * PS - 12}px ${y1 * PS + 12}px, ${x1 * PS + 12}px ${y1 * PS + 12}px, ${x1 * PS + 12}px ${y0 * PS - 12}px, ${x0 * PS - 12}px ${y0 * PS - 12}px)` }} />
          </div>
          <svg style={{ position: 'absolute', left: x0 * PS - 12, top: y0 * PS - 12, overflow: 'visible' }} width={rw} height={rh}>
            <rect x={0} y={0} width={rw} height={rh} rx={18} fill="none" stroke={HONEY} strokeWidth={5} strokeDasharray={per} strokeDashoffset={per * (1 - ring)} />
          </svg>
        </div>
      </div>
      <div style={{ position: 'absolute', left: 0, top: 0, width: W, height: 600, background: `linear-gradient(${BG} 0%, ${BG} 68%, rgba(15,15,15,0) 100%)` }} />
      <Headline top={200} size={84} words={words} />
      <Logo size={96} style={{ position: 'absolute', left: (W - 96) / 2, top: 60, opacity: 0.95 }} />
    </AbsoluteFill>
  );
};

// ---------- CTA ----------
const DIG = '0123456789';
const Roll: React.FC<{ ch: string; d: number; size: number }> = ({ ch, d, size }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [d, d + 24], [0, 1], { ...clamp, easing: Easing.bezier(0.25, 0.8, 0.25, 1) });
  const lh = size * 1.0, tgt = DIG.indexOf(ch);
  return (
    <span style={{ display: 'inline-block', height: lh, overflow: 'hidden', verticalAlign: 'top' }}>
      <span style={{ display: 'block', transform: `translateY(${-(10 + tgt) * t * lh}px)` }}>
        {(DIG + DIG).split('').map((x, j) => <span key={j} style={{ display: 'block', height: lh, lineHeight: `${lh}px` }}>{x}</span>)}
      </span>
    </span>
  );
};

export { W, H, clamp, BG, HONEY, TEXT, DIM, HEB, Glow, Logo, LangCtx, W_, Headline, Shot, Roll };
export type { Rect, Copy };
