#!/usr/bin/env python3
"""
validate.py — enforces the data rules for the PLE question bank.

Handles two paper formats:
  format: "mcq"      four options A-D, one correct answer
  format: "written"  short-answer / structured papers (the real PLE SST shape)

Usage:
    python3 tools/validate.py data/sst-2008.json
    python3 tools/validate.py data/*.json

Exit 0 = clean, 1 = errors. Warnings never fail the run.
"""
import json, sys, glob, re
from collections import Counter

VALID_ANS = {"A", "B", "C", "D"}
MCQ_TYPES = {"mcq"}
WRITTEN_TYPES = {"short", "structured", "alternative", "alternative_structured"}
ERRORS, WARNINGS = [], []


def err(f, msg):  ERRORS.append(f"  [ERROR] {f}: {msg}")
def warn(f, msg): WARNINGS.append(f"  [warn ] {f}: {msg}")


def num_key(n):
    m = re.match(r"^(\d+)([a-z]*)$", str(n).strip().lower())
    return (int(m.group(1)), m.group(2)) if m else (10**6, str(n))


def check_mcq(name, q, qid):
    opts = q.get("options", {}) or {}
    missing = [k for k in "ABCD" if not str(opts.get(k, "")).strip()]
    if missing:
        err(name, f"RULE 3 — {qid} missing option(s) {','.join(missing)}")
    ca = str(q.get("correct_answer", "")).strip().upper()
    if ca not in VALID_ANS:
        err(name, f"{qid} correct_answer must be A/B/C/D, got {ca!r}")
    elif ca in missing:
        err(name, f"{qid} correct_answer '{ca}' points at an empty option")


def check_parts(name, qid, parts, where=""):
    if not parts:
        err(name, f"{qid}{where} is structured but has no parts")
        return
    labels = [str(p.get("label", "")).strip() for p in parts]
    if "" in labels:
        err(name, f"{qid}{where} has a part with no letter")
    for d, c in Counter(labels).items():
        if c > 1:
            err(name, f"{qid}{where} repeats part label '{d}'")
    for p in parts:
        if not str(p.get("text", "")).strip():
            err(name, f"{qid}{where} part ({p.get('label')}) has no text")
        if p.get("parts"):
            check_parts(name, qid, p["parts"], where + f" ({p.get('label')})")


def check_written(name, q, qid):
    t = q["type"]
    if t == "short":
        if not str(q.get("question", "")).strip():
            err(name, f"{qid} has empty question text")
    elif t == "structured":
        check_parts(name, qid, q.get("parts"))
    elif t in ("alternative", "alternative_structured"):
        v = q.get("variants") or {}
        for side in ("christian", "islamic"):
            if side not in v:
                err(name, f"{qid} is an alternative question but has no '{side}' variant")
                continue
            sv = v[side]
            if t == "alternative":
                if not str(sv.get("question", "") or "").strip():
                    err(name, f"{qid} {side} variant has no question text")
            else:
                check_parts(name, qid, sv.get("parts"), f" [{side}]")
                qt = sv.get("quote")
                if qt is not None:
                    if not str(qt.get("text", "")).strip():
                        err(name, f"{qid} [{side}] has a quote block with no text")
                    if not str(qt.get("citation", "")).strip():
                        warn(name, f"{qid} [{side}] quote has no citation")


def check_paper_structure(name, data, qs):
    """Archive-paper checks: count, run, sections, ordering, alternatives."""
    nums = [q.get("number") for q in qs]
    declared = data.get("total_questions", 0)

    if declared and declared != len(qs):
        err(name, f"RULE 10 — total_questions says {declared} but file holds {len(qs)}")

    ints = [n for n in nums if isinstance(n, int)]
    if len(ints) == len(nums) and ints:
        expect = list(range(min(ints), min(ints) + len(ints)))
        if ints != expect:
            gaps = sorted(set(expect) - set(ints))
            if gaps:
                err(name, f"numbering is not continuous — missing {gaps[:15]}")
            if ints != sorted(ints):
                err(name, "RULE 1 — questions are not in original order")

    secs = data.get("sections")
    if secs:
        for letter, (lo, hi) in secs.items():
            actual = [q["number"] for q in qs if q.get("section") == letter]
            if not actual:
                err(name, f"section {letter} declared {lo}-{hi} but holds no questions")
                continue
            if min(actual) != lo or max(actual) != hi:
                err(name, f"section {letter} declared {lo}-{hi} but runs "
                          f"{min(actual)}-{max(actual)}")
            stray = [n for n in actual if not (lo <= n <= hi)]
            if stray:
                err(name, f"section {letter} contains out-of-range questions {stray}")

    for q in qs:
        v = q.get("variants") or {}
        if v.get("christian") and v.get("islamic"):
            c, i = v["christian"].get("question"), v["islamic"].get("question")
            if c and i and c.strip() == i.strip():
                warn(name, f"Q{q['number']} Christian and Islamic wording are identical "
                           "— check this is how the paper prints it")

    alts = [q["number"] for q in qs if q.get("type", "").startswith("alternative")]
    if alts:
        print(f"       Christian/Islamic alternatives at: {alts}")
    allcand = [q["number"] for q in qs if q.get("audience") == "all" and q.get("section") == "B"]
    if allcand:
        print(f"       marked for all candidates: {allcand}")


