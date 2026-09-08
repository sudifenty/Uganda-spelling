# PROJECT HANDOFF — Smart PLE (Uganda-spelling)

**Purpose:** so that any agent picking this up knows (1) where the project started,
(2) where it stands now, and (3) exactly how and where to resume work.
Companion doc: `APP_DOCUMENTATION.md` (what the app does; this file is how the *project* works).
Status at writing: `main` = `3d1e868` · 2026-09-08 · live at `uganda-spelling.vercel.app`.

---

## 1. Quick facts

| What | Value |
|---|---|
| GitHub repo | `https://github.com/sudifenty/Uganda-spelling` (public; branch `main`) |
| Deploy | Vercel auto-deploy from `main` → `uganda-spelling.vercel.app` |
| CI | GitHub Actions “build-check” on every push; poll via `actions/runs?head_sha=<sha>` |
| App source | `ple-app/index.html` (+ `ple-app/data/`, `ple-app/tools/`) |
| Build outputs (committed) | root `index.html`, `sw.js` — **never hand-edit**; produced by `python3 tools/build_all.py` run **from `ple-app/`** |
| Workspace extras | `/home/user/tests` (node --test suite, 10 tests), `/home/user/qa/` (headless-browser regression scripts), `APP_DOCUMENTATION.md`, this file |

## 2. Where we started

The baseline app already had: curriculum study notes (P4–P7, SST/MATH/SCI/ENG) rendered as
kid-friendly cards, a practice-question bank, written exercise sets, SST past papers
2008–2012, a spelling trainer, maths module, profile/class picking, offline single-file
architecture with service worker, and Supabase login.

The owner then asked, in order, for: exams inside the study path; exams as **objective
tap-the-answer MCQs only**; **every** topic to field both a mid and an end exam; the mid
exam placed **after the middle of the taught sub-topics** (reference cards must not shift
it — e.g. P6 SST Topic 1: after “6. Why was the EAC revived?”); sub-topic exercises to be a
**mix** of objective MCQs and open-ended questions; exercises to test **only what has been
read so far**; a wording replacement in P6 EAC; “Practice NO Answers” to go **straight to
the questions** (no notes gate).

## 3. What was built (commit chain on `main`, oldest → newest)

| SHA | Milestone |
|---|---|
| `19e4a5a`→`b1d478d` | study-path engine, kid cards, exercise rendering foundations |
| `99731c3` | milestone exams first cut |
| `4ede2cd` | both exams pure tap-MCQ (A–D pills, one CHECK & SUBMIT, pass ≥50%, RETRY/REVIEW) |
| `925ac37` | every topic fields both exams (notes Q&A → MCQ fallback, `spNoteMCQs`) |
| `4854144` | mid placed after middle of TAUGHT subs (`spTeachCount`/`spRefTitle`); bank theme-name matching (`spThemeHit`); subtopic→section mapping (`spSecFor`); fill→MCQ; bold-fact cloze fallback (`spFacts`/`spFactMCQs`) |
| `6409397` | mid card **always visible** at the midpoint, locked (“complete sub-topics 1–N first”) until reached |
| `0e55687` | sub-topic exercises **mixed**: objective (bank MCQs, exercise conversions, fact clozes) + open-ended |
| `380ff2f` | true/false MCQs from the topic’s own facts → every section mixed |
| `9e2a1d6` | **taught-so-far rule**: cumulative section text for relevance + numeric anchors (a year is only asked once taught); TF never reaches into unread sections |
| `7177519` | P6 EAC sub-topic 4 pinned card renamed to “Why was the East African Community formed?” (owner wording; `KID_PINNED` in `ple-app/index.html`) |
| `3d1e868` | **Practice NO Answers** skips the notes gate (`exStart(...,noGate)` in `tools/exercises_ui.js`; `pmNoAnswers` picks the richest topic) |
| *(this push)* | **Freemium**: 1 free sub-topic (first SST topic, sub 0); 30,000 UGX Airtel paywall (0753 825453, Sudifenty); `smartple_profiles`/`smartple_payments_pending` sync; `#admin` PIN 1234 approve flow |

## 4. Where we are now (current behaviour spec)

- **Mid-Topic Test 🎯**: at `ceil(taught/2)` of the taught sub-topics; visible-but-locked from
  the start; passing (≥50%) unlocks the second half. **End-of-Topic Exam 🏆** after the last
  sub-topic; passing unlocks the next topic. Both: 10 tap-MCQs, fullscreen, EXAM MODE badge;
  records in `smartple_midtests_v1` / `smartple_topicExams_v1`.
- **Question pools (layered, nothing invented):** practice-bank MCQs matched by normalised
  theme words; subtopic-label→section mapping; auto exercises→MCQ; notes Q&A pairs;
  bold-fact clozes; true/false from the topic’s facts. Distractors are always other *true*
  answers from the same topic.
- **Exercises mix:** every taught section’s exercise = up to 2 objective + 2–3 open-ended.
- **Taught-so-far:** relevance judged on cumulative notes text; 4-digit numbers in a question
  must already appear in notes read; verified: no untaught-year question anywhere.
- **Practice NO Answers:** straight into a 10-question drill (no gate). Learning flows
  (WITH Answers, named sets, Random Practice in Exercises) keep the notes gate (`pbUnlocked`).
- **Last full audit:** 122 topics, 0 missing mid, 0 missing end; 810 exercise sections,
  4 open-ended-only — all four *correctly* so (intro “About this topic” sections where
  nothing is taught yet: `P6_SST_T01#0`, `P6_SST_T03#0`; plus thin `P5_ENG_T05#1`, `P5_SST_T08#0`).

## 5. Build & ship (the exact routine)

