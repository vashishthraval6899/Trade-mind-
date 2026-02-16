import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.3):
    """
    Sends prompt to OpenRouter LLM.
    Uses .env for API key.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")

    if not api_key:
        raise Exception("OPENROUTER_API_KEY not found. Check .env file.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        raise Exception("OpenRouter API Error")

    return response.json()["choices"][0]["message"]["content"]
