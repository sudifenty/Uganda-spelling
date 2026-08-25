#!/usr/bin/env python3
"""
validate_exercises.py — safety checks on the Written Exercises bank.

Rules enforced (from the owner's rules):

  1. A question must never be filed under the wrong class or subject.
  2. A question must never be filed under the wrong topic.
  3. Every question must have a non-empty question and a non-empty answer.
  4. Every question must belong to exactly one exercise set — none dropped,
     none duplicated.
  5. Every set must have at least 4 questions and a mark total.
  6. Marking metadata must be sane (kind known, marks >= 1, list questions
     must carry their accepted points).
  7. No question may leak a "complete notes" claim or a false source claim.

Usage: python3 tools/validate_exercises.py
"""
import json, glob, re, sys

KINDS = {"auto", "list", "open", "self"}
CLASSES = ("P4", "P5", "P6", "P7")
SUBJECTS = ("SST", "MATH", "SCI", "ENG")
BANNED = [
    (re.compile(r"\bcomplete notes\b", re.I), 'says "complete notes"'),
    (re.compile(r"according to (the )?(uneb|teacher'?s guide|mk |longhorn)", re.I),
     "claims a source document that is not held"),
    (re.compile(r"\buneb (says|states|requires)\b", re.I), "claims UNEB authority"),
]


def main():
    files = sorted(glob.glob("data/exercises/*.json"))
    if not files:
        print("  no exercise files — nothing to validate")
        return 0

    errors, total_q, total_s = [], 0, 0
    seen_ids = set()

    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        if cls not in CLASSES:
            errors.append(f"{f}: unknown class {cls}")
        if subj not in SUBJECTS:
            errors.append(f"{f}: unknown subject {subj}")

        nq = 0
        for t in d["topics"]:
            qids = {q["id"] for q in t["questions"]}
            if len(qids) != len(t["questions"]):
                errors.append(f"{f} {t['title']}: duplicate question id")

            for q in t["questions"]:
                tag = f"{f} {q['id']}"
                nq += 1
                if q["id"] in seen_ids:
                    errors.append(f"{tag}: id used twice in the bank")
                seen_ids.add(q["id"])

                # 1 + 2 — purity
                if q["class"] != cls or q["subject"] != subj:
                    errors.append(f"{tag}: wrong class/subject "
                                  f"({q['class']}/{q['subject']} in {cls}/{subj})")
                if q["topic"] != t["title"] or q["topic_no"] != t["topic_no"]:
                    errors.append(f"{tag}: wrong topic "
                                  f"({q['topic']!r} in {t['title']!r})")
                if not q["id"].startswith(f"{cls}_{subj}_"):
                    errors.append(f"{tag}: id does not start with {cls}_{subj}_")

                # 3 — content present
                if not q["q"].strip():
                    errors.append(f"{tag}: empty question")
                if not q["a"].strip():
                    errors.append(f"{tag}: empty answer")

                # 6 — marking metadata
                if q["kind"] not in KINDS:
                    errors.append(f"{tag}: unknown marking kind {q['kind']}")
                if q["marks"] < 1:
                    errors.append(f"{tag}: marks below 1")
                if q["kind"] == "list" and len(q["accepted"]) < 2:
                    errors.append(f"{tag}: list question with no accepted points")
                if q["kind"] == "auto" and not q["accepted"]:
                    errors.append(f"{tag}: auto question with no accepted answer")

                # 7 — banned claims
                body = q["q"] + " " + q["a"]
                for rx, why in BANNED:
                    if rx.search(body):
                        errors.append(f"{tag}: {why}")

            # 4 + 5 — sets cover every question exactly once
            in_sets = [i for s in t["sets"] for i in s["qids"]]
            if sorted(in_sets) != sorted(qids):
                missing = qids - set(in_sets)
                extra = set(in_sets) - qids
                if missing:
                    errors.append(f"{f} {t['title']}: {len(missing)} question(s) "
                                  f"in no set — questions must never be dropped")
                if extra:
                    errors.append(f"{f} {t['title']}: set refers to unknown "
                                  f"question(s) {sorted(extra)[:3]}")
            if len(in_sets) != len(set(in_sets)):
                errors.append(f"{f} {t['title']}: a question appears in two sets")
            for s in t["sets"]:
                total_s += 1
                if len(s["qids"]) < 4:
                    errors.append(f"{f} {s['id']}: only {len(s['qids'])} questions")
                if s["marks"] < 1:
                    errors.append(f"{f} {s['id']}: no marks")

        if nq != d["total"]:
            errors.append(f"{f}: header says {d['total']} questions, found {nq}")
        total_q += nq
        print(f"  {f}: {len(d['topics'])} topics, {d['sets']} sets, "
              f"{nq} questions — checked")

    if errors:
        for e in errors[:40]:
            print("  FAIL:", e)
        sys.exit(f"validate_exercises: {len(errors)} problem(s)")
    print(f"  all {total_q} questions in {total_s} sets passed "
          f"— class, subject and topic purity verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
