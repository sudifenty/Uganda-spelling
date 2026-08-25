#!/usr/bin/env python3
"""
build_sst_2011.py — writes data/papers/sst-2011.json from the transcript supplied by the
project owner. Wording preserved verbatim: nothing rewritten, simplified,
modernised, summarised or paraphrased.
"""
import json, os

Y = 2011
SRC = lambda n: f"PLE SST {Y} — Q{n}"


def short(n, text, asset=None, intro=None, asset_ref=None):
    return {"year": Y, "number": n, "section": "A", "type": "short",
            "intro": intro, "question": text, "parts": None, "variants": None,
            "audience": "all", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": asset_ref,
            "requires_original_visual": bool(asset and asset.get("status") == "missing"),
            "parent": None}


def alt(n, christian, islamic, section="A"):
    return {"year": Y, "number": n, "section": section, "type": "alternative",
            "intro": None, "question": None, "parts": None,
            "variants": {"christian": {"question": christian, "parts": None, "quote": None},
                         "islamic":   {"question": islamic,   "parts": None, "quote": None}},
            "audience": "alternative", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": None, "asset_ref": None, "requires_original_visual": False,
            "parent": None}


def structured(n, parts, intro=None, asset=None, audience="all"):
    return {"year": Y, "number": n, "section": "B", "type": "structured",
            "intro": intro, "question": None, "parts": parts, "variants": None,
            "audience": audience, "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": None,
            "requires_original_visual": bool(asset and asset.get("status") == "missing"),
            "parent": None}


def alt_structured(n, christian_parts, islamic_parts,
                   christian_quote=None, islamic_quote=None, asset=None):
    return {"year": Y, "number": n, "section": "B", "type": "alternative_structured",
            "intro": None, "question": None, "parts": None,
            "variants": {
                "christian": {"question": None, "parts": christian_parts, "quote": christian_quote},
                "islamic":   {"question": None, "parts": islamic_parts,   "quote": islamic_quote}},
            "audience": "alternative", "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "asset_ref": None,
            "requires_original_visual": bool(asset and asset.get("status") == "missing"),
            "parent": None}


def p(label, text, sub=None, lines=0, line_labels=None, boxes=0):
    return {"label": label, "text": text, "parts": sub,
            "lines": lines, "line_labels": line_labels, "boxes": boxes}


def missing(kind, caption):
    return {"kind": kind, "file": None, "status": "missing", "caption": caption, "alt": ""}


