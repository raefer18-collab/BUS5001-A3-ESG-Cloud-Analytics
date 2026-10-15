# Q4 – NotebookLM (Gemini Notebook) evaluation log

* **Date:** 11 October 2026 (free personal Google account)
* **Tool:** NotebookLM, now branded *Gemini Notebook* (notebook.google.com)
* **Scenario:** a postgraduate business-analytics student preparing a briefing for a *governance
  workshop on ESG reporting frameworks and Australia's mandatory climate-related disclosures*.
* **Notebook:** "Environmental, Social, and Governance Frameworks" (title auto-generated)

## Sources added (website import)

| # | Source | Result |
|---|---|---|
| S1 | ASIC – Sustainability reporting (asic.gov.au/regulatory-resources/sustainability-reporting/) | Imported |
| S2 | GRI – Standards (globalreporting.org/standards/) | Imported |
| S3 | Wikipedia – Environmental, social, and governance | Imported (URL with commas had to be percent-encoded) |
| S4 | Wikipedia – Greenhouse Gas Protocol | **Failed to import** (red error icon), yet later counted as "4 sources" by Reports |

## Feature tests

| ID | Feature | Prompt / setting | Observed output | Accuracy & relevance | Evidence |
|---|---|---|---|---|---|
| E1 | Source ingestion + auto summary | 4 URLs | Notebook titled and summarised in ~15 s; one source failed silently except for an icon | Summary accurate to sources; failure easy to miss | `01_sources_ingested_auto_summary.jpg` |
| E2 | Grounded Q&A with citations | "Which Australian entities must prepare climate-related sustainability reports, when do requirements start, which standard? Short table." | Table: Chapter 2M entities meeting s292A thresholds; AASB S2; part of annual report; ASIC oversight – each with numbered citations | Correct but **incomplete**: Group 1/2/3 phase-in dates (1 Jan 2025 / 1 Jul 2026 / 1 Jul 2027) were not in the imported ASIC page text, and the tool said so explicitly and offered web search | `02_qa_citations_table.jpg`, `03_qa_acknowledges_gap.jpg` |
| E3 | Hallucination probe (out-of-scope) | "According to the sources, what were La Trobe University's Scope 1 and 2 emissions in 2024, and which GRI standard number covers emissions?" | Declined: "Your sources do not contain…"; described GRI modular structure with citations; offered web search | **No hallucination**. Did not supply GRI 305 because it was absent from sources – correct grounding behaviour, though a student may expect the answer | `04_hallucination_test_refusal.jpg` |
| E4 | Mind Map | Topic: "ESG reporting frameworks and Australian climate disclosure requirements, for a governance workshop" | 4 branches (ESG Reporting Frameworks, Australian Climate Disclosure, Core Dimensions of ESG, Challenges & Verification), expandable to sub-nodes (Legal Foundation, Reporting Content, Administration & Purpose) | Relevant structure; node labels generic; useful for orientation not detail | `05_mind_map.jpg` |
| E5 | Quiz | Default settings | 12 multiple-choice questions with an explanation for every option | Q1 ("ESG first prominence" – answer: 2004 *Who Cares Wins*) correct; skewed to history/trivia rather than workshop needs | `06_quiz_with_explanations.jpg` |
| E6 | Flashcards | Default ("Standard") setting | **57 cards** generated – far more than needed for a briefing; e.g. "What does ESG stand for…", answer cards such as Friedman's critique without naming him | Accurate but many low-level recall items; card answers sometimes lack context | `07_flashcards.jpg`, `08_flashcard_answer.jpg` |
| E7 | Audio Overview | Brief format; focus: "explain ESG reporting, GRI vs AASB S2, greenwashing risks to business-analytics students" | 1 min 45 s two-host podcast titled "How Regulators Catch Corporate…" generated in ~3 min | Content must be verified by listening; no inline citations in audio – evidence quality hardest to check | `09_audio_overview.jpg` |
| E8 | Reports – Briefing doc | Document format, Briefing-doc template, no custom topic | "Executive Briefing: The Architecture, Global Trajectory, and Emerging Challenges of ESG Investing" – exec summary cites US$30 trillion AUM by 2023 and 84 % of sustainable fund assets in Europe | Well structured but **drifted** to investing (from Wikipedia) rather than the governance/disclosure focus; figures are from a tertiary source and need verification | `10_briefing_doc_report.jpg` |

## Observations on limits and platform behaviour

* Usage meter ("AI usage") replaced per-feature limits; heavy Studio use consumes the 5-hour allowance.
* Studio items generate asynchronously in a queue (quiz and flashcards ~1 min, audio ~3 min).
* Source-count inconsistency: chat used 3 sources, Reports reported 4 (including the failed import).
* All outputs carry the banner "Gemini Notebook can make mistakes, so double-check it."

## Scoring (1 = poor, 5 = excellent)

| Feature | Accuracy | Relevance | Workflow usefulness | Risk (5 = low risk) |
|---|---|---|---|---|
| Grounded Q&A + citations | 5 | 4 | 5 | 4 |
| Mind map | 4 | 4 | 3 | 4 |
| Quiz | 4 | 3 | 4 | 3 |
| Flashcards | 4 | 3 | 3 | 3 |
| Audio overview | n/v* | 4 | 4 | 2 |
| Briefing doc report | 4 | 2 | 4 | 2 |

\* not verified – audio content requires manual review by listening.
