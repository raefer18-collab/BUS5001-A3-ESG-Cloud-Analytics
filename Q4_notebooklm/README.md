# Q4 – NotebookLM (Gemini Notebook) feasibility evaluation

**Scenario:** a postgraduate business-analytics student preparing a governance-workshop briefing on ESG
reporting frameworks and Australia's mandatory climate-related disclosures (AASB S2).

| File | Contents |
|---|---|
| [`experiment_log.md`](experiment_log.md) | Sources added, test protocol, prompt/setting for every feature test (E1–E8), observed output, accuracy notes, scores |
| [`screenshots/`](screenshots/) | Evidence for each test, numbered to match the log (01–10) |

## Test protocol

1. One notebook, four web sources (ASIC, GRI, Wikipedia ESG, Wikipedia GHG Protocol – the last failed to import).
2. Each feature run once with default settings or the stated prompt (11 Oct 2026, free tier).
3. Every output screenshotted; factual claims checked against the cited source passage.
4. Two grounding probes: partially answerable (E2) and unanswerable from sources (E3).
5. Each capability scored 1–5 on accuracy, relevance, workflow usefulness and risk (5 = low risk).

## Evidence index

| ID | Feature | Screenshot |
|---|---|---|
| E1 | Source ingestion + auto summary | `01_sources_ingested_auto_summary.jpg` |
| E2 | Grounded Q&A with citations | `02_qa_citations_table.jpg`, `03_qa_acknowledges_gap.jpg` |
| E3 | Hallucination probe | `04_hallucination_test_refusal.jpg` |
| E4 | Mind map | `05_mind_map.jpg` |
| E5 | Quiz | `06_quiz_with_explanations.jpg` |
| E6 | Flashcards | `07_flashcards.jpg`, `08_flashcard_answer.jpg` |
| E7 | Audio overview | `09_audio_overview.jpg` |
| E8 | Reports – briefing doc | `10_briefing_doc_report.jpg` |

**Headline finding:** grounded Q&A was the most trustworthy capability (mean score 4.5/5) – it declined to
invent facts absent from its sources; Studio outputs (reports, quizzes) were useful but drifted in focus and
require verification (scores 3.0–3.75).
