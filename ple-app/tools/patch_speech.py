#!/usr/bin/env python3
"""
patch_speech.py — wire the offline Read Aloud voice into the Notes section.

Idempotent. Adds:
  * the .sp-* stylesheet
  * the module in tools/speech_ui.js (between markers, so it can be replaced)
  * a control bar inside SCREENS.noteRead
  * a post-render hook that prepares the sentences and stops the voice when
    the learner leaves the reading screen

Usage: python3 tools/patch_speech.py     (run from the ple-app folder)
"""
import re, sys, pathlib

APP = pathlib.Path("index.html")
UI = pathlib.Path("tools/speech_ui.js")
NV = pathlib.Path("tools/voice_natural.js")
START = "/* === READ ALOUD MODULE START — replaced by tools/patch_speech.py === */"
END = "/* === READ ALOUD MODULE END === */"

CSS = """
/* ---------- READ ALOUD (inline icons in the header) ---------- */
.sp-in{display:inline-flex;align-items:center;gap:1px;flex:none;margin-left:4px}
.sp-i{width:30px;height:30px;border-radius:999px;border:none;background:transparent;
  color:var(--muted);font-size:14px;line-height:1;display:grid;place-items:center;flex:none;padding:0}
.sp-i.go{background:var(--purple-50);color:var(--purple);font-size:15px}
.sp-i.go.nat{background:var(--green-50);color:var(--green)}
.sp-i.on{background:var(--purple);color:#fff}
.sp-i:active{transform:scale(.86)}
.sp-n{font-size:11px;font-weight:900;color:var(--muted);padding:0 3px;
  letter-spacing:.2px;flex:none;font-variant-numeric:tabular-nums}
@media (max-width:359px){.sp-i{width:27px;height:27px;font-size:13px}}
.sp-s{border-radius:5px;transition:background .15s}
.sp-on{background:var(--amber-100,#ffe9b8);box-shadow:0 0 0 3px var(--amber-100,#ffe9b8)}
.sp-pre{display:block}

.sp-vlist{max-height:210px;overflow-y:auto;border:1.5px solid var(--line);
  border-radius:var(--r-md);padding:4px}
.sp-v{display:flex;align-items:center;gap:7px;padding:7px 8px;border-radius:9px}
.sp-v.on{background:var(--purple-50)}
.sp-v+.sp-v{border-top:1px solid var(--line)}
.sp-vn{flex:1;font-size:13px;font-weight:800;color:var(--navy);line-height:1.3;min-width:0}
.sp-vt{display:block;font-size:10.5px;font-weight:700;color:var(--muted);
  text-transform:uppercase;letter-spacing:.3px;margin-top:2px}
.sp-try,.sp-use{border:1.5px solid var(--purple-100);background:#fff;border-radius:999px;
  padding:5px 11px;font-size:12px;font-weight:800;color:var(--navy);flex:none}
.sp-use{background:var(--purple);border-color:var(--purple);color:#fff}
.sp-using{font-size:11px;font-weight:900;color:var(--purple-ink);flex:none;
  text-transform:uppercase;letter-spacing:.3px}
.sp-help{margin-top:13px;border:1.5px solid var(--line);border-radius:var(--r-md);
  padding:10px 12px;background:var(--bg)}
.sp-help summary{font-size:13px;font-weight:800;color:var(--navy);cursor:pointer}
.sp-help p{font-size:12.5px;color:var(--muted);line-height:1.55;margin-top:9px;font-weight:600}
.sp-help b{color:var(--navy)}

.sp-nat{font-size:11px;color:var(--purple);font-weight:900;flex:none;margin-left:2px}
.nv-box{border:1.5px solid var(--purple-100);border-radius:var(--r-md);padding:12px 13px;
  background:var(--purple-50)}
.nv-box.on{border-color:var(--green);background:var(--green-50)}
.nv-h{display:flex;align-items:center;justify-content:space-between;gap:8px}
.nv-h b{font-size:14.5px;color:var(--navy)}
.nv-tag{font-size:10.5px;font-weight:900;text-transform:uppercase;letter-spacing:.3px;
  color:var(--muted)}
.nv-p{font-size:12.5px;color:var(--muted);line-height:1.55;margin:7px 0 11px;font-weight:600}
.nv-vs{display:flex;flex-direction:column;gap:6px;margin-bottom:11px}
.nv-v{text-align:left;border:1.5px solid var(--line);background:#fff;border-radius:10px;
  padding:8px 10px}
.nv-v.on{border-color:var(--purple);background:#fff;box-shadow:0 0 0 2px var(--purple-100)}
.nv-v b{display:block;font-size:13px;color:var(--navy)}
.nv-v span{display:block;font-size:11.5px;color:var(--muted);font-weight:600;margin-top:2px}
.nv-prog{height:8px;background:#fff;border-radius:999px;overflow:hidden;margin:4px 0 7px}
.nv-prog i{display:block;height:100%;background:var(--purple);transition:width .3s}
.nv-pct{font-size:12px;color:var(--muted);font-weight:700}
.nv-row{display:flex;gap:8px;align-items:center}
.nv-row .btn{flex:1}
.nv-del{border:1.5px solid var(--line);background:#fff;border-radius:999px;padding:9px 13px;
  font-size:12.5px;font-weight:800;color:var(--rose-ink);flex:none}
.nv-note{font-size:11.5px;color:var(--muted);font-weight:600;margin-top:7px;text-align:center}
"""

