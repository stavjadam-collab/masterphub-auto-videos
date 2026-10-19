// AI Video Ad Builder promo: 9:16, voice-timed scenes, male + female narrators, 6 languages.
import React from 'react';
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { W, clamp, BG, HONEY, TEXT, DIM, HEB, Glow, Logo, LangCtx, W_, Headline, Shot, Roll } from './base';
import type { Rect, Copy } from './base';
import COPY from './copy.json';

type VO = { file: string; frames: number; cap: string; g: string };
type L = { heads: string[]; vo: VO[]; ui: { cta: string; credits: string; cost: string; name: string } };
const DATA = COPY as unknown as Record<string, L>;
const FONT: Record<string, Copy> = {
  he: { dir: 'rtl', font: 'Heebo, sans-serif' },
  ar: { dir: 'rtl', font: '"Noto Kufi Arabic", sans-serif' },
};
const fontFor = (l: string): Copy => FONT[l] ?? { dir: 'ltr', font: 'Heebo, Inter, sans-serif' };

const SHOTS = ['setup', 'claims', 'concepts', 'script', 'shots', 'adcopy'];
const FOCUS: Record<string, [Rect, number][]> = {
  he: [[[63, 120, 881, 525], 1.12], [[63, 662, 887, 838], 1.3], [[70, 75, 888, 374], 1.25], [[70, 85, 888, 596], 1.1], [[70, 130, 888, 352], 1.3], [[47, 18, 910, 500], 1.12]],
  en: [[[63, 120, 881, 520], 1.12], [[63, 597, 881, 850], 1.25], [[63, 75, 881, 427], 1.22], [[63, 85, 881, 750], 1.05], [[63, 130, 881, 376], 1.28], [[40, 18, 903, 578], 1.1]],
};
const LEAD = 8;
export const timeline = (lang: string) => {
  const d = DATA[lang];
  const durs = d.vo.slice(0, 7).map((v, i) => v.frames + LEAD + (i === 0 ? 30 : 18));
  const ctaDur = 10 + d.vo[7].frames + 12 + d.vo[8].frames + 70;
  const starts: number[] = []; let t = 0;
  for (const x of durs) { starts.push(t); t += x; }
  return { durs, starts, ctaStart: t, ctaDur, total: t + ctaDur };
};

// spoken-line caption at the bottom
const Caption: React.FC<{ text: string; dur: number }> = ({ text, dur }) => {
  const f = useCurrentFrame();
  const L = React.useContext(LangCtx);
  const a = interpolate(f, [0, 8, dur - 6, dur], [0, 1, 1, 0], clamp);
  return (
    <div style={{ position: 'absolute', top: 1600, width: '100%', display: 'flex', justifyContent: 'center', opacity: a, transform: `translateY(${(1 - Math.min(1, f / 8)) * 16}px)` }}>
      <div style={{ direction: L.dir, maxWidth: 940, textAlign: 'center', fontFamily: L.font, fontWeight: 700, fontSize: 48, lineHeight: 1.35, color: TEXT,
        background: 'rgba(0,0,0,0.62)', border: '1px solid rgba(247,195,26,0.25)', borderRadius: 22, padding: '18px 34px' }}>{text}</div>
    </div>
  );
};

const Hook: React.FC<{ head: string; dur: number }> = ({ head, dur }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [dur - 6, dur], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Glow />
      <Logo size={190} style={{ position: 'absolute', left: (W - 190) / 2, top: 420, opacity: interpolate(f, [0, 14], [0, 1], clamp), transform: `scale(${interpolate(f, [0, 16], [0.7, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) })})` }} />
      <Headline top={760} size={100} start={8} words={W_(head)} />
    </AbsoluteFill>
  );
};

