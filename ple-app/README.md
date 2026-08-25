# Smart PLE — Let's Learn

A mobile-first practice app for Ugandan Upper Primary learners (P.4–P.7).
One self-contained HTML file: no build step to run it, no dependencies, no network calls.
It works offline from a phone's Downloads folder exactly as it does on a server.

---

## What's inside

| | Content |
|---|---|
| **Past-paper archive** | PLE Social Studies **2008–2012** — 5 papers, 275 questions, verbatim |
| **SST practice** | 358 original questions across P.4–P.7 *(target 800 — 45% done)* |
| **Maths practice** | **1,100** original questions, every answer machine-verified |
| **Science practice** | 100 original P.7 questions |
| **Practice questions** | **3,856** — SST · Maths · Science · **English** (new) · 1,919 of them built from the notes |
| **Written exercises** | **2,085 questions in 242 sets** across 121 topics — class → subject → topic → set → submit → marked · offline |
| **Read aloud** | Offline voice for every note — sentence highlighting, maths spoken in words, speed by class, tap a word |
| **Study notes** | **121 NCDC topics** — **P.7, P.6, P.5 complete** (SST, Maths, Science, English) · **P.4 Social Studies** · 234,731 words · offline |
| **Screens** | 26 — home, practice, notes reader, papers, archive reader, results, review, progress, profile |

---

## Folder layout

```
ple-app/                       ← SOURCE OF TRUTH. Edit here.
├── index.html                 the whole application (data embedded by tools/inject.py)
├── README.md                  this file
├── docs/
│   ├── design.md              colour system, typography, contrast audit
│   ├── editing.md             how to change the app
│   ├── past-papers.md         archive schema, sourcing, per-year status
│   ├── sst-practice.md        SST bank rules and progress to 800
│   ├── maths-practice.md      Maths bank and how answers are verified
│   └── notes.md               study-notes rules, structure and validators
├── curriculum/                official NCDC PDFs actually read + what is NOT held
├── notes/                     one markdown file per topic (source of the notes)
├── data/
│   ├── papers/                sst-2008.json … sst-2012.json   (the archive)
│   ├── practice/              sst-p4…p7.json, math-p4…p7.json (the banks)
│   └── notes/                 p7-sst.json                     (the study notes)
└── tools/
    ├── build_all.py           ★ rebuild + validate + embed, in one command
    ├── release.py             ★ generate the deploy folder
    ├── inject.py              embeds datasets into index.html
    ├── build_sst_2008..2012.py   past papers, from supplied transcripts
    ├── build_practice_bank.py    SST bank (+ tools/batches/*.py)
    ├── build_math_bank.py        Maths bank, 800 generated + verified
    ├── qhelpers.py            authoring helpers (M / T / F / P)
    ├── batches/batch2.py      hand-written SST questions
    ├── validate_papers.py     archive rules
    ├── validate_practice.py   SST class purity + 800 target
    └── validate_math.py       Maths purity + re-computes every answer

../PLE-3-ready/                ← GENERATED deploy folder. Never edit by hand.
```

---

## One command

```bash
cd ple-app
python3 tools/build_all.py
```

That runs the whole chain and stops at the first failure, so a broken dataset can never reach
a learner:

```
build papers -> build SST bank -> build Maths bank
   -> validate all three -> embed in index.html
   -> refresh ../PLE-3-ready/ -> package ../smart-ple.zip
```

**`smart-ple.zip` is the single file to download.** It always holds the current build:

```
smart-ple.zip
├── START-HERE.txt      which folder is which
├── PLE-3-ready/        the deploy folder — drag to GitHub
└── ple-app/            the full source — edit here
```

Individual steps if you need them: `tools/release.py` (deploy folder only),
`tools/package.py` (rezip without rebuilding), `tools/inject.py` (re-embed data).

To just look at the app, open `index.html` in any browser.

---

## Deploying

Vercel's **Root Directory** for this project is `PLE-3-ready`, so that folder keeps its name.
It contains only what a browser needs — `index.html`, `vercel.json`, `.nojekyll`, `README.md`.
Datasets and build tools stay here in the source folder; the app never fetches them.

Upload `PLE-3-ready/` to the repository root, commit, and Vercel redeploys in about 30 seconds.
Then hard-refresh with **Ctrl+Shift+R** — a normal refresh serves the cached old build.

---

## Ground rules the tooling enforces

- **Classes never mix.** Every practice question carries its class in the record *and* in its
  ID. Selectors re-check both, plus subject. Verified: 40,000 questions served, 0 leaks.
- **Maths is never wrong.** Each Maths question stores a `calc` expression that
  `validate_math.py` re-evaluates independently. 749 checked, 0 disagreements.
- **Past papers are archives.** Wording is preserved verbatim, including original grammar.
  Nothing is rewritten, and no question claims UNEB origin until a human verifies it.
- **No phantom visuals.** A question referring to "the map below" without a real image file
  is a build error.

## Known gaps

- SST practice is 358/800; the Easy bands in P.6 and P.7 need the most work.
- All five past papers are `verified: false` until cross-checked against the official UNEB
  booklet, and none has an answer key.
- 16 printed visuals across the archive were never supplied and are flagged in-app.
