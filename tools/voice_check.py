#!/usr/bin/env python3
"""Masterphub voice check: run on any text before it goes out.

Usage:
  python3 voice_check.py file1.html file2.md      # check files
  echo "text" | python3 voice_check.py -           # check stdin
  python3 voice_check.py --fix-dashes file.html    # also rewrite dashes in place

Fails (exit 1) on: em/en dashes, banned hype words, AI-tell phrases.
Lists (no fail): every sentence with a number, so each number can be matched to a source.
"""
import re, sys, html

DASH = re.compile(r"[—–]")
BANNED_EN = ["leverage", "utilize", "synergy", "dive into", "let's explore", "it's worth noting", "game changer",
    "game-changer", "unlock", "elevate", "this matters", "why it matters", "matters most", "just as important",
    "is more than a", "rather than simply", "not only about", "what comes next", "looking ahead",
    "adds another layer", "in practice", "dependable", "thoughtful", "meaningful", "is especially helpful",
    "can help you", "makes it easier", "helps you avoid", "perhaps the most", "the most powerful",
    "one of the best things about", "revolutionary", "groundbreaking", "cutting-edge", "seamless", "in today's world"]
BANNED_HE = ["מדהים", "מרתק", "פנומנלי", "יוצא דופן", "מהפכני", "בהחלט", "בוודאי", "כמובן", "בעולם של היום",
    "שאלה מצוינת", "אני כאן לכל שאלה", "זה חשוב", "למה זה חשוב", "מה שהכי חשוב", "חשוב לא פחות",
    "זה לא רק", "יותר מסתם", "ולא פשוט", "מה שבא אחר כך", "במבט קדימה", "מוסיף עוד שכבה",
    "יכול לעזור לך", "מקל על", "עוזר להימנע", "שימושי במיוחד", "אולי הכי", "הכי פופולרי", "חשוב לציין"]
NUM = re.compile(r"\d[\d,.]*\s*(%|x|k|m|b|\$|₪|מיליון|מיליארד|אלף)?", re.I)

def clean(t):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t)

def check(name, raw):
    text = clean(raw)
    errors, numbers = [], []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if DASH.search(line):
            errors.append((i, "dash", line.strip()))
        for w in BANNED_EN:
            if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
                errors.append((i, f"banned: {w}", line.strip()))
        for w in BANNED_HE:
            if w in line:
                errors.append((i, f"banned: {w}", line.strip()))
        for s in re.split(r"(?<=[.!?])\s+", line):
            if NUM.search(s) and not re.fullmatch(r"\s*\d+[.)]\s*", s):
                numbers.append((i, s.strip()))
    print(f"== {name}: {len(errors)} problem(s), {len(numbers)} sentence(s) with numbers")
    for i, kind, l in errors:
        print(f"  FAIL line {i} [{kind}]: {l[:160]}")
    for i, s in numbers[:40]:
        print(f"  NUM  line {i}: {s[:160]}")
    return len(errors)

def fix_dashes(t):
    out = []
    for line in t.split("\n"):
        to = " עד " if re.search(r"[֐-׿]", line) else " to "
        line = re.sub(r"(\d)\s*[–—]\s*(\d)", lambda m: m.group(1) + to + m.group(2), line)
        line = re.sub(r"\s*[—–]\s*", ", ", line)
        out.append(line)
    return "\n".join(out)

if __name__ == "__main__":
    args = sys.argv[1:]
    fix = "--fix-dashes" in args
    args = [a for a in args if a != "--fix-dashes"] or ["-"]
    bad = 0
    for a in args:
        raw = sys.stdin.read() if a == "-" else open(a, encoding="utf-8").read()
        if fix and a != "-":
            raw = fix_dashes(raw)
            open(a, "w", encoding="utf-8").write(raw)
        bad += check(a, raw)
    sys.exit(1 if bad else 0)
