import re
from rules import PATTERN_RULES, WORD_SCORES, NEGATIONS, INTENSIFIERS

def calculate_score(text):

    original_text = str(text)
    text = original_text.lower()
    score = 0

    # ---------------------------
    # Pattern Rules (High Priority)
    # ---------------------------
    for pattern, value in PATTERN_RULES:
        if re.search(pattern, text):
            score += value

    # ---------------------------
    # Word-Level Scoring
    # ---------------------------
    words = re.findall(r"\b\w+\b", text)

    negate = False
    boost = 1

    for word in words:

        if word in NEGATIONS:
            negate = True
            continue

        if word in INTENSIFIERS:
            boost = 2
            continue

        word_score = WORD_SCORES.get(word, 0)

        if negate:
            word_score *= -1
            negate = False

        score += word_score * boost
        boost = 1

    # ---------------------------
    # Sentiment Decision
    # ---------------------------
    if score > 1:
        sentiment = "Positive"
    elif score < -1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return (original_text[:80], score, sentiment)