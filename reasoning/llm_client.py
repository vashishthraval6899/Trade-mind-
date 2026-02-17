import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

# Load .env
load_dotenv()

def query_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.3):
    """
    Sends prompt to Gemini API (new SDK).
    """

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise Exception("GEMINI_API_KEY not found in .env")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )

        return response.text

    except Exception as e:
        print("Gemini API Error:", str(e))
        raise


# 🔥 Test block (only runs when file executed directly)
if __name__ == "__main__":
    print(query_llm("Explain machine learning in simple words."))
