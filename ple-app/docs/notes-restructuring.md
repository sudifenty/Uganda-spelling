# Notes Restructuring Standard — UNEB Revision Format

The owner's restructuring rules (27 Aug 2026) turn every topic into a direct
revision guide: **remove words, not knowledge.** This document is the working
standard. Status lives at the bottom.

## The format

- Sections are **numbered questions**: `## 1. What is a district?` …
  (numbering keeps the Math Lesson Player working).
- The answer follows immediately: the existing definition/facts, preserved.
- Tables, diagrams, syllabus notes: kept as they are (they are already perfect
  revision format).
- Tail sections kept: `COMMON MISTAKES TO AVOID`, `REVISION QUESTIONS`,
  `ANSWERS TO REVISION QUESTIONS` — verbatim.
- `About this topic` keeps the one-line curriculum reference (it feeds
  `curriculum_pages` and the provenance check) + learning objectives +
  the short "how to use" line.

## What is removed (and why it is safe)

| Removed | Why |
|---|---|
| `KEY DEFINITIONS` table | merged into the Q&A sections — every meaning must appear in a Q&A first (checked mechanically) |
| `IMPORTANT FACTS TO REMEMBER` | every bullet must already exist in a Q&A (verified per topic before dropping) |
| `EXAMINATION POINTS` | same — question-style prompts of knowledge already in the Q&As |
| `P.X QUICK REVISION` | a summary of what is already presented = duplication |
| `A note on sources` | provenance metadata, not learner knowledge; the originals remain in git history and `curriculum/SOURCES.md` |

## The validation that gates every batch

1. `validate_notes.py` is format-aware: restructured topics (≥3 numbered
   question sections) must have REVISION QUESTIONS + ANSWERS + curriculum
   pages; classic topics keep the full classic checks.
2. A mechanical preservation check compares old vs new: every old table cell
   and every old KEY-DEFINITIONS meaning must still exist in the new file
   (modulo bold markers/whitespace). Run it before committing each batch.
3. Any definition whose only home was the KEY DEFINITIONS table gets its own
   Q&A section, wording preserved.

## Status

| Batch | Topics | State |
|---|---|---|
| P4 SST 1–2 (pilot) | 2 | ✅ restructured (this commit) |
| P4 SST 3–6 | 4 | ⬜ next |
| P5–P7 all subjects | 115 | ⬜ pending, batch per subject |
