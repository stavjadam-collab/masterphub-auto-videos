---
name: "masterphub-motion"
description: "Use when building any Masterphub promo, teaser or explainer video (Remotion, honeycomb brand, voiceover, multi-language). Holds the house motion style and the promo kit."
---

# Masterphub motion style (MOTION.md)

Read this before building any Masterphub promo, teaser or explainer video. It is the house style. If a request conflicts with it, follow the request and keep everything else from here.

## Start from the kit
- Download: curl -sSLo kit.zip https://izwsmxwjimowaioyplza.supabase.co/storage/v1/object/public/downloads/templates/promo-kit.zip && unzip -oq kit.zip && cd promo-kit
- Contains: src/ (base.tsx with Glow, Logo, Headline, Shot, Roll; Promo.tsx; Root.tsx; copy.json), public/ (logo, music, sfx, reference screenshots), voice_script.py (edge-tts + timing json), clean_screens.py (removes scrollbar and extension bubbles), voice_check.py, fonts/, MOTION.md.
- Install fonts: mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts && fc-cache -f
- npm install remotion@4.0.484 @remotion/cli@4.0.484 react react-dom (or reuse an existing node_modules).
- Change only: copy (voice_script.py), screenshots, and focus rectangles in Promo.tsx.

## Format
- 1080x1920, 30 fps, vertical. 16:9 only when asked.
- Length follows the voice: each scene = voice line + 8 frames lead + 18 frames tail. Hook scene gets +30 frames. CTA holds about 2 seconds after the last word.
- Typical promo: 30 to 50 seconds, 7 scenes + CTA.

## Color and type
- Background #0f0f0f. Honey gold #f7c31a. Text #f4f1ea. Dim text rgba(244,241,234,0.62).
- Hebrew: Heebo 900 headlines, 700 captions. Arabic: Noto Kufi Arabic. Latin: Heebo, Inter.
- Accent words in honey gold, marked in copy with *asterisks*. One or two per headline.
- Fonts installed system-wide. Never load fonts at runtime with FontFace/loadFont: it hangs full renders.

## Brand layer
- Background is always the animated honeycomb (Glow): gold hex cells, a slow wandering light, soft vignette.
- Logo logo_c.png. Hook: 190px, pops in with back easing. Shot scenes: 96px top center. CTA: 280px with a breathing gold glow.

## Motion vocabulary
- Headlines: blur-slide, word by word, 3.5 frames apart, 14 frames each, from 40px below and 10px blur.
- Screenshots: page-cam. Real UI screenshot settles from a 2.5D tilt (16deg X, -12deg Y) in 26 frames, then pushes toward a focus rectangle.
- Focus: gold rounded ring draws on (16 frames), everything outside dims to 55%.
- Numbers: digit roll on the CTA credits number. CTA button: honey pill with masterphub.io, gentle pulse.
- Exits: 6 frame fade. No spins, no bouncing text, no more than 3 flashes per second.

## Captions
- Every spoken line is also a caption: top 1600px, max width 940, 48px, dark glass pill with a thin gold border.
- Caption = spoken text, except brand names: say "מאסטרפאב", show "Masterphub".
- Max two lines. If it wraps to three, shorten the sentence.

## Voice
- edge-tts, rate +4%, trim leading and trailing silence (ffmpeg silenceremove at -45dB).
- Two narrators alternate by scene (male, female) when longer than 20 seconds:
  - he: he-IL-AvriNeural / he-IL-HilaNeural
  - en: en-US-AndrewNeural / en-US-AvaNeural
  - es: es-MX-JorgeNeural / es-MX-DaliaNeural
  - fr: fr-FR-HenriNeural / fr-FR-DeniseNeural
  - pt: pt-BR-AntonioNeural / pt-BR-FranciscaNeural
  - ar: ar-SA-HamedNeural / ar-SA-ZariyahNeural
- Hebrew spoken text for edge-tts: plain spelling, no niqqud (tested worse). Don't put "ה" before פרומפט.
- Certificate error from edge-tts behind the proxy: append /root/.ccr/ca-bundle.crt to certifi's cacert.pem.

## Sound
- Music: bgm-tech-house.mp3 from 40s in, volume 0.11, fade in 10 frames, fade out last 30.
- swoosh-quick at every cut (0.22), impact-deep-whoosh at the CTA (0.25), sparkle-touch 18 frames later (0.3).

## Copy
- Follow stav-voice. Short sentences, no dashes, no hype words.
- Hook = the viewer's problem as a question. Then what it does, what you get, what it costs, where to go.
- Every number comes from the product or a source.
- Run python3 voice_check.py on the script text before rendering.

## Screenshots
- Capture the real tool with Chrome zoom at full viewport, scale 1, save to disk (scale below 1 saves a small file).
- Hide the user's real credit balance. Replace em/en dashes in on-screen UI text before capture.
- Run clean_screens.py to remove the scrollbar and extension bubbles; check a crop of the right edge.
- Hebrew UI for the Hebrew video, English UI for every other language.

## Render and check
- B=$(ls -d /opt/pw-browsers/chromium_headless_shell-1194/*/headless_shell)
- npx remotion render src/index.ts <Comp> out.mp4 --browser-executable=$B --concurrency=2 --timeout=120000
- Run at most two renders in parallel.
- Compress: ffmpeg -crf 25 -preset medium, AAC 128k, -movflags +faststart. Target under 10 MB.
- Pull one frame from the middle of every scene in every language and read every line for overflow before shipping.
- Upload to assets/videos/<name>-<lang>.mp4 with the anon key (new file names only; anon can't overwrite).