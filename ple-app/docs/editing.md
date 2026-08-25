# How to Edit Smart PLE — Working Guide

Everything lives in **one file**: `index.html` (1,388 lines). There is no build step, no
`npm install`, no framework. You edit the file, save, refresh the browser. That's the whole loop.

---

## 0. Which folder is which  ⚠️ READ THIS FIRST

Your Vercel project has **Root Directory = `PLE-3-ready`**. That means Vercel only ever looks
inside that one folder. Everything else in the repo is ignored.

```
PLE-3/
├── .gitattributes
├── ple-app/                 ← IGNORED by Vercel (old leftover copy)
└── PLE-3-ready/             ← ★ THIS IS THE LIVE FOLDER — edit here
    ├── index.html           ← ★ the file that is actually deployed
    ├── DESIGN-NOTES.md
    ├── README.md
    ├── vercel.json
    └── ple-app/             ← IGNORED (nested leftover copy)
```

**Rule: edit `PLE-3-ready/index.html`. Nothing else deploys.**

| Location | Deploys? | Edit here? |
|---|---|---|
| `PLE-3-ready/index.html` | **Yes** | **Yes — this one** |
| `PLE-3-ready/ple-app/index.html` | No | No — delete it |
| `ple-app/index.html` (root level) | No | No — delete it |
| `~/ple-app/` (my workspace) | No | I edit this, then hand you the file |

### Do NOT flatten the repo unless you also change Vercel

Moving `index.html` to the repo root is tidier, but it only works if you do **both** steps:

1. Move the files up to the root
2. Vercel → Settings → Build and Deployment → **clear the Root Directory field** → Redeploy

Do step 1 without step 2 and the site 404s immediately. If you'd rather not touch Vercel again,
just leave it as is and always edit inside `PLE-3-ready/`. That works perfectly well.

### Your live site is out of date

The repo currently holds **v0.1** — the original blue design. The pastel restyle (v0.2) has
never been pushed. Before you start editing, replace these three files inside `PLE-3-ready/`
with the current versions from the workspace:

- `index.html` ← the pastel redesign
- `DESIGN-NOTES.md`
- `EDITING-GUIDE.md`

Otherwise you'll be editing the old design and wondering why your changes look different from
the preview.

---

## 1. The edit loop

```
open index.html in a text editor   (VS Code, Notepad++, even Notepad)
        ↓
change something, save (Ctrl+S)
        ↓
open index.html in Chrome, press Ctrl+R
        ↓
see the change
```

Keep the file open in both the editor and the browser side by side. No server needed.

**Before a big change, make a safety copy:**

```bash
cp index.html index-backup.html
```

Or work on a branch: `git checkout -b my-changes`

---

## 2. Where things are — jump straight to the line

Open the file and press **Ctrl+G** in VS Code to jump to a line number.

### Colours — line 26–35

```
26   --sky:#6CC7F6;    --sky-50:#E9F6FE;  --sky-100:#CDEBFC;  --sky-edge:#4FB2E4;  --sky-ink:#136890;
27   --green: ...
28   --yellow: ...
29   --coral: ...
30   --purple: ...
31   --orange: ...
34   --navy:#2D4159;   --navy-2:#4A6076;  --muted:#5E7285;
```

Each hue has five slots. If you change one, change them as a set:

| Slot | Used for | Rule |
|---|---|---|
| `--sky` | button fills, progress bars, icon fills | the pastel itself |
| `--sky-50` | card backgrounds | very pale version |
| `--sky-100` | borders on tinted cards | slightly stronger |
| `--sky-edge` | the 4px bottom edge of buttons | ~15% darker than base |
| `--sky-ink` | **text** on a `-50` background | dark enough to read |

⚠️ **Check contrast after changing a colour.** Navy text on your new pastel must reach 4.5:1.
Paste both hex codes into <https://webaim.org/resources/contrastchecker/>. If it fails,
lighten the pastel rather than darkening the text.

### App name — line 748

```html
<div class="brand-name">Smart PLE</div>
```

