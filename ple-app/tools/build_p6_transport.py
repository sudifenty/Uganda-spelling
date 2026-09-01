#!/usr/bin/env python3
"""
build_p6_transport.py — P.6 SST Topic 3: TRANSPORT AND COMMUNICATION IN EAST AFRICA.

Replaces the whole topic with the owner's own 111 Q&A cards (word for word,
order 1-111), following the same pipeline as Topics 1 and 2:

  1. writes notes/p6-sst-topic-03-transport-and-communication.md
     (About this topic + 23 sections; card answers are the section bodies)
  2. injects the owner-pinned card sets into index.html's KID_PINNED registry,
     keyed P6_SST_T03|<SECTION TITLE>, so every card renders exactly:
       definition -> cream box, black border 2.5px, rounded 16px
       list       -> white pills, one per line, black border 2.5px,
                     rounded 16px, padding 12px 16px, gap 10px, 18px bold

Run from ple-app/:  python3 tools/build_p6_transport.py
Then run the normal build:  python3 tools/build_all.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from batches_sst import p6_transport_cards as TC

TOPIC_ID = "P6_SST_T03"
MD_PATH = "notes/p6-sst-topic-03-transport-and-communication.md"
HTML_PATH = "index.html"


# ------------------------------------------------------------- markdown ---
def para_for(card):
    """Body paragraph(s) for a card inside the notes markdown.
    Definitions become a bold-led paragraph; lists become bullets."""
    n, q, typ, lines = card
    if typ == "definition":
        return f"{lines[0]}"
    return "\n".join(f"- {ln}" for ln in lines)


def build_markdown():
    L = []
    L.append("# PRIMARY 6 SOCIAL STUDIES")
    L.append("")
    L.append("**Theme: East Africa**")
    L.append("")
    L.append("# TOPIC 3: TRANSPORT AND COMMUNICATION IN EAST AFRICA")
    L.append("")
    L.append("*Curriculum reference: NCDC Primary Six Curriculum, Set One, Social Studies Topic 3,*")
    L.append("*25 periods (`curriculum/P6-SET-ONE-2010.pdf`, topic outline page 313 and pages 332–336).*")
    L.append("")
    L.append("**What you already know:** You know how people in your village send messages and move from")
    L.append("place to place. In P.6 you study **transport and communication in the whole of East")
    L.append("Africa** — the different types of transport, the means of communication, and the part")
    L.append("both play in trade, farming, tourism and development.")
    L.append("")
    L.append("**By the end of this topic you should be able to:**")
    L.append("")
    L.append("- define transport and communication")
    L.append("- name the main types of transport and give their advantages and disadvantages")
    L.append("- name important railway lines, ports, airports, lakes and water bodies")
    L.append("- describe traditional and modern means of communication")
    L.append("- describe the problems facing transport and communication and how they can be improved")
    L.append("- explain how transport and communication promote trade and development")
    L.append("")
    L.append("**A note on sources.** The teaching content of this topic — the definitions, lists and")
    L.append("examination questions — was supplied by the app's owner from the P.6 lesson material.")
    L.append("The key definitions, important facts, examination points and quick revision questions are")
    L.append("found together in the last sections of this topic, where every question carries its own")
    L.append("answer on the same card.")
    L.append("")
    L.append("---")

    for title, orders in TC.SECTIONS:
        L.append("")
        L.append(f"## {title}")
        L.append("")
        if title == "KEY DEFINITIONS":
            # Word | Meaning table built from the owner's key-definition cards
            L.append("| Word | Meaning |")
            L.append("|---|---|")
            for term, meaning in TC.DEFINITION_TABLE:
                L.append(f"| **{term}** | {meaning.rstrip('.')} |")
        elif title == "IMPORTANT FACTS TO REMEMBER":
            for f_ in TC.FACTS:
                L.append(f"- {f_}")
        elif title == "EXAMINATION POINTS AND REVISION QUESTIONS":
            for e in TC.EXAM_POINTS:
                L.append(f"- {e}")
        else:
            for o in orders:
                n, q, typ, lines = TC.card_by_order(o)
                if typ == "definition":
                    L.append(lines[0])
                else:
                    for ln in lines:
                        L.append(f"- {ln}")
                L.append("")
        L.append("")
        L.append("---")

    text = "\n".join(L).rstrip() + "\n"
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  wrote {MD_PATH} ({len(text.split())} words)")


# ------------------------------------------------------------- KID_PINNED ---
def js_str(s):
    """Escape a string for a single-quoted JS string literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


def pin_call(card):
    n, q, typ, lines = card
    if typ == "definition":
        return f"    kpD('{js_str(q)}','{js_str(lines[0])}'),"
    items = ", ".join("'" + js_str(x) + "'" for x in lines)
    return f"    kpL('{js_str(q)}',[{items}]),"


def build_pins_block():
    out = []
    out.append("  /* P.6 TRANSPORT AND COMMUNICATION IN EAST AFRICA — the owner's own 111 cards,")
    out.append("     word for word, order 1-111, split across the topic's sections in the owner's order. */")
    for title, orders in TC.SECTIONS:
        # pin key = section title with the leading "n. " stripped, uppercased
        key_title = title
        import re
        key_title = re.sub(r"^\d+\.\s*", "", title)
        out.append(f"  '{TOPIC_ID}|{key_title.upper()}':[")
        for o in orders:
            out.append(pin_call(TC.card_by_order(o)))
        out.append("  ],")
    return "\n".join(out)


BLOCK_START = "  /* P.6 TRANSPORT AND COMMUNICATION IN EAST AFRICA"


def inject_pins():
    html = open(HTML_PATH, encoding="utf-8").read()

    kstart = html.index("const KID_PINNED={")
    # KID_PINNED closes at the first "\n};" after its opening
    close = html.index("\n};", kstart)
    head, tail = html[:close], html[close:]

    # remove any previously injected T03 block (idempotent re-runs)
    if BLOCK_START in head:
        b = head.index(BLOCK_START)
        head = head[:b].rstrip("\n")

    pins = build_pins_block()
    html = head + "\n" + pins + "\n" + tail

    open(HTML_PATH, "w", encoding="utf-8").write(html)
    print(f"  injected {len(TC.CARDS)} pinned cards into {HTML_PATH} KID_PINNED")


if __name__ == "__main__":
    if not os.path.exists(HTML_PATH):
        sys.exit("Run this from the ple-app folder.")
    build_markdown()
    inject_pins()
    print("  done — now run: python3 tools/build_all.py")