# ── SECTION A · Questions 1–40 ──────────────────────────────────────────────
Q = [
    short(1,  "What name is given to moving air?"),
    short(2,  "Name the main cash crop grown in Kumasi Ghana."),
    short(3,  "Why did Uganda join the World War II?"),
    short(4,  "Which neighboring country of Uganda is mainly covered by equatorial rain forests?"),
    short(5,  "What was the kingdom of the Bachwezi known as?"),
    short(6,  "Name the element which show a map reader what the map is about."),
    short(7,  "Mention any one problem the government of Uganda is trying to solve by introducing Universal Primary Education."),
    short(8,  "Name any one feature on a river that helps in generation of Hydro-Electric power."),
    short(9,  "How did Alexander Mackay promote education in Uganda?"),
    short(10, "Give any one reason why the people of Uganda wanted to be represented in the legislative council (LEGCO)."),
    short(11, "Mention any one way in which farmers in the rural areas can be helped to transport their produce to bigger markets."),
    short(12, "Apart from rainy season, under which other weather condition would one use an umbrella?"),
    short(13, "How are forests important to carpenter?"),
    short(14, "Bbosa was facing the North. He turned clockwise through 90°. What was his new direction?"),
    short(15, "Give any one danger of fishing using poison."),
    short(16, "Mention any one way in which pupils keep laws and order in the school."),
    short(17, "Name any one United Nations organization that has promoted medical treatment of children in Uganda today."),
    short(18, "Why did cotton growing in Tanganyika lead to the Maji-Maji rebellion?"),
    short(19, "Name the body that promotes trade among the West African states."),
    short(20, "What is citizenship by naturalization?"),
    short(21, "What name is given to the laws that are set by the local council of an area?"),
    short(22, "Why is Kiswahili connected to the coming of Arabs?"),
    short(23, "Apart from the Equator, name any one other important line of latitude."),
    short(24, "Give any one reason why fast maturing crops are suitable for growing in Karamoja."),
    short(25, "Name the organization that replaced Organization of African Unity."),
    short(26, "State any one way in which the Arab traders contributed to the economic development of the interior of East Africa."),
    short(27, "In which one way is water important in the formation of rainfall?"),
    short(28, "How did the introduction of cash crops in East Africa help to improve the transport network?"),
    short(29, "Give any one reason why a school should have a weather station."),
    short(30, "Which discovery marked the end of the Stone Age period?"),
    short(31, "Why is English spoken in Nigeria and Uganda?"),
    short(32, "Give any one reason why a child should not move from school to home alone."),
    short(33, "State any one reason why Mombasa is important to the economy of Uganda."),
    short(34, "Give any one reason why Mbale Town is more densely populated than Moyo Town."),
    short(35, "Mention one lake shared by Uganda and the Democratic Republic of Congo (DRC)."),
    short(36, "Why did the British want to form the East Africa Federation?"),

    alt(37, "Mention the religion that existed in Uganda before the introduction of Islam and Christianity.",
            "Mention the religion that existed in Uganda before the introduction of Islam and Christianity."),
    alt(38, "From what did God create Man?",
            "From what did Allah create Man?"),
    alt(39, "What title do we give to the followers of Jesus?",
            "What title do we give to the followers of Muhammad?"),
    alt(40, "Name the country in Africa where Jesus once lived.",
            "Name the country in Africa where Issa once lived."),

    # ── SECTION B · Questions 41–55 ─────────────────────────────────────────
    structured(41,
        intro="Study the sketch map below and use it to answer the questions that follow.",
        asset=missing("sketch map", "Sketch map printed with Question 41 — Questions 41(a–c) depend on it"),
        parts=[
            p("a", "Name any two social services found in this area.", lines=2),
            p("b", "Give any one reason why many people would settle in this area."),
            p("c", "What direction is the post office from the factory?"),
        ]),
    structured(42, parts=[
        p("a", "Name any two plantation crops grown in Uganda.", lines=2),
        p("b", "State any one advantage of plantation farming."),
    ]),
    structured(43, parts=[
        p("a", "Give any two reasons why a family needs to make a budget.", lines=2),
        p("b", "What type of budget can bring development in a family?"),
        p("c", "In which one way can the budget you have mentioned above bring development in the family?"),
    ]),
    structured(44, parts=[
        p("a", "Where in Africa do we find the temperate grassland?"),
        p("b", "Give any two main economic activities of the temperate grassland.", lines=2),
        p("c", "What method is used for growing sugarcane in the area mentioned in (a) above?"),
    ]),
    structured(45, parts=[
        p("a", "Give any two reasons why informal education is good in the community.", lines=2),
        p("b", "In which two ways do parents help their children to learn about their culture?", lines=2),
    ]),
    structured(46, parts=[
        p("a", "State any two reasons why the level of literacy among the girls is lower than that of the boys in Uganda.", lines=2),
        p("b", "Give any two ways in which girls can be encouraged to keep in school to study.", lines=2),
    ]),
    structured(47, parts=[
        p("a", "State any one duty for each of these arms of Government:",
          sub=[p("i", "Parliament"), p("ii", "Executive")]),
        p("b", "What is the main duty of the Speaker of Parliament?"),
        p("c", "State any one condition that can lead to holding a bye-election."),
    ]),
    structured(48, parts=[
        p("a", "State any one reason why the crested crane was selected as one of the items of Uganda's Coat of Arms."),
        p("b", "What does the red colour on the Uganda National Flag represent?"),
        p("c", "Give any one reason why people stand up while singing the National Anthem."),
    ]),
    structured(49, parts=[
        p("a", "Mention any two reasons why the explorers came to Africa.", lines=2),
        p("b", "State any two difficulties early explorers faced in Africa.", lines=2),
    ]),
    structured(50,
        intro="Study the sketch map of Uganda below and then use it to answer the questions that follow.",
        asset=missing("sketch map", "Sketch map of Uganda printed with Question 50 — the answers depend on the map markings"),
        parts=[
            p("a", "Name the town marked A."),
            p("b", "Mention the tourist attraction places marked X and S.", line_labels=["i. X", "ii. S"]),
            p("c", "Use letter P to show the lake where oil has been discovered in Uganda."),
        ]),
    structured(51, parts=[
        p("a", "Give two means of transport used on Lake Victoria.", lines=2),
        p("b", "State any two ways in which transport as a service provides employment to people.", lines=2),
    ]),
    structured(52, parts=[
        p("a", "What is a population census?"),
        p("b", "State any one reason why information on each of these is collected during a population census:",
          sub=[p("i", "Age"), p("ii", "Gender (sex)")]),
        p("c", "Give any one reason why population census is not carried out every year."),
    ]),

    alt_structured(53,
        christian_parts=[
            p("a", "In the story of the prodigal son, what did he ask from his father before he left?"),
            p("b", "What did his father do to him when he returned?"),
            p("c", "How did his brother receive him when he returned?"),
            p("d", "As a Christian, give one lesson you learn from this story."),
        ],
        islamic_parts=[
            p("a", "What is Hadith?"),
            p("b", "When is a grown-up girl not allowed to pray in Islam?"),
            p("c", "Give two reasons why Muslims are supposed to dress properly during prayers."),
        ]),

    alt_structured(54,
        christian_parts=[
            p("a", "Name the missionary who was killed at Luba's palace in Busoga on the order of Kabaka Mwanga."),
            p("b", "Mention two ways in which the Uganda Martyrs showed faith in their religion.", lines=2),
            p("c", "What lesson do Christians learn from the suffering and death of the martyrs?"),
        ],
        islamic_parts=[
            p("a", "Give the name of Prophet Muhammad's uncle who took care of him after the death of his parents."),
            p("b", "Mention two reasons why Prophet Muhammad was loved by his uncle.", lines=2),
            p("c", "How did Prophet Muhammad overcome the plot to kill him by the Meccans?"),
        ]),

    alt_structured(55,
        christian_quote={"text": "\u201c\u2026.I do not know the man you are talking about \u2026..\u201d",
                         "citation": ""},
        christian_parts=[
            p("a", "Who said these words?"),
            p("b", "Why did he say so?"),
            p("c", "Later on, what did he do?"),
            p("d", "As a Christian, what do we learn from this Bible story?"),
        ],
        islamic_parts=[
            p("a", "What is Tayammum?"),
            p("b", "Give three conditions for Tayammum.", lines=3),
        ]),
]

doc = {
    "subject": "sst",
    "subject_name": "Social Studies with Religious Education",
    "level": "PLE / Primary 7",
    "year": Y,
    "paper_title": "PLE Social Studies with Religious Education 2011",
    "total_questions": len(Q),
    "duration_minutes": 135,
    "format": "written",
    "sections": {"A": [1, 40], "B": [41, 55]},
    "re_instruction": ("For Questions 37 to 40 and 53 to 55, answer EITHER the Christian OR the "
                       "Islamic question but not both. No marks will be awarded to a candidate "
                       "who attempts both alternatives."),
    "source": {
        "verified": False,
        "origin": "Transcript supplied by the project owner",
        "obtained_from": "", "checked_by": "", "checked_date": "",
        "notes": ("Wording preserved verbatim, including original grammar. NOT cross-checked "
                  "against the official UNEB booklet, so 'verified' stays false and no question "
                  "claims UNEB origin. Answers were not supplied. Two printed visuals were not "
                  "supplied: Q41 sketch map and Q50 Uganda sketch map.")
    },
    "questions": Q,
}

os.makedirs("data/papers", exist_ok=True)
with open("data/papers/sst-2011.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
print(f"wrote data/papers/sst-2011.json — {len(Q)} questions")
