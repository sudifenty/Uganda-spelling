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
# A table is a source of term->meaning questions when its SECOND column is
# definitional ("Meaning", "What it is", "How it helps", ...). This harvests
# both the classic KEY DEFINITIONS tables and the restructured Q&A tables.
DEF_HEAD = re.compile(r"^(meaning$|what |how |why |danger|full name|service |work$|suggested solution)", re.I)


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


# the app hides "About this topic" and numbers the remaining sections from 0 —
# state.noteSeen keys use those VIEW indices, so every sec we emit must too
ABOUT_SEC = re.compile(r"^about\s+this\s+topic\b", re.I)


def view_map(topic):
    """raw section index -> app view index (About this topic excluded)"""
    m, j = {}, 0
    for i, s in enumerate(topic["sections"]):
        if not ABOUT_SEC.search((s["title"] or "").strip()):
            m[i] = j
            j += 1
    return m


def sec_index(topic, rx):
    vm = view_map(topic)
    for i, s in enumerate(topic["sections"]):
        if re.search(rx, s["title"], re.I):
            return vm.get(i, 0)
    return 0


# sections that AGGREGATE material from the whole topic — a term first
# appearing here has not been taught yet at that point of the notes
AGG_SEC = re.compile(
    r"^(key definitions|important facts|examination points|revision questions"
    r"|answers to revision|a note on sources|.*quick revision|final revision"
    r"|important language|important grammar|main competenc|main grammar"
    r"|common mistakes)", re.I)

STOPW = {"their", "there", "which", "means", "meant", "people", "should",
         "would", "because", "these", "those", "about", "other", "after",
         "before", "first", "words", "given", "using", "called", "being",
         "makes", "things", "someone", "something", "anything", "through",
         "between", "against", "during", "without", "within", "another"}


def section_text(s):
    parts = []
    for b in s["blocks"]:
        if b.get("x"):
            parts.append(str(b["x"]))
        if b.get("items"):
            parts.extend(str(i) for i in b["items"])
        if b.get("head"):
            parts.extend(str(h) for h in b["head"])
        for r in (b.get("rows") or []):
            parts.extend(str(c) for c in r)
    return clean(" ".join(parts)).lower()


def sec_for_def(topic, term, fallback):
    """VIEW index of the section that actually TEACHES the term — where it is
    defined ("X is/are/means...") or asked ("Who/What is a X?"). Only if no
    such section exists do we fall back to the first mention."""
    t_ = re.escape(term.lower().strip())
    pat_def = re.compile(r"\b" + t_ + r"\b[^.]{0,40}\b(is|are|means|refers)\b", re.I)
    pat_q = re.compile(r"(who|what)\s+(is|are)\s+(a\s+|an\s+|the\s+)?" + t_ + r"\b", re.I)
    vm = view_map(topic)
    for i, s in enumerate(topic["sections"]):
        if i not in vm or AGG_SEC.search(s["title"] or ""):
            continue
        st = section_text(s)
        if pat_def.search(st) or pat_q.search(st):
            return vm[i]
    low = term.lower().strip()
    for i, s in enumerate(topic["sections"]):
        if i not in vm or AGG_SEC.search(s["title"] or ""):
            continue
        if low and low in section_text(s):
            return vm[i]
    return fallback


