#!/usr/bin/env python3
"""
audit_notes_completeness.py — the owner's completeness audit.

Checks, for every class and subject:
  1. Thin topics: fewer than 300 words of notes (the build validator
     already refuses < 600, so any hit here means something is wrong).
  2. Questions from nowhere: every notes-practice and written-exercise
     question is checked against ITS OWN topic's notes text — if none of
     the question's distinctive words appear in the notes, the question
     is testing something the notes never taught. Those are listed so the
     notes (or the question) can be fixed. Nothing is auto-written:
     content changes stay a human decision.

Usage: python3 tools/audit_notes_completeness.py     (run from ple-app/)
"""
import glob, json, re, sys

STOP = set("""which term means meant what following statement correct answer called about
under given people number give name list any the with from that this have been will
would should there their these those where when whose whom also into than then them
each other more most some such only very much many both neither either because while
during before after between among through against without within across along being
does done doing said says made make makes take takes taken come comes came""".split())

def words(text, minlen=5):
    return [w for w in re.sub(r"[^a-z0-9\s]", " ", str(text).lower()).split()
            if len(w) >= minlen and w not in STOP]

def topic_text(topic):
    parts = []
    for s in topic["sections"]:
        parts.append(s.get("title", ""))
        for b in s.get("blocks", []):
            parts.append(b.get("x", ""))
            parts.extend(b.get("items", []))
            if b.get("t") == "table":
                parts.extend(b.get("head", []))
                parts.extend(c for r in b.get("rows", []) for c in r)
    return " ".join(parts)

def main():
    thin, nowhere = [], []
    for f in sorted(glob.glob("data/notes/*.json")):
        d = json.load(open(f, encoding="utf-8"))
        cls, subj = d["class"], d["subject"]
        for t in d["topics"]:
            text = topic_text(t)
            if t.get("words", 0) < 300:
                thin.append(f"{t['id']} {t['title']} ({t.get('words', 0)} words)")
            # question coverage for this topic
            nfile = f"data/practice/notes-{subj.lower()}-{cls.lower()}.json"
            efile = f"data/exercises/{cls.lower()}-{subj.lower()}.json"
            qs = []
            try:
                nb = json.load(open(nfile, encoding="utf-8"))
                qs += [q for q in nb["questions"] if q.get("topic") == t["title"]]
            except Exception:
                pass
            try:
                eb = json.load(open(efile, encoding="utf-8"))
                et = [x for x in eb.get("topics", []) if x.get("title") == t["title"]]
                for x in et:
                    qs += x.get("questions", [])
            except Exception:
                pass
            low = text.lower()
            for q in qs:
                stem = q.get("q") or q.get("question") or ""
                key = words(stem)
                if len(key) >= 3 and not any(w in low for w in key):
                    nowhere.append(f"{t['id']} :: {stem[:70]}")
    print(f"  thin topics (<300 words): {len(thin)}")
    for x in thin[:10]:
        print("   THIN:", x)
    print(f"  questions from nowhere (no key term in notes): {len(nowhere)}")
    for x in nowhere[:15]:
        print("   NOWHERE:", x)
    if thin or nowhere:
        print(f"  AUDIT: {len(thin)} thin, {len(nowhere)} unbacked questions — fix before pushing")
        return 1
    print("  AUDIT CLEAN — every question is backed by its topic's notes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
