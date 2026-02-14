import json
import re
from reasoning.llm_client import query_llm

def safe_parse(response):
    if not response:
        raise ValueError("Empty LLM response")

    # Extract JSON block
    json_match = re.search(r"\{.*\}", response, re.DOTALL)

    if not json_match:
        raise ValueError(f"No JSON found in response:\n{response}")

    json_text = json_match.group(0)

    # Clean invalid control characters
    json_text = json_text.replace("\n", " ")
    json_text = json_text.replace("\r", " ")
    json_text = json_text.replace("\t", " ")

    # Remove smart quotes (if any)
    json_text = json_text.replace("“", '"').replace("”", '"')

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode failed.\nExtracted:\n{json_text}\nError:{e}")


def bull_agent(evidence):
    prompt = f"""
You are a bullish equity analyst.

Based on the evidence below, provide:

1. A concise Bull Summary (max 5 sentences)
2. A Bull Score between 0 and 100

Return strictly valid JSON:
{{
  "bull_summary": "short summary paragraph",
  "bull_score": 0
}}

Do not include markdown.
Do not include backticks.
Start directly with {{ and end with }}.

Evidence:
{evidence}
"""
    raw = query_llm(prompt, max_tokens=350)
    return safe_parse(raw)


def bear_agent(evidence):
    prompt = f"""
You are a bearish equity analyst.

Based on the evidence below, provide:

1. A concise Bear Summary (max 5 sentences)
2. A Bear Score between 0 and 100

Return strictly valid JSON:
{{
  "bear_summary": "short summary paragraph",
  "bear_score": 0
}}

Do not include markdown.
Do not include backticks.
Start directly with {{ and end with }}.

Evidence:
{evidence}
"""
    raw = query_llm(prompt, max_tokens=350)
    return safe_parse(raw)

def judge_agent(bull_output, bear_output, score_label, final_score):
    prompt = f"""
You are a neutral portfolio manager.

Quantitative Metrics:
Bull Score: {bull_output.get("bull_score")}
Bear Score: {bear_output.get("bear_score")}
Final Score (Bull - Bear): {final_score}
Preliminary Decision (Score-Based): {score_label}

Bull Analysis:
{bull_output.get("bull_summary")}

Bear Analysis:
{bear_output.get("bear_summary")}

Your task:
1. Validate the score-based decision.
2. Provide a short 3–4 sentence final reasoning summary.
3. Confirm final Decision: BUY / HOLD / SELL.
4. Assign confidence: Low / Medium / High.

Return strict JSON:
{{
  "final_decision": "BUY/HOLD/SELL",
  "confidence": "Low/Medium/High",
  "final_summary": "text"
}}

Do not include markdown.
Start directly with {{ and end with }}.
"""
    raw = query_llm(prompt, max_tokens=350)
    return safe_parse(raw)

