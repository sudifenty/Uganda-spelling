# Smart PLE — APP STRUCTURE & NAVIGATION FLOW
**P4–P7 Ugandan Curriculum Quiz App** · single offline HTML file · live at uganda-spelling.vercel.app
Written for a junior developer. Every screen, button and arrow below is real (checked in the code, commit `f8a3515`).

---

## 1. APP MAP OVERVIEW (all screens, in order of use)

**Entry**
1. `auth` – Sign in / Create account (Supabase email). The app opens here until signed in. Works offline with a cached account ("offline grace").
2. `home` – Welcome landing: logo, "Let's learn together!", two big doors: **START** and **PRACTICE**.

**Learn path (START door)**
3. `start` – Choose Subject (SST · SCI · ENG · MATH cards).
4. `notePath` – the Learning Path / lesson roadmap of a topic (steps unlock one by one).
5. `noteSub` – reading one sub-topic (reading machine: play recording / sentence-by-sentence).
6. `noteChallenge` – mini challenge after reading.
7. (`noteJourney` – guided "learning journey" mode, kept in code, not linked from buttons today.)

**Practice (PRACTICE door)**
8. `practice` – Practice Mode: "Practice WITH Answers" / "Practice NO Answers".
9. `pquestion` – Question screen (1 of 10), WITH-answers mode.
10. `results` – score, stars, confetti.
11. `review` – review every answer with explanations.

**Written exercises (NO-answers door + Exercises tab)**
12. `exercises` – topic list per subject. 13. `exTopic` – sets inside a topic. 14. `exDo` – typed answers, hidden until CHECK. 15. `exResult` – marking + retry mistakes. 16. `exMine` – my exercise history.

**Tab bar (always visible except fullscreen screens)**
`Home · Practice · Notes · Exercises · Papers · Profile`

**Notes tab** – `notes` (topic list) → `notePath` → `noteSub`.
**Papers tab** – `papers` → `paperDetail` → `exam` (fullscreen past-paper) → `results` → `review`; `archive`/`years` filters.
**Spelling** – `spelling` (pick level) → `spellModes` → `spellPractice` → `spellResults`; `spellMistakes` review list.
**Maths** – `mathHome` → `mathLearn` / `mathPlay` → `mathLesson`.
**Profile tab** – `profile` → `avatar`, `settings`, `offline`, `about`, `classPick` (change class P4–P7).
**Progress** – `pprogress` (My Progress climb), reached from `start`.
**Legacy (kept in code, no live buttons)** – `hub` (old menu home), `subjects/topics/question` (old practice picker).

---

## 2. NAVIGATION FLOW (Screen --[Button]--> Screen)

### Entry & home
- `auth` --[CREATE ACCOUNT / SIGN IN]--> `home`
- `home` --[Card: START]--> `start`
- `home` --[Card: PRACTICE]--> `practice`
- `home` --[Tab bar]--> `notes / practice / exercises / papers / profile`

### Learn path
- `start` --[Card: SST / SCI / ENG / MATH]--> `notePath` (first not-finished topic)
- `start` --[Button: back ◀]--> `home`
- `start` --[Pill: Primary N · change]--> `classPick`
- `start` --[Button: Spelling games]--> `spelling`
- `start` --[Button: My progress]--> `pprogress`
- `notePath` --[Button: READ NOTES ✨ / REVIEW  on an unlocked step]--> `noteSub`
- `notePath` --[Button: back ◀]--> `notes`
- `notePath` --[Button: 🎯 Go to Practice for this topic]--> `practice`
- `noteSub` --[Button: back ◀]--> `notePath` · sections advance inside the screen; 🔊 plays the recording
- `notes` --[Card: any topic]--> `notePath`

### Practice WITH answers
- `practice` --[Card: Practice WITH Answers]--> `pquestion` (10 questions, feedback + explanation each)
- `pquestion` --[Tap: option A–D / CHECK / match]--> feedback sheet appears (same screen)
- feedback --[Button: NEXT]--> `pquestion` (next) or `results` (after last)
- `pquestion` --[Button: ✕ quit]--> confirm sheet --[YES, GO HOME]--> `home`
- `results` --[Button: REVIEW ANSWERS]--> `review`
- `results` --[Button: PRACTICE AGAIN]--> `pquestion` (fresh shuffle)
- `results` --[Button: Back to Home]--> `home`
- `review` --[Button: back ◀]--> `results`

