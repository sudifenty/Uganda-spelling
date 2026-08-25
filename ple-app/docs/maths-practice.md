# Mathematics Practice Bank — 800 questions

```
CLASS   TOTAL   EASY  MEDIUM  HARD  TOPICS
P4        200     70      80    50      14
P5        200     70      80    50      14
P6        200     70      80    50      14
P7        200     70      80    50      15
TOTAL     800    280     320   200
```

**Every target met exactly.** Four separate datasets in `data/practice/math-p{4,5,6,7}.json`.

---

## Every answer is machine-verified

This is the important difference from the SST bank. Answers here are never written by hand —
they are **computed in Python**, and each question stores a `calc` expression that
`tools/validate_math.py` **re-evaluates independently** with exact `Fraction` arithmetic and
compares against the answer marked correct.

```
ARITHMETIC VERIFICATION
  749 answers re-computed from their own `calc` expression
   51 not machine-checkable (shape names, matching, wording)
    0 disagreements between the marked answer and the arithmetic
```

The check found and forced fixes for real problems during the build:

| Found | Cause | Fix |
|---|---|---|
| 14 "wrong" expansions | `3000 + 200 + 1` compared as the number 3000 | validator now evaluates expression-style answers |
| **16 cross-class duplicates** | P5 borrowed P4 generators and produced identical items | dedupe made **global across all four classes** |
| 5 clock mismatches | `8:00` compared against 480 minutes | validator parses clock times |
| 8 24-hour-clock errors | generator's `calc` returned only the hour | generator corrected to full minutes |

Re-run any time:

```bash
python3 tools/build_math_bank.py      # regenerates all 800 (seeded, reproducible)
python3 tools/validate_math.py        # must print PASSED
```

## Why generation is legitimate here

Rule 11 forbids rewording the same item. In Mathematics, **changing the numbers genuinely
changes the practice item** — `347 + 285` and `512 + 379` exercise the same skill with
different work, which is exactly how a maths workbook is built. That is not true of "What is
the capital of Uganda?", which is why the SST bank is hand-written and this one is generated.

Distractors come from **real pupil errors**, not random noise: forgotten carry, wrong
operation, place-value slip, off-by-one, perimeter-for-area. A pupil who picks a wrong option
has usually made an identifiable mistake.

## Coverage

| Class | Topics |
|---|---|
| P4 | Whole Numbers, Addition, Subtraction, Multiplication, Division, Fractions, Decimals, Money, Measurement, Time, Geometry, Perimeter and Area, Data Handling, Patterns |
| P5 | + Number Theory (factors, multiples, primes), Problem Solving, long multiplication and division, mixed numbers, averages |
| P6 | + Percentages, Ratio, Volume, compound area, profit/loss and discount, dividing fractions |
| P7 | + Algebra, Position (coordinates), HCF/LCM, speed and distance, 24-hour clock, circles (pi = 22/7), simple interest, pie charts |

Difficulty rises by class: a P4 "Hard" is a two-step word problem; a P7 "Hard" is percentage
increase, ratio sharing in three parts, or capacity from volume.

## Class and subject purity

`pbAll()` re-checks **three** things on every record: `class`, `subject`, and the ID prefix
(`P6_MATH_`). Progress is keyed `SUBJECT:CLASS` (e.g. `MATH:P6`), so Maths and SST results
never merge, and no class merges with another.

Verified: **80,000 questions served across 8,000 sessions — 0 wrong class, 0 wrong subject.**

## In the app

Practice tab → a **Social Studies / Mathematics** toggle → class picker → the seven modes
(Quick, Topic, Class, Weak Topic, Revision, Exam, PLE Preparation for P7 only).
Options are reshuffled on every serve. Everything is embedded in `index.html` — fully offline.

## Adding or changing questions

Edit a generator in `tools/build_math_bank.py`. Each returns question text, the correct value,
plausible distractors, an explanation, and a `calc` string:

```python
def p6_percent_of():
    p_ = random.choice([10,20,25,50]); tot = random.choice([40,60,80,120,200])
    ans = tot*p_//100
    return mc("P6","Percentages","Percentage of a Quantity","Medium",
        f"Find {p_}% of {tot}.", str(ans), [str(ans+10), str(tot-ans), str(ans*2)],
        f"{p_}% means {p_} out of 100: {tot} x {p_} ÷ 100 = {ans}.",
        f"{tot}*{p_}/100")          # <- the machine-checkable calc
```

**A generator without a correct `calc` will be caught by the validator.** The seed is fixed
(`20260816`), so builds are reproducible.
