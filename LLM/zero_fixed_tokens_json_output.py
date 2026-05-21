# pip install openai pandas openpyxl

import pandas as pd
from openai import OpenAI
import time
import json
import re

df = pd.read_excel("task 6.xlsx")

client = OpenAI(
    base_url="https://text2sparql-vllm.tools.eurecom.fr/v1",
    api_key="EMPTY"
)

MODEL = "openai/gpt-oss-120b"
MAX_OUTPUT_TOKENS = 16384

def build_prompt(row):
    return f"""
Analyze the property-level differences between these two SPARQL queries.

Use ONLY the question, the two queries, and the available property labels.

Question:
{row["Question"]}

Ground-truth SPARQL query:
{row["SPARQL query"]}

Predicted SPARQL query:
{row["Predicted SPARQL query"]}

Available property labels:
{row["All_properties_with_labels"]}

Return ONLY valid JSON.
Do NOT use markdown.
Do NOT add text before or after the JSON.

The JSON must have exactly this structure:

{{
  "ground_truth_properties": ["Pxx (label)", "Pyy (label)"],
  "predicted_properties": ["Pxx (label)", "Pzz (label)"],
  "missing_properties": ["properties present in ground truth but absent from prediction"],
  "extra_properties": ["properties present in prediction but absent from ground truth"],
  "effect_on_result": "short explanation of how the missing/extra properties affect or do not affect the result"
}}

Rules:
- Extract Wikidata properties such as P31, P279, P625, etc. from both queries.
- Use labels when available, for example: P31 (instance of).
- Missing = present in ground truth but absent from prediction.
- Extra = present in prediction but absent from ground truth.
- If a list is empty, return [].
- The output must be valid JSON parsable by Python json.loads().
"""

def build_short_retry_prompt(row):
    return f"""
Return ONLY valid JSON.

Question:
{row["Question"]}

Ground-truth SPARQL query:
{row["SPARQL query"]}

Predicted SPARQL query:
{row["Predicted SPARQL query"]}

Available property labels:
{row["All_properties_with_labels"]}

Required JSON format:
{{
  "ground_truth_properties": [],
  "predicted_properties": [],
  "missing_properties": [],
  "extra_properties": [],
  "effect_on_result": ""
}}
"""

def extract_from_response(response):
    data = response.model_dump()
    final_text_parts = []

    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    final_text_parts.append(c.get("text", ""))

    return "\n".join(final_text_parts).strip()

def clean_json_text(text):
    if text is None:
        return ""

    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0).strip()

    return text

def parse_json_output(text):
    try:
        return json.loads(clean_json_text(text))
    except Exception:
        return None

def call_llm(prompt):
    response = client.responses.create(
        model=MODEL,
        input=prompt,
        reasoning={"effort": "medium"},
        temperature=0.0,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )

    return extract_from_response(response)

def get_json_interpretation(row, retries=3):
    last_error = ""
    best_raw = ""

    for _ in range(retries):
        try:
            raw = call_llm(build_prompt(row))
            best_raw = raw

            parsed = parse_json_output(raw)
            if parsed is not None:
                return parsed

            last_error = "Invalid JSON"

        except Exception as e:
            last_error = str(e)

        time.sleep(1)

    for _ in range(retries):
        try:
            raw = call_llm(build_short_retry_prompt(row))
            best_raw = raw

            parsed = parse_json_output(raw)
            if parsed is not None:
                return parsed

            last_error = "Invalid JSON after fallback"

        except Exception as e:
            last_error = str(e)

        time.sleep(1)

    return {
        "ground_truth_properties": [],
        "predicted_properties": [],
        "missing_properties": [],
        "extra_properties": [],
        "effect_on_result": f"ERROR: Failed after retries - {last_error}. Raw output: {best_raw}"
    }

def list_to_string(value):
    if isinstance(value, list):
        return ", ".join(str(x) for x in value) if value else "None"
    return str(value) if value else "None"

def format_interpretation(parsed):
    return f"""Ground-truth properties:
- {list_to_string(parsed.get("ground_truth_properties", []))}

Predicted properties:
- {list_to_string(parsed.get("predicted_properties", []))}

Missing properties:
- {list_to_string(parsed.get("missing_properties", []))}

Extra properties:
- {list_to_string(parsed.get("extra_properties", []))}

Effect on result:
- {parsed.get("effect_on_result", "")}"""

outputs = []

for i, row in df.iterrows():
    print(f"{i+1}/{len(df)} - {row['test_id']}")

    parsed = get_json_interpretation(row)
    outputs.append(format_interpretation(parsed))

    time.sleep(0.5)

df["zero_shot_query_only_interpretation"] = outputs

df.to_excel("task6_zero_shot_query_only_output_fixed.xlsx", index=False)

print("Done - task6_zero_shot_query_only_output_fixed.xlsx")