#!/usr/bin/env python3
"""
build_exercises.py — turn the checked revision questions inside the notes into a
topic-tagged Written Exercises bank.

Every question already lives under exactly one class, one subject and one
curriculum topic, and every one already has an answer that was worked out and
checked when the note was written. Nothing new is invented here: this tool only
re-files what exists and records how each question can be marked.

Marking kinds
-------------
  auto   short factual/numeric answer   -> marked by the app (normalised match)
  list   "Any N of a, b, c ..."         -> marked by counting listed points found
  open   "your own answer"              -> always credited, guidance shown
  self   longer prose answer            -> learner self-marks against the model

Answers are stored in the bank because the app needs them to mark, but the app
must never show them before the learner submits.

Output: data/exercises/p<class>-<subject>.json

Usage: python3 tools/build_exercises.py      (run from the ple-app folder)
"""
import json, glob, os, re, sys

SRC = "data/notes"
OUT = "data/exercises"

SET_SIZE = 10
SET_NAMES = ["Basic Practice", "More Practice", "Further Practice",
             "Extra Practice", "Additional Practice"]

# a question that shows arithmetic and expects working
CALC = re.compile(r"(work out|calculate|find the (sum|difference|product|quotient|value|area|perimeter|average)"
                  r"|add:|subtract|multiply|divide|simplify|solve|express|convert|change)", re.I)
NUMISH = re.compile(r"^[\s\d,.\-+×÷/=°%()a-z ]{1,40}$", re.I)


def clean(s):
    """Strip the markdown emphasis used in the notes."""
    s = re.sub(r"\*\*([\s\S]+?)\*\*", r"\1", s)
    s = re.sub(r"(^|[^*])\*([^*\n]+)\*", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()


def section(topic, rx):
    return next((s for s in topic["sections"] if re.search(rx, s["title"], re.I)), None)


def items(sec):
    if not sec:
        return []
    return [i for b in sec["blocks"] if b["t"] == "ol" for i in b["items"]]


def split_alternatives(ans):
    """For an 'Any N of x, y, z' answer, return the list of acceptable points."""
    body = re.sub(r"^any\s+(\w+)\s+of\s*:?\s*", "", ans, flags=re.I)
    parts = re.split(r"\s*(?:·|;|,| or )\s*", body)
    parts = [p.strip(" .") for p in parts if len(p.strip(" .")) > 2]
    return parts


WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
           "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def classify(q, a):
    """Return (kind, marks, accepted, working_required)."""
    low = a.lower()
    if "your own answer" in low or "your own drawing" in low:
        return "open", 1, [], False
    m = re.match(r"^any\s+(\w+)\s+of", a, re.I)
    if m:
        n = WORDNUM.get(m.group(1).lower())
        if n is None:
            try:
                n = int(m.group(1))
            except ValueError:
                n = 2
        alts = split_alternatives(a)
        if len(alts) >= 2:
            return "list", max(1, min(n, len(alts))), alts, False
    words = a.split()
    if len(words) <= 6 or NUMISH.match(a):
        working = bool(CALC.search(q)) and bool(re.search(r"\d", q))
        return "auto", 1, [a], working
    return "self", 2, [], bool(CALC.search(q)) and bool(re.search(r"\d", q))


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(f"{SRC}/*.json"))
    if not files:
        sys.exit("build_exercises: no notes found — run build_notes.py first")

    grand_q = grand_sets = 0
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        topics_out, nq, nsets = [], 0, 0

        for t in d["topics"]:
            qs = [clean(x) for x in items(section(t, r"^revision questions$"))]
            ans = [clean(x) for x in items(section(t, r"answers to revision"))]
            if not qs:
                continue
            if len(ans) < len(qs):
                sys.exit(f"build_exercises: {t['id']} has {len(qs)} questions "
                         f"but only {len(ans)} answers")

            questions = []
            for i, (q, a) in enumerate(zip(qs, ans), 1):
                kind, marks, accepted, working = classify(q, a)
                questions.append({
                    "id": f"{t['id']}_Q{i:02d}",
                    "class": cls, "subject": subj,
                    "topic_no": t["topic_no"], "topic": t["title"],
                    "n": i, "q": q, "a": a,
                    "kind": kind, "marks": marks,
                    "accepted": accepted, "working": working,
                })

            # split into exercise sets of SET_SIZE
            sets = []
            for k in range(0, len(questions), SET_SIZE):
                chunk = questions[k:k + SET_SIZE]
                if len(chunk) < 4 and sets:          # don't leave a stub set
                    sets[-1]["qids"] += [x["id"] for x in chunk]
                    sets[-1]["marks"] += sum(x["marks"] for x in chunk)
                    continue
                sets.append({
                    "id": f"{t['id']}_S{len(sets)+1}",
                    "name": SET_NAMES[min(len(sets), len(SET_NAMES) - 1)],
                    "qids": [x["id"] for x in chunk],
                    "marks": sum(x["marks"] for x in chunk),
                })

            topics_out.append({
                "topic_no": t["topic_no"], "title": t["title"],
                "topic_id": t["id"],
                "curriculum_pages": t.get("curriculum_pages", ""),
                "total": len(questions),
                "marks": sum(x["marks"] for x in questions),
                "sets": sets, "questions": questions,
            })
            nq += len(questions)
            nsets += len(sets)

        out = {
            "class": cls, "subject": subj,
            "subject_name": d["subject_name"],
            "topics": topics_out, "total": nq, "sets": nsets,
        }
        path = f"{OUT}/p{cls[1]}-{subj.lower()}.json"
        json.dump(out, open(path, "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))
        print(f"  {cls} {d['subject_name']:<18s} {len(topics_out):2d} topics "
              f"{nsets:3d} sets {nq:4d} questions -> {path}")
        grand_q += nq
        grand_sets += nsets

    print(f"  {grand_q} written exercise questions in {grand_sets} sets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
