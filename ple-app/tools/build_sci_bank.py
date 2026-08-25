#!/usr/bin/env python3
"""
build_sci_bank.py — assemble the P.4-P.7 Science practice datasets.

Science is owner-authored only, so this builder just loads the batches in
tools/batches_sci/, removes exact repeats (reporting each), assigns sequential
IDs and writes one file per class that has content.
"""
import json, os, glob, importlib.util, re

OUT = "data/practice"
CLASSES = ("P4", "P5", "P6", "P7")


def main():
    banks = {c: [] for c in CLASSES}
    bdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batches_sci")
    for f in sorted(glob.glob(os.path.join(bdir, "*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        extra = getattr(mod, "EXTRA", {})
        for cls, qs in extra.items():
            banks[cls].extend(qs)
        print("  + " + os.path.basename(f) + ": " +
              ", ".join(f"{c}+{len(q)}" for c, q in extra.items()))

    norm = lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()
    os.makedirs(OUT, exist_ok=True)
    print()
    print(f"{'CLASS':6}{'TOTAL':>7}{'EASY':>7}{'MEDIUM':>8}{'HARD':>6}{'TOPICS':>8}")
    grand = 0
    for cls in CLASSES:
        qs = banks[cls]
        if not qs:
            continue
        seen, kept, skipped = set(), [], []
        for q in qs:
            k = norm(q["question"])
            (skipped if k in seen else kept).append(q)
            seen.add(k)
        if skipped:
            print(f"  ! {cls}: {len(skipped)} exact duplicate(s) not served:")
            for q in skipped:
                print(f"      '{q['question'][:60]}'")
        for i, q in enumerate(kept, 1):
            q["id"] = f"{cls}_SCI_{i:03d}"

        topics = {}
        for q in kept:
            topics.setdefault(q["topic"], set()).add(q["subtopic"])
        doc = {"class": cls, "subject": "Science",
               "curriculum": "Uganda primary Science",
               "topics": {t: sorted(v) for t, v in sorted(topics.items())},
               "total": len(kept), "questions": kept}
        with open(f"{OUT}/sci-{cls.lower()}.json", "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        d = {k: sum(1 for q in kept if q["difficulty"] == k) for k in ("Easy", "Medium", "Hard")}
        grand += len(kept)
        print(f"{cls:6}{len(kept):>7}{d['Easy']:>7}{d['Medium']:>8}{d['Hard']:>6}{len(topics):>8}")
    print(f"\nTOTAL {grand} Science questions written to {OUT}/")


if __name__ == "__main__":
    main()