Also in `<title>` (line 7) and the About screen (~line 1140).

### Subjects — line 653

```js
const SUBJECTS = [
  {id:'eng',  name:'English',        icon:'book',  hue:'sky',    done:62, topics:8},
  {id:'math', name:'Mathematics',    icon:'calc',  hue:'purple', done:48, topics:9},
  {id:'sci',  name:'Science',        icon:'flask', hue:'green',  done:71, topics:7},
  {id:'sst',  name:'Social Studies', icon:'globe', hue:'coral',  done:35, topics:6},
];
```

To **add** a subject, copy a line and change it:

```js
  {id:'rel', name:'Religious Ed.', icon:'book', hue:'orange', done:0, topics:5},
```

- `id` — short, unique, lowercase, no spaces
- `icon` — must be a name from the `I = {...}` list at line 544
- `hue` — must be one of: `sky green yellow coral purple orange`
- `done` / `topics` — placeholder numbers

The grid, the progress screen and the offline list all read from this one array. Add it once,
it appears everywhere.

### Practice modes — line 659

```js
const MODES = [
  {id:'quick', title:'Quick Practice', sub:'10 questions · about 5 minutes', icon:'bolt', hue:'yellow'},
  ...
];
```

Same shape. Delete a line to remove a mode from the Practice screen.

### Papers — line 673

```js
const PAPERS = [
  {id:'p1', title:'Practice Paper 1', sub:'eng', q:50, mins:135, year:'Sample set A', score:82},
];
```

`sub` must match a subject `id`. `q` = question count, `mins` = time allowed, `score` = best
result or `null`.

If you add a paper, also add its id to the offline list at line 690:

```js
offline:{p1:true,p2:true,p3:false,p4:false,p5:false},
```

### Topic names — line 665

```js
const topicsFor = (sid) => { ... name:`Topic ${i+1} · Placeholder` ... }
```

This generates fake topics. When you have real ones, replace the whole function with a plain
lookup:

```js
const TOPICS = {
  eng:  [{id:'eng-t1', name:'Comprehension', pct:40, done:12, total:45, offline:true}],
  math: [{id:'math-t1', name:'Fractions',    pct:60, done:20, total:45, offline:true}],
};
const topicsFor = sid => TOPICS[sid] || [];
```

### Avatars — line 680

```js
const AVATARS = ['🦁','🐬','🦊','🐨','🦉','🐧','🐯','🦄','🌟','🚀','⚽','🎨'];
```

Any emoji works. Keep it to 12 so the grid stays 4×3.

### Question counts — line 1189

```js
const total = mode==='quick'?10:(mode==='mixed'?15:12);
```

Quick = 10, Mixed = 15, everything else = 12.

### Auto-advance timing — line 1209

```js
state.autoT=setTimeout(nextQuestion, ok?1400:2400);
```

1400ms after correct, 2400ms after a miss. Raise the second number if children need longer to
read the correction.

### Exam timer — line 1264

```js
time:10*60,
```

Currently 10 minutes for demo purposes. For a real 2h15m paper: `time:135*60` — or read it from
the paper with `time:p.mins*60`.

### Feedback wording — line 1219

```js
const good=['Well done!','Correct!','Nice work!','You got it!'];
const soft=['Good effort!','Almost there!',"Let's learn this one.",'Try again next time!'];
```

Add Luganda or Swahili phrases here if you want. **Note the quoting:** `"Let's learn this one."`
uses double quotes because the text contains an apostrophe.

### Icons — line 544

```js
const I = {
  home: p=>svg('<path d="M3 10.5 12 3l9 7.5"/>...',p),
```

To add one, grab a 24×24 outline path from <https://lucide.dev> and paste it in the same shape.

### Illustrations — line 583

```js
const ART = { owl:(w=96,mood='happy')=>`<svg viewBox="0 0 120 120" ...`, trophy:..., star:..., bulb:..., books:... }
```

Hand-drawn SVG on a 120×120 grid. Editing these needs some SVG comfort — tell me what you want
drawn and I'll do it instead.

### Screens — lines 744 to 1150

