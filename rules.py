# ══════════════════════════════════════════════════════════
# rules.py — Sentiment Scoring Rules for ParText
# ══════════════════════════════════════════════════════════

# ── Pattern-based rules (checked first, high priority) ──
PATTERN_RULES = [

    # ── STRONG POSITIVE (score +4) ──
    (r"highly recommend|must buy|worth every penny|value for money", 4),
    (r"excellent product|superb product|loved the product|very satisfied", 4),
    (r"exceeded my expectations|beyond expectations|absolutely love it", 4),
    (r"five star|5 star|top notch|world class|outstanding quality", 4),
    (r"couldn't be happier|couldn't be more satisfied|best thing i ever bought", 4),
    (r"completely satisfied|100% satisfied|totally satisfied|fully satisfied", 4),

    # ── GOOD POSITIVE (score +3) ──
    (r"best purchase|works perfectly|awesome product|great quality", 3),
    (r"works great|works fine|working perfectly|works like a charm", 3),
    (r"solid product|reliable product|sturdy product|durable product", 3),
    (r"good value|great value|value for price|worth the price|worth the cost", 3),
    (r"superb quality|fantastic quality|brilliant product|impressive product", 3),
    (r"easy to use|very easy|user friendly|simple to set up|plug and play", 3),
    (r"highly durable|long lasting|built to last|excellent build quality", 3),

    # ── MILD POSITIVE (score +2) ──
    (r"good quality|nice product|happy with the product", 2),
    (r"fast delivery|quick delivery|delivered on time|early delivery|speedy delivery", 2),
    (r"as expected|met expectations|what i expected|exactly as described", 2),
    (r"good packaging|well packed|safely packed|secure packaging", 2),
    (r"looks good|feels good|good finish|nice finish|good build", 2),
    (r"satisfied with|happy with|pleased with|content with", 2),
    (r"good price|affordable price|reasonable price|budget friendly", 2),
    (r"works well|performing well|doing great|functioning well", 2),
    (r"quick response|good support|helpful support|great service", 2),
    (r"genuine product|original product|authentic product", 2),

    # ── STRONG NEGATIVE (score -4) ──
    (r"waste of money|do not buy|don't buy|not worth|very disappointed", -4),
    (r"worst product|poor quality|stopped working|defective product", -4),
    (r"complete waste|total waste|utter waste|money wasted|waste of time", -4),
    (r"worst experience|terrible experience|horrible experience|awful experience", -4),
    (r"absolutely terrible|absolutely horrible|absolutely useless|absolutely pathetic", -4),
    (r"never buy again|will never purchase|regret buying|biggest mistake", -4),
    (r"cheated|fraud|scam|counterfeit|duplicate product|fake item", -4),

    # ── BAD NEGATIVE (score -3) ──
    (r"bad experience|totally useless|very bad|extremely bad", -3),
    (r"damaged product|received damaged|fake product|broken product", -3),
    (r"not working|does not work|stopped working|completely dead|won't turn on", -3),
    (r"poor build|cheap quality|cheaply made|feels cheap|very flimsy", -3),
    (r"stopped functioning|failed after|broke after|died after|burnt out", -3),
    (r"misleading description|false description|not as advertised|wrong product sent", -3),
    (r"extremely disappointed|deeply disappointed|very let down|totally let down", -3),
    (r"pathetic quality|disgusting quality|horrible quality|terrible quality", -3),

    # ── MILD NEGATIVE (score -2) ──
    (r"late delivery|delivery was late|poor delivery|delayed delivery|very slow delivery", -2),
    (r"not as expected|did not meet expectations|below expectations|underwhelming", -2),
    (r"overpriced|too expensive|not worth the price|overcharged", -2),
    (r"poor packaging|damaged packaging|bad packaging|loose packaging", -2),
    (r"difficult to use|hard to use|confusing to use|not user friendly", -2),
    (r"minor issue|small problem|slight defect|minor defect|small issue", -2),
    (r"average product|mediocre product|nothing special|just okay|just ok", -2),
    (r"poor customer service|bad support|no response|ignored complaint", -2),
    (r"looks cheap|cheap look|feels plastic|feels hollow|very light weight", -2),
    (r"not durable|broke easily|fragile product|not sturdy|falls apart", -2),

    # ── PERFORMANCE SIGNALS ──
    (r"battery drains fast|poor battery|bad battery life|battery issue", -3),
    (r"excellent battery|long battery life|great battery|battery lasts long", 3),
    (r"heats up|overheating|gets very hot|too hot to touch", -3),
    (r"no heating issue|stays cool|does not heat|runs cool", 2),
    (r"loud noise|makes noise|rattling sound|weird sound|strange noise", -2),
    (r"silent operation|no noise|quiet motor|runs silently|whisper quiet", 2),
    (r"fast charging|charges quickly|quick charge|charges fast", 3),
    (r"slow charging|takes forever to charge|charging issue|won't charge", -3),
    (r"crystal clear|sharp display|excellent display|vibrant display|bright screen", 3),
    (r"blurry display|dim screen|poor display|bad screen quality|dull screen", -3),

    # ── AFTER SALES / RETURN / WARRANTY ──
    (r"easy return|hassle free return|smooth return|return accepted", 2),
    (r"return rejected|return denied|no return|difficult return|return issue", -3),
    (r"warranty honored|good warranty|claim accepted|warranty claim easy", 2),
    (r"warranty rejected|no warranty support|warranty issue|claim denied", -3),
]


