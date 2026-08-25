#!/usr/bin/env python3
"""
validate_practice.py — enforces the practice-bank rules, above all:
NEVER MIX P.4, P.5, P.6 AND P.7 CONTENT.

Usage:  python3 tools/validate_practice.py
Exit 0 = clean, 1 = errors.
"""
import json, sys, glob, re, os
from collections import Counter, defaultdict

DIFFS = {"Easy", "Medium", "Hard"}
RENDERS = {"mcq", "tf", "fill", "match"}
QTYPES = {"multiple_choice", "fill_blank", "true_false", "matching", "identification",
          "short_answer", "scenario", "map_skill", "comparison", "cause_effect", "application"}
ERRORS, WARNINGS, TARGETS = [], [], []
TARGET_TOTAL = 200
TARGET_DIFF = {'Easy':70,'Medium':80,'Hard':50}


def err(f, m): ERRORS.append(f"  [ERROR] {f}: {m}")
def warn(f, m): WARNINGS.append(f"  [warn ] {f}: {m}")


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()


def check_file(path, seen_ids, seen_text):
    name = os.path.basename(path)
    d = json.load(open(path, encoding="utf-8"))
    cls = d.get("class")
    qs = d.get("questions", [])

    if cls not in ("P4", "P5", "P6", "P7"):
        err(name, f"file class is {cls!r}, expected P4/P5/P6/P7")
        return
    if d.get("total") != len(qs):
        err(name, f"total says {d.get('total')} but file holds {len(qs)}")

    for q in qs:
        qid = q.get("id", "?")

        # ── RULE 1 · CLASS PURITY (checked two independent ways) ───────────
        if q.get("class") != cls:
            err(name, f"CLASS MIXING — {qid} has class={q.get('class')!r} in a {cls} file")
        if not str(qid).startswith(f"{cls}_SST_"):
            err(name, f"CLASS MIXING — {qid} ID prefix does not match {cls}")
        m = re.match(r"^(P[4-7])_SST_", str(qid))
        if m and m.group(1) != q.get("class"):
            err(name, f"CLASS MIXING — {qid} ID class and class field disagree")

        if q.get("subject") != "SST":
            err(name, f"{qid} subject is {q.get('subject')!r}, expected SST")

        # ── uniqueness across ALL classes ──────────────────────────────────
        if qid in seen_ids:
            err(name, f"duplicate ID {qid} (also in {seen_ids[qid]})")
        else:
            seen_ids[qid] = name
        key = norm(q.get("question"))
        if key and key in seen_text:
            err(name, f"duplicate question text — {qid} repeats {seen_text[key]}")
        else:
            seen_text[key] = qid

        # ── required fields ────────────────────────────────────────────────
        for fld in ("topic", "subtopic", "explanation"):
            if not str(q.get(fld) or "").strip():
                err(name, f"{qid} has no {fld}")
        if q.get("difficulty") not in DIFFS:
            err(name, f"{qid} difficulty {q.get('difficulty')!r} must be Easy/Medium/Hard")
        if q.get("questionType") not in QTYPES:
            err(name, f"{qid} unknown questionType {q.get('questionType')!r}")
        if not str(q.get("question") or "").strip():
            err(name, f"{qid} has no question text")

        # ── one, and only one, correct answer ──────────────────────────────
        r = q.get("renderAs")
        if r not in RENDERS:
            err(name, f"{qid} unknown renderAs {r!r}")
        elif r in ("mcq", "tf"):
            opts = q.get("options") or []
            want = 2 if r == "tf" else 4
            if len(opts) != want:
                err(name, f"{qid} has {len(opts)} options, expected {want}")
            bodies = [re.sub(r"^[A-D]\.\s*", "", o) for o in opts]
            if len(set(norm(b) for b in bodies)) != len(bodies):
                err(name, f"{qid} has duplicate option text")
            ca = q.get("correctAnswer")
            letters = "AB" if r == "tf" else "ABCD"
            if ca not in set(letters):
                err(name, f"{qid} correctAnswer {ca!r} must be one of {letters}")
            for b in bodies:
                if not str(b).strip():
                    err(name, f"{qid} has an empty option")
        elif r == "fill":
            ans = q.get("answers") or []
            if not ans:
                err(name, f"{qid} is a fill question with no accepted answers")
            if "______" not in q.get("question", "") and q.get("questionType") == "fill_blank":
                warn(name, f"{qid} is fill_blank but has no blank marker")
        elif r == "match":
            pairs = q.get("pairs") or []
            if len(pairs) < 3:
                err(name, f"{qid} matching needs at least 3 pairs, has {len(pairs)}")
            lefts = [p[0] for p in pairs]
            rights = [p[1] for p in pairs]
            if len(set(lefts)) != len(lefts) or len(set(rights)) != len(rights):
                err(name, f"{qid} matching has repeated items")

        # ── visual questions must not reference an image we don't have ─────
        txt = str(q.get("question", "")).lower()
        if q.get("image"):
            if not os.path.exists(q["image"]):
                err(name, f"{qid} references image {q['image']} which does not exist")
        else:
            for phrase in ("map below", "diagram below", "picture below", "figure below",
                           "shown below", "graph below", "above map"):
                if phrase in txt:
                    err(name, f"{qid} refers to '{phrase}' but has no image — "
                              "never ask a learner to read something that is not there")

    # ── exact counts required by the brief ─────────────────────────────────
    if len(qs) != TARGET_TOTAL:
        TARGETS.append(f"  {cls}: {len(qs)} questions, need {TARGET_TOTAL} "
                       f"({TARGET_TOTAL-len(qs):+d})")
    for lvl, want in TARGET_DIFF.items():
        have = sum(1 for q in qs if q.get("difficulty") == lvl)
        if have != want:
            TARGETS.append(f"  {cls}: {have} {lvl}, need {want} ({want-have:+d})")

    # IDs: owner batches run 001.. contiguously, generated run 501..
    own = sorted(int(q["id"].split("_")[-1]) for q in qs if q.get("origin"))
    gen = sorted(int(q["id"].split("_")[-1].lstrip("G")) for q in qs if not q.get("origin"))
    if own and own != list(range(1, len(own) + 1)):
        err(name, f"{cls} owner-supplied IDs are not contiguous from 001")
    genids = [q["id"] for q in qs if not q.get("origin")]
    if own and genids and not all("_G" in i for i in genids):
        err(name, f"{cls} generated questions must use the G prefix so they cannot "
                  "collide with owner batch numbering")

    tops = Counter(q["topic"] for q in qs)
    print(f"  {name:18} {cls}  {len(qs):>3} questions  {len(tops):>2} topics  "
          f"E{sum(1 for q in qs if q['difficulty']=='Easy')}/"
          f"M{sum(1 for q in qs if q['difficulty']=='Medium')}/"
          f"H{sum(1 for q in qs if q['difficulty']=='Hard')}")
    return cls, qs