HOOK = """
/* keep the voice tied to the reading screen */
const _renderBase = render;
render = function(){
  _renderBase();
  if(state.screen === 'noteRead'){
    if(typeof spPrepare === 'function') spPrepare();
  }else if(typeof spStop === 'function' && (SP.on || SP.paused)){
    spStop();
  }
};
"""


def main():
    if not APP.exists():
        sys.exit("patch_speech: index.html not found")
    app = APP.read_text(encoding="utf-8")
    ui = NV.read_text(encoding="utf-8") + "\n" + UI.read_text(encoding="utf-8")
    changed = []

    # 1 — stylesheet
    if ".sp-in{" not in app:
        marker = "/* ---------- 11. SHEET ---------- */"
        if marker not in app:
            sys.exit("patch_speech: CSS marker not found")
        app = app.replace(marker, CSS.strip() + "\n\n" + marker, 1)
        changed.append("stylesheet")

    # 2 — the module, between markers
    block = START + "\n" + ui.rstrip() + "\n" + HOOK.rstrip() + "\n" + END
    if START in app and END in app:
        a, b = app.index(START), app.index(END) + len(END)
        if app[a:b] != block:
            app = app[:a] + block + app[b:]
            changed.append("read-aloud module (replaced)")
    else:
        marker = "\nrender();\n</script>"
        if marker not in app:
            sys.exit("patch_speech: render() marker not found")
        app = app.replace(marker, "\n" + block + "\n" + marker, 1)
        changed.append("read-aloud module")

    # 3 — the player sits inline in the note-reader header, not as a block
    inline = '    ${spBarHTML()}\n  </header>'
    if "spBarHTML()" not in app:
        anchor = ('    <div><h2 style="font-size:18px">${nEsc(t.title)}</h2>\n'
                  '      <div class="sub">Part ${i+1} of ${t.sections.length}</div></div>\n'
                  '  </header>')
        if anchor not in app:
            sys.exit("patch_speech: note header not found")
        app = app.replace(anchor,
            '    <div style="flex:1;min-width:0"><h2 style="font-size:18px">${nEsc(t.title)}</h2>\n'
            '      <div class="sub">Part ${i+1} of ${t.sections.length}</div></div>\n'
            + inline, 1)
        changed.append("inline player in noteRead")

    APP.write_text(app, encoding="utf-8")
    print("  patched index.html: " + (", ".join(changed) if changed
                                      else "already has Read Aloud"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