def check(path):
    name = path.split("/")[-1]
    try:
        data = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(name, f"not valid JSON — {e}")
        return

    year = data.get("year")
    qs = data.get("questions", [])
    fmt = data.get("format", "mcq")

    if not isinstance(year, int) or not (1990 <= year <= 2100):
        err(name, f"file-level 'year' missing or implausible: {year!r}")
    if not qs:
        err(name, "no questions in file")
        return

    stray = {q.get("year") for q in qs} - {year}
    if stray:
        err(name, f"RULE 6/8 — questions carry other years: {sorted(stray)} (file is {year})")

    nums = [str(q.get("number", "")).strip() for q in qs]
    for n, c in Counter(nums).items():
        if c > 1:
            err(name, f"RULE 2 — question number '{n}' appears {c} times")
    if "" in nums:
        err(name, "RULE 2 — a question has no number")

    parents = set(nums)
    unanswered = 0
    for q in qs:
        qid = f"Q{q.get('number','?')}"
        t = str(q.get("type", "mcq")).strip().lower()

        if t == "stem":
            if not str(q.get("question", "")).strip() and not q.get("asset"):
                err(name, f"{qid} is a stem with neither text nor an asset")
            continue
        if t in MCQ_TYPES:
            check_mcq(name, q, qid)
        elif t in WRITTEN_TYPES:
            check_written(name, q, qid)
        else:
            err(name, f"{qid} has unknown type {t!r}")

        if q.get("answer_status") == "not_supplied":
            unanswered += 1

        rov = q.get("requires_original_visual")
        _a = q.get("asset")
        needs = bool(_a and _a.get("status") == "missing")
        if rov is not None and bool(rov) != needs:
            err(name, f"RULE 5 — {qid} requires_original_visual={rov} but its asset "
                      f"{'is missing' if needs else 'is present or absent'}")

        ref = q.get("asset_ref")
        if ref is not None:
            host = next((x for x in qs if x.get("number") == ref), None)
            if host is None:
                err(name, f"RULE 5 — {qid} references the visual at Q{ref}, which is not in this file")
            elif not host.get("asset"):
                err(name, f"RULE 5 — {qid} references Q{ref}'s visual but Q{ref} has no asset")

        p = q.get("parent")
        if p is not None and str(p) not in parents:
            err(name, f"RULE 4 — {qid} references parent '{p}' which is not in this file")

        a = q.get("asset")
        if a:
            if a.get("status") == "missing":
                warn(name, f"RULE 5 — {qid} needs a printed {a.get('kind','item')} "
                           f"that has not been supplied yet")
            elif a.get("table"):
                t = a["table"]
                hdr = t.get("header", [])
                for row in t.get("rows", []):
                    if len(row) != len(hdr):
                        err(name, f"RULE 5 — {qid} table row '{row[0] if row else '?'}' has "
                                  f"{len(row)} cells but the header has {len(hdr)}")
                if not a.get("alt"):
                    warn(name, f"RULE 5 — {qid} table has no alt text (accessibility)")
                if a.get("transcription_note"):
                    warn(name, f"{qid} transcription note — {a['transcription_note']}")
            elif not a.get("file"):
                err(name, f"RULE 5 — {qid} has an asset with no file path")
            elif not a.get("alt"):
                warn(name, f"RULE 5 — {qid} asset has no alt text (accessibility)")

        src = str(q.get("source", ""))
        if not q.get("verified", False) and re.search(r"\bUNEB\b", src, re.I):
            err(name, f"RULE 9 — {qid} names UNEB in source but verified=false")
        if q.get("verified", False) and not src.strip():
            err(name, f"RULE 9 — {qid} is verified=true but has no source string")
        if "TEMPLATE" in src.upper() and q.get("verified", False):
            err(name, f"RULE 9 — {qid} still says TEMPLATE but is marked verified")

    if fmt == "written":
        check_paper_structure(name, data, qs)

    fv = data.get("source", {}).get("verified", False)
    qv = sum(1 for q in qs if q.get("verified"))
    if fv and qv != len(qs):
        err(name, f"RULE 9 — file marked verified but only {qv}/{len(qs)} questions are")

    status = "VERIFIED" if fv else "unverified"
    print(f"  {name:26} {len(qs):>4} questions  year {year}  {fmt:8} {status}")
    if unanswered:
        warn(name, f"{unanswered}/{len(qs)} questions have no answer recorded "
                   "(answer_status: not_supplied)")


def main():
    args = sys.argv[1:] or sorted(glob.glob("data/papers/*.json"))
    files = [f for a in args for f in (glob.glob(a) if "*" in a else [a])]
    files = [f for f in files if not f.endswith(".template.json")]
    if not files:
        print("No data files found. Put year files in data/papers/ as sst-YYYY.json")
        return 0

    print(f"\nChecking {len(files)} file(s)\n" + "-" * 70)
    for f in sorted(files):
        check(f)
    print("-" * 70)
    for w in WARNINGS: print(w)
    for e in ERRORS:   print(e)
    print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
    if ERRORS:
        print("FAILED — fix the errors above before importing.\n")
        return 1
    print("PASSED — safe to import.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
