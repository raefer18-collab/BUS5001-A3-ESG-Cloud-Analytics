# Q3 – LLM-based ESG message triage

| File | Purpose |
|---|---|
| `data/messages.json` | 8 synthetic ESG messages (the 5 from the brief + 3 stress tests: personal data & safety, mixed praise/issue, prompt injection & conduct) |
| `data/gold_labels.json` | Analyst reference labels (primary issue) |
| `prompts/original_prompt.txt` | Prompt template supplied in the brief |
| `prompts/revised_prompt.txt` | Improved template: role, security rules, controlled vocabularies, urgency decision rules, team mapping, PII redaction, evidence quote, confidence, human-review flag, one-shot example |
| `run_llm.py` | Calls Google Gemini (`gemini-3.8-flash`, temperature 0, JSON mode); 1 run original + 3 runs revised per message; retries on 429/503 |
| `baselines.py` | Rule-based keyword classifier + Hugging Face zero-shot (`MoritzLaurer/deberta-v3-base-zeroshot-v2.0`, local CPU) |
| `compare.py` | Scores each approach against gold labels; checks run-to-run consistency; draws chart |
| `outputs/llm_runs.jsonl` | **Full experiment log** – every call with timestamp, model, latency, raw response |
| `outputs/llm_results.json`, `outputs/baseline_results.json` | Parsed results |
| `outputs/comparison.md`, `.csv`, `accuracy_chart.png` | Comparison tables and chart |

## Headline results (n = 8)

| Approach | Category | Urgency | Team |
|---|---|---|---|
| Gemini – revised prompt | 100 % | 100 % | 100 % |
| Rule-based | 87.5 % | 75 % | 87.5 % |
| HF zero-shot | 87.5 % | 50 % | 87.5 % |

Gemini revised-prompt outputs were identical across 3 runs for all 8 messages. The original prompt
produced valid JSON but with inconsistent structure (array vs object), free-text categories and team
names, and rated message M6 (name + phone number) as LOW sensitivity.

**Caveats:** gold labels were written by the analyst using the same urgency rules embedded in the
revised prompt, and the keyword rules were written with sight of the messages, so both favour their
designers; n = 8 is far too small for production claims. See report section Q3(b)–(c).