# ── Word-level scores (applied after pattern check) ──
WORD_SCORES = {

    # ── Strong Positive (+3) ──
    "excellent":        3,
    "outstanding":      3,
    "superb":           3,
    "exceptional":      3,
    "fantastic":        3,
    "brilliant":        3,
    "extraordinary":    3,
    "flawless":         3,
    "phenomenal":       3,
    "magnificent":      3,

    # ── Good Positive (+2) ──
    "amazing":          2,
    "perfect":          2,
    "awesome":          2,
    "great":            2,
    "love":             2,
    "loved":            2,
    "best":             2,
    "satisfied":        2,
    "impressive":       2,
    "reliable":         2,
    "sturdy":           2,
    "durable":          2,
    "genuine":          2,
    "authentic":        2,
    "smooth":           2,
    "comfortable":      2,
    "convenient":       2,
    "efficient":        2,
    "effective":        2,

    # ── Mild Positive (+1) ──
    "good":             1,
    "nice":             1,
    "happy":            1,
    "fine":             1,
    "decent":           1,
    "ok":               1,
    "okay":             1,
    "works":            1,
    "useful":           1,
    "handy":            1,
    "affordable":       1,
    "fast":             1,
    "quick":            1,
    "clean":            1,
    "neat":             1,
    "solid":            1,
    "recommended":      1,
    "stylish":          1,
    "lightweight":      1,

    # ── Strong Negative (-3) ──
    "worst":           -3,
    "terrible":        -3,
    "horrible":        -3,
    "awful":           -3,
    "atrocious":       -3,
    "dreadful":        -3,
    "disgusting":      -3,
    "pathetic":        -3,
    "fraud":           -3,
    "scam":            -3,
    "fake":            -3,

    # ── Moderate Negative (-2) ──
    "useless":         -2,
    "hate":            -2,
    "hated":           -2,
    "poor":            -2,
    "waste":           -2,
    "disappointed":    -2,
    "disappointing":   -2,
    "defective":       -2,
    "damaged":         -2,
    "broken":          -2,
    "faulty":          -2,
    "failure":         -2,
    "failed":          -2,
    "overpriced":      -2,
    "flimsy":          -2,
    "fragile":         -2,
    "leaking":         -2,
    "scratched":       -2,
    "cracked":         -2,
    "melted":          -2,
    "burned":          -2,

    # ── Mild Negative (-1) ──
    "bad":             -1,
    "problem":         -1,
    "issue":           -1,
    "complaint":       -1,
    "cheap":           -1,
    "uncomfortable":   -1,
    "difficult":       -1,
    "confusing":       -1,
    "slow":            -1,
    "noisy":           -1,
    "heavy":           -1,
    "smell":           -1,
    "smells":          -1,
}


# ── Negation words (flip the score of the next word) ──
NEGATIONS = {
    "not", "no", "never", "none", "neither", "nor",
    "without", "barely", "hardly", "scarcely", "nothing",
    "cannot", "cant", "wont", "doesnt", "didnt",
    "isnt", "wasnt", "arent", "dont",
}


# ── Intensifier words (double the score of the next word) ──
INTENSIFIERS = {
    "very", "extremely", "really", "too", "so", "absolutely",
    "completely", "totally", "utterly", "highly", "incredibly",
    "insanely", "exceptionally", "remarkably", "super", "quite",
    "deeply", "severely", "terribly", "awfully", "genuinely",
}