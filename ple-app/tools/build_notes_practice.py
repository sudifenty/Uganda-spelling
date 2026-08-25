#!/usr/bin/env python3
"""
build_notes_practice.py — derive multiple-choice practice questions from the
study notes, so every class+subject that has notes reaches at least 100
practice questions.

NOTHING IS INVENTED. Every question stem and every correct answer is taken
straight out of a note that was already written against the NCDC curriculum and
checked. The three wrong options are real items lifted from *other* entries in
the same class and subject — they are true statements about something else, so
they read plausibly, but they do not answer the question asked.

Question sources inside each topic
----------------------------------
  KEY DEFINITIONS table   -> "What is meant by X?"  and  "Which term means ...?"
  IMPORTANT FACTS bullets -> a bold phrase is blanked out (cloze)
  EXAMINATION POINTS      -> same treatment
  short revision Q/A      -> asked directly

Safety rules applied
--------------------
  * a distractor is never equal to, or a substring of, the right answer
  * a distractor must come from a different topic where one is available
  * numeric answers only ever get numeric distractors, and word answers word
    distractors, so the shape of the options never gives the answer away
  * distractors that share most of their words with the answer are rejected
  * anything that depends on the learner's own district or own answer is skipped
  * duplicate stems are dropped

Output: data/practice/notes-<subject>-<class>.json

Usage: python3 tools/build_notes_practice.py    (run from the ple-app folder)
"""
import json, glob, os, random, re, sys

SRC = "data/notes"
OUT = "data/practice"
TARGET = 100          # minimum questions per class+subject
CAP = 150             # don't balloon the file
# these must match the labels the app filters on in SUBJ_META, exactly
SUBJ_NAME = {"SST": "SST", "MATH": "Mathematics",
             "SCI": "Science", "ENG": "English"}

SKIP = re.compile(r"your own|\(your |\(name\)|\(list them\)|draw |your district", re.I)
NUMISH = re.compile(r"^[\d,.\s%°/-]+$")


def clean(s):
    s = re.sub(r"\*\*([\s\S]+?)\*\*", r"\1", str(s))
    s = re.sub(r"(^|[^*])\*([^*\n]+)\*", r"\1\2", s)
    s = s.replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def bolds(s):
    return [clean(b) for b in re.findall(r"\*\*([^*]+?)\*\*", str(s))]


