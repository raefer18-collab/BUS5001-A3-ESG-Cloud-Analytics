# Q3 pipeline: configuration, transformations and calculations

## Stages

| Stage | Script | Configuration | Transformation | Output |
|---|---|---|---|---|
| 1 Input | – | 8 messages (`id`, `channel`, `text`); gold labels (category, urgency, team) | – | `data/messages.json`, `data/gold_labels.json` |
| 2 LLM | `run_llm.py` | `gemini-3.8-flash`, temperature 0, `response_mime_type=application/json`; 1 original + 3 revised runs/message; 1 s pause; back-off 5·2ⁱ s on 429/503, max 6 attempts | Placeholders `{message_id}`, `{message}` filled by string replace; `json.loads` with code-fence clean-up fallback | `outputs/llm_runs.jsonl` (32 rows), `outputs/llm_results.json` |
| 3 Baselines | `baselines.py` | Rules: ordered regex, first match wins, defaults OTHER/LOW. Zero-shot: `MoritzLaurer/deberta-v3-base-zeroshot-v2.0`, CPU, template "This message is about {}." | Descriptive labels → category codes; top label taken; team from shared mapping | `outputs/baseline_results.json` |
| 4 Scoring | `compare.py` | Fields: category, urgency, team; n = 8 | Gemini → primary issue (highest urgency CRITICAL>HIGH>MEDIUM>LOW); exact match vs gold | `outputs/comparison.csv/.md`, `accuracy_chart.png` |

## Calculations

* Agreement(approach, field) = matches ÷ 8 × 100
* Consistency(message) = TRUE if the set of (category, urgency) across the 3 revised runs has one element

| Approach | Category | Urgency | Team |
|---|---|---|---|
| Gemini revised | 8/8 = 100 % | 8/8 = 100 % | 8/8 = 100 % |
| Rule-based | 7/8 = 87.5 % | 6/8 = 75 % | 7/8 = 87.5 % |
| HF zero-shot | 7/8 = 87.5 % | 4/8 = 50 % | 7/8 = 87.5 % |

## Proposed Azure production configuration (report Q3(d))

| Component | Trigger / schedule | Key settings |
|---|---|---|
| Logic App `ingest-email` | Outlook *When a new email arrives (V3)*, poll 1 min | normalise to envelope; sender hashed |
| Service Bus `esg-inbound` | – | lock 5 min, max delivery 5 → DLQ, duplicate detection 10 min |
| Function `triage` | Service Bus trigger, max concurrency 8 | managed identity; PII redaction → Prompt Shields → Azure OpenAI (json_schema, temp 0) → schema validation → rule override |
| Cosmos DB `esg-triage/messages` | written by Function | partition `/received_month`, TTL 2 years, no unredacted text |
| Logic App `route-ticket` | Cosmos change feed | ServiceNow ticket; Teams/SMS alert for CRITICAL/HIGH |
| Fabric pipeline | every 15 min | Bronze (raw) → Silver (one row per issue) → Gold (daily KPIs) → Power BI |
| Azure ML evaluation | weekly Mon 03:00 AEST + on prompt change | block release if CRITICAL recall < 100 % or category accuracy < 90 % |
