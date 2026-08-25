#!/usr/bin/env python3
"""
build_sst_2012.py — writes data/papers/sst-2012.json from the transcript supplied by the
project owner. Wording preserved verbatim: nothing rewritten, simplified,
modernised, summarised or paraphrased.

Adds `requires_original_visual: true` on every question whose printed artwork
was not supplied, as requested.
"""
import json, os

Y = 2012
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
    short(1,  "Name the largest natural forest found in the central part of Uganda."),
    short(2,  "Mention the traditional cash crop that grow well on volcanic soils of East Africa."),
    short(3,  "What is the main cause of land fragmentation in Uganda?"),
    short(4,  "Give any one problem caused by too much rainfall to the community."),
    short(5,  "Why should children be encouraged to plant trees to school?"),
    short(6,  "Mention any one human activity which cause the number of wild animals to reduce in national game park."),
    short(7,  "Give the quickest means in which government sends information to its citizens."),
    short(8,  "Mention any one way in which African countries can improve on agricultural production."),
    short(9,  "Apart from constructing schools, state any one way in which missionaries contributed in improving the life of the people of Africa."),
    short(10, "Name the country in the Horn of Africa which was not colonized."),
    short(11, "Which major activity do farmers in Uganda carry out during a dry season?"),
    short(12, "State any one way in which wild animals are important to the people of East Africa."),
    short(13, "Which king in Uganda did Captain Lugard sign as agreement with in 1890?"),
    short(14, "State any one reason why persons aged 18 and above take part in National elections."),
    short(15, "Apart from cultivating crops and grazing animals, mention any other way the people of Uganda use land to earn a living."),
    short(16, "State any one reason why Africa countries are not developing at the same level."),
    short(17, "What is an import tax?"),
    short(18, "What causes ocean current?"),
    short(19, "Give any reason why people should not settle in swamps."),
    short(20, "Why is the government of Uganda building more classrooms in schools across the country?"),
    short(21, "Give any one advantage a tarmac road has over marram road."),
    short(22, "Mention any one danger of polythene paper bags to soil."),
    short(23, "State any one way in which lakes promote crop farming."),
    short(24, "Write any one responsibility carried by the National Environment Management Authority (NEMA)."),
    short(25, "Mention any one material in our environment which can be used for making balls and skipping ropes to enjoy physical education (P.E) lessons."),
    short(26, "Name any one group of people who provide security service in our community."),
    short(27, "In which one way did Dr. Livingstone show the evils of slave trade in East Africa?"),
    short(28, "Mention any one contribution of a teacher to the community."),
    short(29, "Mention any one peaceful method used by British to establish their rule in Uganda."),
    short(30, "In what direction will Bbosa face if he turn through 180° clockwise from the north?"),
    short(31, "Mention any one problem people living in mountain area face."),
    short(32, "State any one way in which the government of Uganda helps pastoralists in semi-arid areas to overcome the problem of lack of water."),
    short(33, "Mention any one factor that makes lumbering to be done in the Democratic Republic of Congo (D.R.C)."),
    short(34, "Give any one characteristic of rift valley lakes."),
    short(35, "In which one way did the coming of early migrants to the coast of East Africa affect lives of the people in that area?"),

    alt(36, "Name the mother of Isaac.",
            "Name the father of prophet Muhammad (PBUH)."),
    alt(37, "As Christian child, how can you show love to your elders?",
            "As an Islamic child, how can you show love to your elders?"),
    alt(38, "Give one example of sin that a pupil can commit at school.",
            "Give any one example of sin that a pupil can commit at school."),
    alt(39, "What was the work of Joseph, the husband of Mary, mother of Jesus Christ?",
            "What was the work of prophet Muhammad\u2019s first wife?"),
    alt(40, "Mention any one similarity between Christianity and Islam.",
            "Mention any one similarity between Islam and Christianity."),

    # ── SECTION B · Questions 41–55 ─────────────────────────────────────────
    structured(41,
        intro=("The diagram below shows the population distribution of two different areas "
               "in a country. Use them to answer the questions that follow."),
        asset=missing("diagram", "Population distribution diagram printed with Question 41"),
        parts=[
            p("a", "What is the population distribution of area:",
              sub=[p("i", "A"), p("ii", "B")]),
            p("b", "Mention any one disadvantage of the population distribution of area B to the country."),
            p("c", "Give any one advantage of the people living in area A over those living in area B."),
        ]),
    structured(42, parts=[
        p("a", "Mention any two economic activities carried out in Kalangala District.", lines=2),
        p("b", "State any one problem that has slowed down the development of Kalangala District."),
        p("c", "In which way can the problem you have mentioned in (b) above be solved?"),
    ]),
    structured(43, parts=[
        p("a", "Give one safe method of keeping money."),
        p("b", "State any three reasons why Ugandans are encouraged to save money today.", lines=3),
    ]),
    structured(44, parts=[
        p("a", "Mention any one way the colonialists used to show that they had control over an area."),
        p("b", "Give any two reasons that made African natives resist payment of taxes.", lines=2),
        p("c", "State any one reason why the colonialists did not want the natives of Kenya to grow cash crops."),
    ]),
    structured(45, parts=[
        p("a", "Why was early man known as the Stone Age man?"),
        p("b", "Mention any two methods Stone Age men used to kill the animals for food.", lines=2),
        p("c", "How did the discovery of iron change man\u2019s way of life?"),
    ]),
    structured(46, parts=[
        p("a", "Which United Nations Agency is responsible for:",
          sub=[p("i", "Preserving culture and promoting research?"),
               p("ii", "Caring for refugees?")]),
        p("b", "State any two ways in which the Red Cross care for war victims.", lines=2),
    ]),
    structured(47, parts=[
        p("a", "What do you call a place where weather is recorded?"),
        p("b", "Write any two elements of weather which are recorded at the place you have named in (a) above.", lines=2),
        p("c", "Mention any one way the recorded information about weather benefits the people in the community."),
    ]),
    structured(48, parts=[
        p("a", "Which was the largest inland slave market in East Africa?"),
        p("b", "Give any two ways Arabs used to get slaves in East Africa.", lines=2),
        p("c", "Mention any one result of slave trade in East Africa."),
    ]),
    structured(49,
        intro="Below is a climatic graph of Town A. Study it carefully and answer the questions that follow.",
        asset=missing("graph", "Climatic graph of Town A printed with Question 49"),
        parts=[
            p("a", "In which month did Town A receive the highest amount of rainfall?"),
            p("b", "Name the month in which the highest temperature was recorded in Town A."),
            p("c", "What was the temperature range of Town A?"),
            p("d", "Name the type of climate experienced in this town."),
        ]),
    structured(50,
        intro="Use the sketch map of East Africa below and answer the questions that follow.",
        asset=missing("sketch map", "Sketch map of East Africa printed with Question 50"),
        parts=[
            p("a", "Name the port marked S."),
            p("b", "Give any one economic activity that is carried out at port S."),
            p("c", "Name the part of River Nile marked with letter L."),
            p("d", "Use letter P to mark the deepest lake in East Africa."),
        ]),

    alt_structured(51,
        christian_parts=[
            p("a", "Mention any two things you learn from Jesus Christ when he was a child.", lines=2),
            p("b", "Give any two things Jesus Christ did to show love to people.", lines=2),
        ],
        islamic_parts=[
            p("a", "Mention any two things you learn from Prophet Muhammad (PBUH) when he was a child.", lines=2),
            p("b", "Give any two things Prophet Muhammad did to show love to people.", lines=2),
        ]),

    alt_structured(52,
        christian_parts=[
            p("a", "State any two things that happened immediately after Jesus Christ\u2019s death on the cross.", lines=2),
            p("b", "Mention the man who went to Pilate to request for Jesus Christ\u2019s body."),
            p("c", "Where was Jesus Christ\u2019s body buried?"),
        ],
        islamic_parts=[
            p("a", "State two things that happened immediately after Prophet Muhammad died.", lines=2),
            p("b", "Name the first successor of Prophet Muhammad (PBUH)."),
            p("c", "Where was Prophet Muhammad buried?"),
        ]),

    alt_structured(53,
        christian_parts=[
            p("a", "Name the organization that unites the Roman Catholic, Orthodox and Anglican churches of Uganda."),
            p("b", "State any three functions of this organization you have mentioned in (a) above.", lines=3),
        ],
        islamic_parts=[
            p("a", "Name the organization that unites the Muslims in Uganda."),
            p("b", "State any three functions of this organization you have mentioned in (a) above.", lines=3),
        ]),

    alt_structured(54,
        christian_parts=[
            p("a", "What is marriage in Christianity?"),
            p("b", "State any two reasons why church marriage is important.", lines=2),
            p("c", "Mention any one gift God gives to married people."),
        ],
        islamic_parts=[
            p("a", "What is Nikah in Islam?"),
            p("b", "Mention any two reasons why Nikah is important.", lines=2),
            p("c", "Mention any one gift Allah gives to married people."),
        ]),

    alt_structured(55,
        christian_parts=[
            p("a", "Who is a Reverend/Priest?"),
            p("b", "State any three ways in which a Reverend/Priest is important in our community.", lines=3),
        ],
        islamic_parts=[
            p("a", "Who is an Imam in Islam?"),
            p("b", "State any three ways in which an Imam is important in our community.", lines=3),
        ]),
]

