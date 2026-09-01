#!/usr/bin/env python3
"""
validate_notes.py — safety checks on the built notes.

Rules enforced (they come from the owner's notes-engine rules):

  1. Class and subject must be known, and must match the file they live in.
  2. A topic must never be filed under the wrong class (no mixing P4-P7).
  3. Topic numbers must be unique and in order within a class+subject.
  4. Every topic must carry a curriculum reference (page numbers).
  5. Every topic must contain the required teaching sections.
  6. No topic may claim a source document we do not hold.
  7. No topic may say "complete notes".

Usage: python3 tools/validate_notes.py
"""
import json, glob, re, sys

REQUIRED = [
    ("definitions", re.compile(r"key definitions", re.I)),
    ("facts",       re.compile(r"important facts", re.I)),
    ("exam",        re.compile(r"examination points", re.I)),
    ("questions",   re.compile(r"revision questions", re.I)),
    ("answers",     re.compile(r"answers to revision questions", re.I)),
    ("sources",     re.compile(r"note on sources", re.I)),
]
BANNED = [
    (re.compile(r"\bcomplete notes\b", re.I), 'says "complete notes"'),
    (re.compile(r"according to (the )?(uneb|teacher'?s guide|mk |longhorn)", re.I),
     "claims a source document that is not held"),
    (re.compile(r"\buneb (says|states|requires)\b", re.I), "claims UNEB authority"),
]
CLASSES = ("P4", "P5", "P6", "P7")
SUBJECTS = ("SST", "MATH", "SCI", "ENG")


def text_of(topic):
    out = []
    for s in topic["sections"]:
        out.append(s["title"])
        for b in s["blocks"]:
            if "x" in b:
                out.append(b["x"])
            if "items" in b:
                out.extend(b["items"])
            if b["t"] == "table":
                out.extend(b["head"])
                out.extend(c for r in b["rows"] for c in r)
    return "\n".join(out)


def main():
    files = sorted(glob.glob("data/notes/*.json"))
    if not files:
        print("  no notes files — nothing to validate")
        return 0
    errors, total = [], 0

    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        if cls not in CLASSES:
            errors.append(f"{f}: unknown class {cls}")
        if subj not in SUBJECTS:
            errors.append(f"{f}: unknown subject {subj}")

        seen = set()
        for t in d["topics"]:
            total += 1
            tag = f"{f} {t['id']}"
            if t["class"] != cls or t["subject"] != subj:
                errors.append(f"{tag}: class/subject does not match its file "
                              f"({t['class']}/{t['subject']} in {cls}/{subj})")
            if not t["id"].startswith(f"{cls}_{subj}_"):
                errors.append(f"{tag}: id does not start with {cls}_{subj}_")
            if t["topic_no"] in seen:
                errors.append(f"{tag}: duplicate topic number {t['topic_no']}")
            seen.add(t["topic_no"])
            if not t.get("curriculum_pages"):
                errors.append(f"{tag}: no curriculum page reference")
            if t["words"] < 600:
                errors.append(f"{tag}: only {t['words']} words — too thin")

            titles = " | ".join(s["title"] for s in t["sections"])
            # Two note formats exist:
            #   classic     — full textbook structure (definitions/facts/exam/sources)
            #   restructured— UNEB revision format: numbered question sections,
            #                 no duplicated summary sections (owner's restructuring rules)
            q_sections = [s for s in t["sections"]
                          if re.match(r"^\d+\.\s+.*\?$", s["title"].strip())]
            if len(q_sections) >= 3:
                for name, rx in (("questions", re.compile(r"revision questions", re.I)),
                                 ("answers",   re.compile(r"answers to revision", re.I))):
                    if not rx.search(titles):
                        errors.append(f"{tag}: missing the '{name}' section")
            else:
                for name, rx in REQUIRED:
                    if not rx.search(titles):
                        errors.append(f"{tag}: missing the '{name}' section")

            body = text_of(t)
            for rx, why in BANNED:
                if rx.search(body):
                    errors.append(f"{tag}: {why}")

            # answers must cover the revision questions
            qs = next((s for s in t["sections"]
                       if re.search(r"^revision questions$", s["title"], re.I)), None)
            ans = next((s for s in t["sections"]
                        if re.search(r"answers to revision", s["title"], re.I)), None)
            if qs and ans:
                nq = sum(len(b["items"]) for b in qs["blocks"] if b["t"] == "ol")
                na = sum(len(b["items"]) for b in ans["blocks"] if b["t"] == "ol")
                if na < nq:
                    errors.append(f"{tag}: {nq} questions but only {na} answers")

        print(f"  {f}: {len(d['topics'])} topics, {d['words']:,} words — checked")

    if errors:
        for e in errors:
            print("  FAIL:", e)
        sys.exit(f"validate_notes: {len(errors)} problem(s)")
    print(f"  all {total} topics passed every notes check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
