#!/usr/bin/env python3
"""
patch_exercises.py — wire the Written Exercises section into index.html.

Idempotent: running it twice changes nothing. It adds
  * const EXERCISE_BANK = {};      (inject.py fills this)
  * the Exercises tab and its screens in TAB_OF
  * the exercise fields on `state`
  * the .ex-* stylesheet
  * the module in tools/exercises_ui.js

Usage: python3 tools/patch_exercises.py     (run from the ple-app folder)
"""
import re, sys, pathlib

APP = pathlib.Path("index.html")
UI = pathlib.Path("tools/exercises_ui.js")

CSS = """
/* ---------- WRITTEN EXERCISES ---------- */
.ex-sum{display:flex;gap:9px;margin:14px 0 4px}
.ex-sum>div{flex:1;background:var(--sky-50);border:1.5px solid var(--sky-100);
  border-radius:var(--r-md);padding:11px 8px;text-align:center}
.ex-sum b{display:block;font-size:19px;color:var(--navy)}
.ex-sum span{font-size:11px;color:var(--muted);font-weight:700}
.ex-meta{display:block;font-size:11.5px;color:var(--muted);font-weight:700;margin-top:3px}
.ex-band{font-size:11px;font-weight:900;color:#fff;border-radius:999px;padding:3px 8px;margin-right:6px}
.ex-qcard{background:var(--sky-50);border:1.5px solid var(--sky-100);
  border-radius:var(--r-lg);padding:15px 15px 16px;margin-bottom:14px}
.ex-qno{font-size:11.5px;font-weight:900;color:var(--sky-ink);letter-spacing:.5px;
  text-transform:uppercase;margin-bottom:6px}
.ex-qtext{font-size:15.5px;line-height:1.55;color:var(--navy);font-weight:600}
.ex-lab{display:block;font-size:12px;font-weight:900;color:var(--muted);
  text-transform:uppercase;letter-spacing:.5px;margin:12px 0 6px}
.ex-area{width:100%;border:1.5px solid var(--line);border-radius:var(--r-md);
  padding:12px 13px;font:inherit;font-size:15px;color:var(--navy);background:#fff;
  min-height:74px;resize:vertical;line-height:1.6}
.ex-area:focus{outline:none;border-color:var(--sky);box-shadow:0 0 0 3px var(--sky-100)}
.ex-area.ex-big{min-height:132px}
.ex-area.ex-work{min-height:118px;font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:14px}
.ex-grid{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 4px}
.ex-dot{width:32px;height:32px;border-radius:9px;border:1.5px solid var(--line);
  background:#fff;font-size:12.5px;font-weight:800;color:var(--muted)}
.ex-dot.fill{background:var(--sky-50);border-color:var(--sky-100);color:var(--navy)}
.ex-dot.on{background:var(--sky);border-color:var(--sky);color:#fff}
.ex-tally{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:12px}
.ex-tally span{font-size:12px;font-weight:800;border-radius:999px;padding:4px 10px}
.t-right{background:var(--green-50);color:var(--green-ink)}
.t-part{background:var(--amber-50);color:var(--amber-ink)}
.t-wrong{background:var(--rose-50);color:var(--rose-ink)}
.t-self{background:var(--sky-50);color:var(--sky-ink)}
.ex-res{border:1.5px solid var(--line);border-left-width:5px;border-radius:var(--r-md);
  padding:13px 14px;margin-bottom:11px;background:#fff}
.ex-res.ok{border-left-color:var(--green)}
.ex-res.pt{border-left-color:var(--amber)}
.ex-res.no{border-left-color:var(--rose)}
.ex-res.sf{border-left-color:var(--sky)}
.ex-res-h{display:flex;justify-content:space-between;align-items:center;
  font-size:12.5px;color:var(--muted);font-weight:800;margin-bottom:7px}
.ex-lab2{font-size:11px;font-weight:900;color:var(--muted);text-transform:uppercase;
  letter-spacing:.5px;margin:11px 0 4px}
.ex-given{background:var(--bg);border-radius:9px;padding:9px 11px;font-size:14.5px;
  color:var(--navy);white-space:pre-wrap;line-height:1.55}
.ex-model{background:var(--green-50);border-radius:9px;padding:9px 11px;font-size:14.5px;
  color:var(--navy);line-height:1.6}
.ex-spell{background:var(--amber-50);border-radius:9px;padding:8px 11px;margin-top:8px;
  font-size:13px;color:var(--amber-ink);line-height:1.5}
.ex-self{display:flex;gap:7px;margin-top:11px;flex-wrap:wrap}
.ex-sb{flex:1;min-width:96px;border:1.5px solid var(--line);background:#fff;
  border-radius:10px;padding:9px 6px;font-size:12.5px;font-weight:800;color:var(--muted)}
.ex-sb.r.on{background:var(--green);border-color:var(--green);color:#fff}
.ex-sb.p.on{background:var(--amber);border-color:var(--amber);color:#fff}
.ex-sb.w.on{background:var(--rose);border-color:var(--rose);color:#fff}
"""


