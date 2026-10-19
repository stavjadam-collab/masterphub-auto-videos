# EffectCraft — שיטת קליפים (19.10.26, קליפ "אהובתי" / "My Love")

## התקנה (בסביבה של קלוד)
- git clone --depth 1 https://github.com/storytold/effectcraft ; cargo build --release -p effectcraft-cli (כ-25 דקות על 2 ליבות, בינארי 86MB).
- גופנים: ~/.fonts — Heebo (כתוביות עברית/אנגלית, d.font="Heebo"; d.fauxBold=true), AmaticSC-Bold (כותרת), HomemadeApple-Regular (חתימה stavjadam).

## איך זה עובד
- gen.py <he|en> בונה סקריפט JSX בסגנון After Effects מהמילים + תזמון מילים מ-faster-whisper (word_timestamps) + 12 תמונות סצנה.
- effectcraft-cli script ml-he.jsx → ml-he.ecproj ; render --format h264 בשני חלקים במקביל (--start/--end), ואז ffmpeg concat + אודיו מקורי.
- עברית מימין לשמאל עובדת בשכבות טקסט. שמות פרמטרים של אפקטים = השמות שמופיעים ב-property(i).name (למשל "Transition Completion", "Glow Radius", "Master Saturation").

## אפקטים בשימוש
CC Rainfall, CC Snowfall (אבקה/אבק באור), CC Light Sweep, Linear/Radial Wipe (חשיפה), CC Page Turn / CC Light Wipe / Iris (מעברים), Lens Flare, Hue/Saturation (אפור→צבע), Glow (רדיוס 12), CC Vignette, wiggle/sin על Rotation.

## ביצועים
- יקרים מאוד: Drop Shadow על טקסט (כ-240ms לפריים, כי שכבת טקסט בגודל הקומפוזיציה), Add Grain (כ-230ms), Glow ברדיוס גדול. במקום צל — Stroke של הטקסט (applyStroke, strokeOverFill=false).
- אחרי אופטימיזציה: כ-1.2 שניות לפריים לכל תהליך כשרצים 2 במקביל → שיר של 3.5 דקות ב-24fps ≈ 50 דקות.

## תמונות
- ג'מיני, שיחה https://gemini.google.com/app/e4473ba683a91d44 — תמונת הייחוס של אור (שיער אדום גלי, משקפיים חומים, מלאה ועגולה) + Downloads\Gemini_Generated_Image_7tfaik7tfaik7tfa.jpeg (הדמות של סתיו משמאל). סתיו אישר ml-s00..s11b, תוקנו s07b/s08b/s09b (הפנים שלו) ו-s04/s05 (אור מעוגלת יותר).
