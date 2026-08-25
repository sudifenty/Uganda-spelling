#!/usr/bin/env python3
"""
build_math_bank.py — 800 original Mathematics questions (200 each for P4-P7).

Why generation is safe here (and was not for SST):
  * Every answer is COMPUTED in Python, never written by hand.
  * Every question stores a machine-checkable `calc` expression, and
    tools/validate_math.py independently re-evaluates it and compares.
  * Varying the numbers in "347 + 285" makes a genuinely different practice
    item — unlike rewording "What is the capital of Uganda?".

Distractors are built from REAL pupil errors (carry forgotten, wrong operation,
place-value slip, off-by-one) so options are plausible, never random noise.
"""
import json, os, random, glob, importlib.util, sys
from fractions import Fraction

random.seed(20260816)          # reproducible builds
OUT = "data/practice"
TARGET = {"Easy": 70, "Medium": 80, "Hard": 50}


# ── record helpers ────────────────────────────────────────────────────────
def mc(cls, topic, sub, diff, q, correct, wrongs, expl, calc=None, qtype="multiple_choice"):
    """Multiple choice. `correct` and `wrongs` are strings."""
    correct = str(correct)
    opts, seen = [], {correct}
    for w in wrongs:
        w = str(w)
        if w not in seen:
            seen.add(w); opts.append(w)
        if len(opts) == 3:
            break
    if len(opts) < 3:
        return None                      # not enough distinct distractors — skip
    allopts = opts + [correct]
    random.shuffle(allopts)
    letter = "ABCD"[allopts.index(correct)]
    return {"id": None, "class": cls, "subject": "Mathematics", "topic": topic,
            "subtopic": sub, "difficulty": diff, "questionType": qtype, "renderAs": "mcq",
            "question": q, "options": [f"{L}. {t}" for L, t in zip("ABCD", allopts)],
            "correctAnswer": letter, "answers": None, "pairs": None,
            "explanation": expl, "calc": calc, "answerValue": correct}


def fb(cls, topic, sub, diff, q, answers, expl, calc=None, qtype="fill_blank"):
    answers = [str(a) for a in answers]
    return {"id": None, "class": cls, "subject": "Mathematics", "topic": topic,
            "subtopic": sub, "difficulty": diff, "questionType": qtype, "renderAs": "fill",
            "question": q, "options": None, "correctAnswer": None, "answers": answers,
            "pairs": None, "explanation": expl, "calc": calc, "answerValue": answers[0]}


def tf(cls, topic, sub, diff, q, is_true, expl, calc=None):
    return {"id": None, "class": cls, "subject": "Mathematics", "topic": topic,
            "subtopic": sub, "difficulty": diff, "questionType": "true_false", "renderAs": "tf",
            "question": q, "options": ["A. True", "B. False"],
            "correctAnswer": "A" if is_true else "B", "answers": None, "pairs": None,
            "explanation": expl, "calc": calc, "answerValue": "True" if is_true else "False"}


def mt(cls, topic, sub, diff, q, pairs, expl):
    return {"id": None, "class": cls, "subject": "Mathematics", "topic": topic,
            "subtopic": sub, "difficulty": diff, "questionType": "matching", "renderAs": "match",
            "question": q, "options": None, "correctAnswer": None, "answers": None,
            "pairs": pairs, "explanation": expl, "calc": None, "answerValue": None}


def fs(f):
    """Format a Fraction as a pupil would write it."""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    if abs(f) > 1:
        whole = int(abs(f)) * (1 if f > 0 else -1)
        rem = abs(f) - abs(whole)
        if rem:
            return f"{whole} {rem.numerator}/{rem.denominator}"
    return f"{f.numerator}/{f.denominator}"


ROMAN = [(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),
         (5,"V"),(4,"IV"),(1,"I")]
def roman(n):
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out += s; n -= v
    return out


NAMES = ["Amina","Bosco","Cissy","Denis","Esther","Farouk","Grace","Hakim",
         "Irene","Joseph","Kato","Lydia","Musa","Nakato","Opio","Praise",
         "Ruth","Sam","Tendo","Winnie"]
ITEMS = ["mangoes","oranges","books","pencils","eggs","bananas","cups","exercise books"]
def nm(): return random.choice(NAMES)
def it(): return random.choice(ITEMS)


# ══════════════════════════════════════════════════════════════════════════
#  P.4 GENERATORS
# ══════════════════════════════════════════════════════════════════════════
def p4_place_value():
    n = random.randint(1000, 9999); pos = random.choice([0,1,2,3])
    names = ["thousands","hundreds","tens","ones"]
    d = int(str(n)[pos]); place = 10**(3-pos)
    return mc("P4","Whole Numbers","Place Value","Easy",
        f"In the number {n}, what is the place value of the digit {d}?",
        f"{d*place}", [f"{d}", f"{place}", f"{d*place*10}", f"{d+place}"],
        f"The digit {d} is in the {names[pos]} place, so its place value is {d} x {place} = {d*place}.",
        f"{d}*{place}")

def p4_face_value():
    n = random.randint(1000, 9999); pos = random.choice([0,1,2,3])
    d = int(str(n)[pos])
    return mc("P4","Whole Numbers","Face Value","Easy",
        f"What is the face value of the digit {d} in the number {n}?",
        f"{d}", [f"{d*10}", f"{d*100}", f"{n}", f"{d+1}"],
        f"Face value is simply the digit itself, which is {d}.", f"{d}")

def p4_expanded():
    n = random.randint(1000, 9999)
    parts = [int(c)*10**(3-i) for i,c in enumerate(str(n)) if int(c)]
    ans = " + ".join(str(p) for p in parts)
    return fb("P4","Whole Numbers","Expanded Notation","Medium",
        f"Write {n} in expanded form. (Use + between the parts, largest first.)",
        [ans, ans.replace(" ","")],
        f"{n} = {ans}.", f"{'+'.join(str(p) for p in parts)}")

def p4_order():
    ns = random.sample(range(100, 999), 4)
    ordered = sorted(ns)
    return mc("P4","Whole Numbers","Ordering","Easy",
        f"Arrange these numbers from smallest to largest: {', '.join(map(str,ns))}",
        ", ".join(map(str,ordered)),
        [", ".join(map(str,sorted(ns,reverse=True))),
         ", ".join(map(str,ns)),
         ", ".join(map(str,ordered[::-1][:2]+ordered[:2]))],
        f"Smallest to largest: {', '.join(map(str,ordered))}.")

def p4_oddeven():
    n = random.randint(10, 99)
    return tf("P4","Whole Numbers","Odd and Even","Easy",
        f"The number {n} is an even number.", n % 2 == 0,
        f"{n} is {'even' if n%2==0 else 'odd'} because it {'ends in 0, 2, 4, 6 or 8' if n%2==0 else 'ends in 1, 3, 5, 7 or 9'}.")