```bash
cd /home/user/Uganda-spelling/ple-app && python3 tools/build_all.py   # expect "AUDIT CLEAN" + "BUILD OK"
# syntax: extract biggest <script> from ../index.html, node --check it
cd /home/user/tests && node --test                                    # 10/10
cd /home/user/qa && node spx7.js && node audit1.js                    # browser regressions (see §7)
```

**Push chain (one atomic command; token inline only, never persisted):**
```bash
git config user.name 'SmartPLE Bot'; git config user.email 'bot@smartple.local'
cp ple-app/index.html /home/user/.backups/src-$(date +%s).html        # /home/user persists; /tmp DOES NOT
git fetch "https://x-access-token:$PAT@github.com/sudifenty/Uganda-spelling.git" main
git update-ref refs/remotes/origin/main FETCH_HEAD && git reset --hard refs/remotes/origin/main
cp <backup> ple-app/index.html   # + any tools/*.js you edited
cd ple-app && python3 tools/build_all.py && cd ..
git add index.html sw.js ple-app && git commit -m "..."
git push "https://x-access-token:$PAT@github.com/sudifenty/Uganda-spelling.git" HEAD:main
# verify: git ls-remote (anon) · curl actions/runs?head_sha= · curl vercel.app | grep <marker>
```
The owner pastes a one-time PAT per push; **advise revoking after every push** and never
reuse a revoked/old one without the owner pasting it again.

## 6. Environment quirks (the things that bite)

1. **Local git rolls back between sessions**: local `HEAD` may show the ancient `1fab708`
   and `.git/config` (identity, remote) may be gone. Remote `main` is the truth — always
   fetch with the PAT before committing; commit+push in ONE chain (a lone commit gets lost).
2. **`/tmp` and `~/.cache` are wiped between sessions**: Playwright, its browsers, OS libs
   (`npx playwright install chromium` + `install-deps`), and any `/tmp` scripts/backups
   vanish. Keep backups and QA scripts under `/home/user` (`/home/user/qa/` already has them).
3. **The build re-injects modules**: `tools/patch_exercises.py` overwrites the exercises
   module in `index.html` from `tools/exercises_ui.js` (same for speech). Edits to `exStart`,
   `exRetry`, exercise screens etc. MUST be made in `tools/exercises_ui.js` or the next build
   silently reverts them. Engine code (`sp*`, `kid*`, `pm*`) lives directly in `ple-app/index.html`.
4. Viewer previews are sandboxed (no network) — test with headless Chromium against
   `file:///home/user/Uganda-spelling/index.html`.

## 7. QA toolkit (`/home/user/qa/`, needs `npm i playwright` + chromium in that folder)

- `spx7.js` — exam regressions: fresh-profile locked mid card at midpoint; pass mid (10 MCQs)
  unlocks sub 7; T03 mid+end with records; thin topic both exams; gated learning path still
  gates; no-gate drill runs.
- `audit1.js` — full audit: both exams per topic; objective+written mix per section.
- `chk5.js` — Practice NO Answers goes straight to `exDo` with 10 questions on a fresh profile.
- `pay1.js` / `pay2.js` — freemium rules: unpaid = first topic/sub 0 only, everything else paywalls; paid = normal sequential unlocks. Regression scripts set `sp_isPaid=1` first.
Plus `/home/user/tests` (`node --test`, 10 tests) and the build’s own `AUDIT CLEAN` gate.

## 8. Where the code lives (`ple-app/index.html` unless stated)

- sp engine ~2780–3000: `spStore/spGates/spTeachCount/spRefTitle/spPool/spNoteMCQs/spConvMCQs/
  spFacts/spFactMCQs/spThemeHit/spSecFor/spFillMCQs/spStart/spSubmit`
- kid cards & sub-topic exercise ~3400–3600: `kidExerciseFor`, `kexRelevant`, `kexNums`,
  `kexAnswer/kexShow/kexText`; `KID_PINNED` owner overrides ~4000–4600
- Practice Mode ~6080: `pmNoAnswers`, `SCREENS.practice`
- Exercises runtime: **`tools/exercises_ui.js`** (`exStart(noGate)`, `exRetry`, marking, screens)
- Unlock gate: `pbUnlocked` (~1800); notes data `ple-app/data/notes/*.json`; exercises
  `ple-app/data/exercises/*.json`; practice banks built by `tools/build_*_bank.py`.

## 9. Owner’s standing rules

1. Edit `ple-app/` only; root files are outputs. Never break the offline single-HTML app.
2. Exams are objective tap-MCQ only; open-ended stays in exercises, without forced answers.
3. Every topic fields both exams; never test content before it is taught.
4. Distractors = other true answers from the same topic; nothing invented.
5. PATs: inline-one-time, never persisted, never sent to the GitHub API, revoke after push.

## 10. Where to start from next

1. **Resume point = remote `main` (`3d1e868`)** + this file. Don’t trust local HEAD; fetch first.
2. Ask the owner for a **fresh PAT** before any push (the last one, `…LfCe`, was spent and
   should be revoked).
3. **Uncommitted in spirit, commit when asked:** `APP_DOCUMENTATION.md` and this handoff file
   (they live in the repo folder but were not pushed — no token was available).
4. **Known open/optional work** (only if the owner asks): the 4 open-ended-only sections
   (§4) could gain objective material if the owner adds bolded facts or bank questions for
   those early sections; content-wording changes follow the `KID_PINNED` pattern (§3, `7177519`).
5. For any new feature: read §6 first (especially the `tools/exercises_ui.js` injection trap),
   run the §5 routine, verify with §7, push with the §5 chain, and finish with anonymous
   `ls-remote` + CI poll + Vercel marker check.

---
*End of handoff. The workspace, the remote repo, and the live site are the sources of truth;
this document is the map between them.*
