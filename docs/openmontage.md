# OpenMontage בשרת

- שרת: SERVER_IP, תיקייה /opt/openmontage.
- Claude Code רץ שם בתוך tmux בשם montage, מחובר כ-Remote Control בשם "Montage". כותבים לו מ-claude.ai/code או מהאפליקציה.
- אחרי ריסטארט לשרת: `tmux new -A -s montage "cd /opt/openmontage && claude --remote-control Montage"`.
- קריינות חינמית באנגלית (Piper), תמלול (faster_whisper), תמונות ווידאו סטוק (Pixabay). אין GPU.
- חסר: מפתח ElevenLabs לעברית, FAL_KEY לתמונות AI.
- פרטים: מסמך הפרויקט claude/openmontage-install-2026-10-15.md.
