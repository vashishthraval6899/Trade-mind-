import os
import requests

OPENROUTER_API_KEY = os.getenv("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")

MODEL = "mistralai/mistral-7b-instruct"

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def query_llm(prompt, max_tokens=500):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional equity research analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        raise Exception("OpenRouter API Error")

    result = response.json()

    return result["choices"][0]["message"]["content"]
