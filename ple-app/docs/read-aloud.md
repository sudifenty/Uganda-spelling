# Read Aloud — the voice in the Notes section

## The honest position on "natural human voice"

The app is **one offline HTML file**. That sets a hard limit, and it is better said
plainly than discovered later.

| Option | Why it was not used |
|---|---|
| Ship recorded audio of the notes | 234,731 words ≈ **30 hours ≈ 1.8 GB**. The whole app is 4.9 MB. |
| Ship a neural voice model (Piper, Coqui) | 25–60 MB of model plus a WASM runtime — it would grow the single file more than tenfold. |
| Call an online voice service | Breaks the offline requirement, which is the point. |

**What is used: the device's own speech engine**, through the browser's
`speechSynthesis`. On a modern Android or iPhone that voice is genuinely natural — Google
and Apple ship neural voices — and once installed it runs **completely offline**. Nothing
is fetched and no text ever leaves the phone.

**What this means in practice:** the app cannot guarantee one particular voice, because it
does not own the voice. It does the next best thing — picks the best voice on the device
and tells the learner how to get a better one.

## Choosing the voice — a woman's voice by default

Voices are scored and the best is used automatically:

* **a woman's voice wins.** Matched against the female names Android, iOS, Windows and
  Chrome actually use — Samantha, Karen, Hazel, Zira, Aria, Asilia, *Google UK English
  Female*, the `en-gb-x-gba` style codes and others. Male voices are pushed down.
* **offline voices next** — a voice needing internet is a last resort
* **East and Southern African English** (en-KE, en-ZA, en-TZ, en-NG), then British English
  — closest to the English a Ugandan learner hears in class
* *natural, neural, enhanced, premium* score higher
* *compact, eSpeak, robot, novelty, Zarvox* are pushed to the bottom

Checked against seven realistic device line-ups:

| Device | Voice chosen |
|---|---|
| Android, Google TTS installed | `en-gb-x-gba` — lady, offline |
| Android, Google UK + US | Google UK English Female — lady |
| iPhone / iPad | Samantha — lady, offline |
| Windows laptop | Microsoft Hazel — lady, offline |
| Kenyan voice present | Asilia — lady, offline |
| Cheap Android, eSpeak only | eSpeak — the device has no female voice at all, so the settings sheet says so and explains how to add one |
| No English voice at all | player replaced by a one-line install instruction |

The learner can still override the choice. The dropdown marks each voice **lady**,
**offline** or **needs internet**.

## Controls — inline, not a block

There is **no player card**. The controls are plain icons sitting **inside the note's
header row**, to the right of the title, so they take up no vertical space at all.

| State | Icons shown |
|---|---|
| Idle | speaker · tap-a-word · settings |
| Playing | pause · `3/12` · back · repeat · forward · stop · tap-a-word · settings |
| No voice installed | settings only |

* 30 px round icons, transparent background, shrinking to 27 px on screens under 360 px
* only the speaker gets a soft tint, so the row stays quiet
* that tint turns **green** when the natural voice is in use, so the learner can see at a
  glance which engine is speaking
* the section progress bar that was already under the header is reused — the player adds
  no bar of its own

## Reading speed by class

The class sets the base speed, and the learner can multiply it.

| Class | Base speed | Why |
|---|---|---|
| P.4 | 0.82× | slower — a transition class, first year of English-only lessons |
| P.5 | 0.90× | learner-friendly |
| P.6 | 0.97× | normal classroom reading |
| P.7 | 1.03× | confident but clear |

On top of that the learner picks **0.75× · 1× · 1.25× · 1.5×**, and there is a volume
slider. Both are remembered on the device.

## Reading maths like a teacher

This is the real work. The notes are full of symbols that a speech engine reads as
gibberish, so the text is rewritten into spoken English first.

| Written | Spoken |
|---|---|
| `3/4 + 1/4 = 1` | three quarters plus one quarter equals one |
| `25 × 4 = 100` | twenty-five multiplied by four equals one hundred |
| `Area = length × width` | area equals length multiplied by width |
| `1 1/2 hours` | one and a half hours |
| `1,250` | one thousand two hundred and fifty |
| `3.5` · `0.25` | three point five · zero point two five |
| `25%` | twenty-five percent |
| `−3 + 5 = 2` | negative three plus five equals two |
| `96 cm²` | ninety-six square centimetres |
| `120 km/hr` | one hundred and twenty kilometres per hour |
| `500 ml` · `10 kg` · `5 cm` | five hundred millilitres · ten kilograms · five centimetres |
| `−4 °C` | negative four degrees Celsius |
| `7:45 a.m.` | seven forty-five a m |
| `6:00` | six o'clock |
| `3:2` | three to two |
| `A ∪ B` · `A ∩ B` | A union B · A intersection B |
| `1962` | **nineteen sixty-two**, not "one thousand nine hundred and sixty-two" |
| `1850s` | the eighteen fifties |
| `2024` · `2007` · `1905` | twenty twenty-four · two thousand and seven · nineteen oh five |

Years are detected as **four digits with no comma in the range 1400–2099**. The notes
always write thousands with a comma (`1,250`), so years and quantities never collide —
checked against all 597 comma-less four-digit numbers in the notes.

## Diagrams and worked columns

A fenced block is looked at before it is read:

* mostly letters → **read normally**
* mostly digits (a column addition) → *"A worked calculation is shown here. Follow the
  working with your eyes."*
* mostly lines and boxes (a compass rose, a Venn diagram) → *"A diagram is shown here.
  Look at it as you listen."*

Reading `| / \ + ---` aloud would be worse than useless.

## Following along

The section is split into sentences, each wrapped in a span. The sentence being spoken is
**highlighted in amber** and scrolled into view. Tables are read cell by cell, lists item
by item.

## Hear a word

The speaker button turns on word tapping. Tap any word and it is spoken on its own,
slightly slower. Useful for *equator, photosynthesis, oesophagus, Bunyoro-Kitara*.

## Everything still works offline

The voice stops automatically when the learner leaves the reading screen, so it never
follows them into another part of the app. Notes, exercises, highlighting, saved progress
and diagrams are unaffected whether or not a voice is installed.

## What was tested

* **28 speech cases** covering fractions, decimals, percentages, negatives, units, areas,
  speeds, times, ratios, sets, years and decades — **all pass**
* the normaliser was run over **every sentence of every note — 24,884 in all**: no
  crashes, no `undefined`, no leftover markdown
* all 597 four-digit comma-less numbers in the notes were checked before turning on year
  reading
* the voice picker was run against **seven device line-ups** — a woman's voice is chosen
  on every one that has one

**Not testable here:** how the voice actually *sounds*. That depends on the device. Try it
on the phone the learners will use, and if it sounds robotic, install a better voice under
*Settings → Text-to-speech* and pick it from the dropdown.
