"""Runs the original and revised ESG triage prompts through Google Gemini.

Each message is sent once with the original prompt and three times with the revised prompt
(temperature 0) so run-to-run consistency can be measured. Every call is appended to
outputs/llm_runs.jsonl with a timestamp, model name, latency and raw response.

Usage:  set GEMINI_API_KEY in the environment, then  python run_llm.py
"""
import datetime as dt
import json
import os
import sys
import time

from google import genai
from google.genai import errors, types

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]
REVISED_RUNS = 3


def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


def call(client, model, prompt, attempts=6):
    for i in range(attempts):
        start = time.time()
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"),
            )
            return resp.text, round(time.time() - start, 2)
        except errors.APIError as e:
            # 429 rate limit / 503 overloaded are transient: back off and retry.
            if e.code not in (429, 500, 503) or i == attempts - 1:
                raise
            wait = 5 * 2 ** i
            print(f"  {e.code} from API, retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)


def parse(text):
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        # The original prompt does not force a JSON object, so try stripping code fences.
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            return json.loads(cleaned), f"needed cleanup: {e}"
        except json.JSONDecodeError:
            return None, f"invalid JSON: {e}"


def pick_model(client):
    for m in MODELS:
        try:
            call(client, m, 'Return {"ok": true} as JSON.')
            return m
        except Exception as e:  # model not available for this key / region
            print(f"model {m} unavailable: {e}", file=sys.stderr)
    sys.exit("No Gemini model available - check GEMINI_API_KEY.")


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set.")
    client = genai.Client(api_key=key)
    model = pick_model(client)
    print("Using model:", model)

    messages = json.loads(load("data/messages.json"))
    original = load("prompts/original_prompt.txt")
    revised = load("prompts/revised_prompt.txt")
    os.makedirs(OUT, exist_ok=True)

    results = {}
    with open(os.path.join(OUT, "llm_runs.jsonl"), "a", encoding="utf-8") as log:
        for m in messages:
            jobs = [("original", 1, original.replace("{message}", m["text"]))]
            jobs += [("revised", i + 1, revised.replace("{message_id}", m["id"]).replace("{message}", m["text"]))
                     for i in range(REVISED_RUNS)]
            for variant, run, prompt in jobs:
                text, latency = call(client, model, prompt)
                parsed, note = parse(text)
                rec = {"timestamp": dt.datetime.now().isoformat(timespec="seconds"), "model": model,
                       "message_id": m["id"], "prompt_variant": variant, "run": run,
                       "latency_s": latency, "valid_json": parsed is not None, "parse_note": note,
                       "raw_response": text, "parsed": parsed}
                log.write(json.dumps(rec, ensure_ascii=False) + "\n")
                results.setdefault(m["id"], {}).setdefault(variant, []).append(parsed)
                print(f"{m['id']} {variant} run {run}: valid={parsed is not None} ({latency}s)")
                time.sleep(1)  # stay inside free-tier rate limits

    with open(os.path.join(OUT, "llm_results.json"), "w", encoding="utf-8") as f:
        json.dump({"model": model, "results": results}, f, indent=2, ensure_ascii=False)
    print("Saved outputs/llm_results.json")


if __name__ == "__main__":
    main()
