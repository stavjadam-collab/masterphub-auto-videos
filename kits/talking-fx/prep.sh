#!/usr/bin/env bash
# הכנה: קליפ מהטלפון -> work/ עם הרקע, הדמות השקופה והאורך
# שימוש: bash prep.sh clip.mp4 [work_dir]
set -e
SRC="$1"; W="${2:-work}"; mkdir -p "$W"
cp gsap.min.js template.html "$W/"
# אנכי 1080x1920, 30 פריימים, בלי לשנות את הסאונד
ffmpeg -loglevel error -y -i "$SRC" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" -c:v libx264 -crf 16 -c:a aac "$W/video.mp4"
# הדמות בלי רקע (מודל מקומי, בערך 0.6 שניות לפריים)
npx -y hyperframes remove-background "$W/video.mp4" -o "$W/person.webm"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/video.mp4")
sed -i "s/{{DUR}}/$D/g" "$W/template.html"; mv "$W/template.html" "$W/index.html"
echo "ready: $W  duration=$D"
