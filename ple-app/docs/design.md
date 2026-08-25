# Smart PLE — Design Notes
### Upper Primary (P4–P7) PLE Practice App · UI/UX prototype v0.2

**File:** `index.html` — one self-contained file. No build step, no dependencies.

---

## 1. Colour system

Six pastel hues. Every hue ships as three values so colour is never guessed:

| Hue | Base | Tint (`-50`) | Ink (`-ink`) | Meaning |
|---|---|---|---|---|
| Sky Blue | `#6CC7F6` | `#E9F6FE` | `#136890` | **Practice** |
| Green | `#8DD58A` | `#EDF8EC` | `#2F6B3A` | **Progress · Correct** |
| Warm Yellow | `#FFD166` | `#FFF6E0` | `#8A6410` | **Past Papers** |
| Purple | `#A78BFA` | `#F1ECFE` | `#5B44B5` | **Topics** |
| Soft Orange | `#FFB088` | `#FFF1E9` | `#9C5227` | **Achievements** |
| Soft Coral | `#FF8AAE` | `#FFEFF4` | `#A83E60` | **Profile · Try again** |

Neutrals: navy text `#2D4159` (never pure black), secondary `#4A6076`, muted `#5E7285`,
backgrounds mist `#F2F6FA` / cream `#FFF6E6` / warm-white `#FFFCF6`, borders `#E4EDF5`.

**Rules enforced throughout**
- Page background is mist or cream — never pure white everywhere. White is reserved for cards.
- **Base** colours are for fills (buttons, bars, icons). **Tints** are for card backgrounds.
  **Inks** are the only colours allowed for text on a tint.
- Colour meaning is fixed. A green thing always means progress or correct; coral always means
  "try again" — never a random accent.
- Subject identity borrows from the same six hues (English = sky, Maths = purple,
  Science = green, Social Studies = coral) so no seventh colour is ever introduced.
- Gradients appear in exactly three places (Continue hero, Results hero, Profile hero) and are
  two adjacent pastels only.

### Contrast audit — all 21 text pairs pass WCAG AA (≥ 4.5:1)

```
navy / sky button        5.54     muted / mist            4.58
navy / green button      5.97     muted / white           4.97
navy / yellow button     7.24     sky-ink / sky-50        5.59
navy / coral button      4.72     green-ink / green-50    5.86
navy / mist background   9.61     yellow-ink / yellow-50  4.99
navy / cream card        9.73     coral-ink / coral-50    5.37
navy / white card       10.44     purple-ink / purple-50  6.18
navy / answer tint       9.48     orange-ink / orange-50  5.21
```

Achieved by putting **navy text on pastel buttons** rather than white text. White-on-pastel
measured 2–2.6:1 and was rejected; darkening the pastels to carry white text would have made
them the bright saturated colours the brief rules out. Navy-on-pastel keeps the palette soft
*and* legible.

---

## 2. Typography

Nunito (900/800/700 for headings and labels, 700 for body), loaded from Google Fonts with a
rounded-system fallback stack: `Poppins → Varela Round → ui-rounded → SF Pro Rounded →
Segoe UI Rounded → system-ui`. If the font never loads — offline, or in a sandboxed preview —
the app still renders in a rounded face, so nothing breaks.

Question text 21px/800 · answers 17.5px/700 · body 17px · nothing meaningful below 12px.
Numbers use `tabular-nums` so timers and scores don't jitter.

*To make the build 100% offline-pure, delete the two `<link>` tags in `<head>`.*

---

## 3. Illustrations

Five hand-drawn inline SVGs — zero network, ~1 KB each, scale to any size:

- **Owl study-buddy** (two moods: `happy`, `think`) — logo, home hero, feedback bar, confirm sheets, about
- **Trophy** — high score, exam confirmation
- **Star** — mid score
- **Light bulb** — low score ("let's learn this one")
- **Books** — papers section

Flat pastel shapes, simple geometry, friendly but not toddler-ish — the owl reads as a study
companion rather than a cartoon pet.

---

## 4. Depth & shape

Shadows are very light (`0 2px 6px rgba(45,65,89,.055)`) and always paired with a 1.5px border
— on pastel backgrounds a border defines the card edge far better than a shadow. Buttons use a
solid 4px bottom edge instead of a blurred glow, which gives a soft chunky press that suits
children and costs nothing to render. Radii: 14 / 20 / 26 / 32px.

---

## 5. Motion

Everything is 120–450ms on one shared easing curve. Buttons translate 3px down and drop their
bottom edge. Correct answers scale to 1.03; wrong answers sway 4px (never a harsh shake). The
owl nods once in the feedback bar. Confetti is 22 pastel pieces that fade out. Score counts up
over ~700ms. Progress bars and the donut grow from zero on entry. Nothing loops, nothing moves
in the background, nothing animates while a question is being read.
All of it collapses under `prefers-reduced-motion: reduce`.

---

## 6. Feedback tone

| Outcome | Colour | Illustration | Words |
|---|---|---|---|
| Correct | soft green | owl, happy, nods | "Well done!" · "Correct!" · "Nice work!" |
| Incorrect | soft coral | owl, thinking | "Good effort!" · "Almost there!" · "Let's learn this one." |

No red. No "wrong", "failed" or "incorrect" anywhere in the interface. The correct option is
always highlighted in green so a miss becomes a demonstration rather than a verdict. Feedback
carries three signals — colour, icon and words — so it never depends on colour alone.

---

## 7. Screens (14)

Home · Practice modes · Subject select · Topic select · Question · Answer feedback · Results ·
Review answers · Past Papers · Paper detail · Exam confirm · Exam question · Progress · Profile
(+ avatar picker, offline manager, settings, about)

Flow: `Home → Practice → Subject → Topic → Question → Answer → Next`. Bottom tabs
(Home · Practice · Papers · Profile) are always one tap away. No hamburger menu anywhere.

## 8. Placeholders

No academic content. Swap the `SUBJECTS`, `MODES`, `PAPERS` and `topicsFor()` data blocks at
the top of the script — no layout changes required.