doc = {
    "subject": "sst",
    "subject_name": "Social Studies with Religious Education",
    "level": "PLE / Primary 7",
    "year": Y,
    "paper_title": "PLE Social Studies with Religious Education 2012",
    "total_questions": len(Q),
    "duration_minutes": 135,
    "format": "written",
    "sections": {"A": [1, 40], "B": [41, 55]},
    "re_instruction": ("For Questions 36 to 40 and 51 to 55, answer EITHER the Christian OR the "
                       "Islamic question but not both. No mark will be awarded to a candidate "
                       "who attempts both alternatives in a particular number."),
    "source": {
        "verified": False,
        "origin": "Transcript supplied by the project owner",
        "obtained_from": "", "checked_by": "", "checked_date": "",
        "notes": ("Wording preserved verbatim, including original grammar. NOT cross-checked "
                  "against the official UNEB booklet, so 'verified' stays false and no question "
                  "claims UNEB origin. Answers were not supplied. Three printed visuals were not "
                  "supplied: Q41 population distribution diagram, Q49 climatic graph of Town A, "
                  "Q50 East Africa sketch map.")
    },
    "questions": Q,
}

os.makedirs("data/papers", exist_ok=True)
with open("data/papers/sst-2012.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
print(f"wrote data/papers/sst-2012.json — {len(Q)} questions")