def main():
    if not APP.exists():
        sys.exit("patch_exercises: index.html not found")
    app = APP.read_text(encoding="utf-8")
    ui = UI.read_text(encoding="utf-8")
    changed = []

    # 1 — the bank placeholder, right after NOTES_BANK
    if "const EXERCISE_BANK" not in app:
        m = re.search(r"^const NOTES_BANK = .*?;\n", app, re.S | re.M)
        if not m:
            sys.exit("patch_exercises: NOTES_BANK not found")
        app = app[:m.end()] + "const EXERCISE_BANK = {};\n" + app[m.end():]
        changed.append("EXERCISE_BANK placeholder")

    # 2 — tab
    if "{id:'exercises'" not in app:
        app = app.replace("  {id:'notes',label:'Notes',icon:'book'},\n",
                          "  {id:'notes',label:'Notes',icon:'book'},\n"
                          "  {id:'exercises',label:'Exercises',icon:'target'},\n", 1)
        changed.append("Exercises tab")

    # 3 — TAB_OF entries
    if "exercises:'exercises'" not in app:
        app = app.replace("  notes:'notes',noteTopic:'notes',noteRead:'notes',\n",
                          "  notes:'notes',noteTopic:'notes',noteRead:'notes',\n"
                          "  exercises:'exercises',exTopic:'exercises',exDo:'exercises',"
                          "exResult:'exercises',exMine:'exercises',\n", 1)
        changed.append("TAB_OF routes")

    # 4 — state fields
    if "exsubject" not in app:
        app = app.replace("  nsubject:'SST', ntopic:null, nsec:0, noteSeen:{},\n",
                          "  nsubject:'SST', ntopic:null, nsec:0, noteSeen:{},\n"
                          "  exsubject:'MATH', exTid:null, exRun:null,\n", 1)
        changed.append("state fields")

    # 5 — CSS
    if ".ex-qcard" not in app:
        marker = "/* ---------- 11. SHEET ---------- */"
        if marker not in app:
            sys.exit("patch_exercises: CSS marker not found")
        app = app.replace(marker, CSS.strip() + "\n\n" + marker, 1)
        changed.append("stylesheet")

    # 6 — the module itself, between its markers, just before render();
    START = "/* === EXERCISES MODULE START — replaced by tools/patch_exercises.py === */"
    END = "/* === EXERCISES MODULE END === */"
    block = START + "\n" + ui.rstrip() + "\n" + END
    if START in app and END in app:
        a, b = app.index(START), app.index(END) + len(END)
        if app[a:b] != block:
            app = app[:a] + block + app[b:]
            changed.append("exercises module (replaced)")
    else:
        marker = "\nrender();\n</script>"
        if marker not in app:
            sys.exit("patch_exercises: render() marker not found")
        app = app.replace(marker, "\n" + block + "\n" + marker, 1)
        changed.append("exercises module")

    APP.write_text(app, encoding="utf-8")
    if changed:
        print("  patched index.html: " + ", ".join(changed))
    else:
        print("  index.html already has the Written Exercises section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
