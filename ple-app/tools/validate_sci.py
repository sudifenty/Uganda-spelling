#!/usr/bin/env python3
"""
validate_sci.py — checks the Science practice datasets.

Enforces the same separation rules as the other banks: class purity, subject
purity, unique IDs, unique questions, four distinct options, one correct
answer, explanation, topic and subtopic on every record.
"""
import json, sys, glob, os, re
from collections import Counter

ERRORS, WARNINGS = [], []
def err(f, m): ERRORS.append(f"  [ERROR] {f}: {m}")
def warn(f, m): WARNINGS.append(f"  [warn ] {f}: {m}")
norm = lambda t: re.sub(r"[^a-z0-9 ]", "", str(t).lower()).strip()


def check(path, seen_ids, seen_text, byclass):
    name = os.path.basename(path)
    d = json.load(open(path, encoding="utf-8"))
    cls, qs = d.get("class"), d.get("questions", [])
    if cls not in ("P4", "P5", "P6", "P7"):
        err(name, f"bad class {cls!r}"); return

    for q in qs:
        qid = q.get("id", "?")
        if q.get("class") != cls:
            err(name, f"CLASS MIXING — {qid} has class={q.get('class')!r} in a {cls} file")
        if not str(qid).startswith(f"{cls}_SCI_"):
            err(name, f"CLASS MIXING — {qid} ID prefix does not match {cls}")
        if q.get("subject") != "Science":
            err(name, f"SUBJECT MIXING — {qid} subject is {q.get('subject')!r}, expected Science")

        if qid in seen_ids:
            err(name, f"duplicate ID {qid}")
        seen_ids[qid] = name
        k = norm(q.get("question"))
        if k in seen_text:
            err(name, f"duplicate question — {qid} repeats {seen_text[k]}")
        seen_text[k] = qid

        for fld in ("topic", "subtopic", "explanation", "question"):
            if not str(q.get(fld) or "").strip():
                err(name, f"{qid} missing {fld}")
        if q.get("difficulty") not in ("Easy", "Medium", "Hard"):
            err(name, f"{qid} bad difficulty {q.get('difficulty')!r}")

        opts = q.get("options") or []
        if len(opts) != 4:
            err(name, f"{qid} has {len(opts)} options, expected 4")
        bodies = [re.sub(r"^[A-D]\.\s*", "", o).strip() for o in opts]
        if len(set(bodies)) != len(bodies):
            err(name, f"{qid} has duplicate option text")
        if q.get("correctAnswer") not in set("ABCD"):
            err(name, f"{qid} correctAnswer {q.get('correctAnswer')!r} invalid")

        txt = norm(q.get("question"))
        for p in ("diagram below", "figure below", "picture below", "shown below"):
            if p in txt and not q.get("image"):
                err(name, f"{qid} refers to '{p}' but has no image")

    nums = sorted(int(q["id"].split("_")[-1]) for q in qs)
    if nums != list(range(1, len(qs) + 1)):
        err(name, f"{cls} IDs are not sequential 001..{len(qs):03d}")

    byclass[cls] = qs
    tp = Counter(q["topic"] for q in qs)
    dd = Counter(q["difficulty"] for q in qs)
    print(f"  {name:16} {cls}  {len(qs):>3} questions  {len(tp):>2} topics  "
          f"E{dd['Easy']}/M{dd['Medium']}/H{dd['Hard']}")


def main():
    files = sorted(glob.glob("data/practice/sci-p*.json"))
    if not files:
        print("No Science datasets found."); return 0
    print(f"\nChecking {len(files)} dataset(s)\n" + "-" * 68)
    seen_ids, seen_text, byclass = {}, {}, {}
    for f in files:
        check(f, seen_ids, seen_text, byclass)
    print("-" * 68)

    print("\nCROSS-CLASS PURITY")
    cl = sorted(byclass)
    if len(cl) < 2:
        print(f"  only {cl[0] if cl else 'no'} class has Science content")
    for i, a in enumerate(cl):
        for b in cl[i + 1:]:
            sh = {norm(q["question"]) for q in byclass[a]} & {norm(q["question"]) for q in byclass[b]}
            if sh:
                err("cross-class", f"{a} and {b} share {len(sh)} question(s)")
            print(f"  {a} vs {b}: {'OK' if not sh else str(len(sh))+' SHARED'}")

    # Science must not collide with SST or Mathematics either
    print("\nCROSS-SUBJECT PURITY")
    for other, label in (("sst-p*.json", "SST"), ("math-p*.json", "Mathematics")):
        otxt = set()
        for f in glob.glob(f"data/practice/{other}"):
            for q in json.load(open(f, encoding="utf-8"))["questions"]:
                otxt.add(norm(q["question"]))
        clash = sum(1 for qs in byclass.values() for q in qs if norm(q["question"]) in otxt)
        if clash:
            err("cross-subject", f"Science shares {clash} question(s) with {label}")
        print(f"  Science vs {label}: {'OK' if not clash else str(clash)+' SHARED'}")

    for w in WARNINGS: print(w)
    for e in ERRORS: print(e)
    print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
    if ERRORS:
        print("FAILED\n"); return 1
    print("PASSED — class and subject purity verified.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
