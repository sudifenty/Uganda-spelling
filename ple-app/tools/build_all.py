#!/usr/bin/env python3
"""
build_all.py — regenerate every dataset, validate it, and embed it in the app.

    python3 tools/build_all.py

Stops at the first failure. Nothing is embedded unless validation passes,
so a broken dataset can never reach a learner.
"""
import subprocess, sys, os

STEPS = [
    ("Build past papers 2008-2012", [
        [sys.executable, "tools/build_sst_2008.py"],
        [sys.executable, "tools/build_sst_2009.py"],
        [sys.executable, "tools/build_sst_2010.py"],
        [sys.executable, "tools/build_sst_2011.py"],
        [sys.executable, "tools/build_sst_2012.py"],
    ]),
    ("Build SST practice bank",   [[sys.executable, "tools/build_practice_bank.py"]]),
    ("Build Mathematics bank",    [[sys.executable, "tools/build_math_bank.py"]]),
    ("Build Science bank",        [[sys.executable, "tools/build_sci_bank.py"]]),
    ("Build study notes",         [[sys.executable, "tools/build_notes.py"]]),
    ("Validate past papers",      [[sys.executable, "tools/validate_papers.py"]]),
    ("Validate SST practice",     [[sys.executable, "tools/validate_practice.py",
                                    "--allow-partial"]]),
    ("Validate Mathematics",      [[sys.executable, "tools/validate_math.py"]]),
    ("Validate Science",          [[sys.executable, "tools/validate_sci.py"]]),
    ("Validate study notes",      [[sys.executable, "tools/validate_notes.py"]]),
    ("Wire the app sections",     [[sys.executable, "tools/patch_exercises.py"],
                                   [sys.executable, "tools/patch_speech.py"]]),
    ("Practice from notes",       [[sys.executable, "tools/build_notes_practice.py"]]),
    ("Validate notes practice",   [[sys.executable, "tools/validate_notes_practice.py"]]),
    ("Build written exercises",   [[sys.executable, "tools/build_exercises.py"]]),
    ("Validate written exercises",[[sys.executable, "tools/validate_exercises.py"]]),
    ("Audit notes completeness",  [[sys.executable, "tools/audit_notes_completeness.py"]]),
    ("Embed everything in index.html", [[sys.executable, "tools/inject.py"]]),
]


def main():
    if not os.path.exists("index.html"):
        sys.exit("Run this from the ple-app folder.")
    for title, cmds in STEPS:
        print(f"\n=== {title} " + "=" * max(0, 56 - len(title)))
        for cmd in cmds:
            r = subprocess.run(cmd, capture_output=True, text=True)
            out = (r.stdout or "").rstrip()
            if out:
                print("\n".join("  " + l for l in out.splitlines()[-14:]))
            if r.returncode != 0:
                print((r.stderr or "").rstrip()[-1500:])
                sys.exit(f"\nFAILED at: {title} ({' '.join(cmd)})")
    import shutil
    for d in ("tools/__pycache__", "tools/batches/__pycache__"):
        if os.path.isdir(d):
            shutil.rmtree(d)

    # ONE file to download, always at the same place
    shutil.copy2("index.html", "../index.html")
    size = os.path.getsize("../index.html")

    # PWA: stamp the service worker with THIS build's version (content hash
    # of the app file), so every deployment is a new version automatically.
    import hashlib
    ver = hashlib.sha256(open("index.html", "rb").read()).hexdigest()[:12]
    sw = open("sw.js", encoding="utf-8").read()
    open("../sw.js", "w", encoding="utf-8").write(sw.replace("__SW_VERSION__", ver))
    shutil.copy2("manifest.webmanifest", "../manifest.webmanifest")
    shutil.copy2("icons/icon.png", "../icon.png")
    print(f"  PWA: service worker v{ver} + manifest + icon -> repo root")
    print("\n" + "=" * 62)
    print(f"BUILD OK — index.html ready ({size:,} bytes)")
    print("Download that one file. Nothing else is needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
