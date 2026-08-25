# Practice questions built from the study notes

## Why

Nine of the sixteen class+subject slots in the **Practice** tab had fewer than 100
questions, and English had none at all. Rather than invent questions, they were derived
from notes that were already written against the NCDC curriculum and checked.

## Before and after

| Class | SST | Maths | Science | English |
|---|---:|---:|---:|---:|
| P.4 | 105 → **255** | 200 → **200** | 0 → **0** | 0 → **0** |
| P.5 | 77 → **227** | 200 → **350** | 0 → **150** | 0 → **150** |
| P.6 | 75 → **194** | 200 → **350** | 0 → **150** | 0 → **150** |
| P.7 | 480 → **630** | 500 → **650** | 100 → **250** | 0 → **150** |

**1,919 new questions.** Fourteen of the sixteen slots are now at or above 100.

**P.4 Science and P.4 English are still at zero, and that is honest.** They can only be
built from notes, and the P.4 Science and English notes have not been written yet. The
syllabuses are held and verified, so both can be filled as soon as those notes exist.

## Nothing is invented

Every stem and every correct answer is lifted from a note. The three wrong options are
real items taken from **other** entries in the same class and subject — true statements
about something else, so they read plausibly but do not answer the question asked.

| Source in the note | Question made |
|---|---|
| KEY DEFINITIONS table | *"What is meant by X?"* and *"Which term means …?"* |
| IMPORTANT FACTS bullet | the bold phrase is blanked out |
| EXAMINATION POINTS bullet | same |
| a short revision question | asked directly |

## Rules the builder follows

* a distractor is never equal to, inside, or containing the right answer
* a distractor is taken from a **different topic** wherever one is available
* **shape matching** — a one-word answer only gets one-word distractors, a number only
  gets numbers, and option lengths are kept comparable, so the answer is never
  guessable from the look of the options
* distractors sharing 60% or more of their words with the answer are thrown out
* a fill-in stem must still read as a sentence: at least five words left after the blank,
  and the blank never starts the sentence
* anything depending on the learner's own district or own answer is skipped
* duplicate stems are dropped
* the random seed is fixed per class+subject, so rebuilding gives the same questions

## What the validator checks

`tools/validate_notes_practice.py` fails the build on any of:

* class or subject not matching the file
* not exactly four options, or options not labelled A, B, C, D in order
* `correctAnswer` not pointing at the option holding `answerValue` — checked, not assumed
* any other option repeating, containing, or contained by the right answer
* two options the same, or an empty option
* duplicate id or duplicate stem
* a missing origin, or any claim of UNEB origin

All **1,919 pass**.

## Wiring

`tools/build_notes_practice.py` writes `data/practice/notes-<subject>-<class>.json`.
`inject.py` merges them into the bank the Practice tab already uses — SST into
`PRACTICE_BANK`, Maths into `MATH_BANK`, Science into `SCI_BANK` — and fills the new
`ENG_BANK`. **English is now a fourth subject in the practice switcher.**

The subject label on each question matches `SUBJ_META` exactly (`SST`, `Mathematics`,
`Science`, `English`); the app re-checks class and subject on every record before showing
it, and a mismatch means the question is silently skipped, so the labels have to agree.

## Honest limits

* These are **recall and definition questions**. They test whether the learner has read
  and understood the notes. They are not a substitute for the worked, multi-step
  questions in **Written Exercises**, and they are not modelled on any past paper.
* Because distractors come from elsewhere in the same subject, a very well-read learner
  may occasionally spot one that is obviously off-topic. That is the price of not
  inventing content.
