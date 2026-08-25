#!/usr/bin/env python3
"""Shared helpers for authoring SST practice questions.

IDs are NOT written by hand — build_practice_bank.py renumbers every class
sequentially (P4_SST_001 … P4_SST_200), so batches can never collide.
"""

def rec(cls, topic, sub, diff, qtype, render, question, explanation,
        options=None, correct=None, answers=None, pairs=None):
    return {
        "id": None, "class": cls, "subject": "SST",
        "topic": topic, "subtopic": sub,
        "difficulty": diff, "questionType": qtype, "renderAs": render,
        "question": question, "options": options, "correctAnswer": correct,
        "answers": answers, "pairs": pairs, "explanation": explanation,
    }


def M(cls, topic, sub, diff, q, opts, correct, expl, qtype="multiple_choice"):
    """Multiple choice — four options, exactly one correct."""
    return rec(cls, topic, sub, diff, qtype, "mcq", q, expl,
               options=[f"{L}. {t}" for L, t in zip("ABCD", opts)], correct=correct)


def T(cls, topic, sub, diff, q, correct, expl):
    """True / False."""
    return rec(cls, topic, sub, diff, "true_false", "tf", q, expl,
               options=["A. True", "B. False"], correct=correct)


def F(cls, topic, sub, diff, q, answers, expl, qtype="fill_blank"):
    """Typed answer. `answers` lists every spelling accepted."""
    return rec(cls, topic, sub, diff, qtype, "fill", q, expl, answers=answers)


def P(cls, topic, sub, diff, q, pairs, expl):
    """Matching — tap a chip to pair each item."""
    return rec(cls, topic, sub, diff, "matching", "match", q, expl, pairs=pairs)
