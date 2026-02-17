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

    summary_prompt = f"""
You are a bullish equity analyst.

Summarize the bullish case in max 80 words.
No markdown. Just plain text.

Evidence:
{evidence[:3000]}
"""
    summary = query_llm(summary_prompt, max_tokens=300, temperature=0.2)

    score_prompt = f"""
Based on the bullish strength described below,
return ONLY a number between 0 and 100.

Summary:
{summary}
"""
    score_text = query_llm(score_prompt, max_tokens=50, temperature=0)

    try:
        score = int(''.join(filter(str.isdigit, score_text)))
    except:
        score = 50

    return {
        "bull_summary": summary.strip(),
        "bull_score": max(0, min(score, 100))
    }


def bear_agent(evidence):

    summary_prompt = f"""
You are a bearish equity analyst.

Summarize the bearish case in max 80 words.
No markdown. Just plain text.

Evidence:
{evidence[:3000]}
"""
    summary = query_llm(summary_prompt, max_tokens=300, temperature=0.2)

    score_prompt = f"""
Based on the bearish risk described below,
return ONLY a number between 0 and 100.

Summary:
{summary}
"""
    score_text = query_llm(score_prompt, max_tokens=50, temperature=0)

    try:
        score = int(''.join(filter(str.isdigit, score_text)))
    except:
        score = 50

    return {
        "bear_summary": summary.strip(),
        "bear_score": max(0, min(score, 100))
    }


def judge_agent(bull_output, bear_output, score_label, final_score):

    summary_prompt = f"""
You are a neutral portfolio manager.

Bull Score: {bull_output.get("bull_score")}
Bear Score: {bear_output.get("bear_score")}
Final Score: {final_score}
Preliminary Decision: {score_label}

In max 80 words:
1. Validate decision
2. Provide final decision: BUY / HOLD / SELL
3. Give confidence: Low / Medium / High

Respond in this format exactly:

Decision: BUY/HOLD/SELL
Confidence: Low/Medium/High
Summary: short explanation
"""
    response = query_llm(summary_prompt, max_tokens=400, temperature=0.2)

    decision = "HOLD"
    confidence = "Medium"

    if "BUY" in response.upper():
        decision = "BUY"
    elif "SELL" in response.upper():
        decision = "SELL"

    if "HIGH" in response.upper():
        confidence = "High"
    elif "LOW" in response.upper():
        confidence = "Low"

    return {
        "final_decision": decision,
        "confidence": confidence,
        "final_summary": response.strip()
    }