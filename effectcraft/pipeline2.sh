#!/bin/bash
# finishes the Hebrew clip, renders + finishes English. Adds the song cover on the last 7 seconds.
cd /home/claude/mv
EC=/home/claude/ec/effectcraft/target/release/effectcraft-cli
finish() { # lang
  L=$1
  D=$(python3 -c "import json;print(json.load(open('plan-$L.json'))['dur'])")
  CS=$(python3 -c "print(round($D-7,2))")
  printf "file '%s_a.mp4'\nfile '%s_b.mp4'\n" $L $L > list_$L.txt
  ffmpeg -v error -y -f concat -safe 0 -i list_$L.txt -c copy ${L}_v.mp4
  # cover card: fades in over the ending, centered, 860px, soft shadow-free
  ffmpeg -v error -y -i ${L}_v.mp4 -loop 1 -i cover.jpg -i ${L}.mp3 \
    -filter_complex "[1:v]scale=860:860,format=rgba,fade=t=in:st=${CS}:d=2.5:alpha=1[cv];[0:v][cv]overlay=(W-w)/2:(H-h)/2:enable='gte(t,${CS})':shortest=1[v]" \
    -map "[v]" -map 2:a -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart ${L}_final.mp4
  # small copy under 29MB for the computer folder (x265, 2-pass)
  VB=$(python3 -c "print(int((28.5*8*1024)/$D - 160))")
  ffmpeg -v error -y -i ${L}_final.mp4 -c:v libx265 -b:v ${VB}k -x265-params pass=1:log-level=error -an -f null /dev/null
  ffmpeg -v error -y -i ${L}_final.mp4 -c:v libx265 -b:v ${VB}k -x265-params pass=2:log-level=error -tag:v hvc1 -c:a aac -b:a 128k -movflags +faststart ${L}_small.mp4
  echo "$L done $(date) $(du -h ${L}_final.mp4 ${L}_small.mp4 | tr '\n' ' ')" >> pipeline.log
}
while pgrep -f "out he_" >/dev/null; do sleep 20; done
finish he
D=$(python3 -c "import json;print(json.load(open('plan-en.json'))['dur'])"); H=$(python3 -c "print(round($D/2,2))")
$EC render --project ml-en.ecproj --comp ML --out en_a.mp4 --format h264 --start 0 --end $H --audio off --progress > r_en_a.log 2>&1 &
$EC render --project ml-en.ecproj --comp ML --out en_b.mp4 --format h264 --start $H --end $D --audio off --progress > r_en_b.log 2>&1 &
wait
finish en
