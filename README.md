# BUS5001 Assessment 3 – RPA, AI and Cloud-Enabled ESG Analytics

Evidence repository for the Assessment 3 report (La Trobe University, BUS5001 Cloud Platforms).
It contains the build artefacts and experiment logs referenced in the report.

| Folder | Report section | Contents |
|---|---|---|
| [`Q1_dialogflow/`](Q1_dialogflow/) | Q1 – ESG chatbot | Source for the *EcoAssist ESG Incident Reporter* Dialogflow CX agent (`build_agent.py`), the generated JSON agent package, test transcripts and screenshots |
| [`Q3_llm_triage/`](Q3_llm_triage/) | Q3 – LLM message triage | Original and revised prompts, test messages, gold labels, Gemini run log (`outputs/llm_runs.jsonl`), rule-based and Hugging Face zero-shot baselines, comparison tables and chart; [`PIPELINE.md`](Q3_llm_triage/PIPELINE.md) documents configuration, transformations and calculations |
| [`Q4_notebooklm/`](Q4_notebooklm/) | Q4 – NotebookLM evaluation | Test protocol, experiment log of each NotebookLM (Gemini Notebook) feature test, screenshots and scores |
| [`diagrams/`](diagrams/) | All | Report diagrams (conversation map, cloud workflow, attack chain, shared responsibility, Azure architecture) and the script that draws them |

## Reproducing the Q3 experiment

```bash
pip install google-genai transformers torch pandas matplotlib tabulate
set GEMINI_API_KEY=<your key>          # never commit keys
python Q3_llm_triage/run_llm.py        # Gemini, original + revised prompts (3 runs each)
python Q3_llm_triage/baselines.py      # rule-based + HF zero-shot (runs locally)
python Q3_llm_triage/compare.py        # accuracy table, consistency check, chart
```

## Rebuilding the Q1 agent

```bash
python Q1_dialogflow/build_agent.py    # writes agent_package/ and EcoAssist_agent.zip
```
Restore the zip in the Conversational Agents console: Agents ▸ ⋮ ▸ Restore ▸ Upload.

## Responsible-use notes

* All test messages are **synthetic**; names and phone numbers in message M6 are fictitious.
* No API keys or credentials are stored in this repository.
* Generative AI assistance was used in preparing parts of this work, as declared in the
  AI acknowledgement submitted with the report.
