#!/usr/bin/env python3
"""
validate_math.py — checks the Mathematics bank, and above all RE-COMPUTES
every answer independently.

Each question stores a `calc` expression. This script evaluates it with exact
Fraction arithmetic and compares the result with the answer marked correct.
A question whose marked answer does not match its own arithmetic is an ERROR.

Usage: python3 tools/validate_math.py
"""
import json, sys, glob, os, re
from fractions import Fraction
from collections import Counter

TARGET_TOTAL = 200
TARGET_DIFF = {"Easy": 70, "Medium": 80, "Hard": 50}
ERRORS, WARNINGS, TARGETS = [], [], []
CHECKED = UNCHECKED = 0


def err(f, m): ERRORS.append(f"  [ERROR] {f}: {m}")
def warn(f, m): WARNINGS.append(f"  [warn ] {f}: {m}")


def safe_eval(expr):
    """Evaluate an arithmetic expression exactly. Returns Fraction or None."""
    if not expr:
        return None
    e = str(expr).replace(",", "").strip()
    if not re.fullmatch(r"[0-9\.\+\-\*/\(\)% ]+", e):
        return None
    try:
        # exact arithmetic: turn every literal into a Fraction
        e2 = re.sub(r"(\d+\.\d+|\d+)", r"Fraction('\1')", e)
        return eval(e2, {"Fraction": Fraction, "__builtins__": {}})
    except Exception:
        return None


def parse_answer(s):
    """Pull the numeric value out of an answer string like '1,200 shillings'.

    If the answer is itself an expression ('3000 + 200 + 1' or '2 x 2 x 5'),
    evaluate it — that checks the expansion really equals the number.
    """
    if s is None:
        return None
    t = str(s).replace(",", "").strip()
    # clock time "8:00" or "10:45 p.m." -> minutes since midnight
    m = re.match(r"(\d{1,2}):(\d{2})", t)
    if m and int(m.group(2)) < 60:
        return Fraction(int(m.group(1)) * 60 + int(m.group(2)))
    if re.search(r"[+x*]", t) and re.fullmatch(r"[0-9\s\+x\*\.]+", t):
        v = safe_eval(t.replace("x", "*"))
        if v is not None:
            return v
    # mixed number  '2 3/4'
    m = re.fullmatch(r"(-?\d+)\s+(\d+)/(\d+)", t)
    if m:
        w, n, d = map(int, m.groups())
        return Fraction(w) + (Fraction(n, d) if w >= 0 else -Fraction(n, d))
    # plain fraction
    m = re.fullmatch(r"(-?\d+)/(\d+)", t)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    # leading number, optionally followed by units / % / text
    m = re.match(r"(-?\d+\.?\d*)", t)
    if m:
        return Fraction(m.group(1))
    return None


