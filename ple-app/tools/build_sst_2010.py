#!/usr/bin/env python3
"""
build_sst_2010.py — writes data/papers/sst-2010.json from the transcript supplied by the
project owner. Wording preserved verbatim: nothing rewritten, simplified,
modernised, summarised or paraphrased.

New structures introduced by the 2010 paper:
  intro         a lead-in line above a short question ("Study the diagram below…")
  asset_ref     a question that uses the diagram printed at another question (Q13 -> Q12)
  line_labels   answer blanks with printed letters instead of i/ii  (Q47 a: A ___ B ___)
  boxes         empty drawing boxes printed on the paper            (Q51 c)
  quote         a scripture passage with its citation               (Q55)
"""
import json, os

Y = 2010
SRC = lambda n: f"PLE SST {Y} — Q{n}"


def short(n, text, asset=None, intro=None, asset_ref=None):
    return {"year": Y, "number": n, "section": "A", "type": "short",
            "intro": intro, "question": text, "parts": None, "variants": None,
            "audience": "all", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": asset_ref, "parent": None}


def alt(n, christian, islamic, section="A"):
    return {"year": Y, "number": n, "section": section, "type": "alternative",
            "intro": None, "question": None, "parts": None,
            "variants": {"christian": {"question": christian, "parts": None, "quote": None},
                         "islamic":   {"question": islamic,   "parts": None, "quote": None}},
            "audience": "alternative", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": None, "asset_ref": None, "parent": None}


def structured(n, parts, intro=None, asset=None, audience="all"):
    return {"year": Y, "number": n, "section": "B", "type": "structured",
            "intro": intro, "question": None, "parts": parts, "variants": None,
            "audience": audience, "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": None, "parent": None}


def alt_structured(n, christian_parts, islamic_parts,
                   christian_quote=None, islamic_quote=None, asset=None):
    return {"year": Y, "number": n, "section": "B", "type": "alternative_structured",
            "intro": None, "question": None, "parts": None,
            "variants": {
                "christian": {"question": None, "parts": christian_parts, "quote": christian_quote},
                "islamic":   {"question": None, "parts": islamic_parts,   "quote": islamic_quote}},
            "audience": "alternative", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": None, "parent": None}


def p(label, text, sub=None, lines=0, line_labels=None, boxes=0):
    return {"label": label, "text": text, "parts": sub,
            "lines": lines, "line_labels": line_labels, "boxes": boxes}


def missing(kind, caption):
    return {"kind": kind, "file": None, "status": "missing", "caption": caption, "alt": ""}


# ── SECTION A · Questions 1–40 ──────────────────────────────────────────────
Q = [
    short(1,  "Name the largest fresh water lake found on the central plateau of Uganda."),
    short(2,  "Name the system of government that is practiced in Uganda today."),
    short(3,  "Mention any one national symbol found on the Ugandan currency."),
    short(4,  "Name any one place at school where physical education lessons are conducted."),
    short(5,  "Which element gives detailed information about a map?"),
    short(6,  "Give any one reason why a radio is important to the community."),
    short(7,  "How did the independence of Eritrea affect Ethiopia?"),
    short(8,  "What role did Dr. Kwame Nkrumah play towards promoting Pan-Africanism?"),
    short(9,  "Mention any one advantage of a nuclear family over an extended family."),
    short(10, "How do citizens of Uganda show their respect when singing the national anthem?"),
    short(11, "Mention the weather condition suitable for winnowing grains."),
    short(12, "What name is given to the above type of budget?",
          intro="Study the diagram below and answer the questions that follow.",
          asset=missing("diagram", "Budget diagram printed with Question 12")),
    short(13, "What is the advantage of having the type of budget shown in the diagram above?",
          asset_ref=12),
    short(14, "Give any one reason why a health centre should have an ambulance."),
    short(15, "State any one way in which a national constitution promotes people\u2019s rights."),
    short(16, "How does altitude influence the climate of an area?"),
    short(17, "Why was Africa called a dark continent by the Europeans?"),
    short(18, "Give any one way in which culture is important in a community."),
    short(19, "Mention any one reason why the Velds of South Africa are suitable for sheep rearing."),
    short(20, "Why was the bird below chosen as the Uganda National Emblem?",
          asset=missing("image", "Bird image printed with Question 20 (Uganda National Emblem)")),
    short(21, "State any one way in which games and sports are important in a community."),
    short(22, "What type of tax is paid on locally manufactured goods?"),
    short(23, "How is a national identity card useful to a citizen of Uganda?"),
    short(24, "How does afforestation influence the climatic condition of a place?"),
    short(25, "Mention any one way through which poverty can be reduced in a community."),
    short(26, "What is a population structure?"),
    short(27, "Name the political party that led Kenya to independence."),
    short(28, "Apart from being used for transport, state any one other reason why the Sabiny keep donkeys."),
    short(29, "Why should busy roads have humps?"),
    short(30, "Mention any one place where a wind sock is found."),
    short(31, "What time is it at town X which is located 45° East if it is 6:00am at Greenwich?"),
    short(32, "How is Lake Victoria similar to Lake Kyoga in terms of formation?"),
    short(33, "State any one way in which forests improve people\u2019s health."),
    short(34, "What moral lesson do we learn from the legend of the spear and the bead?"),
    short(35, "Name any one common market in which Uganda is a member."),

    alt(36, "Who was the wife of Adam?",
            "Who was the wife of Adam?"),
    alt(37, "Name the fasting period for Christians.",
            "Name the fasting period for Muslims."),
    alt(38, "Why is the Bible called a Holy book?",
            "Why is the Qur\u2019an called a Holy book?"),
    alt(39, "Name the angel who brought the good news about the birth of Jesus Christ.",
            "Name the angel who brought the good news about the birth of Prophet Isa."),
    alt(40, "Name the servant of God who suffered from serious illness but remained faithful.",
            "Mention the prophet of Allah who suffered from serious illness but remained faithful."),

    # ── SECTION B · Questions 41–55 ─────────────────────────────────────────
    structured(41, parts=[
        p("a", "Name the body that is responsible for organising population census in Uganda."),
        p("b", "Mention any two reasons why the government conducts population census.", lines=2),
        p("c", "State any one challenge faced by the enumerators during census."),
    ]),
    structured(42, parts=[
        p("a", "Mention the system of administration that was used by the French in West Africa."),
        p("b", "Give any two ways in which the system in (a) above was implemented.", lines=2),
        p("c", "State any one negative effect of the above named system."),
    ]),
    structured(43, parts=[
        p("a", "Name any two minerals mined in South Africa.", lines=2),
        p("b", "State any two economic benefits of the mining industry to South Africa.", lines=2),
    ]),
    structured(44, parts=[
        p("a", "Name the kingdom that replaced the Chwezi dynasty of Bunyoro-Kitara."),
        p("b", "State any two economic contributions of the Chwezi to Uganda.", lines=2),
        p("c", "Give any one reason why the Chwezi empire collapsed."),
    ]),
    structured(45, intro="Study the sketch map of East Africa below and answer the questions that follow.",
               asset=missing("sketch map", "Sketch map of East Africa printed with Question 45"),
               parts=[
                   p("a", "Name the river marked L."),
                   p("b", "Where was the homeland of the ethnic group that entered East Africa using route Y?"),
                   p("c", "Mention the traditional cash crop grown on the Island marked Z."),
                   p("d", "How has the railway line marked X contributed to the economic development of Zambia?"),
               ]),
    structured(46, parts=[
        p("a", "State any two roles of the security organs in Uganda.", lines=2),
        p("b", "Give any two challenges faced by the security organs while performing their duties.", lines=2),
    ]),
    structured(47, intro="Study the sketch map below and answer the questions that follow.",
               asset=missing("sketch map", "Sketch map printed with Question 47"),
               parts=[
                   p("a", "Name the features marked by the following letters.", line_labels=["A", "B"]),
                   p("b", "Name any one other river in Africa that ends in the same way as river marked C above."),
                   p("c", "How is the part marked A economically important to Nigeria?"),
               ]),
    structured(48, parts=[
        p("a", "Mention any two materials the Early man used for making his tools.", lines=2),
        p("b", "How did the Early man use bolas to live a better life?"),
        p("c", "Give any one reason why the discovery of fire was important to the early man."),
    ]),
    structured(49, parts=[
        p("a", "What is a national election?"),
        p("b", "Mention any two bad practices done by people during the national elections.", lines=2),
        p("c", "In which one way is a voters\u2019 register important during elections?"),
    ]),
    structured(50, intro="Study the sketch map of Uganda below and answer the questions that follow.",
               asset=missing("sketch map", "Sketch map of Uganda printed with Question 50"),
               parts=[
                   p("a", "Name the National Game Park found at place marked P."),
                   p("b", "State any one reason why there are no crocodiles in the National Game Park marked S."),
                   p("c", "State any two economic benefits of National Game Parks in Uganda.", lines=2),
               ]),

    alt_structured(51,
        asset=missing("drawing boxes", "Drawing boxes printed with Question 51"),
        christian_parts=[
            p("a", "Name any one symbol in Christianity."),
            p("b", "State any one way symbols are important to Christians."),
            p("c", "Draw any two symbols of Christianity in the boxes below.", boxes=2),
        ],
        islamic_parts=[
            p("a", "Name one symbol in Islam."),
            p("b", "State any one way symbols are important to Muslims."),
            p("c", "Draw any two symbols of Islam in the boxes provided below.", boxes=2),
        ]),

    alt_structured(52,
        christian_parts=[
            p("a", "Apart from Christianity and Islam, mention any one other religion practiced in Uganda."),
            p("b", "State any three roles of a Christian religious leader to the government of Uganda.", lines=3),
        ],
        islamic_parts=[
            p("a", "Apart from Islam and Christianity, mention any one other religion practiced in Uganda."),
            p("b", "State any three roles of a Muslim religious leader to the government of Uganda.", lines=3),
        ]),

    alt_structured(53,
        christian_parts=[
            p("a", "Who was the mother of Jesus Christ?"),
            p("b", "State any two ways in which Jesus Christ showed friendship to people?", lines=2),
            p("c", "Mention any one way a Christian child can show friendship to others."),
        ],
        islamic_parts=[
            p("a", "Who was the mother of Prophet Muhammed (P.B.U.H)."),
            p("b", "State any two ways in which Prophet Muhammed (P.B.U.H) showed friendship to people.", lines=2),
            p("c", "Mention any one way a Muslim child can show friendship to others."),
        ]),

    alt_structured(54,
        christian_parts=[
            p("a", "Name the town where Jesus entered during Palm Sunday."),
            p("b", "Mention any two ways in which the Christians of the above named town welcomed Jesus Christ.", lines=2),
            p("c", "Why did Jesus Christ go to the above named town?"),
        ],
        islamic_parts=[
            p("a", "Name the town where Prophet Muhammed (P.B.U.H) migrated to from Mecca."),
            p("b", "Mention any two ways in which the people of the above named town reacted to His visit.", lines=2),
            p("c", "Why did Prophet Muhammed (P.B.U.H) migrate to the above named town?"),
        ]),

    alt_structured(55,
        christian_quote={
            "text": ("\u201cHe never changes. No one can oppose Him or stop Him from doing what He "
                     "wants to do\u2026\u2026. I tremble with fear before Him.\u201d"),
            "citation": "(Job: 23: 13-15)"},
        islamic_quote={
            "text": ("\u201cHe is the First (nothing is before Him) and the Last (nothing is after Him), "
                     "the Most High (nothing is above Him) and the most Near (nothing is nearer than Him). "
                     "And He is All-knower of everything\u2026..\u201d"),
            "citation": "(Surah Al-Hadid 57:3)"},
        christian_parts=[
            p("a", "Who is talked about in the quotation above?"),
            p("b", "Mention two things that one can do to appreciate the one talked about in the quotation above.", lines=2),
            p("c", "State any one service people get from the one named in (a) above."),
        ],
        islamic_parts=[
            p("a", "Who is talked about in the quotation above?"),
            p("b", "Mention two things that one can do to appreciate the one talked about in the quotation above.", lines=2),
            p("c", "State any one service people get from the one named in (a) above."),
        ]),
]

doc = {
    "subject": "sst",
    "subject_name": "Social Studies with Religious Education",
    "level": "PLE / Primary 7",
    "year": Y,
    "paper_title": "PLE Social Studies with Religious Education 2010",
    "total_questions": len(Q),
    "duration_minutes": 135,
    "format": "written",
    "sections": {"A": [1, 40], "B": [41, 55]},
    "re_instruction": ("For Questions 36 to 40 and 51 to 55, answer EITHER the Christian OR the "
                       "Islamic questions but not both. No marks will be awarded to a candidate "
                       "who attempts both alternatives in a particular number."),
    "source": {
        "verified": False,
        "origin": "Transcript supplied by the project owner",
        "obtained_from": "", "checked_by": "", "checked_date": "",
        "notes": ("Wording preserved verbatim. NOT cross-checked against the official UNEB "
                  "booklet, so 'verified' stays false and no question claims UNEB origin. "
                  "Answers were not supplied. Six printed visuals were not supplied: Q12 budget "
                  "diagram (also used by Q13), Q20 bird image, Q45 East Africa sketch map, Q47 "
                  "sketch map, Q50 Uganda sketch map, Q51 drawing boxes.")
    },
    "questions": Q,
}

os.makedirs("data/papers", exist_ok=True)
with open("data/papers/sst-2010.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
print(f"wrote data/papers/sst-2010.json — {len(Q)} questions")
