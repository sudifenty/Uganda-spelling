#!/usr/bin/env python3
"""
build_sst_2009.py — writes data/papers/sst-2009.json from the transcript supplied by the
project owner. Wording preserved verbatim: nothing rewritten, simplified,
modernised, summarised or paraphrased.
"""
import json, os

Y = 2009
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
            "variants": {"christian": {"question": christian, "parts": None},
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
            "variants": {"christian": {"question": None, "parts": christian_parts},
                         "islamic":   {"question": None, "parts": islamic_parts}},
            "audience": "alternative",
            "answer": None, "answer_status": "not_supplied",
            "topic": "", "subtopic": "", "source": SRC(n), "verified": False,
            "asset": None, "parent": None}


def p(label, text, sub=None, lines=0):
    return {"label": label, "text": text, "parts": sub, "lines": lines}


def missing_asset(kind, caption):
    return {"kind": kind, "file": None, "status": "missing", "caption": caption, "alt": ""}


# Q41 climate table — decoded from the supplied transcript.
# The 12th month label reads "J" in the transcript where December would be
# expected. Left exactly as supplied; flagged in transcription_note.
CLIMATE_TABLE = {
    "kind": "table", "file": None, "status": "supplied",
    "caption": "Table showing the climate of place A",
    "alt": ("Table of monthly temperature in degrees Celsius and rainfall in "
            "millimetres for place A."),
    "table": {
        "header": ["Month", "J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "J"],
        "rows": [
            ["Temperature °C", 22, 21, 22, 24, 23, 25, 21, 21, 23, 22, 24, 25],
            ["Rainfall (mm)", 100, 90, 100, 150, 130, 165, 90, 95, 120, 110, 150, 160],
        ],
    },
    "transcription_note": ("The 12th month is printed as 'J' in the supplied transcript; "
                           "December would be expected. Left exactly as supplied — "
                           "check against the original paper."),
}

# ── SECTION A · Questions 1–40 ──────────────────────────────────────────────
Q = [
    short(1,  "What helps a person to find the actual distance between two places on a map?"),
    short(2,  "Name any one food crop that grows well in a swamp."),
    short(3,  "What is the compass direction of Mt. Elgon from Mt. Ruwenzori?"),
    short(4,  "Apart from colonial rulers which other group of people helped to develop social service in Uganda?"),
    short(5,  "What does the road sign below mean?",
          asset=missing_asset("road sign", "Road sign printed with Question 5")),
    short(6,  "Give one reason why farmers are advised to plant crops in the beginning of a rainy season."),
    short(7,  "Name the winds that brings rain to East Africa."),
    short(8,  "Which mineral is mined in the Osukuru hills in Tororo?"),
    short(9,  "Which people used dhows to come to East Africa?"),
    short(10, "How many countries does Uganda share its border with?"),
    short(11, "Why was Uganda known as a \u201cprotectorate\u201d?"),
    short(12, "Why is Dr. Kwame Nkurumah remembered in Ghana?"),
    short(13, "Mention one reason why goats are more common than cattle in most parts of East Africa."),
    short(14, "Give one advantage of exporting processed goods other than raw materials."),
    short(15, "How can a small scale sugarcane grower in Jinja benefit from the nearby Kakira sugar factory?"),
    short(16, "What is Bwindi National park famous for?"),
    short(17, "Give one reason why the people living in the Sahara Desert wear turbans on their heads."),
    short(18, "State any one way in which the discovery of iron improved the life of the early man."),
    short(19, "State any one way in which freedom of association practiced in Uganda today."),
    short(20, "Mention any one way in which nomadic pastoralism in North-Eastern Uganda can be reduced."),
    short(21, "What is the advantage of a country having its own seaport?"),
    short(22, "Give one reason why the North Eastern part of East Africa receives little rainfall."),
    short(23, "Why is it difficult for one to travel by boat along the Victoria Nile?"),
    short(24, "Give any one way in which people can encourage to live and work in rural areas."),
    short(25, "In which agreement were the boundaries of Buganda drawn?"),
    short(26, "Give one reason why Mutesa 1 was not happy with the missionaries."),
    short(27, "Why should citizen obey the laws of country?"),
    short(28, "Mention one source of income for the colonial government in Uganda."),
    short(29, "Why is air transport used by very few people in Africa?"),
    short(30, "State one reason why the coastal areas of East Africa have high temperatures."),
    short(31, "Name the physical feature that forms the natural boundary between Tanzania and Democratic Republic of Congo (Zaire)."),
    short(32, "State one reason why traditional education is important to your community."),
    short(33, "How did the coming of the Luo-Babiito affect the Bunyoro-Kitara kingdom?"),
    short(34, "What is the importance of a National Anthem in a country?"),
    short(35, "Name the port at the East African coast where the railway line from Tanzania to Zambia begins."),
    short(36, "Give one reason why the people of South Africa fought against Apartheid."),

    alt(37, "What does wine in the Holy Eucharist represent?",
            "Why should a Moslem read Suratu Nas every day?"),
    alt(38, "Who was the mother of John the Baptist?",
            "Who was the father of prophet Muhammad (S.A.W)?"),
    alt(39, "How did Jesus show his power over death?",
            "Why do Muslims wash a dead body before it is buried?"),
    alt(40, "What was Moses\u2019 work before he was called by God?",
            "Write a single word which means \u201cTotal submission to the will of Allah\u201d."),

    # ── SECTION B · Questions 41–55 ─────────────────────────────────────────
    structured(41, intro="Study the table below showing the climate of place A and answer the questions that follow.",
               asset=CLIMATE_TABLE,
               parts=[
                   p("a", "In which month of the year does place A receive the highest amount of rainfall?"),
                   p("b", "Give any one reason why crops can be grown at any time of the year at place A."),
                   p("c", "Mention one cash crop that can grow well under this type of climate."),
                   p("d", "Calculate the temperature range of place A."),
               ]),
    structured(42, parts=[
        p("a", "Mention any one problem that can be caused by floods."),
        p("b", "Give two ways in which the government can help the people affected by floods."),
    ]),
    structured(43, parts=[
        p("a", "Give the importance of each of the following in the development of an industry:",
          sub=[p("i", "Labour"), p("ii", "Capital")]),
        p("b", "Mention any two reasons why good roads are important in the development of an industry."),
    ]),
    structured(44, parts=[
        p("a", "Give any two reasons why people migrate from one place to another."),
        p("b", "Mention any two problems caused by low population density in some rural parts."),
    ]),
    structured(45, parts=[
        p("a", "Mention any two modern cattle keeping practices done today."),
        p("b", "Which of the methods mentioned above is practiced mainly in Central Kenya?"),
        p("c", "How can artificial insemination help a farmer in Uganda?"),
    ]),
    structured(46, intro="Study the map of Sudan below and answer the questions that follow.",
               asset=missing_asset("map", "Map of Sudan printed with Question 46"),
               parts=[
                   p("a", "Name the country marked A."),
                   p("b", "What is the major cash crop grown in the area marked S?"),
                   p("c", "Give one reason why area marked S is good for the growing of crops."),
                   p("d", "Mention any one problem faced by farmers in the area marked S."),
               ]),
    structured(47, parts=[
        p("a", "State any two problems faced by Arabs when spreading Islam in East Africa."),
        p("b", "Mention any two changes that the Arabs brought to East Africa."),
    ]),
    structured(48, parts=[
        p("a", "State any one of the child rights."),
        p("b", "Mention any two of the children's responsibilities."),
        p("c", "State any two reasons why children should know their rights and responsibilities."),
    ]),
    structured(49, parts=[
        p("a", "Mention any one area in Uganda where the people fought against British colonialists."),
        p("b", "Give any two reasons why the people in those areas fought against the British."),
        p("c", "In which way did Semei Kakungulu help the British colonialists in Uganda?"),
    ]),
    structured(50, parts=[
        p("a", "Give any two causes of large family size in Uganda."),
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
            p("c", "What didn\u2019t the people of Taif like about Muhammad?"),
            p("d", "What lesson do we learn from what happened to Muhammad?"),
        ]),

    alt_structured(54,
        christian_parts=[
            p("a", "What is Holy Matrimony?"),
            p("b", "State one reason that may stop Holy Matrimony from taking place."),
            p("c", "Give one reason that may allow someone who had married in church before to marry again."),
            p("d", "Mention any one advantage of Holy Matrimony."),
        ],
        islamic_parts=[
            p("a", "What is Nikah?"),
            p("b", "Give three conditions that allow Nikah to take place.", lines=3),
        ]),

    structured(55, audience="all",
               intro="This question is for all candidates (both Christians and Muslims) to answer.",
               parts=[
                   p("a", "Give any two qualities of a God-fearing person.", lines=2),
                   p("b", "State any two ways in which religious organizations have improved the lives of the people of Uganda.", lines=2),
               ]),
]

doc = {
    "subject": "sst",
    "subject_name": "Social Studies with Religious Education",
    "level": "PLE / Primary 7",
    "year": Y,
    "paper_title": "PLE Social Studies with Religious Education 2009",
    "total_questions": len(Q),
    "duration_minutes": 135,
    "format": "written",
    "sections": {"A": [1, 40], "B": [41, 55]},
    "source": {
        "verified": False,
        "origin": "Transcript supplied by the project owner",
        "obtained_from": "", "checked_by": "", "checked_date": "",
        "notes": ("Wording preserved verbatim. NOT cross-checked against the official UNEB "
                  "booklet, so 'verified' stays false and no question claims UNEB origin. "
                  "Answers were not supplied. Q41 climate table WAS supplied and is stored as "
                  "data. Q5 road sign and Q46 Sudan map were NOT supplied and are marked as "
                  "requiring the original artwork.")
    },
    "questions": Q,
}

os.makedirs("data/papers", exist_ok=True)
with open("data/papers/sst-2009.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
print(f"wrote data/papers/sst-2009.json — {len(Q)} questions")
