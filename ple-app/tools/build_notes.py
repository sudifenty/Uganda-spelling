#!/usr/bin/env python3
"""
build_notes.py — turn the curriculum-checked markdown notes in notes/ into
data/notes/<class>-<subject>.json so they can be embedded in the app.

Nothing here invents content. It only converts what is already written in the
markdown files into blocks the app can render offline:

    h1 h2 h3   headings
    p          paragraph
    ul ol      bullet / numbered list
    table      head row + body rows
    note       block quote

Each file must be named:  p<class digit>-<subject>-topic-<nn>-<slug>.md
e.g. p7-sst-topic-03-climate-of-africa.md

Usage: python3 tools/build_notes.py      (run from the ple-app folder)
"""
import json, os, re, glob, sys

SRC = "notes"
OUT = "data/notes"

SUBJECTS = {"sst": "Social Studies", "math": "Mathematics", "sci": "Science",
            "eng": "English"}
NAME_RE = re.compile(r"^p(\d)-([a-z]+)-topic-(\d{2})-([a-z0-9\-]+)\.md$")

# Phrases we must never publish as a source claim unless the document is held.
FAKE_SOURCE = re.compile(
    r"according to (the )?(uneb|ncdc teacher|teacher'?s guide|mk |longhorn|fountain)",
    re.I)


# ---------------------------------------------------------------- markdown ---
def split_table_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_divider(cells):
    return all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c)


def parse_markdown(text):
    """Return a flat list of blocks."""
    lines = text.split("\n")
    blocks, i, para = [], 0, []

    def flush():
        if para:
            blocks.append({"t": "p", "x": " ".join(para).strip()})
            para.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()

        if not s:                                   # blank line
            flush(); i += 1; continue

        if s.startswith("```"):                     # fenced block (working out)
            flush(); i += 1; buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i].rstrip()); i += 1
            i += 1
            blocks.append({"t": "pre", "x": "\n".join(buf)})
            continue

        if re.fullmatch(r"-{3,}", s):               # horizontal rule
            flush(); blocks.append({"t": "hr"}); i += 1; continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)       # heading
        if m:
            flush()
            blocks.append({"t": "h%d" % min(len(m.group(1)), 3), "x": m.group(2).strip()})
            i += 1; continue

        if s.startswith("> "):                      # block quote
            flush(); buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            blocks.append({"t": "note", "x": " ".join(buf).strip()}); continue

        if s.startswith("|") and i + 1 < len(lines) \
           and is_divider(split_table_row(lines[i + 1])):
            flush()
            head = split_table_row(lines[i]); i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i])); i += 1
            blocks.append({"t": "table", "head": head, "rows": rows}); continue

        if re.match(r"^[-*]\s+", s):                # bullet list
            flush(); items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()); i += 1
                # a wrapped continuation line
                while i < len(lines) and lines[i].startswith("  ") \
                        and lines[i].strip() and not re.match(r"^\s*[-*]\s+", lines[i]):
                    items[-1] += " " + lines[i].strip(); i += 1
            blocks.append({"t": "ul", "items": items}); continue

        if re.match(r"^\d+\.\s+", s):               # numbered list
            flush(); items, start = [], int(re.match(r"^(\d+)\.", s).group(1))
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()); i += 1
                while i < len(lines) and lines[i].startswith("   ") \
                        and lines[i].strip() and not re.match(r"^\s*\d+\.\s+", lines[i]):
                    items[-1] += " " + lines[i].strip(); i += 1
            blocks.append({"t": "ol", "items": items, "start": start}); continue

        para.append(s); i += 1

    flush()
    return blocks


SMALL = {"of", "the", "on", "in", "and", "to", "a", "an", "for", "at", "by",
         "from", "with", "into"}
ACRONYMS = {"UN", "OAU", "AU", "EAC", "SST", "PLE", "NCDC", "UNEB", "AIDS"}


def nice_title(t):
    words = t.split()
    out = []
    for i, w in enumerate(words):
        if w in ACRONYMS:
            out.append(w); continue
        lw = w.lower()
        if i and lw in SMALL:
            out.append(lw); continue
        out.append("-".join(p[:1].upper() + p[1:] for p in lw.split("-")))
    return " ".join(out)


