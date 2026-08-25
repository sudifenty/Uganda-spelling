#!/usr/bin/env python3
"""
decode_p4_math.py — recover readable text from P4-MATHEMATICS.pdf.

The NCDC P.4 Mathematics PDF embeds subset fonts with no ToUnicode map, so
ordinary text extraction returns control characters (only 12.6% letters).
pdfminer returns (cid:NNN) codes instead, and those codes follow a fixed
offset, worked out from letter frequency and context:

    cid 3          -> space
    cid 4..29      -> A..Z        (cid = ord(ch) - 61)
    cid 131..156   -> a..z        (cid = ord(ch) + 34)
    cid 882..891   -> 0..9
    punctuation    -> the PUNCT table below, each confirmed from context

Result: 65.8% letters — the syllabus content is readable.

Usage: python3 tools/decode_p4_math.py     (run from the ple-app folder)
Writes: curriculum/_p4_math_raw.txt
"""
import re, sys
from pdfminer.high_level import extract_text

SRC = "curriculum/P4-MATHEMATICS.pdf"
OUT = "curriculum/_p4_math_raw.txt"

PUNCT = {3:' ', 484:'.', 481:',', 486:'-', 483:':', 482:';',
         523:'(', 524:')', 491:'?', 823:'@', 428:'&', 512:'/',
         934:'[half]', 938:'[box]', 945:'='}
# page furniture and decorative glyphs — dropped
DROP = {349, 448, 454, 430, 1004, 1005, 1006, 1007, 1008, 1009,
        1010, 1011, 1012, 1013}

MAP = dict(PUNCT)
for i in range(26):
    MAP[4 + i]   = chr(ord('A') + i)
    MAP[131 + i] = chr(ord('a') + i)
for i in range(10):
    MAP[882 + i] = str(i)


def main():
    raw = extract_text(SRC)
    out = re.sub(r"\(cid:(\d+)\)",
                 lambda m: '' if int(m.group(1)) in DROP
                           else MAP.get(int(m.group(1)), ''),
                 raw)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    open(OUT, "w", encoding="utf-8").write(out)
    letters = len(re.findall(r"[A-Za-z]", out))
    pct = letters / max(len(out), 1) * 100
    print(f"  {OUT}: {len(out):,} chars, {letters:,} letters ({pct:.1f}%)")
    if pct < 50:
        sys.exit("decode_p4_math: output still looks garbled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