def words(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def too_similar(a, b):
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return True
    ov = len(wa & wb) / min(len(wa), len(wb))
    return ov >= 0.6


def band(s):
    """Group answers by length so the options never differ in shape."""
    n = len(s.split())
    return 1 if n == 1 else 2 if n <= 3 else 3 if n <= 7 else 4


def same_shape(a, b):
    if bool(NUMISH.match(a)) != bool(NUMISH.match(b)):
        return False
    if band(a) != band(b):
        return False
    # keep the printed options roughly the same length too
    la, lb = len(a), len(b)
    return max(la, lb) <= max(18, min(la, lb) * 2.6)


def sec(topic, rx):
    return next((s for s in topic["sections"] if re.search(rx, s["title"], re.I)), None)


def ol_items(s):
    return [i for b in s["blocks"] if b["t"] == "ol" for i in b["items"]] if s else []


def ul_items(s):
    return [i for b in s["blocks"] if b["t"] == "ul" for i in b["items"]] if s else []


def collect(pack):
    """Pull raw material out of every topic of one class+subject."""
    defs, facts, shorts = [], [], []
    for t in pack["topics"]:
        tno, title = t["topic_no"], t["title"]
        d = sec(t, r"^key definitions$")
        if d:
            for b in d["blocks"]:
                if b["t"] == "table" and len(b["head"]) >= 2:
                    for r in b["rows"]:
                        if len(r) < 2:
                            continue
                        term, mean = clean(r[0]), clean(r[1])
                        if term and mean and not SKIP.search(term + mean) \
                           and len(mean.split()) >= 3:
                            defs.append((tno, title, term, mean))
        for name in (r"^important facts", r"^examination points"):
            s = sec(t, name)
            for it in ul_items(s):
                txt = clean(it)
                if SKIP.search(txt) or len(txt.split()) < 6:
                    continue
                for b in bolds(it):
                    if 1 <= len(b.split()) <= 7 and b.lower() not in txt.lower()[:0] + " ":
                        facts.append((tno, title, txt, b))
                        break
        qs = [clean(x) for x in ol_items(sec(t, r"^revision questions$"))]
        ans = [clean(x) for x in ol_items(sec(t, r"answers to revision"))]
        for q, a in zip(qs, ans):
            if SKIP.search(q) or SKIP.search(a):
                continue
            if 1 <= len(a.split()) <= 6 and not a.lower().startswith("any "):
                shorts.append((tno, title, q, a))
    return defs, facts, shorts


def pick_distractors(rng, correct, pool, topic_no, n=3):
    """pool: list of (topic_no, text)."""
    other = [p for p in pool if p[0] != topic_no]
    rng.shuffle(other)
    same = [p for p in pool if p[0] == topic_no]
    rng.shuffle(same)
    def norm(s):
        return re.sub(r"\s+", " ", s.strip().rstrip(".").lower())

    out, taken = [], {norm(correct)}
    for _, cand in other + same:
        if len(out) == n:
            break
        if not cand or norm(cand) in taken:
            continue
        if cand.lower() in correct.lower() or correct.lower() in cand.lower():
            continue
        if not same_shape(correct, cand):
            continue
        if too_similar(correct, cand):
            continue
        out.append(cand)
        taken.add(norm(cand))
    return out if len(out) == n else None


def make(rng, cls, subj, kind, tno, topic, stem, correct, pool, seq):
    ds = pick_distractors(rng, correct, pool, tno)
    if not ds:
        return None
    opts = ds + [correct]
    rng.shuffle(opts)
    letters = "ABCD"
    idx = opts.index(correct)
    return {
        "id": f"{cls}_{subj}_N{seq:03d}",
        "class": cls, "subject": SUBJ_NAME[subj],
        "topic": topic, "subtopic": kind,
        "difficulty": "Easy" if kind == "definition" else "Medium",
        "questionType": "multiple_choice", "renderAs": "mcq",
        "question": stem,
        "options": [f"{letters[i]}. {o}" for i, o in enumerate(opts)],
        "correctAnswer": letters[idx],
        "answers": None, "pairs": None,
        "answerValue": correct,
        "explanation": f"From the {cls} {SUBJ_NAME[subj]} notes, topic {tno}: {topic}.",
        "origin": "Built from the app's own curriculum-checked study notes "
                  "(not a UNEB past paper)",
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(f"{SRC}/*.json"))
    if not files:
        sys.exit("build_notes_practice: no notes found")

    made_any = False
    for f in files:
        pack = json.load(open(f, encoding="utf-8"))
        cls, subj = pack["class"], pack["subject"]
        rng = random.Random(f"{cls}-{subj}-v1")     # stable between builds
        defs, facts, shorts = collect(pack)

        mean_pool = [(t, m) for t, _, _, m in defs]
        term_pool = [(t, x) for t, _, x, _ in defs]
        bold_pool = [(t, b) for t, _, _, b in facts]
        ans_pool = [(t, a) for t, _, _, a in shorts]

        out, seen, seq = [], set(), 1

        def add(kind, tno, topic, stem, correct, pool):
            nonlocal seq
            key = re.sub(r"\W+", "", stem.lower())[:90]
            if key in seen or len(out) >= CAP:
                return
            q = make(rng, cls, subj, kind, tno, topic, stem, correct, pool, seq)
            if q:
                out.append(q)
                seen.add(key)
                seq += 1

        # 1 — definitions, both directions
        for tno, topic, term, mean in defs:
            add("definition", tno, topic, f"What is meant by \u201c{term}\u201d?", mean, mean_pool)
        for tno, topic, term, mean in defs:
            add("term", tno, topic, f"Which term means: {mean}", term, term_pool)
        # 2 — short revision questions
        for tno, topic, q, a in shorts:
            add("recall", tno, topic, q, a, ans_pool)
        # 3 — cloze from facts and examination points
        for tno, topic, txt, b in facts:
            stem = re.sub(re.escape(b), "__________", txt, count=1)
            if "__________" not in stem:
                continue
            rest = stem.replace("__________", " ").split()
            if len(rest) < 5:                      # "Main fish: ____" is not a question
                continue
            if stem.strip().startswith("__________"):
                continue
            add("fact", tno, topic, f"Complete: {stem}", b, bold_pool)

        path = f"{OUT}/notes-{subj.lower()}-{cls.lower()}.json"
        json.dump({"class": cls, "subject": SUBJ_NAME[subj],
                   "source": "study notes", "questions": out},
                  open(path, "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))
        flag = "" if len(out) >= TARGET else f"  (only {len(out)} — below {TARGET})"
        print(f"  {cls} {SUBJ_NAME[subj]:<15s} {len(out):4d} questions -> {path}{flag}")
        made_any = True

    if not made_any:
        sys.exit("build_notes_practice: nothing built")
    return 0


if __name__ == "__main__":
    sys.exit(main())
