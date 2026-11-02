# Smart PLE — App Documentation

**Smart PLE** is an offline-first revision app for Ugandan primary learners (Primary 4–7),
built around the NCDC curriculum and the PLE (Primary Leaving Examination) format.
The entire app ships as **one HTML file** (`index.html`) plus a service worker (`sw.js`),
so a learner can download it once and use it with no internet.

- Live site: `uganda-spelling.vercel.app` (deployed from GitHub `sudifenty/Uganda-spelling`, `main` branch)
- Source of truth for the app code: `ple-app/` (the root `index.html` is a build output — never edit it by hand)
- Build command (run **from `ple-app/`**): `python3 tools/build_all.py`

---

## 1. Classes, subjects and content volumes

| Area | P4 | P5 | P6 | P7 |
|---|---|---|---|---|
| Notes topics — SST | – | 12 | 5 | 10 |
| Notes topics — MATH | 1 | 12 | 12 | 11 |
| Notes topics — SCI | – | 12 | 12 | 8 |
| Notes topics — ENG | – | 8 | 6 | 7 |
| Practice-bank questions | 255 | 227 | 182 | 630 |
| Written exercises — SST | 120 | 180 | 40 | 200 |
| Written exercises — MATH | 18 | 215 | 200 | 165 |
| Written exercises — SCI | – | 180 | 200 | 120 |
| Written exercises — ENG | – | 160 | 138 | 180 |

Subjects are `SST`, `MATH`, `SCI`, `ENG` (`SUBJ_META`). SST past papers 2008–2012 are embedded
(`QUESTION_BANK`, built by `tools/build_sst_2008.py … 2012.py`). A `MATH_BANK` and a
`SPELLING_BANK` back the Maths and Spelling modules.

## 2. Navigation

Bottom tab bar: **Home · Practice · Notes · Exercises · Papers · Profile**.
The app has ~50 screens (`SCREENS`), the main ones being:

| Screen | Purpose |
|---|---|
| `home` / `hub` | Dashboard, daily streaks, recent activity, companion owl |
| `practice` | Practice Mode chooser (WITH / NO answers) |
| `notes` → `noteTopic` → `notePath` → `noteSub` | Study notes: topic list → study path → sub-topic reader |
| `spExam` | Mid-Topic and End-of-Topic exams (fullscreen, EXAM MODE) |
| `exercises` → `exTopic` → `exDo` → `exResult` | Written exercise sets |
| `papers` → `years` → `archive` → `paperDetail` | PLE past papers 2008–2012 |
| `mathHome/mathLearn/mathPlay/mathLesson` | Maths learn & play |
| `spellDifficulty/spellModes/spellPractice/spellResults/spellMistakes` | Spelling trainer |
| `profile`, `classPick`, `avatar`, `settings`, `progress` | Account, class, avatar, sound/voice, records |

## 3. Notes & the Study Path

Each topic is a sequence of sub-topics (sections). Learners read them **in order**;
a sub-topic unlocks when the previous one is completed. The reader renders
kid-friendly cards generated from the notes:

- **flip cards** (question front / answer back),
- **group cards** (a named list, e.g. member countries),
- **defex cards** (definition + EXAMPLES tiles — the engine splits “X: a, b, c” sentences
  so examples render as big tiles),
- **pinned cards** (`KID_PINNED`) — owner-written overrides keyed by topic + section.

### End-of-sub-topic exercise (mixed)
Every taught sub-topic ends in an exercise that **mixes**:

- **Objective questions** — tap-the-answer pills (A–D), including true/false items.
  Sources, in priority order: the section’s own cards; theme-matched practice-bank MCQs;
  auto-marked written exercises re-cast as MCQs; the section’s bolded key facts as cloze MCQs;
  true/false statements built from the topic’s own facts.
- **Open-ended questions** — answered in the on-screen boxes (or the exercise book);
  a model answer can be revealed for self-checking.

**Taught-so-far rule:** an exercise only tests what has been read. Relevance is checked
against the *cumulative* notes text of sections 1→current, and any question carrying a
year/number (e.g. “in 1967”) is blocked until that number has actually appeared in the
notes read so far. Nothing is invented: every distractor is another true answer from the
same topic.

### Milestone exams
- **Mid-Topic Test 🎯** — placed immediately after the middle of the *taught* sub-topics
  (`half = ceil(taught/2)`). Trailing reference cards (KEY DEFINITIONS, IMPORTANT DATES,
  REVISION QUESTIONS, ANSWERS…, QUICK REVISION, notes-on-sources, MAP WORK) are **not**
  lessons and never shift the midpoint. The card is visible from the start, shown locked
  (“complete sub-topics 1–N first”) until reached. Passing (≥50%) unlocks the second half.
- **End-of-Topic Exam 🏆** — offered after the last sub-topic; passing unlocks the next topic.
- Both are 10 objective tap-MCQs, fullscreen with an EXAM MODE badge, one CHECK & SUBMIT,
  RETRY/REVIEW on fail. Records persist in `smartple_midtests_v1` / `smartple_topicExams_v1`.
