# SST Question Bank — Build Guide

## Read this first

**I did not write any questions, and I won't.** I don't hold verified UNEB PLE papers, and
generating 18 years of realistic-looking SST questions would break two of your own rules:

> 7. Do not invent missing questions.
> 9. Do not mark a question as official UNEB unless its source has been verified.

Invented past papers are worse than no past papers — a child revises for an exam that never
existed, and the app's credibility is gone the first time a teacher spots it. So everything
here is the machinery around the content. You supply verified papers; the pipeline enforces
your rules and the app displays them correctly.

---

## 1. Where to get verified papers

**Authoritative:** UNEB sells official past paper booklets at the **UNEB Publications Office,
Communications House, Kampala**. PLE booklets are available through 2024 [(UNEB, Aug 2025)](https://x.com/UNEB_UG/status/1961333432350306378).
This is the only source where "official UNEB" is a claim you can actually stand behind, and
buying it also settles the copyright question.

**Secondary (verify against the booklet before trusting):**

| Source | Coverage |
|---|---|
| [Sharebility / Mukalele pool](https://www.mukalele.net/sharebility/) | PLE SST by year, PDF |
| [ecolebooks.com](https://www.ecolebooks.com/download-primary-7-test-exam-and-revision-papers-pdf-p7-past-papers-uganda/) | P7 SST 1992–2010+ |
| [fresh-teacher.github.io/primary](https://fresh-teacher.github.io/primary/) | SST 1996–2015 by year |
| [asbatdigitallibrary.org](https://www.asbatdigitallibrary.org/) | includes 2022 marking guides |

⚠️ These are community re-uploads. Years get mislabelled, pages go missing, and answer keys are
often someone's guess. Treat them as a typing aid, not as truth. Note that even a commercial app
like *Past Papers UG* ships a disclaimer that it is not affiliated with UNEB — do the same.

**Two things to sort out before publishing:** whether you have permission to redistribute UNEB
questions, and whether you can display answer keys. Ask UNEB directly. A revision app that
reproduces whole papers commercially is a different legal position from a teacher's photocopy.

---

## 2. The workflow

```
verified paper (PDF or booklet)
        ↓  type it up
data/sst-questions.csv
        ↓  python3 tools/csv_to_json.py data/sst-questions.csv
data/sst-2008.json, sst-2009.json, …  +  data/bank.js
        ↓  python3 tools/validate.py data/*.json
PASSED
        ↓  paste bank.js over QUESTION_BANK in index.html
app shows real papers
```

### Step 1 — type into the CSV

Copy `data/import-template.csv` to `data/sst-questions.csv` and open it in Excel, LibreOffice or
Google Sheets. One row per question. Columns:

| Column | Notes |
|---|---|
| `year` | 2008 — never change this later (**Rule 8**) |
| `number` | `1`, `2`, `3a` — exactly as printed (**Rule 2**) |
| `section` | A / B |
| `type` | `mcq`, or `stem` for a shared map/table/passage |
| `question` | exact wording |
| `option_a`–`option_d` | all four, always (**Rule 3**) |
| `correct_answer` | A / B / C / D |
| `topic`, `subtopic` | your own tagging, optional |
| `source` | `UNEB PLE SST 2008 - Q1` — only once verified |
| `verified` | `FALSE` until a human has checked it |
| `asset_*` | for maps, diagrams, tables (**Rule 5**) |
| `parent` | `3` on rows `3a`, `3b` (**Rule 4**) |

**Shared stems.** When one map serves Q3a–3c, add a `stem` row numbered `3` carrying the map,
then set `parent=3` on 3a, 3b, 3c. The app shows the stem above each subquestion, so they can
never be separated. Stem rows need no options.

**Set `verified` to TRUE only after a person has compared the typed question against the paper.**
The validator refuses any row that names UNEB while still unverified.

### Step 2 — convert

```bash
python3 tools/csv_to_json.py data/sst-questions.csv
```

Writes one JSON file per year, plus `data/bank.js`.

### Step 3 — validate

```bash
python3 tools/validate.py data/*.json
```

Enforces all ten rules:

| Rule | Check |
|---|---|
| 1 · original order | warns if numbering is out of sequence |
| 2 · original numbering | rejects duplicates and blanks |
| 3 · all choices kept | rejects a missing A/B/C/D, or a key pointing at an empty option |
| 4 · subquestions with parent | rejects an orphan `parent` reference |
| 5 · assets attached | rejects an asset with no file; warns on missing alt text |
| 6 · no mixing years | rejects any question whose year ≠ the file's year |
| 7 · nothing invented | reports numbering gaps for you to confirm |
| 8 · year never changed | same check as Rule 6 |
| 9 · no false UNEB claim | rejects "UNEB" in source while `verified:false` |
| 10 · whole paper together | rejects `total_questions` ≠ actual count |

Exit code 0 = clean, 1 = errors. Wire it into CI if you like.

### Step 4 — import

Open `data/bank.js`, copy everything, and paste it over the `QUESTION_BANK` line in
`index.html`. The app picks it up on the next refresh.

---

## 3. What the app does with it

**Papers tab → subject → year list.** Each subject shows how many years exist. Selecting
Social Studies lists 2008, 2009, 2010 … plus an **ALL YEARS** card at the top.

Choosing a single year offers two things:

- **FULL PAPER · IN ORDER** — the historical paper, question 1 to the end, original order and
  numbering, nothing shuffled, nothing regrouped by topic
- **Quick practice from this year** — a shuffled sample from that year only

**ALL YEARS** mixes the whole bank.

**Every question carries its origin.** Under the answers the learner sees:

```
Question source: PLE Social Studies 2012 — Q17
```

The same label appears on the Review Answers screen. The year travels with the question
through shuffling, mixing and retries — it is part of the record, not a display option.

**Questions I Got Wrong** builds itself. A miss adds the question's key to a retry list; getting
it right later removes it. Practice → *Questions I Got Wrong* replays only those.

**Modes now available:** Quick · Topic · Mixed · Exam · **Practice by Year** ·
**Questions I Got Wrong**, plus Full Paper and Mixed Years reached through the year screen.

**Sample Mode.** With `QUESTION_BANK` empty the app still runs on placeholders and labels every
question *"Sample Mode · no verified paper loaded"* — so a demo can never be mistaken for real
past papers.

---

## 4. Realistic effort

A PLE SST paper is around 50–60 questions. Typing, keying and checking one year is roughly
2–4 hours. Eighteen years is **60–100 hours** of careful work. Options:

1. **Start with three years** (say 2022–2024) and ship. Recent papers matter most.
2. **Split the typing** among teachers — one year each, CSV per person, concatenate.
3. **OCR the PDFs** then correct by hand. Faster, but OCR mangles map labels and numbers, so
   the checking pass is non-negotiable.

Whichever route, keep `verified:false` until a human has signed off. The validator will not let
a claim of UNEB origin through without it.

---

## 5. Files

```
data/
├── import-template.csv        ← copy this, type into it
├── sst-2008.template.json     ← the JSON shape, annotated
└── bank.js                    ← generated; paste into index.html
tools/
├── csv_to_json.py             ← CSV → year files + bank.js
└── validate.py                ← enforces the 10 rules
```

Both scripts are plain Python 3, no packages to install.

---

## 6. Written papers (added for PLE SST 2008)

The real PLE SST paper is **not multiple choice**, so the schema carries two formats.

| `format` | Shape | Rendered as |
|---|---|---|
| `mcq` | four options, one key | practice quiz with A/B/C/D buttons |
| `written` | short answer + structured parts | **Archive Mode** — the paper as printed |

Question types inside a written paper:

| `type` | Used for |
|---|---|
| `short` | Section A single-answer question |
| `structured` | Section B question with lettered parts (nested `i`/`ii` supported) |
| `alternative` | Christian **OR** Islamic variant of a short question |
| `alternative_structured` | Christian **OR** Islamic variant, each with its own parts |

`audience: "all"` marks a question answered by every candidate.

**Archive Mode** shows one question at a time in original order, with a Christian/Islamic
toggle on alternative questions, a *Show answer* button, and the source line
`PLE Social Studies 2008 — Q17`. There is no scoring: an archive is for reading the paper as
it was set, not for grading.

### 2008 status

- 55 questions, Section A 1–40, Section B 41–55 — all 11 structure checks pass
- Wording preserved verbatim; nothing rewritten or simplified
- **Answers not supplied** — every question is `answer_status: "not_supplied"`, and
  *Show answer* says so rather than inventing one
- **Three printed items missing**: Q16 map symbol, Q41 climate table, Q46 map of Sudan.
  Each is flagged in the app so a learner is never asked to read something that isn't there
- `verified: false` until someone compares it against the official UNEB booklet. No question
  claims UNEB origin while that is the case

### 2009 status

- 55 questions, Section A 1–40, Section B 41–55 — all 13 structure checks pass
- Wording preserved verbatim
- **Q41 climate table supplied** and stored as data (12 months, 12 temperatures,
  12 rainfall values), rendered as a real table. The 12th month reads `J` in the
  transcript where December would be expected — left as supplied, flagged in-app
- **Q5 road sign and Q46 Sudan map not supplied** — flagged as requiring the original artwork
- Answers not supplied
- `verified: false` until cross-checked against the official UNEB booklet

⚠️ **Section B overlap with 2008.** As supplied, 4 of the 15 Section B questions (43, 49, 51, 52)
are word-for-word identical to 2008, and 10 more are 85–100% similar. Section A is completely
distinct (0/40 shared). This pattern suggests the Section B portion of one transcript may have
been copied from the other. Both are stored exactly as given — worth checking against the
original papers before marking either year verified.

### 2010 status

- 55 questions, Section A 1–40, Section B 41–55 — all 11 structure checks pass
- Wording preserved verbatim; zero overlap with 2008 or 2009 (0 shared items either way)
- **Different RE layout from 2008/2009:** alternatives sit at **Q36–40** and **Q51–55**
  (2008/2009 use Q37–40 and Q53–54). Q41–50 are for all candidates
- **Six visuals not supplied** — Q12 budget diagram, Q20 bird image, Q45 East Africa sketch map,
  Q47 sketch map, Q50 Uganda sketch map, Q51 drawing boxes. Each is flagged in-app
- **Q13 shares Q12's diagram** via `asset_ref`, so the two stay connected
- Answers not supplied; `verified: false`

⚠️ **Q36 Christian and Islamic wording are identical** ("Who was the wife of Adam?"). Stored as
supplied and flagged by the validator — worth checking the original, since the Islamic version
often reads "Hawa".

### Structures added for 2010

| Field | Meaning |
|---|---|
| `intro` | lead-in above a question ("Study the diagram below…") |
| `asset_ref` | this question uses the visual printed at another question |
| `line_labels` | answer blanks with printed letters (Q47 a: `A ___  B ___`) |
| `boxes` | empty drawing boxes printed on the paper (Q51 c) |
| `quote` | scripture passage with citation (Q55) |

### 2012 status

- 55 questions, Section A 1–40, Section B 41–55 — all 14 structure checks pass
- Wording preserved verbatim **including original grammar** (e.g. Q13 "sign as agreement with",
  Q30 "if he turn through") — this is an archive, so transcription errors in the source are
  reproduced rather than silently corrected
- RE layout matches 2010: alternatives at **Q36–40** and **Q51–55**; Q41–50 for all candidates
- Zero overlap with 2008, 2009 or 2010 (0 shared items with each)
- **Three visuals not supplied** — Q41 population distribution diagram, Q49 climatic graph of
  Town A, Q50 East Africa sketch map. All three carry `requires_original_visual: true`
- Q49 and Q50 are unanswerable without their artwork
- Answers not supplied; `verified: false`

### `requires_original_visual`

Now set on every question in every year whose printed artwork is missing, and cross-checked by
the validator against the asset itself so the flag can't drift:

| Year | Questions awaiting original artwork |
|---|---|
| 2008 | 16, 41, 46 |
| 2009 | 5, 46 |
| 2010 | 12, 20, 45, 47, 50, 51 |
| 2012 | 41, 49, 50 |

**2011 has never been supplied** — the archive currently runs 2008, 2009, 2010, 2012.

### 2011 status

- 55 questions, Section A 1–40, Section B 41–55 — all 13 structure checks pass
- Wording preserved verbatim including original grammar (Q6 "the element which show",
  Q13 "important to carpenter")
- **A third RE layout:** alternatives at **Q37–40 and Q53–55**. Section A runs 36 plain
  questions before the RE block (2008/2009 run 36, 2010/2012 run 35)
- Zero overlap with any other year
- **Two visuals not supplied** — Q41 sketch map, Q50 Uganda sketch map, both
  `requires_original_visual: true`. Q41(a–c) and Q50(a–c) are unanswerable without them
- Answers not supplied; `verified: false`

⚠️ **Q37 Christian and Islamic wording are identical** ("Mention the religion that existed in
Uganda before the introduction of Islam and Christianity."). Plausible for this question, but
flagged by the validator — same pattern as 2010 Q36.

### RE layout by year — they genuinely differ

| Year | Alternative questions | Plain Section A questions |
|---|---|---|
| 2008 | 37–40, 53–54 | 1–36 |
| 2009 | 37–40, 53–54 | 1–36 |
| 2010 | 36–40, 51–55 | 1–35 |
| 2011 | 37–40, 53–55 | 1–36 |
| 2012 | 36–40, 51–55 | 1–35 |

The archive now holds **2008–2012, 275 questions, five complete papers**.
