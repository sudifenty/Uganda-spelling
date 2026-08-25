# Study Notes — how they are made

## What is in the app now

| Class | Subject | Topics | Words | Source read |
|---|---|---|---|---|
| P.7 | Social Studies | 10 of 10 | 26,856 | `curriculum/PRIMARY-SEVEN-SET-ONE.pdf` (NCDC © 2012) |
| P.7 | Mathematics | 11 of 11 | 17,087 | same document |
| P.7 | Integrated Science | 8 of 8 | 16,568 | same document |
| P.7 | **English** | **7 of 7** | **15,509** | same document |
| P.6 | Social Studies | 5 of 5 | 14,202 | `curriculum/P6-SET-ONE-2010.pdf` (NCDC © 2010) |
| P.6 | Mathematics | 12 of 12 | 18,338 | same document |
| P.6 | Integrated Science | 12 of 12 | 25,413 | same document |
| P.6 | **English** | **6 of 6** | **12,289** | same document |
| P.5 | Social Studies | 12 of 12 | 22,515 | `curriculum/P5-SET-ONE-2010.pdf` (NCDC © 2010) |
| P.5 | Integrated Science | 12 of 12 | 21,559 | same document |
| P.5 | **Mathematics** | **12 of 12** | **18,439** | same document |
| P.5 | English | 8 of 8 | 14,499 | same document |
| P.4 | **Social Studies** | **6 of 6** | **11,457** | `curriculum/P4-SOCIAL-STUDIES-2010.pdf` (NCDC © 2010) |
| | **Total** | **121 topics** | **234,731** | |

**P.7, P.6 and P.5 are complete.** For **P.4**, Social Studies is written; **Mathematics
(12), English (8) and Integrated Science (12) remain** — all three curriculum documents are
now held and verified (see `curriculum/p4-topics.md`), so those notes can be written. Until
they are, the app shows an honest empty screen for those three subjects rather than
guessing.

**P.4 Social Studies is written about "our district" in general.** Every topic of that
syllabus is about the learner's own district, and the syllabus names none, so the notes teach
the ideas and leave district facts to the learner. No facts about any particular district
have been invented.

## The rules these notes follow

1. The **NCDC curriculum is the highest authority**. Every topic, sub-topic and period
   count comes from the PDF, and each note states the pages it came from.
2. **No invented sources.** No note says "according to NCDC/the Teacher's Guide/MK". Where
   a document is not held, the note or the screen says: *"The exact curriculum/source
   document is not available to verify this section."*
3. **No note claims to be "complete notes"** — `validate_notes.py` fails the build if that
   phrase appears.
4. **Classes are never mixed.** A note carries its class and subject, `build_notes.py`
   files it by class + subject, `validate_notes.py` re-checks it, `inject.py` re-checks it
   again, and the app re-checks each record before showing it.
5. **Written for a P.7 learner** — primary-school English, not secondary-school notes.

6. **Every calculation is checked.** In Mathematics and Science, each worked example and
   each answer was computed and verified before it was written down.
7. **Sensitive sub-topics** (for example the "sex deviations" list in Science Topic 8) are
   handled as **child protection, health risk and the law** only — no explicit detail —
   and the note says plainly that no NCDC guidance document for teaching it was held.

## Structure of every topic (the same 12–17 parts)

- About this topic — what you already know, and what you should be able to do
- Numbered teaching sections that follow the syllabus sub-topics in order
- KEY DEFINITIONS · IMPORTANT FACTS TO REMEMBER · EXAMINATION POINTS
- MAP WORK (Social Studies) or COMMON MISTAKES TO AVOID (Mathematics)
- REVISION QUESTIONS (20, graded A–E) · ANSWERS TO REVISION QUESTIONS
- P.7 QUICK REVISION
- A note on sources

## Files

```
notes/p7-sst-topic-01 … topic-10       Social Studies (10 files)
notes/p7-math-topic-01 … topic-11      Mathematics (11 files)
notes/p7-sci-topic-01 … topic-08       Integrated Science (8 files)
tools/build_notes.py       markdown  -> data/notes/p7-sst.json, p7-math.json, p7-sci.json
tools/validate_notes.py    safety checks (see below)
tools/inject.py            data/notes/*.json -> const NOTES_BANK in index.html
```

File names must be `p<class>-<subject>-topic-<nn>-<slug>.md`, e.g.
`p6-sst-topic-01-people-of-east-africa.md`. Anything else fails the build.

## What `validate_notes.py` refuses to ship

- a topic filed under the wrong class or subject
- a duplicated topic number
- a topic with no curriculum page reference
- a topic under 600 words
- a missing KEY DEFINITIONS / IMPORTANT FACTS / EXAMINATION POINTS / REVISION QUESTIONS /
  ANSWERS / note-on-sources section
- fewer answers than revision questions
- the words "complete notes", "according to UNEB/the Teacher's Guide", or any UNEB claim

## Adding a new class or subject later

1. Download the NCDC syllabus for that class into `curriculum/` and read it.
2. Record the verified topic list in `curriculum/p<class>-topics.md`.
3. Write one markdown file per topic in `notes/`, following the structure above.
4. Run `python3 tools/build_all.py`. The notes appear in the app automatically under that
   class and subject; no code change is needed.

## In the app

Subjects with notes but **no practice bank yet** (English) show a plain note on the topic
page instead of the "Practise questions" button.

**Notes** is the third tab. Choose class → subject → topic → part. Progress ticks show the
parts already read. Everything works with no internet.
