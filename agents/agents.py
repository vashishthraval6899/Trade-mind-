import json
import re
from reasoning.llm_client import query_llm

def safe_parse(response):
    if not response:
        raise ValueError("Empty LLM response")

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned:\n{response[:300]}\nError:{e}")


def bull_agent(evidence):
    prompt = f"""
You are a bullish equity analyst.

Analyze the evidence and return ONLY strict JSON.

Requirements:
- bull_summary: max 120 words
- bull_score: integer 0-100

Return EXACT JSON:

{{
  "bull_summary": "...",
  "bull_score": 0
}}

No commentary. No markdown. No extra text.

Evidence:
{evidence[:4000]}
"""
    raw = query_llm(prompt, max_tokens=500)
    return safe_parse(raw)


def bear_agent(evidence):
    prompt = f"""
You are a bearish equity analyst.

Analyze the evidence and return ONLY strict JSON.

Requirements:
- bear_summary: max 120 words
- bear_score: integer 0-100

Return EXACT JSON:

{{
  "bear_summary": "...",
  "bear_score": 0
}}

No commentary. No markdown. No extra text.

Evidence:
{evidence[:4000]}
"""
    raw = query_llm(prompt, max_tokens=500)
    return safe_parse(raw)


def judge_agent(bull_output, bear_output, score_label, final_score):
    prompt = f"""
You are a neutral portfolio manager.

Inputs:
Bull Score: {bull_output.get("bull_score")}
Bear Score: {bear_output.get("bear_score")}
Final Score: {final_score}
Preliminary Decision: {score_label}

Bull Summary:
{bull_output.get("bull_summary")}

Bear Summary:
{bear_output.get("bear_summary")}

Return ONLY strict JSON:

{{
  "final_decision": "BUY/HOLD/SELL",
  "confidence": "Low/Medium/High",
  "final_summary": "max 100 words"
}}

No commentary. No markdown. Only JSON.
"""
    raw = query_llm(prompt, max_tokens=500)
    return safe_parse(raw)