const CTA: React.FC<{ dur: number; ui: L['ui']; lang: string }> = ({ dur, ui, lang }) => {
  const f = useCurrentFrame();
  const L = React.useContext(LangCtx);
  const a = (d: number) => interpolate(f, [d, d + 14], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const end = interpolate(f, [dur - 14, dur], [1, 0], clamp);
  const btn = a(60);
  const pulse = 1 + 0.025 * Math.max(0, Math.sin(((f - 100) / 27.85) * Math.PI)) * (f > 100 ? 1 : 0);
  const nameFont = lang === 'he' ? HEB : 'Heebo, Inter, sans-serif';
  return (
    <AbsoluteFill style={{ opacity: end }}>
      <Glow />
      <div style={{ position: 'absolute', top: 110, width: '100%', display: 'flex', justifyContent: 'center', opacity: a(0), transform: `scale(${0.85 + 0.15 * a(0)})`, filter: `drop-shadow(0 0 ${30 + 20 * Math.sin(f / 12)}px rgba(247,195,26,0.45))` }}>
        <Logo size={280} />
      </div>
      <Headline top={440} size={100} start={6} words={W_(ui.cta)} />
      <div style={{ position: 'absolute', top: 600, width: '100%', textAlign: 'center', fontFamily: HEB, fontWeight: 900, color: HONEY, fontSize: 290, lineHeight: 1, opacity: a(16), direction: 'ltr' }}>
        <Roll ch="1" d={18} size={290} /><Roll ch="0" d={22} size={290} />
      </div>
      <div style={{ position: 'absolute', top: 910, width: '100%', textAlign: 'center', fontFamily: L.font, fontWeight: 800, color: TEXT, fontSize: 70, direction: L.dir, opacity: a(30) }}>{ui.credits}</div>
      <div style={{ position: 'absolute', top: 1010, width: '100%', textAlign: 'center', fontFamily: L.font, fontWeight: 500, color: DIM, fontSize: 50, direction: L.dir, opacity: a(42) }}>{ui.cost}</div>
      <div style={{ position: 'absolute', top: 1170, width: '100%', display: 'flex', justifyContent: 'center', opacity: btn, transform: `translateY(${(1 - btn) * 30}px) scale(${pulse})` }}>
        <div style={{ background: HONEY, color: '#111', fontFamily: HEB, fontWeight: 900, fontSize: 64, padding: '28px 80px', borderRadius: 26, direction: 'ltr' }}>masterphub.io</div>
      </div>
      <div style={{ position: 'absolute', top: 1360, width: '100%', textAlign: 'center', fontFamily: nameFont, fontWeight: 600, color: DIM, fontSize: 46, direction: lang === 'he' ? 'rtl' : 'ltr', opacity: a(74) }}>{ui.name}</div>
    </AbsoluteFill>
  );
};

export const Promo: React.FC<{ lang?: string }> = ({ lang = 'he' }) => {
  const d = DATA[lang]; const tl = timeline(lang);
  const fk = lang === 'he' ? 'he' : 'en'; const sfx = lang === 'he' ? '' : '_en';
  const vo7 = d.vo[7], vo8 = d.vo[8];
  const c7 = tl.ctaStart + 10, c8 = c7 + vo7.frames + 12;
  return (
    <LangCtx.Provider value={fontFor(lang)}>
      <AbsoluteFill style={{ background: BG }}>
        <Sequence from={0} durationInFrames={tl.durs[0]}><Hook head={d.heads[0]} dur={tl.durs[0]} /></Sequence>
        {SHOTS.map((s, i) => {
          const k = i + 1; const [focus, push] = FOCUS[fk][i];
          return <Sequence key={s} from={tl.starts[k]} durationInFrames={tl.durs[k]}>
            <Shot dur={tl.durs[k]} src={`${s}${sfx}.png`} focus={focus} push={push} ringAt={24} words={W_(d.heads[k])} />
          </Sequence>;
        })}
        <Sequence from={tl.ctaStart} durationInFrames={tl.ctaDur}><CTA dur={tl.ctaDur} ui={d.ui} lang={lang} /></Sequence>
        {/* captions + voices */}
        {d.vo.slice(0, 7).map((v, k) => (
          <Sequence key={'c' + k} from={tl.starts[k] + LEAD} durationInFrames={v.frames + 10}><Caption text={v.cap} dur={v.frames + 10} /></Sequence>
        ))}
        <Sequence from={c7} durationInFrames={vo7.frames + 8}><Caption text={vo7.cap} dur={vo7.frames + 8} /></Sequence>
        <Sequence from={c8} durationInFrames={vo8.frames + 40}><Caption text={vo8.cap} dur={vo8.frames + 40} /></Sequence>
        {d.vo.slice(0, 7).map((v, k) => (
          <Sequence key={'v' + k} from={tl.starts[k] + LEAD} durationInFrames={v.frames + 4}><Audio src={staticFile(v.file)} volume={1} /></Sequence>
        ))}
        <Sequence from={c7} durationInFrames={vo7.frames + 4}><Audio src={staticFile(vo7.file)} /></Sequence>
        <Sequence from={c8} durationInFrames={vo8.frames + 4}><Audio src={staticFile(vo8.file)} /></Sequence>
        <Audio src={staticFile('bgm-tech-house.mp3')} startFrom={30 * 40} volume={(f) => 0.11 * interpolate(f, [0, 10, tl.total - 30, tl.total], [0, 1, 1, 0], clamp)} />
        {tl.starts.slice(1).map((s, i) => <Sequence key={'s' + i} from={s} durationInFrames={30}><Audio src={staticFile('swoosh-quick.mp3')} volume={0.22} /></Sequence>)}
        <Sequence from={tl.ctaStart} durationInFrames={60}><Audio src={staticFile('impact-deep-whoosh.mp3')} volume={0.25} /></Sequence>
        <Sequence from={tl.ctaStart + 18} durationInFrames={60}><Audio src={staticFile('sparkle-touch.mp3')} volume={0.3} /></Sequence>
      </AbsoluteFill>
    </LangCtx.Provider>
  );
};
