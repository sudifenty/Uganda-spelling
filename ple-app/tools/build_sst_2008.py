#!/usr/bin/env python3
"""
build_sst_2008.py — writes data/papers/sst-2008.json from the transcript supplied by the
project owner. Wording is preserved verbatim: nothing is rewritten, simplified,
modernised, summarised or paraphrased.

Question types used:
  short                  Section A, single short-answer question
  alternative            Section A, Christian OR Islamic variant (Q37-40)
  structured             Section B, question with lettered parts
  alternative_structured Section B, Christian OR Islamic variant, each with parts (Q53-54)
"""
import json, os

Y = 2008
SRC = lambda n: f"PLE SST {Y} — Q{n}"


def short(n, text, asset=None):
    return {"year": Y, "number": n, "section": "A", "type": "short",
            "question": text, "parts": None, "variants": None, "audience": "all",
            "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "parent": None}


def alt(n, christian, islamic):
    return {"year": Y, "number": n, "section": "A", "type": "alternative",
            "question": None, "parts": None,
            "variants": {
                "christian": {"question": christian, "parts": None},
                "islamic":   {"question": islamic,   "parts": None}},
            "audience": "alternative",
            "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": None, "parent": None}


def structured(n, parts, intro=None, asset=None, audience="all"):
    return {"year": Y, "number": n, "section": "B", "type": "structured",
            "question": intro, "parts": parts, "variants": None, "audience": audience,
            "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": asset, "parent": None}


def alt_structured(n, christian_parts, islamic_parts):
    return {"year": Y, "number": n, "section": "B", "type": "alternative_structured",
            "question": None, "parts": None,
            "variants": {
                "christian": {"question": None, "parts": christian_parts},
                "islamic":   {"question": None, "parts": islamic_parts}},
            "audience": "alternative",
            "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": None, "parent": None}


def p(label, text, sub=None):
    return {"label": label, "text": text, "parts": sub}


def missing_asset(kind, caption):
    return {"kind": kind, "file": None, "status": "missing",
            "caption": caption, "alt": ""}


# ── SECTION A · Questions 1–40 ──────────────────────────────────────────────
Q = [
    short(1,  "State one problem affecting cattle keeping in Karamoja region."),
    short(2,  "Give any importance of mountains to farmers who live near them."),
    short(3,  "Mention any one disadvantage of building in a wetland."),
    short(4,  "Give one reason why it was easier for the British to rule Buganda and not Lango or West Nile."),
    short(5,  "What is the similarity between the Motto of Uganda and the first verse of the National Anthem?"),
    short(6,  "Why is Carl Peters important in the history of East Africa?"),
    short(7,  "Give one reason why there are many different types of natural vegetation in Africa."),
    short(8,  "Suggest one way of improving the labour force in Africa."),
    short(9,  "Give one reason why landslides are not common in many parts of Central and Northern Uganda."),
    short(10, "Name an international economic organization that includes Nigeria, Algeria and Libya."),
    short(11, "State one way in which the coming of Arabs affected the people of East Africa."),
    short(12, "State one way in which the police contributes to the welfare of other people in a community."),
    short(13, "Give one contribution made by Omukama Kasagama of Toro in the colonization of Uganda by the British."),
    short(14, "Mention the instrument that is used to measure the amount of rainfall at a weather station."),
    short(15, "Name the ethnic group of people who occupy the North-Eastern part of Uganda."),
    short(16, "Why is the symbol below important on a map?",
          asset=missing_asset("symbol", "Map symbol printed with Question 16")),
    short(17, "In which way is the formation of Lake Kyoga different from that of Lake Edward?"),
    short(18, "Identify any one problem faced by people living near a cement industry."),
    short(19, "Suggest any one way the government can help the people in rural areas to increase agricultural produce."),
    short(20, "In which way does peace promote development of the country?"),
    short(21, "Why is it difficult to carry out crop farming in north-eastern Kenya?"),
    short(22, "State one reason controlling population increase is difficult."),
    short(23, "How did the explorers contribute to the colonization of Uganda?"),
    short(24, "State the importance of political parties in Uganda before 1962."),
    short(25, "On which dam is Sennar Dam found?"),
    short(26, "How is the harvesting of cocoa in Ghana different from harvesting coffee in Uganda?"),
    short(27, "State one way in which the African Union (A.U.) is helping member states to solve the problem of civil wars."),
    short(28, "Apart from providing water for industrial use, how has Lake Victoria contributed to the growth of industries in Uganda?"),
    short(29, "In which way is an extinct volcano different from an active volcano?"),
    short(30, "Name the major crop grown in the Kirombero Irrigation Scheme in Tanzania."),
    short(31, "Why did Egypt try to colonize Uganda?"),
    short(32, "How are camels helpful to the Berbers of North Africa?"),
    short(33, "Give one problem the builders of the Uganda Railway faced in the Nandi area."),
    short(34, "State one reason why crop farming is common in the highlands area of Kisoro."),
    short(35, "Apart from being cloudy or windy, give any one other change of weather."),
    short(36, "Mention one reason why the Equator is marked 0°."),

    alt(37, "Why did God create Eve?",
            "Why did Allah create Hawa?"),
    alt(38, "Why do Christians ask for the Holy Spirit to be with them?",
            "Why is the angel who is always on the right-hand side of every Muslim important?"),
    alt(39, "What is the difference between Cana and Canaan?",
            "Give one way in which Yusuf's dream was fulfilled."),
    alt(40, "In which way does God communicate to his people?",
            "How do Muslims show respect to the Holy House of Allah?"),

    # ── SECTION B · Questions 41–55 ─────────────────────────────────────────
    structured(41, intro="Study the table showing the climate of place A and answer:",
               asset=missing_asset("table", "Table showing the climate of place A"),
               parts=[
                   p("a", "In which month of the year does place A receive the highest amount of rainfall?"),
                   p("b", "Give one reason why crops can be grown at any time of the year at place A."),
                   p("c", "Mention one cash crop that can grow well under this type of climate."),
                   p("d", "Calculate the temperature range of place A."),
               ]),
    structured(42, parts=[
        p("a", "Mention any two problems that can be caused by floods."),
        p("b", "Give two ways in which the government can help the people affected by floods."),
    ]),
    structured(43, parts=[
        p("a", "Give the importance of each of the following in the development of an industry:",
          sub=[p("i", "Labour"), p("ii", "Capital")]),
        p("b", "Mention any two reasons why good roads are important in the development of an industry."),
    ]),
    structured(44, parts=[
        p("a", "Give any two reasons why people migrate from one place to another."),
        p("b", "Mention any two problems caused by low population density in some rural areas."),
    ]),
    structured(45, parts=[
        p("a", "Mention any two modern cattle-keeping methods being practiced today."),
        p("b", "Which of the methods mentioned above is practiced mainly in Central Kenya?"),
        p("c", "How can artificial insemination help a cattle farmer in Uganda?"),
    ]),
    structured(46, intro="Study the map of Sudan and answer:",
               asset=missing_asset("map", "Map of Sudan printed with Question 46"),
               parts=[
                   p("a", "Name the country marked A."),
                   p("b", "What is the major cash crop grown in the area marked S?"),
                   p("c", "Give one reason why area S is good for growing crops."),
                   p("d", "Mention any one problem faced by farmers in area S."),
               ]),
    structured(47, parts=[
        p("a", "State any two problems faced by Arabs when spreading Islam in East Africa."),
        p("b", "Mention any two good changes the Arabs brought to East Africa."),
    ]),
    structured(48, parts=[
        p("a", "State any one of the children's rights."),
        p("b", "Mention any one of the children's responsibilities."),
        p("c", "State any two reasons why children should know their rights and responsibilities."),
    ]),
    structured(49, parts=[
        p("a", "Mention any one area in Uganda where the people fought against British colonialists."),
        p("b", "Give any two reasons why the people in those areas fought against the British."),
        p("c", "In which way did Semei Kakungulu help the British colonialists in Uganda?"),
    ]),
    structured(50, parts=[
        p("a", "Give any two causes of large family sizes in Uganda."),
        p("b", "Mention any two problems of having a large family."),
    ]),
    structured(51, intro="Give any two ways in which each of the following has helped the people of Uganda:",
               parts=[
                   p("a", "Red Cross / Red Crescent"),
                   p("b", "United Nations International Children's Emergency Fund (UNICEF)"),
               ]),
    structured(52, parts=[
        p("a", "Give any two reasons why it was important for African countries to unite after getting independence."),
        p("b", "State any two reasons why most African countries continue to depend on foreign countries."),
    ]),

    alt_structured(53,
        christian_parts=[
            p("a", "\u201cBlessed are you among women and blessed is the fruit of your womb.\u201d Who said these words?"),
            p("b", "What is the meaning of the word \u201cfruit\u201d mentioned above?"),
            p("c", "Why was Mary \u201cblessed among women\u201d?"),
            p("d", "\u201cBehold, servant of the Lord; let it happen to me according to your word.\u201d What lesson do we learn from this?"),
        ],
        islamic_parts=[
            p("a", "What did Muhammad do to the woman who wanted to poison him?"),
            p("b", "What happened to Muhammad when he went to ask for help from the people of Taif?"),
            p("c", "What didn't the people of Taif like about Muhammad?"),
            p("d", "What lesson do we learn from what happened to Muhammad?"),
        ]),

    alt_structured(54,
        christian_parts=[
            p("a", "What is Holy Matrimony?"),
            p("b", "State one reason that may stop Holy Matrimony from taking place."),
            p("c", "Give one reason that may allow someone who had married in church before to marry again."),
        ],
        islamic_parts=[
            p("a", "What is Nikah?"),
            p("b", "Give three conditions that allow Nikah to take place."),
        ]),

    structured(55, audience="all",
               intro="For all candidates — both Christians and Muslims:",
               parts=[
                   p("a", "Give any two qualities of a God-fearing person."),
                   p("b", "State any two ways in which religious organizations have improved the lives of the people of Uganda."),
               ]),
]

doc = {
    "subject": "sst",
    "subject_name": "Social Studies with Religious Education",
    "level": "PLE / Primary 7",
    "year": Y,
    "paper_title": "PLE Social Studies with Religious Education 2008",
    "total_questions": len(Q),
    "duration_minutes": 135,
    "format": "written",
    "sections": {"A": [1, 40], "B": [41, 55]},
    "source": {
        "verified": False,
        "origin": "Transcript supplied by the project owner",
        "obtained_from": "",
        "checked_by": "",
        "checked_date": "",
        "notes": ("Wording preserved verbatim from the supplied transcript. NOT yet cross-checked "
                  "against the official UNEB booklet, so 'verified' stays false and no question "
                  "claims UNEB origin. Answers were not supplied: every answer_status is "
                  "'not_supplied'. Three printed items are missing: the Q16 map symbol, the Q41 "
                  "climate table and the Q46 map of Sudan.")
    },
    "questions": Q,
}

os.makedirs("data/papers", exist_ok=True)
with open("data/papers/sst-2008.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)

print(f"wrote data/papers/sst-2008.json — {len(Q)} questions")
