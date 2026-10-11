"""Compares Gemini (revised prompt) against the rule-based and zero-shot baselines.

Reads outputs/llm_results.json and outputs/baseline_results.json, scores each approach against
data/gold_labels.json, and writes:
  outputs/comparison.csv, outputs/comparison.md, outputs/accuracy_chart.png
"""
import collections
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
FIELDS = ["issue_category", "urgency", "recommended_team"]


def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return json.load(f)


def primary_issue(parsed):
    """Highest-urgency issue from a revised-prompt response."""
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    issues = (parsed or {}).get("issues") or []
    issues = sorted(issues, key=lambda i: order.get(i.get("urgency"), 9))
    return issues[0] if issues else {}


def main():
    gold = {k: v for k, v in load("data/gold_labels.json").items() if not k.startswith("_")}
    llm = load("outputs/llm_results.json")["results"]
    base = load("outputs/baseline_results.json")["results"]

    rows, consistency = [], {}
    for mid, g in gold.items():
        runs = [primary_issue(p) for p in llm[mid]["revised"]]
        # Consistency: do all revised-prompt runs agree on category and urgency?
        consistency[mid] = len({(r.get("issue_category"), r.get("urgency")) for r in runs}) == 1
        first = runs[0]
        n_issues = len((llm[mid]["revised"][0] or {}).get("issues") or [])
        for approach, pred in [("Gemini (revised prompt)", first),
                               ("Rule-based", base[mid]["rule_based"]),
                               ("HF zero-shot", base[mid]["zero_shot"])]:
            row = {"message_id": mid, "approach": approach}
            for f in FIELDS:
                row[f] = pred.get(f, "")
                row[f + "_correct"] = pred.get(f) == g[f]
            if approach.startswith("Gemini"):
                row["issues_found"] = n_issues
                row["human_review"] = first.get("human_review_required")
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "comparison.csv"), index=False)

    acc = df.groupby("approach")[[f + "_correct" for f in FIELDS]].mean().mul(100).round(1)
    acc.columns = ["Category %", "Urgency %", "Team %"]

    with open(os.path.join(OUT, "comparison.md"), "w", encoding="utf-8") as f:
        f.write("# Classification comparison against analyst gold labels\n\n")
        f.write(acc.to_markdown() + "\n\n")
        f.write("## Per-message predictions (category / urgency)\n\n")
        piv = df.assign(pred=df.issue_category + " / " + df.urgency).pivot(
            index="message_id", columns="approach", values="pred")
        piv.insert(0, "Gold", [f"{gold[m]['issue_category']} / {gold[m]['urgency']}" for m in piv.index])
        f.write(piv.to_markdown() + "\n\n")
        f.write("## Gemini run-to-run consistency (3 runs, temperature 0)\n\n")
        for mid, ok in consistency.items():
            f.write(f"- {mid}: {'consistent' if ok else 'INCONSISTENT'}\n")
    print(acc)
    print("Consistent messages:", sum(consistency.values()), "/", len(consistency))

    ax = acc.plot(kind="bar", figsize=(7, 4), color=["#2a6f97", "#61a5c2", "#a9d6e5"], rot=0)
    ax.set_ylabel("Agreement with gold labels (%)")
    ax.set_ylim(0, 105)
    ax.set_title("ESG message triage: LLM vs baselines (n=8 messages)")
    ax.legend(loc="lower right")
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "accuracy_chart.png"), dpi=200)


if __name__ == "__main__":
    main()
