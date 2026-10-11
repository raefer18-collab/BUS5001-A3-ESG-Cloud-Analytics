"""Two non-LLM baselines for ESG message triage.

1. Rule-based keyword classifier (transparent, deterministic).
2. Hugging Face zero-shot classifier (MoritzLaurer/deberta-v3-base-zeroshot-v2.0, run locally).

Usage:  python baselines.py   -> writes outputs/baseline_results.json
"""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
ZS_MODEL = "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"

CATEGORY_RULES = [  # first match wins
    ("HAZARDOUS_MATERIALS", r"chemical|solvent|spill|toxic|asbestos|hazard|drum|fumes|dizzy"),
    ("GOVERNANCE_CONDUCT", r"harass|discriminat|bully|comments about|misconduct|fraud|bribe|unsafe raising"),
    ("ACCESSIBILITY", r"accessib|wheelchair|ramp|lift|elevator|disab"),
    ("WATER", r"water|leak|tap|flood|pipe"),
    ("ENERGY", r"air ?con|lights?|lighting|heating|energy|power|electric"),
    ("WASTE_RECYCLING", r"recycl|bin|waste|rubbish|litter|dump"),
    ("PROCUREMENT_SUPPLIER", r"supplier|vendor|procure|purchas|contract"),
]
URGENCY_RULES = [
    ("CRITICAL", r"dizzy|injur|hurt|fire|toxic|fumes|chemical|solvent|unsafe|asap|emergency"),
    ("HIGH", r"all morning|running|flood|blocked|two days|disab|harass|discriminat"),
    ("MEDIUM", r"again|overnight|contaminat|policy|not meet|broken"),
]
TEAMS = {
    "WATER": "Facilities Maintenance", "FACILITIES_GENERAL": "Facilities Maintenance",
    "ENERGY": "Energy & Sustainability Office", "WASTE_RECYCLING": "Waste & Recycling Services",
    "HAZARDOUS_MATERIALS": "Health, Safety & Environment (HSE)",
    "ACCESSIBILITY": "Accessibility & Inclusion Team", "PROCUREMENT_SUPPLIER": "Sustainable Procurement",
    "GOVERNANCE_CONDUCT": "People & Culture / Integrity (confidential)", "OTHER": "ESG Service Desk",
}
ZS_LABELS = {
    "water leak or water waste": "WATER",
    "energy waste such as lights or air conditioning": "ENERGY",
    "recycling bins or waste contamination": "WASTE_RECYCLING",
    "hazardous chemicals or toxic materials": "HAZARDOUS_MATERIALS",
    "accessibility barrier for people with disabilities": "ACCESSIBILITY",
    "supplier or procurement compliance": "PROCUREMENT_SUPPLIER",
    "workplace harassment, discrimination or misconduct": "GOVERNANCE_CONDUCT",
    "general building maintenance": "FACILITIES_GENERAL",
}
ZS_URGENCY = {
    "immediate danger to people's health or safety": "CRITICAL",
    "urgent problem causing ongoing damage": "HIGH",
    "recurring problem that should be fixed soon": "MEDIUM",
    "minor issue or general feedback": "LOW",
}


def first_match(rules, text, default):
    for label, pattern in rules:
        if re.search(pattern, text, re.I):
            return label
    return default


def rule_based(text):
    cat = first_match(CATEGORY_RULES, text, "OTHER")
    return {"issue_category": cat, "urgency": first_match(URGENCY_RULES, text, "LOW"),
            "recommended_team": TEAMS[cat]}


def main():
    from transformers import pipeline

    messages = json.load(open(os.path.join(HERE, "data/messages.json"), encoding="utf-8"))
    clf = pipeline("zero-shot-classification", model=ZS_MODEL, device=-1)
    results = {}
    for m in messages:
        start = time.time()
        cat = clf(m["text"], list(ZS_LABELS), hypothesis_template="This message is about {}.")
        urg = clf(m["text"], list(ZS_URGENCY), hypothesis_template="This message describes a {}.")
        zs_cat = ZS_LABELS[cat["labels"][0]]
        results[m["id"]] = {
            "rule_based": rule_based(m["text"]),
            "zero_shot": {
                "issue_category": zs_cat, "category_score": round(cat["scores"][0], 3),
                "category_ranking": [(ZS_LABELS[l], round(s, 3)) for l, s in zip(cat["labels"], cat["scores"])],
                "urgency": ZS_URGENCY[urg["labels"][0]], "urgency_score": round(urg["scores"][0], 3),
                "recommended_team": TEAMS[zs_cat], "latency_s": round(time.time() - start, 2),
            },
        }
        print(m["id"], results[m["id"]]["rule_based"]["issue_category"], "|", zs_cat)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "baseline_results.json"), "w", encoding="utf-8") as f:
        json.dump({"zero_shot_model": ZS_MODEL, "results": results}, f, indent=2)
    print("Saved outputs/baseline_results.json")


if __name__ == "__main__":
    main()