### Practice NO answers (written test)
- `practice` --[Card: Practice NO Answers]--> `exDo` (10 shuffled written questions of first topic)
- `exDo` --[Button: CHECK MY ANSWERS]--> `exResult`
- `exDo` --[Button: back ◀]--> `exTopic` (attempt thrown away on purpose)
- `exResult` --[Button: retry mistakes]--> `exDo` (only the wrong ones)
- `exercises` --[Row: topic]--> `exTopic` --[Button: a set / random]--> `exDo`

### Papers, spelling, profile
- `papers` --[Card: paper]--> `paperDetail` --[Button: START]--> `exam` --[submit]--> `results`
- `spelling` --[Card: Easy/Medium/Hard]--> `spellModes` --[Card: mode]--> `spellPractice` --[last word]--> `spellResults`
- `profile` --[rows]--> `avatar / settings / offline / about / classPick`

---

## 3. WIREFRAME DESCRIPTIONS (top → bottom)

**Global chrome:** background **#FFF8E7 cream** with tiny star/confetti dots; white cards **rounded 24px** with soft shadows; owl mascot (graduation cap) on banner top-right; two Ugandan kid stickers (girl with book, boy with globe+flag) cheering under the main card; green fixed bottom bar on question screens; 6-tab bar at the bottom on normal screens (hidden on fullscreen: question, exam, results, review, archive, pquestion, spellPractice, spellResults, mathPlay).

- **auth:** owl + logo, email + password fields, SIGN IN / CREATE ACCOUNT buttons, offline-grace note.
- **home:** centered book-logo + "Smart PLE" + tagline; "Let's learn together!"; yellow START card (owl + big label); blue PRACTICE card (book+clipboard icon); footer "Safe · Fun · Offline Ready" + 3 dots.
- **start:** back circle + "Choose Subject" title + subtitle + 🇺🇬 + class pill; 4 subject cards (colour bar + round icon + big code + sub-name + chevron); 2 small buttons (Spelling, My progress); footer with real question count.
- **practice:** back + "Practice Mode"; brand row (book logo, flag, class pill); subject chips with emojis; "Choose how you want to practice today"; green WITH card (tick disc), blue NO card (clipboard disc); yellow 💡 tip strip; footer; kids sticker.
- **pquestion:** flag banner (class · subject · difficulty · topic · subtopic) with owl top-right; progress card "Question N of T" + teal bar; question card: **28px bold blue centred question**, "Choose the correct answer below", 4 pastel pills (letter disc + subject emoji + 20px bold text); two kids under the card; green "Tap an answer to continue →" bar.
- **results:** trophy/star/bulb art by score, big % score, 4 stat chips, REVIEW / PRACTICE AGAIN / HOME buttons, confetti at ≥75%.
- **notePath:** teal LEARNING PATH banner (flag + class + subject + owl); cheer strip "X of N complete"; green rail with stars; step dots (✓ green / glowing yellow number / smiling padlock); cards (blue glowing current with READ NOTES ✨, white done with REVIEW ⭐, grey locked); kids; practice button.
- **exDo:** header topic + set + question x of y; progress bar; question card; typed answer box(es) (+ working area); CHECK MY ANSWERS at the end; answers hidden until then.
- **notes / exercises lists:** pagehead with logo; class + subject chips; mini stats; topic cards with progress bars.
- **spelling screens:** hero 🔤 card; level cards; big word / input / options; score screen.

---

## 4. STATE DIAGRAMS

