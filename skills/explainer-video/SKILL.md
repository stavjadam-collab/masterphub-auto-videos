---
name: "explainer-video"
description: "Make a short vertical (9:16) explainer or teaser video with an AI voiceover (Hebrew or English), animated branded scenes, burned-in captions and a handwritten signature."
---

# Explainer Video

Turns a list of scenes into a 1080x1920 MP4: each scene gets a spoken line (AI voice), a visual layout and a caption. Scene length follows the voice automatically.

## Setup (once)

```bash
pip install edge-tts pillow        # add --break-system-packages if pip asks
# ffmpeg must be installed: winget install ffmpeg  /  brew install ffmpeg  /  apt install ffmpeg
```
Fonts (Heebo for Hebrew, Anton, Caveat) download automatically on first run.
If edge-tts fails with a certificate error (corporate/TLS proxy), append the system CA bundle to certifi's cacert.pem.

## Workflow

1. Understand the goal: what the video explains, language (he/en), who it's for, any images the user gave (a product photo, a before/after pair, a result image).
2. Write the script: 5 to 8 scenes, one or two short spoken sentences each. Aim for 30 to 50 seconds total. Open with a hook, end with a call to action (a link or a thank-you).
3. Write `spec.json` (format below), next to the images.
4. Run: `python scripts/make_video.py spec.json out.mp4`
5. Check a few frames (e.g. `ffmpeg -ss 5 -i out.mp4 -frames:v 1 check.jpg`) for text overflow before handing the file over. Shorten titles if a line wraps into an image.

## Spec format

```json
{
  "lang": "he",
  "voice": "he-IL-AvriNeural",
  "rate": "+0%",
  "brand": {"name": "MASTERPHUB", "signature": "stavjadam", "accent": "#F5B400", "background": "#0D0B08", "text": "#F5ECD7"},
  "scenes": [
    {"type": "hero", "image": "result.png", "title": "הופכים לקריקטורה", "subtitle": "בארבעה צעדים", "say": "רוצים להפוך לקריקטורה? ככה עושים את זה."},
    {"type": "step", "step": 1, "title": "מעתיקים פרומפט", "card": {"title": "Pointing at You", "body": "short description", "button": "הועתק!"}, "say": "צעד ראשון. מעתיקים את הפרומפט."},
    {"type": "step", "step": 2, "title": "מצרפים תמונה", "image": "me.jpg", "subtitle": "תמונה אחת ברורה", "say": "צעד שני. מצרפים תמונה."},
    {"type": "compare", "title": "וזה מה שיוצא", "before": "me.jpg", "after": "result.png", "say": "וזו התוצאה."},
    {"type": "stat", "rows": [{"big": "50", "label": "פרומפטים"}, {"big": "+ 20", "label": "מטורפים"}], "button": "example.com", "say": "..."},
    {"type": "text", "image": "result.png", "title": "תודה ענקית", "highlight": "ליורי", "subtitle": "על הרעיון", "say": "תודה ליורי."}
  ]
}
```

- `say`: the spoken line. It is also the caption, unless `caption` is given. Use `caption` when the spoken form differs from the written one: write English brand names phonetically in `say` for the Hebrew voice ("מאסטרפאב", "צ'אט ג'י פי טי") and normally in `caption` ("masterphub.io", "ChatGPT").
- Keep English phrases inside Hebrew captions together with non-breaking spaces (` `), e.g. `"Pointing at You"`.
- Scene types: `hero` (big image + title), `step` (numbered step with an image, a text card, or just a subtitle), `compare` (before/after images, right-to-left in Hebrew), `stat` (big numbers + optional button), `text` (title/highlight/subtitle, optional image, optional button).
- Voices: Hebrew `he-IL-AvriNeural` (male, preferred) / `he-IL-HilaNeural` (female); English `en-US-AvaNeural` / `en-US-AndrewNeural`. List all: `edge-tts --list-voices`.
- Image paths are relative to the spec file. Photos of real people: only the user's own or with their consent.

## Writing tips
- Short sentences. One idea per scene.
- Titles: 2 to 3 words so they fit on one line.
- Hebrew content for an audience: gender-neutral plural ("מעתיקים", "מצרפים").

## Script craft (story arc, copy rules, checks)
Write the script as five beats, then map beats to scenes:
1. Question (first 10%): open on the thing people get wrong, as an image, not a title card.
2. Model (10 to 35%): the smallest correct picture of how it works, one element per beat.
3. Proof (35 to 75%): one real case, cause and effect shown on screen.
4. Turn (75 to 90%): change one variable and show what follows.
5. Payoff (last 10%): the opening image again, now read correctly, plus one next step.

Discovery before writing: say the one idea in the viewer's own words, split facts into must-know and cut list (the cut list stays out), find the belief most viewers hold that turns out to be wrong.

Copy rules:
- Max two short lines on screen at once. Plain words before jargon.
- One name per thing, used every time.
- Every number has a source. If you cannot name it, cut it.
- Do not ask for approval on creative calls. Decide, and log the decision in one line. Stop only for missing rights, unsafe content, or an ambiguity that changes the goal.

Hebrew voice rule: use the male voice `he-IL-AvriNeural`, rate +0%. Write `say` in plain spelling without niqqud (niqqud made the voice worse in testing), and keep `caption` identical. Do not attach the prefix "ה" to the word פרומפט in spoken text (the voice mispronounces it); reword the sentence. Listen to the result once with the user before publishing.

Checks before handing over (do not just claim them):
- Watch it muted: the sequence of captions alone should tell the story.
- Listen with the picture off: the voice alone should carry the logic.
- Captions at least 4.5:1 contrast, no flashing over 3 times a second, nothing on screen longer than the voice needs.
- Pull frames at the start, middle and end of each scene (`ffmpeg -ss T -i out.mp4 -frames:v 1`) and read every line for overflow.
- Keep a short before/after pair of any frame you fixed.