def main():
    files = sorted(glob.glob("data/practice/sst-p*.json"))
    if not files:
        print("No practice datasets found in data/practice/")
        return 1
    print(f"\nChecking {len(files)} dataset(s)\n" + "-" * 72)
    seen_ids, seen_text, byclass = {}, {}, {}
    for f in files:
        res = check_file(f, seen_ids, seen_text)
        if res:
            byclass[res[0]] = res[1]
    print("-" * 72)

    # ── cross-dataset purity: no ID or text may appear under two classes ───
    print("\nCROSS-CLASS PURITY")
    classes = sorted(byclass)
    for i, a in enumerate(classes):
        for b in classes[i + 1:]:
            sa = {norm(q["question"]) for q in byclass[a]}
            sb = {norm(q["question"]) for q in byclass[b]}
            shared = sa & sb
            status = "OK" if not shared else f"{len(shared)} SHARED"
            if shared:
                err("cross-class", f"{a} and {b} share question text: {list(shared)[:3]}")
            print(f"  {a} vs {b}: {status}")
    for c in classes:
        bad = [q["id"] for q in byclass[c] if not q["id"].startswith(c)]
        print(f"  {c}: {len(byclass[c])} questions, all IDs prefixed {c} — "
              f"{'YES' if not bad else 'NO ' + str(bad[:3])}")

    for w in WARNINGS: print(w)
    for e in ERRORS: print(e)

    print(f"\nINTEGRITY: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
    if ERRORS:
        print("  FAILED — fix these before importing.")
    else:
        print("  PASSED — class purity, IDs, answers and explanations all verified.")

    have = sum(len(v) for v in byclass.values())
    print(f"\nTARGET (200 per class / 70 Easy, 80 Medium, 50 Hard):")
    if TARGETS:
        for t in TARGETS: print(t)
        print(f"\n  {have}/800 questions written ({have/800*100:.0f}%). "
              f"{800-have} still to author.")
        print("  Add them to tools/batches/ and re-run the builder.")
    else:
        print("  MET — exactly 200 per class with the required difficulty split.")

    if ERRORS:
        return 1
    if TARGETS and "--allow-partial" not in sys.argv:
        print("\nEXIT 1: integrity is clean but the 800-question target is not yet met.")
        print("Use --allow-partial to build with what exists.\n")
        return 1
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