- Every topic fields both exams: when a bank is thin, the engine falls back to
  notes Q&A pairs and bold-fact clozes so a test can always be built.

## 4. Practice Mode

- **Practice WITH Answers** — quick shuffled practice with explanations after each answer.
- **Practice NO Answers** — PLE-style drill: goes **straight to the questions** (no notes
  gate), 10 shuffled questions from the selected subject’s richest topic; answers stay
  hidden until checked.
- Inside the Exercises tab, the *learning* flows (named sets, Random Practice) keep the
  notes-unlock gate by design.

## 5. Written Exercises

Topics contain sets (e.g. “Basic Practice”, “More Practice”). Questions carry a `kind`:

| kind | marking |
|---|---|
| `auto` | exact/normalised match against accepted answers |
| `list` | fuzzy per-item marking (“name any four…”) |
| `self` | model answer shown for self-marking |
| `open` | learner’s own answer, no marking |

Multi-box answers: “Give any 3…” renders three numbered boxes; essay verbs
(explain/describe/why/how) get one big box. Runs are never resumed — leaving discards the
attempt and the next run is a fresh shuffle.

## 6. Past Papers, Maths, Spelling

- **Papers:** NCDC SST papers 2008–2012, sectioned, with marking; year → paper → question flow.
- **Maths:** learn lessons and timed play from `MATH_BANK` (P4–P7).
- **Spelling:** difficulty levels and modes, speech synthesis, mistake book
  (`smartple_spelling`) for targeted review.

## 7. Profile, progress & offline

- Sign-in (Supabase) is optional; class (P4–P7), avatar, sound/voice settings live in Profile.
- Progress records: `smartple_last` (recent activity), `smartple_daily` (streaks),
  `smartple_notes_learning`, `smartple_cpa`, `smartple_seen`, exercise DB (`EXDB`),
  plus UI prefs (`app_muted`, `ple_voice`, `ple_rate`, `ple_vol`, `ple_engine`, …).
- **Offline-first:** a service worker caches the single file; updates arrive on refresh
  (learners should hard-refresh after a new release).

## 7b. Freemium: free trial + manual MoMo paywall

- **Free rule (single decision point `spSubFree` / `isFreeAllowed`):** an unpaid account may
  open ONLY the first SST topic of its class (e.g. `P6_SST_T01`) and ONLY its first taught
  sub-topic (index 0). Everything else — sub 1+, mid/end exams, Topic 2+, other subjects,
  Practice modes, papers, exercises — shows the paywall.
- **Paid flag:** `smartple_profiles.is_paid` (Supabase) synced to `localStorage sp_isPaid`
  on login/online; offline trusts the cache. Owner unlocks by setting `is_paid=true`
  (dashboard or in-app `#admin`).
- **Paywall screen:** “Unlock All — 30,000 UGX One-Time”; Step 1 send 30,000 UGX to
  Airtel Money **0753 825453 (Name: Sudifenty)**; Step 2 form (your phone, payment phone,
  Airtel transaction ID) inserts into `smartple_payments_pending` and tags the profile;
  confirmation: “Received! We will verify and unlock in 10 mins. WhatsApp 0753825453 if delay.”
  Verification is manual (no Airtel API).
- **Admin:** `#admin` route, PIN 1234, lists pending payments with APPROVE
  (sets `is_paid=true`, `paid_at`, pending row → approved).

## 8. Architecture & build pipeline

`ple-app/index.html` is the app source; `tools/build_all.py` regenerates **all** datasets,
validates each (nothing embeds unless validation passes), audits notes completeness, and
embeds everything into `index.html`, then copies it to the repo root. Steps include:
past-paper builders → practice/Maths/Science bank builders → notes builder → validators →
`patch_exercises.py` / `patch_speech.py` (re-inject their modules from `tools/*.js` —
**edit those files, not the injected copy in index.html**) → `build_notes_practice.py` →
`build_exercises.py` → `audit_notes_completeness.py` → `inject.py`.

Key embedded banks: `NOTES_BANK`, `PRACTICE_BANK`, `EXERCISE_BANK`, `MATH_BANK`,
`QUESTION_BANK`, `SPELLING_BANK`, `ENG_BANK`, `SCI_BANK`.

### Engine rules (owner’s teaching policy, enforced in code)
1. No question from nowhere — bank MCQs must match the section’s taught text.
2. Exercises test only what has been read so far (cumulative text + numeric anchors).
3. Definitions vs examples are visually split; question words choose the answer style.
4. Reference/revision cards are study aids, not lessons (they never move the exam midpoint).
5. Distractors are always other *true* answers from the same topic — never invented.

## 9. Verification & release workflow

- `node --test` (suite in the workspace `tests/`) — engine regressions.
- Headless-browser audits verify: every topic fields both exams, every sub-topic exercise
  mixes objective + open-ended, no un-taught question leaks, exam unlock gating works.
- Release: commit `index.html` + `sw.js` + `ple-app/` together → push to `main` →
  CI build-check runs → Vercel auto-deploys. Pushes use a one-time personal access token
  supplied per release (rotated after every push).

---
*Generated from the live app build (commit `3d1e868`, 2026-09-08).*
