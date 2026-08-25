#!/usr/bin/env python3
"""
validate_notes_practice.py — safety checks on the practice questions that were
derived from the study notes.

Rules enforced:

  1. Class and subject must match the file they live in (no mixing).
  2. Exactly four options, labelled A, B, C, D in order.
  3. The letter in correctAnswer must point at the option holding the right
     answer — checked against answerValue, not assumed.
  4. No other option may repeat, contain, or be contained by the right answer.
  5. Every option must be non-empty and distinct.
  6. No duplicate question ids and no duplicate stems inside a file.
  7. Every question must say where it came from, and must never claim UNEB.
  8. Every class+subject that has notes must reach the 100-question target.

Usage: python3 tools/validate_notes_practice.py
"""
import json, glob, re, sys

TARGET = 100
LETTERS = "ABCD"
# a claim of UNEB origin is banned; the standard disclaimer is not a claim
DISCLAIMER = "not a UNEB past paper"
BANNED = re.compile(r"\buneb\b|according to (the )?(teacher'?s guide|mk )", re.I)


def main():
    files = sorted(glob.glob("data/practice/notes-*.json"))
    if not files:
        print("  no notes-derived practice files — nothing to validate")
        return 0

    errors, total = [], 0
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        ids, stems = set(), set()

        for q in d["questions"]:
            total += 1
            tag = f"{f} {q['id']}"

            if q["class"] != cls or q["subject"] != subj:
                errors.append(f"{tag}: wrong class/subject "
                              f"({q['class']}/{q['subject']} in {cls}/{subj})")
            if not q["id"].startswith(f"{cls}_"):
                errors.append(f"{tag}: id does not start with {cls}_")
            if q["id"] in ids:
                errors.append(f"{tag}: duplicate id")
            ids.add(q["id"])

            key = re.sub(r"\W+", "", q["question"].lower())[:90]
            if key in stems:
                errors.append(f"{tag}: duplicate question stem")
            stems.add(key)
            if len(q["question"].split()) < 3:
                errors.append(f"{tag}: stem too short")

            opts = q["options"]
            if len(opts) != 4:
                errors.append(f"{tag}: {len(opts)} options, expected 4")
                continue
            texts = []
            for i, o in enumerate(opts):
                want = f"{LETTERS[i]}. "
                if not o.startswith(want):
                    errors.append(f"{tag}: option {i+1} is not labelled {want.strip()}")
                    texts.append(o)
                else:
                    texts.append(o[len(want):])
            if len(set(t.strip().lower() for t in texts)) != 4:
                errors.append(f"{tag}: two options are the same")
            if any(not t.strip() for t in texts):
                errors.append(f"{tag}: an option is empty")

            letter = q.get("correctAnswer", "")
            if letter not in LETTERS:
                errors.append(f"{tag}: correctAnswer {letter!r} is not A-D")
                continue
            av = (q.get("answerValue") or "").strip()
            if not av:
                errors.append(f"{tag}: no answerValue to check against")
                continue
            at = texts[LETTERS.index(letter)].strip()
            if at != av:
                errors.append(f"{tag}: correctAnswer points at {at!r} "
                              f"but the answer is {av!r}")
            for i, t in enumerate(texts):
                if i == LETTERS.index(letter):
                    continue
                tl, al = t.strip().lower(), av.lower()
                if tl == al:
                    errors.append(f"{tag}: option {LETTERS[i]} repeats the answer")
                elif len(al) > 6 and (tl in al or al in tl):
                    errors.append(f"{tag}: option {LETTERS[i]} overlaps the answer")

            if not q.get("origin"):
                errors.append(f"{tag}: no origin recorded")
            blob = json.dumps(q, ensure_ascii=False).replace(DISCLAIMER, "")
            if BANNED.search(blob):
                errors.append(f"{tag}: claims a source that is not held")

        short = "" if len(d["questions"]) >= TARGET else \
                f"  BELOW TARGET ({len(d['questions'])}/{TARGET})"
        if short:
            errors.append(f"{f}: only {len(d['questions'])} questions, "
                          f"target is {TARGET}")
        print(f"  {f}: {len(d['questions'])} questions — checked{short}")

    if errors:
        for e in errors[:40]:
            print("  FAIL:", e)
        sys.exit(f"validate_notes_practice: {len(errors)} problem(s)")
    print(f"  all {total} notes-derived practice questions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
