#!/usr/bin/env python3
"""
inject.py — embed every dataset into index.html.

The app is one offline file, so all data lives inside it. This script is the
ONLY thing that should edit those embedded blocks; never hand-edit them.

  data/papers/sst-YYYY.json   -> QUESTION_BANK + PAPER_META   (past-paper archive)
  data/practice/sst-p*.json   -> PRACTICE_BANK                (SST practice)
  data/practice/math-p*.json  -> MATH_BANK                    (Maths practice)
  data/notes/p*-*.json        -> NOTES_BANK                   (study notes)
  data/exercises/p*-*.json    -> EXERCISE_BANK                (written exercises)

Usage: python3 tools/inject.py        (run from the ple-app folder)
"""
import json, re, sys, os, glob

APP = "index.html"
BUILD_ONLY = ("calc", "answerValue")      # verification fields, not needed at runtime


def load_papers():
    years, meta = {}, {}
    for f in sorted(glob.glob("data/papers/sst-*.json")):
        d = json.load(open(f, encoding="utf-8"))
        y = str(d["year"])
        years[y] = d["questions"]
        meta[f"sst-{y}"] = {"title": d["paper_title"], "format": d["format"],
                            "sections": d["sections"]}
    return {"sst": years}, meta


def load_practice(prefix, keep_calc=False):
    bank = {}
    for f in sorted(glob.glob(f"data/practice/{prefix}-p*.json")):
        d = json.load(open(f, encoding="utf-8"))
        qs = []
        for q in d["questions"]:
            # Maths keeps calc + answerValue: the Maths Adventure UI shows
            # step-by-step working and the number pad from them.
            drop = () if (keep_calc and prefix == "math") else BUILD_ONLY
            qs.append({k: v for k, v in q.items() if k not in drop})
        bank[d["class"]] = {"class": d["class"], "topics": d["topics"],
                            "total": d["total"], "questions": qs}
    return bank


def load_notes_practice(subj):
    """Questions derived from the study notes, merged into the same bank."""
    out = {}
    for f in sorted(glob.glob(f"data/practice/notes-{subj}-p*.json")):
        d = json.load(open(f, encoding="utf-8"))
        out[d["class"]] = [{k: v for k, v in q.items() if k not in BUILD_ONLY}
                           for q in d["questions"]]
    return out


def merge_practice(bank, extra):
    """Add notes-derived questions to a practice bank, keeping it pure."""
    for cls, qs in extra.items():
        b = bank.setdefault(cls, {"class": cls, "topics": [], "total": 0,
                                  "questions": []})
        have = {q["id"] for q in b["questions"]}
        for q in qs:
            if q["id"] in have or q["class"] != cls:
                continue
            b["questions"].append(q)
            have.add(q["id"])
        seen = []
        for q in b["questions"]:
            if q.get("topic") and q["topic"] not in seen:
                seen.append(q["topic"])
        b["topics"] = seen
        b["total"] = len(b["questions"])
    return bank


def load_exercises():
    out = {}
    for f in sorted(glob.glob("data/exercises/p*-*.json")):
        d = json.load(open(f, encoding="utf-8"))
        out.setdefault(d["class"], {})[d["subject"]] = d
    return out


def load_notes():
    """class -> subject -> {subject_name, total, words, topics[]}"""
    bank = {}
    for f in sorted(glob.glob("data/notes/p*-*.json")):
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        topics = [t for t in d["topics"]
                  if t["class"] == cls and t["subject"] == subj]
        if len(topics) != len(d["topics"]):
            sys.exit(f"inject: {f} contains a topic filed under the wrong class/subject")
        bank.setdefault(cls, {})[subj] = {
            "subject_name": d["subject_name"], "total": len(topics),
            "words": d["words"], "topics": topics}
    return bank


def replace(app, pattern, replacement, label):
    new, n = re.subn(pattern, lambda _: replacement, app, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"inject: could not find the {label} block in {APP}")
    return new


def main():
    if not os.path.exists(APP):
        sys.exit(f"inject: run this from the folder containing {APP}")
    app = open(APP, encoding="utf-8").read()
    before = len(app)

    papers, meta = load_papers()
    practice = load_practice("sst")
    maths = load_practice("math", keep_calc=True)
    sci = load_practice("sci")
    notes = load_notes()
    exercises = load_exercises()

    practice = merge_practice(practice, load_notes_practice("sst"))
    maths    = merge_practice(maths,    load_notes_practice("math"))
    sci      = merge_practice(sci,      load_notes_practice("sci"))
    english  = merge_practice({},       load_notes_practice("eng"))

    j = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))

    app = replace(app,
        r"const QUESTION_BANK = \{.*?\};\nObject\.assign\(PAPER_META, \{.*?\}\);",
        f"const QUESTION_BANK = {j(papers)};\nObject.assign(PAPER_META, {j(meta)});",
        "QUESTION_BANK / PAPER_META")
    app = replace(app, r"const PRACTICE_BANK = \{.*?\};\n",
                  f"const PRACTICE_BANK = {j(practice)};\n", "PRACTICE_BANK")
    app = replace(app, r"const MATH_BANK = \{.*?\};\n",
                  f"const MATH_BANK = {j(maths)};\n", "MATH_BANK")
    app = replace(app, r"const SCI_BANK = \{.*?\};\n",
                  f"const SCI_BANK = {j(sci)};\n", "SCI_BANK")
    app = replace(app, r"const ENG_BANK = \{.*?\};\n",
                  f"const ENG_BANK = {j(english)};\n", "ENG_BANK")
    app = replace(app, r"const NOTES_BANK = \{.*?\};\n",
                  f"const NOTES_BANK = {j(notes)};\n", "NOTES_BANK")
    app = replace(app, r"const EXERCISE_BANK = \{.*?\};\n",
                  f"const EXERCISE_BANK = {j(exercises)};\n", "EXERCISE_BANK")

    open(APP, "w", encoding="utf-8").write(app)

    pq = sum(len(v) for v in papers["sst"].values())
    sq = sum(v["total"] for v in practice.values())
    mq = sum(v["total"] for v in maths.values())
    print(f"  past papers   {len(papers['sst']):>2} years   {pq:>4} questions")
    print(f"  SST practice  {len(practice):>2} classes {sq:>4} questions")
    print(f"  Maths practice{len(maths):>3} classes {mq:>4} questions")
    sq2 = sum(v["total"] for v in sci.values())
    print(f"  Science       {len(sci):>3} classes {sq2:>4} questions")
    nt = sum(len(v["topics"]) for c in notes.values() for v in c.values())
    nw = sum(v["words"] for c in notes.values() for v in c.values())
    print(f"  Study notes   {len(notes):>3} classes {nt:>4} topics  {nw:,} words")
    print(f"  {APP}: {before:,} -> {len(app):,} bytes")


if __name__ == "__main__":
    main()