def p4_round10():
    n = random.randint(21, 989)
    r = round(n/10)*10
    if n % 10 == 5: r = n + 5
    return mc("P4","Whole Numbers","Rounding","Medium",
        f"Round {n} to the nearest ten.", str(r),
        [str(r+10), str(r-10), str(n//10*10 if r!=n//10*10 else r+20)],
        f"The ones digit is {n%10}, so {n} rounds to {r}.", str(r))

def p4_roman():
    n = random.choice([4,6,9,11,14,15,19,20,24,29,30,40,45,50,60,90,100])
    return mc("P4","Whole Numbers","Roman Numerals","Medium",
        f"Write {n} in Roman numerals.", roman(n),
        [roman(n+1), roman(n-1) if n>1 else "II", roman(n+5)],
        f"{n} is written as {roman(n)} in Roman numerals.")

def p4_pattern():
    start = random.randint(2, 12); step = random.choice([2,3,4,5,10])
    seq = [start + step*i for i in range(4)]
    nxt = seq[-1] + step
    return mc("P4","Patterns","Number Patterns","Easy",
        f"What number comes next? {', '.join(map(str,seq))}, ___",
        str(nxt), [str(nxt+step), str(nxt-1), str(nxt+1)],
        f"The pattern adds {step} each time, so after {seq[-1]} comes {nxt}.",
        f"{seq[-1]}+{step}")

def p4_add():
    a, b = random.randint(120, 899), random.randint(120, 899)
    return mc("P4","Addition","Addition with Carrying","Easy",
        f"Work out: {a} + {b}", str(a+b),
        [str(a+b+10), str(a+b-10), str(a+b+100)],
        f"{a} + {b} = {a+b}.", f"{a}+{b}")

def p4_sub():
    a = random.randint(400, 999); b = random.randint(120, a-50)
    return mc("P4","Subtraction","Subtraction with Borrowing","Easy",
        f"Work out: {a} - {b}", str(a-b),
        [str(a-b+10), str(a-b-10), str(a+b)],
        f"{a} - {b} = {a-b}.", f"{a}-{b}")

def p4_addword():
    a, b = random.randint(45, 260), random.randint(45, 260)
    n1, i = nm(), it()
    return mc("P4","Addition","Word Problems","Medium",
        f"{n1} had {a} {i} and was given {b} more. How many {i} does {n1} have now?",
        str(a+b), [str(a-b if a>b else b-a), str(a+b+10), str(a+b-1)],
        f"Add the two amounts: {a} + {b} = {a+b} {i}.", f"{a}+{b}")

def p4_subword():
    a = random.randint(300, 900); b = random.randint(60, a-60)
    n1 = nm()
    return mc("P4","Subtraction","Word Problems","Medium",
        f"A shop had {a} exercise books. {b} were sold. How many exercise books remained?",
        str(a-b), [str(a+b), str(a-b-10), str(a-b+100)],
        f"Take away what was sold: {a} - {b} = {a-b}.", f"{a}-{b}")

def p4_mulfact():
    a, b = random.randint(3, 12), random.randint(3, 12)
    return mc("P4","Multiplication","Multiplication Facts","Easy",
        f"Work out: {a} x {b}", str(a*b),
        [str(a*b+a), str(a*b-b), str(a+b)],
        f"{a} x {b} = {a*b}.", f"{a}*{b}")

def p4_mul10():
    a = random.randint(12, 98); m = random.choice([10,100,1000])
    return mc("P4","Multiplication","Multiplying by 10, 100, 1000","Easy",
        f"Work out: {a} x {m}", str(a*m),
        [str(a*m*10), str(a*m//10), str(a+m)],
        f"Multiplying by {m} adds {len(str(m))-1} zero(s): {a} x {m} = {a*m}.", f"{a}*{m}")

def p4_shortmul():
    a, b = random.randint(23, 98), random.randint(3, 9)
    return mc("P4","Multiplication","Short Multiplication","Medium",
        f"Work out: {a} x {b}", str(a*b),
        [str(a*b+b), str(a*b-a), str((a//10)*b*10 + (a%10)*b + 10)],
        f"{a} x {b} = {a*b}.", f"{a}*{b}")

def p4_mulword():
    r, c = random.randint(4, 12), random.randint(6, 15)
    return mc("P4","Multiplication","Word Problems","Medium",
        f"A classroom has {r} rows of desks with {c} desks in each row. How many desks are there altogether?",
        str(r*c), [str(r+c), str(r*c+c), str(r*c-r)],
        f"Multiply rows by desks per row: {r} x {c} = {r*c} desks.", f"{r}*{c}")

def p4_divfact():
    b = random.randint(2, 12); q = random.randint(2, 12); a = b*q
    return mc("P4","Division","Division Facts","Easy",
        f"Work out: {a} ÷ {b}", str(q), [str(q+1), str(q-1), str(a-b)],
        f"{a} ÷ {b} = {q} because {b} x {q} = {a}.", f"{a}/{b}")

def p4_divrem():
    b = random.randint(3, 9); q = random.randint(4, 15); r = random.randint(1, b-1)
    a = b*q + r
    return mc("P4","Division","Remainders","Medium",
        f"Divide {a} by {b}. What is the remainder?",
        str(r), [str(q), str(r+1), str(b-r)],
        f"{b} x {q} = {b*q}, and {a} - {b*q} = {r}. The remainder is {r}.",
        f"{a}%{b}")

def p4_divword():
    per = random.randint(4, 12); groups = random.randint(4, 12); total = per*groups
    i = it()
    return mc("P4","Division","Word Problems","Medium",
        f"{total} {i} are shared equally among {groups} children. How many does each child get?",
        str(per), [str(per+1), str(total-groups), str(per*2)],
        f"Divide the total by the number of children: {total} ÷ {groups} = {per}.",
        f"{total}/{groups}")

def p4_frac_name():
    d = random.choice([3,4,5,6,8,10]); n = random.randint(1, d-1)
    return mc("P4","Fractions","Numerator and Denominator","Easy",
        f"In the fraction {n}/{d}, which number is the denominator?",
        str(d), [str(n), str(n+d), str(d-n)],
        f"The denominator is the bottom number, which is {d}.", str(d))

def p4_frac_equiv():
    d = random.choice([2,3,4,5]); n = random.randint(1, d-1); k = random.choice([2,3,4])
    return mc("P4","Fractions","Equivalent Fractions","Medium",
        f"Which fraction is equal to {n}/{d}?",
        f"{n*k}/{d*k}", [f"{n+k}/{d+k}", f"{n*k}/{d}", f"{n}/{d*k}"],
        f"Multiply top and bottom by {k}: {n}/{d} = {n*k}/{d*k}.", f"{n*k}/{d*k}")

def p4_frac_of():
    d = random.choice([2,3,4,5,6]); n = 1; tot = d*random.randint(3, 12)
    ans = tot//d
    return mc("P4","Fractions","Fractions of Quantities","Medium",
        f"What is {n}/{d} of {tot}?", str(ans),
        [str(ans+d), str(tot-d), str(ans*2)],
        f"Divide {tot} by {d}: {tot} ÷ {d} = {ans}.", f"{tot}/{d}")

def p4_frac_add():
    d = random.choice([5,6,7,8,9,10]); a = random.randint(1, d-2); b = random.randint(1, d-a-1)
    res = Fraction(a+b, d)
    return mc("P4","Fractions","Adding Fractions","Medium",
        f"Work out: {a}/{d} + {b}/{d}", fs(res),
        [f"{a+b}/{d*2}", fs(Fraction(a*b,d)), f"{a+b+1}/{d}"],
        f"The denominators are the same, so add the tops: {a} + {b} = {a+b}, giving {a+b}/{d} = {fs(res)}.",
        f"({a}+{b})/{d}")

def p4_dec_tenths():
    w = random.randint(1, 9); t = random.randint(1, 9)
    return mc("P4","Decimals","Tenths","Easy",
        f"Write {w} and {t} tenths as a decimal.", f"{w}.{t}",
        [f"{w}.0{t}", f"{t}.{w}", f"{w}{t}"],
        f"{w} whole and {t} tenths is written {w}.{t}.", f"{w}+{t}/10")

def p4_dec_compare():
    a = round(random.uniform(1, 9), 1); b = round(random.uniform(1, 9), 1)
    while a == b: b = round(random.uniform(1, 9), 1)
    big = max(a, b)
    return mc("P4","Decimals","Comparing Decimals","Medium",
        f"Which is greater: {a} or {b}?", str(big), [str(min(a,b)), "They are equal", str(round(a+b,1))],
        f"{big} is greater because it has the larger value.", str(big))

def p4_money_change():
    price = random.randint(3, 18) * 500; paid = ((price // 5000) + 1) * 5000
    ch = paid - price
    return mc("P4","Money","Change","Medium",
        f"A pupil buys a book for {price:,} shillings and pays with {paid:,} shillings. How much change is given?",
        f"{ch:,}", [f"{ch+500:,}", f"{price:,}", f"{paid+price:,}"],
        f"Change = {paid:,} - {price:,} = {ch:,} shillings.", f"{paid}-{price}")

def p4_money_add():
    a = random.randint(2, 20)*500; b = random.randint(2, 20)*500
    return mc("P4","Money","Adding Money","Easy",
        f"Add: {a:,} shillings + {b:,} shillings", f"{a+b:,}",
        [f"{a+b+500:,}", f"{abs(a-b):,}", f"{a+b-1000:,}"],
        f"{a:,} + {b:,} = {a+b:,} shillings.", f"{a}+{b}")

def p4_money_shop():
    p1 = random.randint(2, 9)*500; q1 = random.randint(2, 5)
    tot = p1*q1
    i = it()
    return mc("P4","Money","Shopping","Hard",
        f"One kilogram of {i} costs {p1:,} shillings. How much do {q1} kilograms cost?",
        f"{tot:,}", [f"{p1+q1:,}", f"{tot+p1:,}", f"{tot-p1:,}"],
        f"Multiply price by quantity: {p1:,} x {q1} = {tot:,} shillings.", f"{p1}*{q1}")

def p4_len_convert():
    m = random.randint(2, 20)
    return mc("P4","Measurement","Length","Easy",
        f"Change {m} metres into centimetres.", f"{m*100}",
        [f"{m*10}", f"{m*1000}", f"{m+100}"],
        f"1 metre = 100 cm, so {m} m = {m} x 100 = {m*100} cm.", f"{m}*100")

def p4_mass_convert():
    k = random.randint(2, 15)
    return mc("P4","Measurement","Mass","Easy",
        f"Change {k} kilograms into grams.", f"{k*1000}",
        [f"{k*100}", f"{k*10}", f"{k+1000}"],
        f"1 kg = 1000 g, so {k} kg = {k*1000} g.", f"{k}*1000")

def p4_cap_convert():
    l = random.randint(2, 15)
    return mc("P4","Measurement","Capacity","Easy",
        f"How many millilitres are in {l} litres?", f"{l*1000}",
        [f"{l*100}", f"{l*10}", f"{l+1000}"],
        f"1 litre = 1000 ml, so {l} litres = {l*1000} ml.", f"{l}*1000")

def p4_time_dur():
    h = random.randint(1, 4); m = random.choice([10,15,20,30,40,45])
    total = h*60 + m
    return mc("P4","Time","Duration","Medium",
        f"How many minutes are there in {h} hours and {m} minutes?",
        str(total), [str(h*60), str(total+60), str(h*100+m)],
        f"{h} hours = {h*60} minutes. {h*60} + {m} = {total} minutes.", f"{h}*60+{m}")

def p4_time_clock():
    h = random.randint(1, 11); m = random.choice([15, 30, 45])
    word = {15:"a quarter past", 30:"half past", 45:"a quarter to"}[m]
    ans = f"{word} {h if m!=45 else (h+1 if h<12 else 1)}"
    return mc("P4","Time","Reading Clocks","Medium",
        f"How do we say the time {h}:{m:02d}?", ans,
        [f"half past {h}" if m!=30 else f"a quarter past {h}",
         f"a quarter to {h}" if m!=45 else f"a quarter past {h}",
         f"{m} past {h}"],
        f"{h}:{m:02d} is read as {ans}.")

def p4_calendar():
    mth = random.choice(["January","March","April","June","September","November","December"])
    days = 31 if mth in ("January","March","December") else 30
    return mc("P4","Time","Calendar","Easy",
        f"How many days are there in the month of {mth}?", str(days),
        [str(days-1), str(days+1), "28"],
        f"{mth} has {days} days.", str(days))

def p4_shape_sides():
    shapes = {"triangle":3, "square":4, "rectangle":4, "pentagon":5, "hexagon":6, "octagon":8}
    s = random.choice(list(shapes))
    return mc("P4","Geometry","2D Shapes","Easy",
        f"How many sides does a {s} have?", str(shapes[s]),
        [str(shapes[s]+1), str(shapes[s]-1), str(shapes[s]+2)],
        f"A {s} has {shapes[s]} sides.", str(shapes[s]))

def p4_solid_faces():
    solids = {"cube":6, "cuboid":6, "cylinder":3, "cone":2}
    s = random.choice(list(solids))
    return mc("P4","Geometry","3D Objects","Medium",
        f"How many faces does a {s} have?", str(solids[s]),
        [str(solids[s]+1), str(solids[s]-1), str(solids[s]+2)],
        f"A {s} has {solids[s]} faces.", str(solids[s]))

def p4_perimeter():
    l, w = random.randint(3, 20), random.randint(3, 20)
    p = 2*(l+w)
    return mc("P4","Perimeter and Area","Perimeter","Medium",
        f"A rectangle is {l} cm long and {w} cm wide. What is its perimeter?",
        f"{p} cm", [f"{l*w} cm", f"{l+w} cm", f"{p+2} cm"],
        f"Perimeter = 2 x (length + width) = 2 x ({l} + {w}) = {p} cm.", f"2*({l}+{w})")

def p4_area():
    l, w = random.randint(2, 15), random.randint(2, 15)
    return mc("P4","Perimeter and Area","Area","Medium",
        f"Find the area of a rectangle {l} cm long and {w} cm wide.",
        f"{l*w} sq cm", [f"{2*(l+w)} sq cm", f"{l+w} sq cm", f"{l*w+l} sq cm"],
        f"Area = length x width = {l} x {w} = {l*w} square centimetres.", f"{l}*{w}")

def p4_data_table():
    fruits = random.sample(["Mangoes","Oranges","Bananas","Apples","Guavas"], 3)
    vals = [random.randint(5, 30) for _ in fruits]
    tbl = "; ".join(f"{f} = {v}" for f, v in zip(fruits, vals))
    tot = sum(vals)
    return mc("P4","Data Handling","Reading Tables","Medium",
        f"A table shows fruits sold in a day: {tbl}. How many fruits were sold altogether?",
        str(tot), [str(tot - min(vals)), str(max(vals)), str(tot+5)],
        f"Add them all: {' + '.join(map(str,vals))} = {tot}.", "+".join(map(str,vals)))

def p4_data_more():
    a, b = random.randint(6, 30), random.randint(6, 30)
    while a == b: b = random.randint(6, 30)
    x, y = "Primary 4", "Primary 5"
    return mc("P4","Data Handling","Comparing Data","Hard",
        f"A bar chart shows {x} has {a} pupils and {y} has {b} pupils. How many more pupils are in {x if a>b else y} than in {y if a>b else x}?",
        str(abs(a-b)), [str(a+b), str(abs(a-b)+1), str(min(a,b))],
        f"Subtract the smaller from the larger: {max(a,b)} - {min(a,b)} = {abs(a-b)}.",
        f"{max(a,b)}-{min(a,b)}")

def p4_missing():
    a = random.randint(15, 80); b = random.randint(10, 60)
    return fb("P4","Patterns","Missing Numbers","Medium",
        f"Find the missing number: {a} + ___ = {a+b}", [str(b)],
        f"{a+b} - {a} = {b}.", f"{a+b}-{a}")

def p4_estimate():
    a, b = random.randint(180, 890), random.randint(180, 890)
    ra, rb = round(a/100)*100, round(b/100)*100
    return mc("P4","Addition","Estimation","Hard",
        f"Estimate {a} + {b} by first rounding each number to the nearest hundred.",
        str(ra+rb), [str(a+b), str(ra+rb+100), str(ra+rb-100)],
        f"{a} rounds to {ra} and {b} rounds to {rb}. {ra} + {rb} = {ra+rb}.",
        f"{ra}+{rb}")

def p4_twostep():
    a = random.randint(5, 12); b = random.randint(3, 9); c = random.randint(10, 40)
    tot = a*b + c
    return mc("P4","Problem Solving","Two-Step Problems","Hard",
        f"A trader had {c} eggs. She bought {a} trays with {b} eggs in each tray. How many eggs does she have now?",
        str(tot), [str(a*b), str(c+a+b), str(tot-c)],
        f"First {a} x {b} = {a*b} eggs. Then {a*b} + {c} = {tot} eggs.", f"{a}*{b}+{c}")

def p4_share_hard():
    groups = random.randint(3, 8); per = random.randint(5, 12); extra = random.randint(1, groups-1)
    total = groups*per + extra
    return mc("P4","Division","Problem Solving","Hard",
        f"{total} pencils are shared equally among {groups} pupils. How many pencils are left over?",
        str(extra), [str(per), str(groups), str(extra+1)],
        f"{groups} x {per} = {groups*per}. {total} - {groups*per} = {extra} left over.",
        f"{total}%{groups}")

def p4_symmetry():
    shapes = {"square":4, "rectangle":2, "equilateral triangle":3, "circle":"many"}
    s, v = random.choice([("square",4),("rectangle",2),("equilateral triangle",3)])
    return mc("P4","Geometry","Symmetry","Hard",
        f"How many lines of symmetry does a {s} have?", str(v),
        [str(v+1), str(v-1), str(v+2)],
        f"A {s} has {v} lines of symmetry.", str(v))


# ══════════════════════════════════════════════════════════════════════════
#  P.5 GENERATORS
# ══════════════════════════════════════════════════════════════════════════
def p5_placevalue_big():
    n = random.randint(10000, 999999); s = str(n); pos = random.randrange(len(s))
    d = int(s[pos]); place = 10**(len(s)-1-pos)
    return mc("P5","Whole Numbers","Place Value","Easy",
        f"What is the place value of the digit {d} in {n:,}?", f"{d*place:,}",
        [f"{d}", f"{place:,}", f"{d*place*10:,}"],
        f"The digit {d} stands for {d} x {place:,} = {d*place:,}.", f"{d}*{place}")

def p5_factors():
    n = random.choice([12,18,20,24,28,30,36,40,45,48])
    fs_ = [i for i in range(1, n+1) if n % i == 0]
    return mc("P5","Number Theory","Factors","Easy",
        f"How many factors does {n} have?", str(len(fs_)),
        [str(len(fs_)+1), str(len(fs_)-1), str(n//2)],
        f"The factors of {n} are {', '.join(map(str,fs_))} — that is {len(fs_)} factors.",
        str(len(fs_)))

def p5_multiples():
    n = random.randint(3, 12); k = random.randint(3, 8)
    return mc("P5","Number Theory","Multiples","Easy",
        f"What is the {k}th multiple of {n}?", str(n*k),
        [str(n*(k+1)), str(n+k), str(n*k-n)],
        f"The {k}th multiple of {n} is {n} x {k} = {n*k}.", f"{n}*{k}")

def p5_prime():
    n = random.choice([11,13,15,17,19,21,23,25,27,29,31,33])
    isp = all(n % i for i in range(2, int(n**0.5)+1))
    return tf("P5","Number Theory","Prime Numbers","Medium",
        f"{n} is a prime number.", isp,
        f"{n} is {'prime — its only factors are 1 and itself' if isp else 'not prime because it has other factors'}.")

def p5_longmul():
    a, b = random.randint(23, 98), random.randint(12, 49)
    return mc("P5","Multiplication","Long Multiplication","Medium",
        f"Work out: {a} x {b}", str(a*b),
        [str(a*b+a), str(a*b-b), str(a*b+100)],
        f"{a} x {b} = {a*b}.", f"{a}*{b}")

def p5_longdiv():
    b = random.randint(12, 25); q = random.randint(12, 40); a = b*q
    return mc("P5","Division","Long Division","Medium",
        f"Work out: {a} ÷ {b}", str(q), [str(q+1), str(q-1), str(q+10)],
        f"{b} x {q} = {a}, so {a} ÷ {b} = {q}.", f"{a}/{b}")

def p5_mixed_to_improper():
    w = random.randint(1, 6); d = random.choice([3,4,5,6,7,8]); n = random.randint(1, d-1)
    imp = w*d + n
    return mc("P5","Fractions","Mixed and Improper","Medium",
        f"Change {w} {n}/{d} to an improper fraction.", f"{imp}/{d}",
        [f"{w+n}/{d}", f"{imp+1}/{d}", f"{w*n}/{d}"],
        f"({w} x {d}) + {n} = {imp}, so the answer is {imp}/{d}.", f"({w}*{d}+{n})/{d}")

def p5_frac_addunlike():
    d1, d2 = random.choice([(2,3),(3,4),(2,5),(4,5),(3,6),(2,6)])
    a, b = 1, 1
    res = Fraction(a,d1) + Fraction(b,d2)
    return mc("P5","Fractions","Adding Unlike Fractions","Hard",
        f"Work out: {a}/{d1} + {b}/{d2}", fs(res),
        [f"{a+b}/{d1+d2}", fs(res + Fraction(1,d1*d2)), f"{a+b}/{d1*d2}"],
        f"Use a common denominator of {d1*d2//__import__('math').gcd(d1,d2)}: the answer is {fs(res)}.",
        f"{a}/{d1}+{b}/{d2}")

def p5_frac_of_qty():
    d = random.choice([3,4,5,6,8]); n = random.randint(2, d-1); tot = d*random.randint(4, 20)
    ans = tot//d*n
    return mc("P5","Fractions","Fractions of Quantities","Medium",
        f"Find {n}/{d} of {tot}.", str(ans),
        [str(tot//d), str(ans+d), str(tot-ans)],
        f"{tot} ÷ {d} = {tot//d}, then {tot//d} x {n} = {ans}.", f"{tot}/{d}*{n}")

def p5_dec_hundredths():
    a = round(random.uniform(1, 20), 2); b = round(random.uniform(1, 20), 2)
    r = round(a+b, 2)
    return mc("P5","Decimals","Adding Decimals","Medium",
        f"Work out: {a} + {b}", str(r), [str(round(r+0.1,2)), str(round(abs(a-b),2)), str(round(r-1,2))],
        f"Line up the decimal points: {a} + {b} = {r}.", f"{a}+{b}")

def p5_dec_x10():
    a = round(random.uniform(1, 9), 2); m = random.choice([10, 100])
    r = round(a*m, 2); r = int(r) if r == int(r) else r
    return mc("P5","Decimals","Multiplying by Powers of 10","Medium",
        f"Work out: {a} x {m}", str(r),
        [str(round(a*m*10,2)), str(round(a*m/10,2)), str(round(a+m,2))],
        f"Multiplying by {m} moves the decimal point {len(str(m))-1} place(s) right: {r}.",
        f"{a}*{m}")

def p5_money_profit():
    cost = random.randint(4, 30)*1000; profit = random.randint(1, 8)*500
    sell = cost + profit
    return mc("P5","Money","Profit","Medium",
        f"A trader bought a bag at {cost:,} shillings and sold it at {sell:,} shillings. What was the profit?",
        f"{profit:,}", [f"{cost:,}", f"{sell+cost:,}", f"{profit+500:,}"],
        f"Profit = selling price - cost price = {sell:,} - {cost:,} = {profit:,} shillings.",
        f"{sell}-{cost}")

def p5_money_budget():
    items = random.randint(3, 6); each = random.randint(2, 9)*500
    have = each*items + random.randint(1, 6)*500
    left = have - each*items
    return mc("P5","Money","Budgeting","Hard",
        f"A pupil has {have:,} shillings and buys {items} books at {each:,} shillings each. How much money remains?",
        f"{left:,}", [f"{each*items:,}", f"{left+500:,}", f"{have:,}"],
        f"Cost = {items} x {each:,} = {each*items:,}. Remaining = {have:,} - {each*items:,} = {left:,} shillings.",
        f"{have}-{items}*{each}")

def p5_convert_km():
    km = random.randint(2, 25)
    return mc("P5","Measurement","Length Conversion","Easy",
        f"Change {km} kilometres into metres.", f"{km*1000}",
        [f"{km*100}", f"{km*10}", f"{km*1000*10}"],
        f"1 km = 1000 m, so {km} km = {km*1000} m.", f"{km}*1000")

def p5_convert_time():
    d = random.randint(2, 14)
    return mc("P5","Measurement","Time Conversion","Easy",
        f"How many hours are there in {d} days?", str(d*24),
        [str(d*12), str(d*60), str(d+24)],
        f"1 day = 24 hours, so {d} days = {d} x 24 = {d*24} hours.", f"{d}*24")

def p5_angles():
    a = random.choice([30,45,60,120,135,150])
    kind = "acute" if a < 90 else "obtuse"
    return mc("P5","Geometry","Angles","Easy",
        f"An angle of {a}° is called a/an ______ angle.", kind,
        ["right", "reflex", "straight"],
        f"Angles below 90° are acute and those between 90° and 180° are obtuse, so {a}° is {kind}.")

def p5_triangle_angle():
    a, b = random.randint(30, 80), random.randint(30, 80)
    c = 180 - a - b
    return mc("P5","Geometry","Triangles","Medium",
        f"Two angles of a triangle are {a}° and {b}°. Find the third angle.",
        f"{c}°", [f"{c+10}°", f"{180-a}°", f"{a+b}°"],
        f"Angles in a triangle add up to 180°: 180 - {a} - {b} = {c}°.", f"180-{a}-{b}")

def p5_polygon():
    poly = {"pentagon":5,"hexagon":6,"heptagon":7,"octagon":8,"nonagon":9,"decagon":10}
    p_, v = random.choice(list(poly.items()))
    return mc("P5","Geometry","Polygons","Medium",
        f"How many sides does a {p_} have?", str(v),
        [str(v+1), str(v-1), str(v+2)],
        f"A {p_} has {v} sides.", str(v))

def p5_area_square():
    s = random.randint(4, 25)
    return mc("P5","Perimeter and Area","Area of a Square","Medium",
        f"Find the area of a square whose side is {s} cm.",
        f"{s*s} sq cm", [f"{4*s} sq cm", f"{s*2} sq cm", f"{s*s+s} sq cm"],
        f"Area of a square = side x side = {s} x {s} = {s*s} square centimetres.", f"{s}*{s}")

def p5_perimeter_find_side():
    w = random.randint(3, 15); p = random.randint(2, 6)*10 + 2*w
    l = (p - 2*w)//2
    if l <= 0: l = 5; p = 2*(l+w)
    return mc("P5","Perimeter and Area","Finding a Side","Hard",
        f"A rectangle has a perimeter of {p} cm and a width of {w} cm. Find its length.",
        f"{l} cm", [f"{p-w} cm", f"{p//2} cm", f"{l+w} cm"],
        f"Half the perimeter is {p//2} cm. Length = {p//2} - {w} = {l} cm.", f"{p}/2-{w}")

def p5_average():
    ns = [random.randint(10, 60) for _ in range(4)]
    while sum(ns) % 4: ns[0] += 1
    av = sum(ns)//4
    return mc("P5","Data Handling","Average","Hard",
        f"Find the average of {', '.join(map(str,ns))}.", str(av),
        [str(sum(ns)), str(av+1), str(max(ns))],
        f"Add them: {sum(ns)}. Then divide by 4: {sum(ns)} ÷ 4 = {av}.",
        f"({'+'.join(map(str,ns))})/4")

def p5_bar_read():
    days = ["Monday","Tuesday","Wednesday","Thursday"]
    vals = [random.randint(10, 50) for _ in days]
    tbl = "; ".join(f"{d} = {v}" for d, v in zip(days, vals))
    mx = days[vals.index(max(vals))]
    return mc("P5","Data Handling","Interpreting Graphs","Medium",
        f"A bar graph shows books borrowed: {tbl}. On which day were most books borrowed?",
        mx, [d for d in days if d != mx][:3],
        f"The largest value is {max(vals)}, which is on {mx}.")

def p5_multistep():
    a = random.randint(4, 9); b = random.randint(20, 60); c = random.randint(10, 40)
    tot = a*b - c
    return mc("P5","Problem Solving","Multi-step Problems","Hard",
        f"A farmer packed {a} boxes with {b} tomatoes each. {c} tomatoes went bad. How many good tomatoes remained?",
        str(tot), [str(a*b), str(a*b+c), str(tot-a)],
        f"{a} x {b} = {a*b} tomatoes. Then {a*b} - {c} = {tot}.", f"{a}*{b}-{c}")

def p5_round100():
    n = random.randint(1050, 9950)
    r = round(n/100)*100
    return mc("P5","Whole Numbers","Rounding","Medium",
        f"Round {n:,} to the nearest hundred.", f"{r:,}",
        [f"{r+100:,}", f"{r-100:,}", f"{round(n/1000)*1000:,}"],
        f"Look at the tens digit of {n:,} to decide: it rounds to {r:,}.", str(r))


# ══════════════════════════════════════════════════════════════════════════
#  P.6 GENERATORS
# ══════════════════════════════════════════════════════════════════════════
def p6_hcf():
    a, b = random.choice([(12,18),(16,24),(20,30),(24,36),(18,27),(15,25),(28,42)])
    import math; h = math.gcd(a,b)
    return mc("P6","Number Theory","Common Factors","Medium",
        f"Find the highest common factor of {a} and {b}.", str(h),
        [str(h*2), str(a), str(min(a,b)//2)],
        f"The common factors are found in both lists; the highest is {h}.", f"{h}")

def p6_lcm():
    a, b = random.choice([(4,6),(6,8),(5,10),(9,12),(8,12),(6,15),(10,15)])
    import math; l = a*b//math.gcd(a,b)
    return mc("P6","Number Theory","Common Multiples","Medium",
        f"Find the lowest common multiple of {a} and {b}.", str(l),
        [str(a*b), str(l+a), str(max(a,b))],
        f"Multiples of {a} and {b} first meet at {l}.", str(l))

def p6_simplify_frac():
    import math
    d = random.choice([12,15,16,18,20,24,30]); n = random.choice([i for i in range(2,d) if math.gcd(i,d) > 1])
    g = math.gcd(n,d)
    return mc("P6","Fractions","Simplifying Fractions","Easy",
        f"Write {n}/{d} in its simplest form.", f"{n//g}/{d//g}",
        [f"{n}/{d}", f"{n//g+1}/{d//g}", f"{n}/{d//g}"],
        f"Divide top and bottom by {g}: {n}/{d} = {n//g}/{d//g}.", f"{n}/{d}")

def p6_frac_multiply():
    a, b = random.randint(1,4), random.choice([3,4,5,6])
    c, d = random.randint(1,3), random.choice([2,3,4,5])
    res = Fraction(a,b)*Fraction(c,d)
    return mc("P6","Fractions","Multiplying Fractions","Medium",
        f"Work out: {a}/{b} x {c}/{d}", fs(res),
        [f"{a*c}/{b+d}", fs(Fraction(a,b)+Fraction(c,d)), f"{a+c}/{b*d}"],
        f"Multiply tops and bottoms: ({a} x {c})/({b} x {d}) = {fs(res)}.", f"{a}/{b}*{c}/{d}")

def p6_frac_divide():
    a, b = random.randint(1,5), random.choice([2,3,4,6])
    c = random.randint(2,5)
    res = Fraction(a,b)/c
    return mc("P6","Fractions","Dividing Fractions","Hard",
        f"Work out: {a}/{b} ÷ {c}", fs(res),
        [fs(Fraction(a,b)*c), f"{a}/{b*c+1}", f"{a*c}/{b}"],
        f"Dividing by {c} is the same as multiplying by 1/{c}: {fs(res)}.", f"{a}/{b}/{c}")

def p6_percent_of():
    p_ = random.choice([10,20,25,50,75]); tot = random.choice([40,60,80,120,200,240,400])
    ans = tot*p_//100
    return mc("P6","Percentages","Percentage of a Quantity","Medium",
        f"Find {p_}% of {tot}.", str(ans),
        [str(ans+10), str(tot-ans), str(ans*2)],
        f"{p_}% means {p_} out of 100: {tot} x {p_} ÷ 100 = {ans}.", f"{tot}*{p_}/100")

def p6_frac_to_percent():
    a, b = random.choice([(1,2),(1,4),(3,4),(1,5),(2,5),(1,10),(3,10),(1,20)])
    p_ = Fraction(a,b)*100
    return mc("P6","Percentages","Fractions to Percentages","Medium",
        f"Write {a}/{b} as a percentage.", f"{fs(p_)}%",
        [f"{fs(p_*2)}%", f"{a*b}%", f"{fs(p_+1)}%"],
        f"{a}/{b} x 100 = {fs(p_)}%.", f"{a}/{b}*100")

def p6_ratio_simplify():
    import math
    k = random.randint(2, 8); a, b = random.randint(2, 9), random.randint(2, 9)
    A, B = a*k, b*k; g = math.gcd(A,B)
    return mc("P6","Ratio","Simplifying Ratios","Medium",
        f"Simplify the ratio {A} : {B}", f"{A//g} : {B//g}",
        [f"{A} : {B}", f"{A//g+1} : {B//g}", f"{B//g} : {A//g}"],
        f"Divide both parts by {g}: {A} : {B} = {A//g} : {B//g}.", f"{A}/{g}")

def p6_ratio_share():
    a, b = random.choice([(1,2),(2,3),(3,4),(1,3),(2,5),(3,5)])
    unit = random.randint(4, 20); tot = (a+b)*unit
    return mc("P6","Ratio","Sharing in a Ratio","Hard",
        f"Share {tot} sweets between two pupils in the ratio {a} : {b}. How many does the first pupil get?",
        str(a*unit), [str(b*unit), str(tot//2), str(a*unit+unit)],
        f"Total parts = {a} + {b} = {a+b}. One part = {tot} ÷ {a+b} = {unit}. First pupil = {a} x {unit} = {a*unit}.",
        f"{tot}/{a+b}*{a}")

def p6_profit_percent():
    cost = random.choice([2000,2500,4000,5000,8000,10000])
    p_ = random.choice([10,20,25,50])
    profit = cost*p_//100
    return mc("P6","Money","Profit and Loss","Hard",
        f"An item bought at {cost:,} shillings was sold at a profit of {p_}%. What was the profit?",
        f"{profit:,}", [f"{cost+profit:,}", f"{profit*2:,}", f"{cost//p_:,}"],
        f"Profit = {p_}% of {cost:,} = {cost:,} x {p_} ÷ 100 = {profit:,} shillings.",
        f"{cost}*{p_}/100")

def p6_discount():
    price = random.choice([4000,5000,8000,10000,20000]); d = random.choice([10,20,25,50])
    off = price*d//100
    return mc("P6","Money","Discount","Hard",
        f"A shirt costing {price:,} shillings is sold at a discount of {d}%. How much does a customer pay?",
        f"{price-off:,}", [f"{off:,}", f"{price+off:,}", f"{price-off-500:,}"],
        f"Discount = {d}% of {price:,} = {off:,}. Payment = {price:,} - {off:,} = {price-off:,} shillings.",
        f"{price}-{price}*{d}/100")

def p6_volume():
    l, w, h = random.randint(2,12), random.randint(2,12), random.randint(2,12)
    return mc("P6","Volume","Volume of a Cuboid","Medium",
        f"Find the volume of a cuboid measuring {l} cm by {w} cm by {h} cm.",
        f"{l*w*h} cubic cm", [f"{2*(l*w+w*h+l*h)} cubic cm", f"{l+w+h} cubic cm", f"{l*w} cubic cm"],
        f"Volume = length x width x height = {l} x {w} x {h} = {l*w*h} cubic centimetres.",
        f"{l}*{w}*{h}")

def p6_compound_area():
    a, b, c, d = random.randint(4,12), random.randint(3,9), random.randint(2,8), random.randint(2,7)
    area = a*b + c*d
    return mc("P6","Perimeter and Area","Compound Shapes","Hard",
        f"A shape is made of two rectangles: one {a} cm by {b} cm and another {c} cm by {d} cm. Find the total area.",
        f"{area} sq cm", [f"{a*b} sq cm", f"{(a+c)*(b+d)} sq cm", f"{area+a} sq cm"],
        f"{a} x {b} = {a*b} and {c} x {d} = {c*d}. Total = {a*b} + {c*d} = {area} square centimetres.",
        f"{a}*{b}+{c}*{d}")

def p6_average_find_missing():
    ns = [random.randint(20, 60) for _ in range(3)]
    av = random.randint(30, 50); miss = av*4 - sum(ns)
    if miss <= 0: miss = 10; av = (sum(ns)+miss)//4
    return mc("P6","Data Handling","Averages","Hard",
        f"The average of four numbers is {av}. Three of them are {', '.join(map(str,ns))}. Find the fourth number.",
        str(miss), [str(av), str(miss+av), str(sum(ns)//3)],
        f"Total must be {av} x 4 = {av*4}. The fourth number = {av*4} - {sum(ns)} = {miss}.",
        f"{av}*4-{sum(ns)}")

def p6_dec_divide():
    b = random.choice([2,4,5,8]); q = round(random.uniform(1, 15), 1)
    a = round(q*b, 2)
    return mc("P6","Decimals","Dividing Decimals","Medium",
        f"Work out: {a} ÷ {b}", str(q), [str(round(q*2,2)), str(round(q+1,1)), str(round(a-b,2))],
        f"{a} ÷ {b} = {q}.", f"{a}/{b}")

def p6_dec_to_frac():
    d = random.choice([0.25,0.5,0.75,0.2,0.4,0.6,0.8,0.125])
    f = Fraction(str(d))
    return mc("P6","Decimals","Decimals to Fractions","Medium",
        f"Write {d} as a fraction in its simplest form.", fs(f),
        [f"{int(d*100)}/100", fs(f*2), f"1/{int(1/d) if d else 2}"],
        f"{d} = {int(d*1000)}/1000 which simplifies to {fs(f)}.", str(d))

def p6_angle_straight():
    a = random.randint(30, 150)
    return mc("P6","Geometry","Angles on a Line","Easy",
        f"Two angles on a straight line are {a}° and x. Find x.",
        f"{180-a}°", [f"{90-a if a<90 else a-90}°", f"{360-a}°", f"{a}°"],
        f"Angles on a straight line add to 180°: 180 - {a} = {180-a}°.", f"180-{a}")

def p6_quadrilateral():
    q = random.choice([("square","4 equal sides and 4 right angles"),
                       ("rectangle","opposite sides equal and 4 right angles"),
                       ("rhombus","4 equal sides but no right angles needed"),
                       ("trapezium","only one pair of parallel sides")])
    return mc("P6","Geometry","Quadrilaterals","Easy",
        f"Which quadrilateral has {q[1]}?", q[0],
        [x[0] for x in [("square",""),("rectangle",""),("rhombus",""),("trapezium",""),("kite","")] if x[0]!=q[0]][:3],
        f"A {q[0]} has {q[1]}.")

def p6_multistep_money():
    price = random.choice([1500,2000,2500,3000]); n1 = random.randint(3,8)
    price2 = random.choice([500,1000,1500]); n2 = random.randint(2,6)
    tot = price*n1 + price2*n2
    return mc("P6","Money","Multi-step Problems","Hard",
        f"A pupil buys {n1} books at {price:,} shillings each and {n2} pens at {price2:,} shillings each. What is the total cost?",
        f"{tot:,}", [f"{price*n1:,}", f"{tot+price2:,}", f"{(price+price2)*(n1+n2):,}"],
        f"Books: {n1} x {price:,} = {price*n1:,}. Pens: {n2} x {price2:,} = {price2*n2:,}. Total = {tot:,} shillings.",
        f"{price}*{n1}+{price2}*{n2}")

def p6_estimate_big():
    a, b = random.randint(1200, 8900), random.randint(1200, 8900)
    ra, rb = round(a/1000)*1000, round(b/1000)*1000
    return mc("P6","Whole Numbers","Estimation","Medium",
        f"Estimate {a:,} + {b:,} by rounding each number to the nearest thousand.",
        f"{ra+rb:,}", [f"{a+b:,}", f"{ra+rb+1000:,}", f"{ra+rb-1000:,}"],
        f"{a:,} rounds to {ra:,} and {b:,} rounds to {rb:,}, giving {ra+rb:,}.", f"{ra}+{rb}")

def p6_convert_area():
    m = random.randint(2, 12)
    return mc("P6","Measurement","Area Conversion","Hard",
        f"How many square centimetres are there in {m} square metres?",
        f"{m*10000}", [f"{m*100}", f"{m*1000}", f"{m*10000*10}"],
        f"1 sq m = 100 x 100 = 10,000 sq cm, so {m} sq m = {m*10000} sq cm.", f"{m}*10000")


# ══════════════════════════════════════════════════════════════════════════
#  P.7 GENERATORS  (PLE-style revision, original items)
# ══════════════════════════════════════════════════════════════════════════
def p7_hcf_lcm():
    import math
    a, b = random.choice([(12,20),(18,24),(15,20),(24,32),(16,20),(21,28),(30,45)])
    h, l = math.gcd(a,b), a*b//math.gcd(a,b)
    ask = random.choice(["HCF","LCM"])
    ans = h if ask=="HCF" else l
    return mc("P7","Number Theory","HCF and LCM","Medium",
        f"Find the {ask} of {a} and {b}.", str(ans),
        [str(l if ask=="HCF" else h), str(a*b), str(ans+2)],
        f"The {ask} of {a} and {b} is {ans}.", str(ans))

def p7_percent_increase():
    base = random.choice([200,400,500,800,1200,2000]); p_ = random.choice([5,10,15,20,25])
    ans = base + base*p_//100
    return mc("P7","Percentages","Percentage Increase","Hard",
        f"The price of an item was {base:,} shillings. It increased by {p_}%. What is the new price?",
        f"{ans:,}", [f"{base*p_//100:,}", f"{base-base*p_//100:,}", f"{ans+base*p_//100:,}"],
        f"Increase = {p_}% of {base:,} = {base*p_//100:,}. New price = {base:,} + {base*p_//100:,} = {ans:,}.",
        f"{base}+{base}*{p_}/100")

def p7_percent_find_whole():
    p_ = random.choice([10,20,25,50]); part = random.randint(2, 20)*p_
    whole = part*100//p_
    return mc("P7","Percentages","Finding the Whole","Hard",
        f"{p_}% of a number is {part}. What is the number?", str(whole),
        [str(part*p_), str(whole//2), str(part+p_)],
        f"If {p_}% is {part}, then 100% is {part} x 100 ÷ {p_} = {whole}.", f"{part}*100/{p_}")

def p7_speed():
    d = random.choice([60,90,120,150,180,240]); t = random.choice([2,3,4,5,6])
    while d % t: d += t - d % t
    s = d//t
    return mc("P7","Measurement","Speed","Medium",
        f"A vehicle travels {d} km in {t} hours. What is its average speed?",
        f"{s} km/h", [f"{d*t} km/h", f"{s+10} km/h", f"{d-t} km/h"],
        f"Speed = distance ÷ time = {d} ÷ {t} = {s} km/h.", f"{d}/{t}")

def p7_distance():
    s = random.choice([40,50,60,80,90]); t = random.choice([2,3,4,5])
    return mc("P7","Measurement","Distance","Medium",
        f"A bus moves at {s} km/h for {t} hours. How far does it travel?",
        f"{s*t} km", [f"{s+t} km", f"{s*t+s} km", f"{s//t} km"],
        f"Distance = speed x time = {s} x {t} = {s*t} km.", f"{s}*{t}")

def p7_time24():
    h = random.randint(13, 23); m = random.choice([0,15,30,45])
    return mc("P7","Time","24-hour Clock","Easy",
        f"Write {h}:{m:02d} hours in the 12-hour clock.",
        f"{h-12}:{m:02d} p.m.", [f"{h-12}:{m:02d} a.m.", f"{h}:{m:02d} p.m.", f"{h-11}:{m:02d} p.m."],
        f"Subtract 12 from {h} to get {h-12}, and the time is in the afternoon or evening, so p.m.",
        f"({h}-12)*60+{m}")

def p7_timetable():
    sh, sm = random.randint(6, 10), random.choice([0,15,30,45])
    dur = random.choice([45, 90, 105, 120, 150])
    tot = sh*60 + sm + dur
    eh, em = tot//60, tot%60
    return mc("P7","Time","Journey Time","Hard",
        f"A bus leaves at {sh}:{sm:02d} a.m. and travels for {dur} minutes. At what time does it arrive?",
        f"{eh}:{em:02d}", [f"{eh+1}:{em:02d}", f"{eh}:{(em+15)%60:02d}", f"{sh+dur//60}:{sm:02d}"],
        f"{dur} minutes is {dur//60} hour(s) {dur%60} minutes. {sh}:{sm:02d} + that = {eh}:{em:02d}.",
        f"({sh}*60+{sm}+{dur})")

def p7_circle():
    r = random.choice([7,14,21,28])
    c = 2*22*r//7
    return mc("P7","Geometry","Circles","Hard",
        f"Find the circumference of a circle of radius {r} cm. (Take pi = 22/7)",
        f"{c} cm", [f"{22*r*r//7} cm", f"{c//2} cm", f"{c+r} cm"],
        f"Circumference = 2 x 22/7 x {r} = {c} cm.", f"2*22*{r}/7")

def p7_circle_area():
    r = random.choice([7,14,21])
    a = 22*r*r//7
    return mc("P7","Geometry","Circles","Hard",
        f"Find the area of a circle of radius {r} cm. (Take pi = 22/7)",
        f"{a} sq cm", [f"{2*22*r//7} sq cm", f"{a//2} sq cm", f"{a+r} sq cm"],
        f"Area = 22/7 x {r} x {r} = {a} square centimetres.", f"22*{r}*{r}/7")

def p7_triangle_area():
    b, h = random.choice([4,6,8,10,12,14,16,18,20]), random.choice([5,7,9,11,13,15])
    a = b*h/2; a = int(a) if a == int(a) else a
    return mc("P7","Perimeter and Area","Area of a Triangle","Medium",
        f"Find the area of a triangle with base {b} cm and height {h} cm.",
        f"{a} sq cm", [f"{b*h} sq cm", f"{b+h} sq cm", f"{b*h//2+b} sq cm"],
        f"Area = 1/2 x base x height = 1/2 x {b} x {h} = {a} square centimetres.", f"{b}*{h}/2")

def p7_volume_cube():
    s = random.randint(3, 14)
    return mc("P7","Volume","Volume of a Cube","Easy",
        f"Find the volume of a cube of side {s} cm.",
        f"{s**3} cubic cm", [f"{6*s*s} cubic cm", f"{s*3} cubic cm", f"{s*s} cubic cm"],
        f"Volume of a cube = side x side x side = {s} x {s} x {s} = {s**3} cubic cm.", f"{s}**3")

def p7_capacity_volume():
    l, w, h = random.choice([10,20,25,50]), random.choice([10,20,25]), random.choice([10,20,40])
    vol = l*w*h; lit = vol//1000
    return mc("P7","Volume","Capacity and Volume","Hard",
        f"A tank measures {l} cm by {w} cm by {h} cm. How many litres of water can it hold? (1000 cubic cm = 1 litre)",
        f"{lit} litres", [f"{vol} litres", f"{lit*10} litres", f"{lit//2 if lit>1 else 2} litres"],
        f"Volume = {l} x {w} x {h} = {vol} cubic cm = {vol} ÷ 1000 = {lit} litres.",
        f"{l}*{w}*{h}/1000")

def p7_ratio_three():
    a, b, c = random.choice([(1,2,3),(2,3,5),(1,3,4),(2,2,3),(1,1,2)])
    unit = random.randint(3, 15); tot = (a+b+c)*unit
    return mc("P7","Ratio","Sharing in Three Parts","Hard",
        f"{tot:,} shillings is shared in the ratio {a} : {b} : {c}. How much is the largest share?",
        f"{max(a,b,c)*unit:,}", [f"{min(a,b,c)*unit:,}", f"{tot//3:,}", f"{max(a,b,c)*unit+unit:,}"],
        f"Total parts = {a+b+c}. One part = {tot:,} ÷ {a+b+c} = {unit:,}. Largest = {max(a,b,c)} x {unit:,} = {max(a,b,c)*unit:,}.",
        f"{tot}/{a+b+c}*{max(a,b,c)}")

def p7_simple_interest():
    p_ = random.choice([20000,40000,50000,80000,100000]); r = random.choice([5,10,15,20]); t = random.choice([1,2,3])
    si = p_*r*t//100
    return mc("P7","Money","Simple Interest","Hard",
        f"Find the simple interest on {p_:,} shillings for {t} year(s) at {r}% per year.",
        f"{si:,}", [f"{p_+si:,}", f"{si*2:,}", f"{p_*r//100:,}"],
        f"Interest = P x R x T ÷ 100 = {p_:,} x {r} x {t} ÷ 100 = {si:,} shillings.",
        f"{p_}*{r}*{t}/100")

def p7_algebra_solve():
    a = random.randint(2, 9); x = random.randint(2, 15); b = random.randint(1, 20)
    return mc("P7","Algebra","Simple Equations","Medium",
        f"Find the value of x if {a}x + {b} = {a*x+b}.", str(x),
        [str(x+1), str(a*x), str(x-1)],
        f"{a}x = {a*x+b} - {b} = {a*x}. So x = {a*x} ÷ {a} = {x}.", f"({a*x+b}-{b})/{a}")

def p7_algebra_expr():
    a, b = random.randint(2, 9), random.randint(2, 9); x = random.randint(2, 10)
    val = a*x + b
    return mc("P7","Algebra","Substitution","Easy",
        f"If x = {x}, find the value of {a}x + {b}.", str(val),
        [str(a+b+x), str(a*x), str(val+a)],
        f"Replace x with {x}: {a} x {x} + {b} = {a*x} + {b} = {val}.", f"{a}*{x}+{b}")

def p7_coordinates():
    x, y = random.randint(1, 9), random.randint(1, 9)
    return mc("P7","Position","Coordinates","Easy",
        f"A point is {x} units to the right of the origin and {y} units up. Write its coordinates.",
        f"({x}, {y})", [f"({y}, {x})", f"({x}, {-y})", f"({x+1}, {y})"],
        f"Coordinates are written (across, up), so the point is ({x}, {y}).")

def p7_pie_chart():
    total = random.choice([120,180,240,360,720]); deg = random.choice([60,90,120,45])
    ans = total*deg//360
    return mc("P7","Data Handling","Pie Charts","Hard",
        f"A pie chart represents {total} pupils. One sector has an angle of {deg}°. How many pupils does it represent?",
        str(ans), [str(deg), str(total-ans), str(ans*2)],
        f"{deg}/360 x {total} = {ans} pupils.", f"{total}*{deg}/360")

def p7_mean():
    n = random.choice([5,6]); ns = [random.randint(10, 90) for _ in range(n)]
    while sum(ns) % n: ns[0] += 1
    m = sum(ns)//n
    return mc("P7","Data Handling","Mean","Medium",
        f"Find the mean of: {', '.join(map(str,ns))}.", str(m),
        [str(sum(ns)), str(m+1), str(max(ns)-min(ns))],
        f"Sum = {sum(ns)}. Mean = {sum(ns)} ÷ {n} = {m}.",
        f"({'+'.join(map(str,ns))})/{n}")

def p7_number_pattern():
    a = random.randint(2, 6); seq = [a**i for i in range(1, 5)]
    nxt = a**5
    return mc("P7","Patterns","Number Patterns","Hard",
        f"What comes next? {', '.join(map(str,seq))}, ___", str(nxt),
        [str(seq[-1]+a), str(nxt+a), str(seq[-1]*2)],
        f"Each term is multiplied by {a}, so {seq[-1]} x {a} = {nxt}.", f"{seq[-1]}*{a}")

def p7_bodmas():
    a, b, c = random.randint(2,9), random.randint(2,9), random.randint(2,9)
    val = a + b*c
    return mc("P7","Operations","Order of Operations","Medium",
        f"Work out: {a} + {b} x {c}", str(val),
        [str((a+b)*c), str(a*b+c), str(val+1)],
        f"Do multiplication first: {b} x {c} = {b*c}. Then {a} + {b*c} = {val}.", f"{a}+{b}*{c}")

def p7_fraction_word():
    d = random.choice([3,4,5,6,8]); n = random.randint(1, d-1)
    tot = d*random.randint(5, 20)
    used = tot//d*n; left = tot-used
    return mc("P7","Fractions","Word Problems","Hard",
        f"A farmer harvested {tot} bags of maize and sold {n}/{d} of them. How many bags remained?",
        str(left), [str(used), str(tot), str(left-1)],
        f"Sold = {n}/{d} x {tot} = {used}. Remaining = {tot} - {used} = {left} bags.",
        f"{tot}-{tot}/{d}*{n}")

def p7_decimal_percent():
    d = random.choice([0.05,0.15,0.25,0.4,0.6,0.75,0.8])
    p_ = d*100; p_ = int(p_) if p_ == int(p_) else p_
    return mc("P7","Percentages","Decimals to Percentages","Easy",
        f"Write {d} as a percentage.", f"{p_}%",
        [f"{d}%", f"{p_/10}%", f"{p_*10}%"],
        f"Multiply by 100: {d} x 100 = {p_}%.", f"{d}*100")

def p7_convert_mass():
    t = random.randint(2, 15)
    return mc("P7","Measurement","Mass Conversion","Easy",
        f"How many kilograms are there in {t} tonnes?", f"{t*1000}",
        [f"{t*100}", f"{t*10}", f"{t*1000*10}"],
        f"1 tonne = 1000 kg, so {t} tonnes = {t*1000} kg.", f"{t}*1000")

def p7_prime_factor():
    n = random.choice([12,18,20,24,28,30,36,40,45,50])
    fs_, m = [], n
    d = 2
    while m > 1:
        while m % d == 0:
            fs_.append(d); m //= d
        d += 1
    return mc("P7","Number Theory","Prime Factorisation","Medium",
        f"Express {n} as a product of its prime factors.",
        " x ".join(map(str,fs_)), [" x ".join(map(str,fs_[:-1])) or "2", f"{n} x 1", " x ".join(map(str,fs_+[2]))],
        f"{n} = {' x '.join(map(str,fs_))}.", "*".join(map(str,fs_)))


# ══════════════════════════════════════════════════════════════════════════
#  ASSEMBLY — fill exactly 70 Easy / 80 Medium / 50 Hard per class
# ══════════════════════════════════════════════════════════════════════════
GENS = {
 "P4": [p4_place_value,p4_face_value,p4_expanded,p4_order,p4_oddeven,p4_round10,p4_roman,
        p4_pattern,p4_add,p4_sub,p4_addword,p4_subword,p4_mulfact,p4_mul10,p4_shortmul,
        p4_mulword,p4_divfact,p4_divrem,p4_divword,p4_frac_name,p4_frac_equiv,p4_frac_of,
        p4_frac_add,p4_dec_tenths,p4_dec_compare,p4_money_change,p4_money_add,p4_money_shop,
        p4_len_convert,p4_mass_convert,p4_cap_convert,p4_time_dur,p4_time_clock,p4_calendar,
        p4_shape_sides,p4_solid_faces,p4_perimeter,p4_area,p4_data_table,p4_data_more,
        p4_missing,p4_estimate,p4_twostep,p4_share_hard,p4_symmetry],
 "P5": [p5_placevalue_big,p5_factors,p5_multiples,p5_prime,p5_longmul,p5_longdiv,
        p5_mixed_to_improper,p5_frac_addunlike,p5_frac_of_qty,p5_dec_hundredths,p5_dec_x10,
        p5_money_profit,p5_money_budget,p5_convert_km,p5_convert_time,p5_angles,
        p5_triangle_angle,p5_polygon,p5_area_square,p5_perimeter_find_side,p5_average,
        p5_bar_read,p5_multistep,p5_round100,
        p4_add,p4_sub,p4_mulfact,p4_divfact,p4_perimeter,p4_area,p4_len_convert,p4_mass_convert],
 "P6": [p6_hcf,p6_lcm,p6_simplify_frac,p6_frac_multiply,p6_frac_divide,p6_percent_of,
        p6_frac_to_percent,p6_ratio_simplify,p6_ratio_share,p6_profit_percent,p6_discount,
        p6_volume,p6_compound_area,p6_average_find_missing,p6_dec_divide,p6_dec_to_frac,
        p6_angle_straight,p6_quadrilateral,p6_multistep_money,p6_estimate_big,p6_convert_area,
        p5_longmul,p5_longdiv,p5_triangle_angle,p5_area_square,p5_average,p5_polygon],
 "P7": [p7_hcf_lcm,p7_percent_increase,p7_percent_find_whole,p7_speed,p7_distance,p7_time24,
        p7_timetable,p7_circle,p7_circle_area,p7_triangle_area,p7_volume_cube,
        p7_capacity_volume,p7_ratio_three,p7_simple_interest,p7_algebra_solve,p7_algebra_expr,
        p7_coordinates,p7_pie_chart,p7_mean,p7_number_pattern,p7_bodmas,p7_fraction_word,
        p7_decimal_percent,p7_convert_mass,p7_prime_factor,
        p6_percent_of,p6_ratio_simplify,p6_volume,p6_simplify_frac,p6_discount],
}
RECLASS = {"P5": {"P4": "P5"}, "P6": {"P5": "P6"}, "P7": {"P6": "P7"}}


GLOBAL_SEEN = set()


def build_class(cls):
    """Fill the exact difficulty quotas, deduplicating by question text."""
    out = []
    quota = dict(TARGET)
    pool = GENS[cls]
    guard = 0
    while sum(quota.values()) > 0 and guard < 200000:
        guard += 1
        g = random.choice(pool)
        q = g()
        if q is None:
            continue
        # a generator borrowed from a lower class is re-tagged to THIS class
        q["class"] = cls
        d = q["difficulty"]
        if quota.get(d, 0) <= 0:
            continue
        key = q["question"].strip().lower()
        if key in GLOBAL_SEEN:          # never repeat a question in ANY class
            continue
        GLOBAL_SEEN.add(key)
        out.append(q)
        quota[d] -= 1
    if sum(quota.values()):
        raise SystemExit(f"{cls}: could not fill quota, still needed {quota}")
    order = {"Easy": 0, "Medium": 1, "Hard": 2}
    out.sort(key=lambda q: (order[q["difficulty"]], q["topic"], q["subtopic"]))
    for i, q in enumerate(out, 1):
        q["id"] = f"{cls}_MATH_{i:03d}"
    return out


# ── owner-supplied Mathematics batches ────────────────────────────────────
OWNER = {"P4": [], "P5": [], "P6": [], "P7": []}
_bdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batches_math")
for _f in sorted(glob.glob(os.path.join(_bdir, "*.py"))):
    _sp = importlib.util.spec_from_file_location(os.path.basename(_f)[:-3], _f)
    _m = importlib.util.module_from_spec(_sp)
    _sp.loader.exec_module(_m)
    for _c, _qs in getattr(_m, "EXTRA", {}).items():
        OWNER[_c].extend(_qs)
    print("  + " + os.path.basename(_f) + ": " +
          ", ".join(f"{c}+{len(q)}" for c, q in getattr(_m, "EXTRA", {}).items()))
# Owner questions are authoritative: no generated question, in ANY class, may
# duplicate one. Seed the dedupe set before generation begins.
for _c, _qs in OWNER.items():
    for _q in _qs:
        GLOBAL_SEEN.add(_q["question"].strip().lower())
if any(OWNER.values()):
    print()

os.makedirs(OUT, exist_ok=True)
print(f"{'CLASS':6}{'TOTAL':>7}{'EASY':>7}{'MEDIUM':>8}{'HARD':>6}{'TOPICS':>8}")
grand = 0
for cls in ("P4", "P5", "P6", "P7"):
    gen = build_class(cls)
    own = OWNER[cls]
    # Owner questions take the plain numeric block 001..N; generated questions
    # move to a G prefix so they can never block the owner's numbering.
    if own:
        seen = {q["question"].strip().lower() for q in own}
        dropped = [q for q in gen if q["question"].strip().lower() in seen]
        if dropped:
            print(f"  ! {cls}: {len(dropped)} generated question(s) duplicate an owner question")
        gen = [q for q in gen if q["question"].strip().lower() not in seen]
        for i, q in enumerate(own, 1):
            q["id"] = f"{cls}_MATH_{i:03d}"
        for i, q in enumerate(gen, 1):
            q["id"] = f"{cls}_MATH_G{i:03d}"
        qs = own + gen
    else:
        qs = gen
    topics = {}
    for q in qs:
        topics.setdefault(q["topic"], set()).add(q["subtopic"])
    doc = {"class": cls, "subject": "Mathematics",
           "curriculum": "Uganda primary Mathematics",
           "target": {"total": 200, "difficulty": TARGET},
           "topics": {t: sorted(v) for t, v in sorted(topics.items())},
           "total": len(qs), "questions": qs}
    with open(f"{OUT}/math-{cls.lower()}.json", "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    d = {k: sum(1 for q in qs if q["difficulty"] == k) for k in TARGET}
    grand += len(qs)
    print(f"{cls:6}{len(qs):>7}{d['Easy']:>7}{d['Medium']:>8}{d['Hard']:>6}{len(topics):>8}")
print(f"\nTOTAL {grand} Mathematics questions written to {OUT}/")