def sec_for_text(topic, text, fallback):
    """VIEW index of the teaching section for `text` — the section whose own
    words best cover the distinctive words of the text (at least 60% of
    them). Best coverage wins, so "safety rules for cyclists" lands on the
    cyclists section, not on an earlier section that merely mentions the
    word "cyclists"."""
    ws = [w for w in re.findall(r"[a-z]{5,}", str(text).lower()) if w not in STOPW]
    if not ws:
        return fallback
    vm = view_map(topic)
    best_i, best_r = None, 0.0
    for i, s in enumerate(topic["sections"]):
        if i not in vm or AGG_SEC.search(s["title"] or ""):
            continue
        st = section_text(s)
        hits = sum(1 for w in ws if w in st)
        r = hits / float(len(ws))
        if r >= 0.6 and r > best_r:
            best_i, best_r = vm[i], r
    return best_i if best_i is not None else fallback


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
        didx = sec_index(t, r"^key definitions$")
        if d:
            for b in d["blocks"]:
                if b["t"] == "table" and len(b["head"]) >= 2:
                    for r in b["rows"]:
                        if len(r) < 2:
                            continue
                        term, mean = clean(r[0]), clean(r[1])
                        if term and mean and not SKIP.search(term + mean) \
                           and len(mean.split()) >= 3:
                            defs.append((tno, title, term, mean,
                                         sec_for_def(t, term, didx)))
        # restructured Q&A notes (and classic body tables): every
        # definitional two-column table in every section is material.
        # ROLE columns are skipped: "What is meant by X?" must never ask
        # for a role (owner's wording rule) — roles are asked in the notes
        # exercises as "What was the role of X?" instead.
        ROLE_HEAD = re.compile(r"what (it|the person) does|what it did|\brole\b|^work$|function|duty|responsib|importance|why it matters|how it helps|^uses?$|used for", re.I)
        ROLE_ANS = re.compile(r"^(ran|carried|controlled|managed|promoted|provided|collected|flew|handled|lent|supplied|transported|delivered|supervised|maintained|operated|ensured|served|worked|used to|used for|shows?|makes?|provides?|helps?|represents?|protects?|prevents?|carries|forms?|connects?|serves?|supplies|controls?|manages?|promotes?|collects?|handles?|runs?|responsible for)\b", re.I)
        vmap = view_map(t)
        for si, s_ in enumerate(t["sections"]):
            vsi = vmap.get(si)
            for b in s_["blocks"]:
                if b["t"] == "table" and len(b.get("head", [])) == 2 \
                   and DEF_HEAD.match(b["head"][1].strip()) \
                   and not ROLE_HEAD.search(b["head"][1].strip()):
                    for r in b["rows"]:
                        if len(r) < 2:
                            continue
                        term, mean = clean(r[0]), clean(r[1])
                        if term and mean and not SKIP.search(term + mean) \
                           and 3 <= len(mean.split()) <= 15 \
                           and 1 <= len(term.split()) <= 5 \
                           and not NUMISH.match(mean) \
                           and not ROLE_ANS.match(mean):
                            defs.append((tno, title, term, mean,
                                         vsi if (vsi is not None and not AGG_SEC.search(s_["title"] or ""))
                                         else sec_for_def(t, term, vsi if vsi is not None else 0)))
        for name in (r"^important facts", r"^examination points"):
            s = sec(t, name)
            fidx = sec_index(t, name)
            for it in ul_items(s):
                txt = clean(it)
                if SKIP.search(txt) or len(txt.split()) < 6:
                    continue
                for b in bolds(it):
                    if 1 <= len(b.split()) <= 7 and b.lower() not in txt.lower()[:0] + " ":
                        facts.append((tno, title, txt, b, fidx))
                        break
        qs = [clean(x) for x in ol_items(sec(t, r"^revision questions$"))]
        ans = [clean(x) for x in ol_items(sec(t, r"answers to revision"))]
        ridx = sec_index(t, r"^revision questions$")
        for q, a in zip(qs, ans):
            if SKIP.search(q) or SKIP.search(a):
                continue
            if 1 <= len(a.split()) <= 6 and not a.lower().startswith("any "):
                shorts.append((tno, title, q, a,
                               sec_for_text(t, q + " " + a, ridx)))
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


def make(rng, cls, subj, kind, tno, topic, stem, correct, pool, seq, sec=None):
    ds = pick_distractors(rng, correct, pool, tno)
    if not ds:
        return None
    opts = ds + [correct]
    rng.shuffle(opts)
    letters = "ABCD"
    idx = opts.index(correct)
    q = {
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
    if isinstance(sec, int):
        # index of the notes section that teaches this — the app only offers
        # the question once the learner has read up to that section
        q["sec"] = sec
    return q


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

        mean_pool = [(t, m) for t, _, _, m, _ in defs]
        term_pool = [(t, x) for t, _, x, _, _ in defs]
        bold_pool = [(t, b) for t, _, _, b, _ in facts]
        ans_pool = [(t, a) for t, _, _, a, _ in shorts]

        out, seen, seq = [], set(), 1

        def add(kind, tno, topic, stem, correct, pool, sec=None):
            nonlocal seq
            key = re.sub(r"\W+", "", stem.lower())[:90]
            if key in seen or len(out) >= CAP:
                return
            q = make(rng, cls, subj, kind, tno, topic, stem, correct, pool, seq, sec)
            if q:
                out.append(q)
                seen.add(key)
                seq += 1

        # 1 — definitions, both directions
        for tno, topic, term, mean, sidx in defs:
            add("definition", tno, topic, f"What is meant by \u201c{term}\u201d?", mean, mean_pool, sidx)
        for tno, topic, term, mean, sidx in defs:
            add("term", tno, topic, f"Which term means: {mean}", term, term_pool, sidx)
        # 2 — short revision questions
        for tno, topic, q, a, sidx in shorts:
            add("recall", tno, topic, q, a, ans_pool, sidx)
        # 3 — cloze from facts and examination points
        for tno, topic, txt, b, sidx in facts:
            stem = re.sub(re.escape(b), "__________", txt, count=1)
            if "__________" not in stem:
                continue
            rest = stem.replace("__________", " ").split()
            if len(rest) < 5:                      # "Main fish: ____" is not a question
                continue
            if stem.strip().startswith("__________"):
                continue
            add("fact", tno, topic, f"Complete: {stem}", b, bold_pool, sidx)

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