```
Kid taps an option (WITH answers)
[pquestion] --tap--> lock options
   |-- correct --> green glow + owl "Correct!" + explanation + sound
   |-- wrong   --> coral shake + "Not quite." + explanation + sound
   --[NEXT]--> question+1  or  [results] when last

Kid taps an option (NO answers / exam)
[pquestion/exDo] --tap--> neutral "Answer saved", NO colour/sound/score
   --[NEXT]--> next  --end--> [results] shows everything with REVIEW

Quiz finishes --> [results]: >=75% trophy+confetti, 50-74 star, <50 bulb
Close app mid-quiz --> reload lands on auth/home; the run is NOT resumed
   (next run is a fresh shuffle); saved things survive: exercises after
   CHECK, notes sections seen, spelling mistakes, maths steps.
```

---

## 5. DATA FLOW

- **Questions live INSIDE the single HTML file** as constants (offline-first, no `/data/*.json`): `PRACTICE_BANK` (SST), `MATH_BANK`, `SCI_BANK`, `ENG_BANK`, `EXERCISE_BANK`, `NOTES_BANK`, `SPELLING_BANK`.
- **Safety guard:** every selected question is re-checked for class + subject + id-prefix before reaching a child. Nothing from another class can leak in.
- **Score:** `session.correct / session.total` → percent; tones at 75% / 50%.
- **Saved on device (localStorage):** `ple_exercises_v1` (exercise attempts & %), `smartple_seen` (note sections read), `smartple_spelling` (misspelled words), `smartple_math`, `smartple_cpa`, `smartple_last` (continue card), `app_muted`, audio prefs.
- **In memory per visit:** practice tallies (`state.progress`) — they power the "so far X of Y correct" strip for that visit.
- **Server:** Supabase holds the account; signed-in activity events (screen views, answers) are queued and flushed to Supabase.

---

## 6. UI RULES (MUST FOLLOW FOR ALL SCREENS)

1. **Background:** #FFF8E7 with a 12%-opacity watermark pattern (Uganda map outline + kids-playing silhouettes + banana leaf + stars) plus tiny confetti dots. *(Shipped now: cream + confetti dots; watermark art is the next pass.)*
2. **Card:** white #FFFBF6, rounded 24px, soft shadow, max-width 380px centred. *(Shipped now: #FFFDF6 cards at 24px — retint to #FFFBF6 next pass.)*
3. **Owl mascot 48px** sitting on the top-right edge of every question card. *(Shipped now: owl 58–86px on banners; standardise to 48px card-edge next pass.)*
4. **Kids rule:** physical question (food, map, animal, tool) → 2 Ugandan kids ~200px tall HOLDING/POINTING at the object in the centre; abstract → kids peeking 56px from bottom corners only. *(Shipped now: kids duo sticker under the question card; per-question object art is the next pass.)*
5. **Options:** 4 pills, height 68px, beige #F5EBD8, rounded 20px; A–D light-blue circle; 36px icon next to the letter; text 20px bold #0A2F4F. Selected correct = #DFF5D8 + green glow. *(Shipped now: 70px pastel pills with letter discs + subject emoji + green glow on correct; align palette next pass.)*
6. **Fonts:** question 26px+ bold dark blue; options 20px bold. *(Shipped now: 28px blue question, 20px options.)*

---

## 7. EXAMPLE SCREEN (real one, described build-ready)

**Screen: pquestion — "Which one is a traditional Ugandan food?"**
- Header banner: 🇺🇬 flag tile + "P4 SST · Easy · Culture · Traditional food", owl perched top-right.
- Progress card: "Question 1 of 10" left, "1/10" right, teal bar 10% filled.
- Question card (white, 24px radius): question in 28px bold blue centred; sub "Choose the correct answer below".
- Options, top→bottom: **A** orange pill + 🍜 icon + "Pasta"; **B** pink pill + 🍕 + "Pizza"; **C** blue pill + 🍔 + "Burger"; **D** green pill + 🍃 basket icon + "Matooke" (correct → light-green #DFF5D8 + green glow + owl cheer + explanation "Matooke (steamed green bananas) is a traditional Ugandan food.").
- Kids: girl (arms up) + boy (thumbs up) stickers under the card.
- Footer bar: green "Tap an answer to continue →".
- Back state: ✕ opens "Stop practising?" sheet → YES, GO HOME → `home`.

*Build note:* colours/emojis above are today's shipped look; section 6 lists the target palette to align in the next decoration pass.