| Screen | Line |
|---|---|
| Home | 744 |
| Practice modes | 788 |
| Question | 847 |
| Papers | 875 |
| Results | 952 |
| Progress | 1010 |
| Profile | 1078 |

Each is a function returning HTML. `SCREENS.home = () => ` ... `` ` ``

---

## 3. Adding a whole new screen

Three steps.

**1. Write it** (put it near the other screens):

```js
SCREENS.help = () => `
  <header class="pagehead">
    <button class="back" onclick="back()" aria-label="Go back">${I.back(22)}</button>
    <div><h2>Help</h2><div class="sub">How to use the app</div></div>
  </header>
  <div class="card">
    <p>Your content here.</p>
  </div>
`;
```

**2. Tell the tab bar which tab stays lit** — add to `TAB_OF` (line 712):

```js
const TAB_OF = { ..., help:'profile' };
```

**3. Link to it** from somewhere, e.g. add a row in the Profile menu:

```html
<button class="menu-item" onclick="go('help')">
  ${iconBox('info','sky',20,44)}<b>Help</b><span class="chev">${I.chev(20)}</span>
</button>
```

`go('help')` navigates forward, `back()` returns.

---

## 4. Reusable pieces — copy these

```html
<!-- Card -->
<div class="card">content</div>
<div class="card warm">cream card</div>

<!-- Buttons -->
<button class="btn btn-primary btn-lg">BLUE</button>
<button class="btn btn-green">GREEN</button>
<button class="btn btn-yellow">YELLOW</button>
<button class="btn btn-coral">CORAL</button>
<button class="btn btn-ghost">WHITE OUTLINE</button>

<!-- Coloured icon chip -->
${iconBox('book','sky',26)}

<!-- Pills -->
<span class="pill off">Offline</span>
<span class="pill dl">Info</span>
<span class="pill warn">Try again</span>

<!-- Hint strip -->
<div class="hint-strip green">${I.check(20)} <span>Message</span></div>

<!-- Progress bar -->
<div class="bar"><i style="width:60%"></i></div>

<!-- Section heading -->
<div class="section-title">My heading</div>
```

---

## 5. Three things that will break the app

The screens are JavaScript **template literals** — text inside backticks. Three characters are
special:

| Character | Problem | Fix |
|---|---|---|
| `` ` `` backtick | ends the template early | write `` \` `` |
| `${` | starts a code expression | write `\${` |
| `'` apostrophe inside `onclick='...'` | closes the attribute | use `&#39;` or restructure |

**If the screen goes blank:** press **F12** in Chrome → **Console** tab. The red error names the
line. 95% of the time it's an unclosed `` ` `` or a missing `}`.

Recover with `git checkout index.html` (discards your edits) or your backup copy.

---

## 6. Saving your work

```bash
cd PLE-3
git status                                    # see what changed
git add PLE-3-ready/index.html                # note the folder!
git commit -m "change subject colours"
git push
```

Vercel redeploys automatically in ~30 seconds. Watch the Deployments tab — a green tick means
it's live; hard-refresh with **Ctrl+Shift+R** to bypass your browser cache.

**Write real commit messages.** Your history currently reads `Initial commit`, `error`, `iii` —
in two weeks that tells you nothing. `fix: exam timer reads paper duration` does.

---

## 7. Quick reference — most likely first edits

| Want to change | Line | Notes |
|---|---|---|
| App name | 748, 7 | plus About screen |
| A colour | 26–31 | change all 5 slots, check contrast |
| Add a subject | 653 | one line in the array |
| Add a paper | 673 | plus `offline` list at 687 |
| Real topic names | 665 | replace the generator |
| Learner name / class | 687 | `name:'Amina N.', klass:'P6'` |
| Encouragement phrases | 1219 | keep them positive |
| Exam length | 1264 | `time: p.mins*60` |
| Questions per practice | 1189 | |

---

**Not sure how to do something?** Describe the change in plain words — "make the Papers screen
show a filter by subject", "add a Luganda option" — and I'll make it and show you the diff.
