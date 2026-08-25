# SST Practice Bank — P.4 to P.7

Four **separate** datasets. The learner's class is the primary filter for everything.

```
data/practice/sst-p4.json     43 questions   18 topics   E19 / M19 / H5
data/practice/sst-p5.json     32 questions   17 topics   E6  / M19 / H7
data/practice/sst-p6.json     32 questions   18 topics   E3  / M16 / H13
data/practice/sst-p7.json     45 questions    6 topics   E6  / M17 / H22
                             ─────────────
                             152 questions
```

**These are original questions written for this app.** No PLE paper is copied. They are kept
entirely separate from the past-paper archive in `data/sst-YYYY.json`.

---

## Class purity — enforced three times

The brief's most important rule is *never mix classes*. It is enforced at three layers, not by
discipline:

1. **In the data** — every record carries `class: "P6"` *and* an ID prefixed `P6_SST_`.
   Two independent signals that must agree.
2. **In the validator** — `tools/validate_practice.py` rejects a class-field mismatch, an ID
   prefix mismatch, a disagreement between the two, a duplicate ID or question text across
   *any* two datasets, and any question text shared between classes.
3. **In the app** — `pbAll(cls)` filters by class *and* re-checks each record's own class field.
   `startPractice()` applies a final `items.filter(q => q.class === cls)` before anything is
   shown. A wrong-class record cannot reach a learner even if the data were corrupted.

Verified: 5,000 served questions per class, **0 foreign questions**.

---

## Question record

```json
{
  "id": "P7_SST_GEO_002", "class": "P7", "subject": "SST",
  "topic": "Geography", "subtopic": "Physical Features",
  "difficulty": "Medium", "questionType": "multiple_choice", "renderAs": "mcq",
  "question": "Which of these features was formed by faulting?",
  "options": ["A. Mount Elgon", "B. Lake Albert", "C. Lake Victoria", "D. Mount Muhavura"],
  "correctAnswer": "B",
  "explanation": "Lake Albert lies in the Rift Valley, formed when land sank between faults."
}
```

`questionType` is the pedagogical label (multiple_choice, scenario, cause_effect, comparison,
application, map_skill, identification, fill_blank, short_answer, true_false, matching).
`renderAs` tells the app how to draw it:

| renderAs | Count | Learner does |
|---|---|---|
| `mcq` | 101 | taps one of four options |
| `fill` | 43 | types an answer (accepted spellings in `answers`) |
| `tf` | 4 | taps True or False |
| `match` | 4 | taps a chip to pair each item |

---

## Practice modes

Quick (10) · Topic · Class · **Weak Topic** (auto-built from topics below 60% after 2+ attempts)
· Revision (20) · Exam (20) · **PLE Preparation — P7 only**, refused with a message for other classes.

Answer options are shuffled on every serve. Shuffling never loses the correct answer —
verified across 2,020 shuffles of every MCQ.

## Progress

Kept per class in `state.progress[cls]` — attempted, correct, and a per-topic breakdown.
P4 performance is never added to P7. The progress screen shows accuracy per topic and offers
a one-tap weak-topic session.

## Feedback

Correct → "Correct!" + the explanation. Wrong → "Not quite." + the explanation of the right
idea. No harsh wording anywhere.

---

## Status against the 800 target

```
CLASS   HAVE  TARGET   GAP        EASY     MEDIUM       HARD   TOPICS
P4       105     200     95      47/70      46/80      12/50       25
P5        77     200    123      15/70      44/80      18/50       25
P6        75     200    125       5/70      38/80      32/50       30
P7       101     200     99      11/70      45/80      45/50        6
TOTAL    358     800    442                                  45% done
```

**442 questions remain to be authored.** The validator now enforces the target and exits 1
until it is met, listing the exact shortfall per class and per difficulty band. Integrity
(class purity, IDs, answers, explanations) passes cleanly today — the only failure is the count.

```bash
python3 tools/validate_practice.py                  # fails: target not met, shows the gap
python3 tools/validate_practice.py --allow-partial  # passes if integrity is clean
```

### Why not 800 in one go

Each question needs a class-appropriate concept, three plausible distractors and a
child-readable explanation. Padding to 800 would produce the near-duplicates Rule 11 forbids
("What is the capital of Uganda?" three ways), which is worse for a learner than a smaller
honest bank. The remaining 442 are best written in batches of 50–100, ideally with a Ugandan
SST teacher checking level-appropriateness.

### Adding the next batch

Create `tools/batches/batch3.py`:

```python
from qhelpers import M, T, F, P

P4 = [
  M("P4","Weather","Seasons","Easy","Which season has the most rainfall?",
    ["Dry season","Wet season","Windy season","Cold season"],"B",
    "The wet season is when most rain falls."),
]
P5, P6, P7 = [], [], []
EXTRA = {"P4": P4, "P5": P5, "P6": P6, "P7": P7}
```

Then:

```bash
python3 tools/build_practice_bank.py     # merges every batch, renumbers IDs 001..N
python3 tools/validate_practice.py       # shows the remaining gap
```

**IDs are assigned by the builder**, sequentially per class (`P4_SST_001` … `P4_SST_105`).
Batches can never collide, and duplicate IDs are impossible by construction.

### Priority for the next batches

The difficulty gaps matter more than the raw totals:

| Class | Most needed |
|---|---|
| P6 | **+65 Easy** — currently only 5 |
| P7 | **+59 Easy** — recall-level revision questions |
| P5 | **+55 Easy** |
| P4 | **+38 Hard** — reasoning that is still P4-appropriate |

## Verified in the shipped app

- 358 questions, **0 foreign records**, **0 duplicate IDs**
- 40,000 questions served across 4,000 simulated sessions — **0 class leaks**
- 9 question types in use: multiple_choice 200, fill_blank 65, cause_effect 31, map_skill 23,
  scenario 14, true_false 10, matching 7, application 6, comparison 2
- Answer options shuffled every serve; the correct answer is never lost
