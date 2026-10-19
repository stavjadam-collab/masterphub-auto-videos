# MOTION.md: Masterphub video style

Read this before building any Masterphub promo, teaser or explainer video. It is the house style. If a request conflicts with it, follow the request and keep everything else from here.

## Format
- 1080x1920, 30 fps, vertical. 16:9 only when asked.
- Length follows the voice: each scene = voice line + 8 frames lead + 18 frames tail. Hook scene gets +30 frames to land. CTA holds 2 seconds after the last word.
- Typical promo: 30 to 50 seconds, 7 scenes + CTA.

## Color and type
- Background #0f0f0f. Honey gold #f7c31a. Text #f4f1ea. Dim text rgba(244,241,234,0.62).
- Hebrew: Heebo 900 for headlines, 700 for captions. Arabic: Noto Kufi Arabic. Latin: Heebo, Inter.
- Accent words in honey gold, marked in copy with *asterisks*. One or two accent words per headline, never more.
- Fonts are installed system-wide (~/.fonts). Never load fonts at runtime with FontFace/loadFont: it hangs full renders.

## Brand layer
- Background is always the animated honeycomb (Glow): gold hex cells, a slow light that wanders and lights cells near it, soft vignette.
- Logo: logo_c.png (transparent hive logo). Hook: 190px, pops in with back easing. Shot scenes: 96px, top center. CTA: 280px with a breathing gold glow.

## Motion vocabulary
- Headlines: blur-slide, word by word, 3.5 frames apart, 14 frames each, from 40px below and 10px blur.
- Screenshots: page-cam. Real UI screenshot settles from a 2.5D tilt (16deg X, -12deg Y) in 26 frames, then pushes slowly toward a focus rectangle.
- Focus: a gold rounded ring draws on around the focus area (16 frames), everything outside it dims to 55%.
- Numbers: digit roll (odometer) for the credits number on the CTA.
- CTA button: honey pill with masterphub.io, gentle pulse.
- Exits: 6 frame fade. No spins, no bounces on text, no flashing more than 3 times a second.

## Captions
- Every spoken line is also a caption: bottom, top 1600px, max width 940, 48px, dark glass pill (rgba(0,0,0,0.62)) with a thin gold border.
- Caption text = spoken text, except brand names: say "מאסטרפאב", show "Masterphub".
- Max two lines on screen. If a caption wraps to three lines, shorten the sentence.

## Voice
- edge-tts, rate +4%, leading and trailing silence trimmed (ffmpeg silenceremove at -45dB).
- Two narrators alternate by scene (male, female) when the video is longer than 20 seconds.
  - he: he-IL-AvriNeural / he-IL-HilaNeural
  - en: en-US-AndrewNeural / en-US-AvaNeural
  - es: es-MX-JorgeNeural / es-MX-DaliaNeural
  - fr: fr-FR-HenriNeural / fr-FR-DeniseNeural
  - pt: pt-BR-AntonioNeural / pt-BR-FranciscaNeural
  - ar: ar-SA-HamedNeural / ar-SA-ZariyahNeural
- Hebrew spoken lines: plain spelling, no niqqud with edge-tts (tested: niqqud made it worse). Don't put "ה" before פרומפט.
- If the proxy blocks edge-tts with a certificate error, append /root/.ccr/ca-bundle.crt to certifi's cacert.pem.

## Sound
- Music bed: bgm-tech-house.mp3 from 40s in, volume 0.11, fade in 10 frames, fade out last 30.
- swoosh-quick at every scene cut (0.22), impact-deep-whoosh at the CTA (0.25), sparkle-touch 18 frames later (0.3).

## Copy rules (stav-voice)
- Short sentences. No dashes of any kind. No hype words (amazing, revolutionary, game changer, מדהים, מהפכני).
- Hook = the viewer's problem as a question. Then what you do, what you get, what it costs, where to go.
- Every number must come from the product or a source. If you can't name it, cut it.
- Run voice_check.py on the script before rendering.

## Screenshots
- Capture the real tool at 958x854 with Chrome zoom (scale 1, save to disk). Scale below 1 saves a small file.
- Hide the user's real credit balance. Replace any em/en dash in on-screen UI text before capture.
- Remove browser extension bubbles and the scrollbar (inpaint the bubble at a fixed point, repeat column 940 over 943+).
- Hebrew UI for the Hebrew video, English UI for every other language.

## Render
- Remotion 4.0.484, headless shell: $(ls -d /opt/pw-browsers/chromium_headless_shell-1194/*/headless_shell)
- npx remotion render src/index.ts <Comp> out.mp4 --browser-executable=$B --concurrency=2 --timeout=120000
- Then ffmpeg -crf 25 -preset medium, AAC 128k, +faststart. Target under 10 MB.
- Check: pull a frame from the middle of every scene and read every line for overflow before you ship.

## Kit
The full Remotion project (components, assets, voice script) is the promo kit: the VAB promo is the reference build. Reuse base.tsx (Glow, Logo, Headline, Shot, Roll) and change only the copy, screenshots and focus rectangles.