def sectionise(blocks):
    """Group blocks into readable sections: a new section starts at h1 or h2."""
    sections, cur = [], None
    for b in blocks:
        if b["t"] in ("h1", "h2"):
            if cur:
                sections.append(cur)
            cur = {"title": b["x"], "blocks": []}
        else:
            if cur is None:
                cur = {"title": "Introduction", "blocks": []}
            cur["blocks"].append(b)
    if cur:
        sections.append(cur)
    clean = []
    for sec in sections:
        blks = [b for b in sec["blocks"] if b["t"] != "hr"]
        if not blks:
            continue
        title = sec["title"]
        if re.match(r"^PRIMARY \d+ ", title, re.I):      # banner line only
            continue
        if re.match(r"^TOPIC\s+\d+:", title, re.I):
            title = "About this topic"
        clean.append({"title": title, "blocks": blks})
    return clean


def words_of(blocks):
    n = 0
    for b in blocks:
        if b["t"] in ("p", "note", "pre") or b["t"].startswith("h"):
            n += len(b.get("x", "").split())
        elif b["t"] in ("ul", "ol"):
            n += sum(len(x.split()) for x in b["items"])
        elif b["t"] == "table":
            n += sum(len(c.split()) for c in b["head"])
            n += sum(len(c.split()) for r in b["rows"] for c in r)
    return n


# -------------------------------------------------------------------- main ---
def main():
    if not os.path.isdir(SRC):
        sys.exit("build_notes: notes/ folder not found — run from ple-app/")
    os.makedirs(OUT, exist_ok=True)

    banks, problems = {}, []

    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        fn = os.path.basename(path)
        m = NAME_RE.match(fn)
        if not m:
            problems.append(f"{fn}: file name does not follow "
                            "p<class>-<subject>-topic-<nn>-<slug>.md")
            continue
        cls, subj, tno, slug = "P" + m.group(1), m.group(2), int(m.group(3)), m.group(4)
        if subj not in SUBJECTS:
            problems.append(f"{fn}: unknown subject '{subj}'")
            continue

        text = open(path, encoding="utf-8").read()
        if FAKE_SOURCE.search(text):
            problems.append(f"{fn}: contains an unverifiable source claim")

        blocks = parse_markdown(text)

        # title = the TOPIC n: ... heading
        title, periods, pages = None, None, None
        for b in blocks:
            if b["t"].startswith("h") and b["x"].upper().startswith("TOPIC "):
                title = b["x"]
                break
        if not title:
            problems.append(f"{fn}: no 'TOPIC n: ...' heading found")
            continue
        head_text = "\n".join(b.get("x", "") for b in blocks[:8])
        pm = re.search(r"(\d+)\s+periods", head_text, re.I)
        if pm:
            periods = int(pm.group(1))
        gm = re.search(r"pages?\s+([\d\u2013\-–, ]+)\)", head_text)
        if gm:
            pages = gm.group(1).strip()

        secs = sectionise(blocks)
        rec = {
            "id": f"{cls}_{subj.upper()}_T{tno:02d}",
            "class": cls,
            "subject": subj.upper(),
            "topic_no": tno,
            "title": nice_title(re.sub(r"^TOPIC\s+\d+:\s*", "", title,
                                       flags=re.I).strip()),
            "heading": title,
            "slug": slug,
            "periods": periods,
            "curriculum_pages": pages,
            "words": words_of(blocks),
            "sections": secs,
        }
        banks.setdefault((cls, subj), []).append(rec)

    if problems:
        for p in problems:
            print("  PROBLEM:", p)
        sys.exit("build_notes: fix the problems above")

    total = 0
    for (cls, subj), topics in sorted(banks.items()):
        topics.sort(key=lambda t: t["topic_no"])
        nos = [t["topic_no"] for t in topics]
        if len(set(nos)) != len(nos):
            sys.exit(f"build_notes: duplicate topic numbers in {cls} {subj}")
        out = {
            "class": cls,
            "subject": subj.upper(),
            "subject_name": SUBJECTS[subj],
            "total": len(topics),
            "words": sum(t["words"] for t in topics),
            "topics": topics,
        }
        f = os.path.join(OUT, f"{cls.lower()}-{subj}.json")
        json.dump(out, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        total += len(topics)
        print(f"  {cls} {SUBJECTS[subj]:<15} {len(topics):>2} topics  "
              f"{out['words']:>6,} words  -> {f}")
    print(f"  {total} topic note sets built")


if __name__ == "__main__":
    main()