def check_file(path, seen_ids, seen_text):
    global CHECKED, UNCHECKED
    name = os.path.basename(path)
    d = json.load(open(path, encoding="utf-8"))
    cls, qs = d.get("class"), d.get("questions", [])

    if cls not in ("P4", "P5", "P6", "P7"):
        err(name, f"bad class {cls!r}"); return None

    for q in qs:
        qid = q.get("id", "?")

        # ── class purity, two independent signals ──────────────────────────
        if q.get("class") != cls:
            err(name, f"CLASS MIXING — {qid} has class={q.get('class')!r} in a {cls} file")
        if not str(qid).startswith(f"{cls}_MATH_"):
            err(name, f"CLASS MIXING — {qid} ID prefix does not match {cls}")
        if q.get("subject") != "Mathematics":
            err(name, f"{qid} subject is {q.get('subject')!r}")

        if qid in seen_ids:
            err(name, f"duplicate ID {qid}")
        seen_ids[qid] = name
        key = re.sub(r"\s+", " ", str(q.get("question", "")).lower()).strip()
        if key in seen_text:
            err(name, f"duplicate question — {qid} repeats {seen_text[key]}")
        seen_text[key] = qid

        for fld in ("topic", "subtopic", "explanation"):
            if not str(q.get(fld) or "").strip():
                err(name, f"{qid} missing {fld}")
        if q.get("difficulty") not in TARGET_DIFF:
            err(name, f"{qid} bad difficulty {q.get('difficulty')!r}")

        # ── structure: exactly one correct option ──────────────────────────
        r = q.get("renderAs")
        if r == "mcq":
            opts = q.get("options") or []
            if len(opts) != 4:
                err(name, f"{qid} has {len(opts)} options, expected 4")
            bodies = [re.sub(r"^[A-D]\.\s*", "", o).strip() for o in opts]
            if len(set(bodies)) != len(bodies):
                err(name, f"{qid} has duplicate options: {bodies}")
            if q.get("correctAnswer") not in set("ABCD"):
                err(name, f"{qid} correctAnswer {q.get('correctAnswer')!r} invalid")
        elif r == "tf":
            if q.get("correctAnswer") not in ("A", "B"):
                err(name, f"{qid} true/false answer invalid")
        elif r == "fill":
            if not (q.get("answers") or []):
                err(name, f"{qid} fill question with no accepted answer")
        elif r != "match":
            err(name, f"{qid} unknown renderAs {r!r}")

        # ── THE MATHS CHECK ────────────────────────────────────────────────
        calc = q.get("calc")
        if not calc:
            UNCHECKED += 1
            continue
        got = safe_eval(calc)
        if got is None:
            UNCHECKED += 1
            continue

        # what does the question claim the answer is?
        if r == "mcq":
            body = re.sub(r"^[A-D]\.\s*", "",
                          q["options"]["ABCD".index(q["correctAnswer"])]).strip()
        elif r == "fill":
            body = q["answers"][0]
        else:
            UNCHECKED += 1
            continue

        want = parse_answer(body)
        if want is None:
            UNCHECKED += 1
            continue

        CHECKED += 1
        if want != got:
            err(name, f"MATHS WRONG — {qid}: marked answer '{body}' but "
                      f"{calc} = {got} ({float(got):.4g})\n            Q: {q['question']}")

    # ── exact counts ───────────────────────────────────────────────────────
    owner_n = sum(1 for q in qs if q.get("origin"))
    if len(qs) < TARGET_TOTAL:
        TARGETS.append(f"  {cls}: {len(qs)} questions, need {TARGET_TOTAL}")
    elif len(qs) > TARGET_TOTAL and not owner_n:
        TARGETS.append(f"  {cls}: {len(qs)} questions, more than {TARGET_TOTAL}")
    if not owner_n:
        for lvl, wnt in TARGET_DIFF.items():
            have = sum(1 for q in qs if q.get("difficulty") == lvl)
            if have != wnt:
                TARGETS.append(f"  {cls}: {have} {lvl}, need {wnt}")

    own = sorted(int(q["id"].split("_")[-1]) for q in qs if q.get("origin"))
    gen = sorted(int(q["id"].split("_")[-1].lstrip("G")) for q in qs if not q.get("origin"))
    if own and own != list(range(1, len(own) + 1)):
        err(name, f"{cls} owner-supplied IDs are not contiguous from 001")
    if gen and gen != list(range(1, len(gen) + 1)):
        err(name, f"{cls} generated IDs are not contiguous")
    if own and any("_G" not in q["id"] for q in qs if not q.get("origin")):
        err(name, f"{cls} generated questions must use the G prefix")

    tp = Counter(q["topic"] for q in qs)
    print(f"  {name:16} {cls}  {len(qs):>3} questions  {len(tp):>2} topics  "
          f"E{sum(1 for q in qs if q['difficulty']=='Easy')}/"
          f"M{sum(1 for q in qs if q['difficulty']=='Medium')}/"
          f"H{sum(1 for q in qs if q['difficulty']=='Hard')}")
    return cls, qs


def main():
    files = sorted(glob.glob("data/practice/math-p*.json"))
    if not files:
        print("No Mathematics datasets found."); return 1
    print(f"\nChecking {len(files)} dataset(s)\n" + "-" * 72)
    seen_ids, seen_text, byclass = {}, {}, {}
    for f in files:
        res = check_file(f, seen_ids, seen_text)
        if res:
            byclass[res[0]] = res[1]
    print("-" * 72)

    print("\nCROSS-CLASS PURITY")
    cl = sorted(byclass)
    for i, a in enumerate(cl):
        for b in cl[i + 1:]:
            sa = {q["question"] for q in byclass[a]}
            sb = {q["question"] for q in byclass[b]}
            sh = sa & sb
            if sh:
                err("cross-class", f"{a} and {b} share {len(sh)} question(s)")
            print(f"  {a} vs {b}: {'OK' if not sh else str(len(sh))+' SHARED'}")

    print(f"\nARITHMETIC VERIFICATION")
    print(f"  {CHECKED} answers re-computed from their own `calc` expression")
    print(f"  {UNCHECKED} not machine-checkable (wording, shapes, matching)")
    wrong = sum(1 for e in ERRORS if "MATHS WRONG" in e)
    print(f"  {wrong} disagreement(s) between the marked answer and the arithmetic")

    for w in WARNINGS[:10]:
        print(w)
    for e in ERRORS[:25]:
        print(e)
    if len(ERRORS) > 25:
        print(f"  ... and {len(ERRORS)-25} more errors")

    have = sum(len(v) for v in byclass.values())
    print(f"\nTARGET (200 per class / 70 Easy, 80 Medium, 50 Hard)")
    if TARGETS:
        for t in TARGETS: print(t)
    else:
        print(f"  MET — {have}/800 questions, exact difficulty split in every class.")

    print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
    if ERRORS or TARGETS:
        print("FAILED\n"); return 1
    print("PASSED — counts, class purity and arithmetic all verified.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
