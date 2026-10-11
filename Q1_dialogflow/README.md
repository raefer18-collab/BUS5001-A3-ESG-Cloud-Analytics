# Q1 – EcoAssist ESG Incident Reporter (Dialogflow CX)

**Use case:** sustainability incident reporting assistant – staff report water leaks, energy waste,
recycling contamination, hazardous spills and accessibility barriers; the bot collects structured
details, triages risk, routes to the right team and escalates emergencies or sensitive matters to people.

* Platform: Google Cloud Conversational Agents (Dialogflow CX), project `cloudplatformAs3`, region `global`
* Build approach: the agent is defined as code in [`build_agent.py`](build_agent.py), which generates a
  Dialogflow CX **JSON package** (`agent_package/`, zipped as `EcoAssist_agent.zip`) that is restored into
  the console (Agent ▸ Restore). This keeps the design version-controlled and reproducible.

## Components

| Component | Implementation |
|---|---|
| Intents (7 + 2 defaults) | `report.incident`, `get.guidance`, `check.status`, `escalate.human`, `confirm.yes`, `confirm.no`, `end.conversation` (+ Default Welcome / Negative) |
| Custom entities (5) | `incident_type` (map, 6 values + synonyms, fuzzy), `risk_level`, `contact_pref`, `guidance_topic`, `report_ref` (regex `ESG-?[A-Za-z0-9]{4,8}`) |
| System entities | `@sys.any` (location), `@sys.email` (redacted in logs) |
| Pages (12) | Incident Details (form), Emergency Escalation, Contact Preference, Collect Contact, Confirm Report, Route To Team, Report Submitted, Anything Else, Sustainability Guidance, Check Report Status, Human Handover, End Conversation |
| Branching | Conditional routes on `risk_level` (immediate danger → emergency), `contact_pref` (consent), `incident_type` × `risk_level` (team + priority) |
| Fallback | Flow-level `sys.no-match-1/2/3` (escalating help → human), `sys.no-input-default`, per-parameter reprompt handlers |
| Endpoints | Report reference generated with `$sys.func.UPPER($sys.func.MID($sys.func.UUID(),1,6))`; live-agent hand-off payload; End Session |

## Test transcripts (simulator, 11 Oct 2026)

| # | Scenario | Path exercised | Result |
|---|---|---|---|
| T1 | Water leak, ongoing, wants updates | report.incident (entity pre-filled) → form → contact → email → confirm → Route To Team | Ref ESG-808279, Facilities Maintenance (Plumbing), **HIGH** |
| T2 | Nonsense input, then chemical spill with fumes | no-match-1 → report → risk = immediate danger | **Emergency Escalation**, HSE, CRITICAL, ref ESG-898D44 |
| T3 | Battery disposal question, then anonymous energy-waste report, then "no" | guidance → report → anonymous → confirm.no | Guidance answer; parameters cleared and re-collected |
| T4 | Three unrecognised inputs | no-match-1 → no-match-2 → no-match-3 | Hand-off to ESG Service Desk |
| T5 | Status check + confidential conduct issue | check.status (regex entity) → escalate.human | Status IN PROGRESS; confidential hand-off |

Screenshots are in the report (Figures Q1-x).
