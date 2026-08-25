# Written Exercises — how the section works

## The flow

```
WRITTEN EXERCISES
  → CLASS      P.4 · P.5 · P.6 · P.7
  → SUBJECT    Social Studies · Mathematics · Science · English
  → TOPIC      only the NCDC topics of that class and subject
  → SET        Basic Practice · More Practice · … · Random Practice
  → QUESTIONS  one at a time, with a writing area (and a working area in Maths)
  → SUBMIT
  → RESULTS    marks, right / partly / wrong, spelling notes, the answer
  → REVIEW MY MISTAKES  ·  TRY AGAIN  ·  SAVE AND FINISH
```

## Where the questions come from

**Nothing here is new or invented.** Every question is a revision question that was
already written into a topic note, checked against the NCDC curriculum, and answered.
`tools/build_exercises.py` re-files them by class → subject → topic and records how each
one can be marked.

| | |
|---|---|
| Questions | **2,085** |
| Exercise sets | **242** |
| Topics covered | **121** |
| Classes | P.4 (SST only) · P.5 · P.6 · P.7 |

Each topic's questions are split into sets of ten. A topic with 15 questions gets two
sets; the short remainder is folded into the previous set so **no question is ever
dropped** — `validate_exercises.py` fails the build if one is.

## Why the MCQ practice bank was not used

`data/practice/*.json` holds 2,212 multiple-choice questions. They carry a `topic` field,
but those labels are the bank's own (`Geography`, `Number Theory`, `Addition`) and do
**not** match the NCDC curriculum topic names (`Location of Africa on the Map of the
World`, `Patterns and Sequences`). Mapping one onto the other would mean guessing, and a
wrong guess would file a question under the wrong topic. They are therefore left in the
existing **Practice** tab, where they are only ever shown by class and subject.

## How marking works, offline

| Kind | How many | How it is marked |
|---|---|---|
| `auto` | 621 | Short or numeric answer. Compared after normalising case, punctuation and dashes. Numbers must match; wording may differ. A near miss (one or two letters out) still earns the mark and shows a spelling note. |
| `list` | 322 | An *"Any four of …"* answer. The listed points are split up and the app counts how many the learner mentioned — **one mark per point**, so partial credit is normal. |
| `open` | 10 | *"Your own answer"* — always credited, with guidance shown. |
| `self` | 1,132 | A longer written answer. The app does **not** guess. After submitting, the learner sees the model answer and taps **I got it right / Partly / Not right**. |

**46% is marked by the app; 54% the learner marks against the answer.** That split is
deliberate. Marking a child's prose by string matching would fail them for saying the
right thing in different words, and that is worse than asking them to check honestly.

### Marking accuracy, measured

Run over all 2,085 questions:

| The learner types… | auto right | auto wrong |
|---|---|---|
| the model answer exactly | **621 / 621** | 0 — no correct answer is ever marked wrong |
| the model answer with a spelling slip | 617 / 621 | 4 |
| nonsense | 4 | 617 |
| nothing | 0 | 621 |

## Answers stay hidden

`SCREENS.exDo` never renders the answer. The render harness checks all 2,085 question
screens for a leaked answer and finds none.

**Being honest about the limit:** the app is one offline HTML file, so the answers are
inside the file. A learner who opens the page source could read them. Hiding them
properly needs a server, which would break offline use. The section is built for a
learner who wants to practise, not to defeat someone determined to cheat.

## The questions are shuffled every time

Opening an exercise **always builds a fresh run**:

* the questions are put in a new random order (Fisher–Yates, so the shuffle is even —
  `sort(() => Math.random() - 0.5)` is not);
* it always starts at **question 1**;
* **nothing is resumed.** If a learner leaves part-way through, that attempt is thrown
  away. Coming back gives a new shuffle from the beginning, with no old answers kept.

A named set always contains **exactly its own questions** — only the order changes, so
nothing is added or dropped. **Random Practice** goes further and draws a different
sample from the whole topic each time.

Both screens say this plainly, so a learner is never surprised to lose their place.

Checked over 400 openings of one 10-question set: all 10 questions appear first between
28 and 52 times, and six consecutive openings gave six different orders.

## What is saved

Progress lives in `localStorage` on that device only — nothing is sent anywhere.

* **My exercises** — date, topic, set, marks and score for the last 60 finished sets.
* **Topic progress** — attempted, correct, percentage, and a band:
  **Good** (75%+) · **Needs practice** (50–74%) · **Needs work** (under 50%).

## Not built yet

* **Mixed Revision** across several topics — the spec asks for it; the per-topic sets came
  first. The data supports it whenever it is wanted.
* **Search** across topics.
* Religious Education, Local Language and CAPE — **no curriculum document is held for
  these**, so they are not offered at all rather than shown empty.
* P.4 Mathematics, English and Science — the syllabuses are held and verified, but the
  notes are not written yet, so those screens say so plainly.

## Rebuilding

`python3 tools/build_all.py` runs `build_exercises.py`, then `validate_exercises.py`
(class, subject and topic purity; no dropped or duplicated question; marking metadata
sane), then embeds `EXERCISE_BANK` into `index.html`.

`tools/patch_exercises.py` adds the section to `index.html` and is safe to re-run.
