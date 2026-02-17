import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

# Load environment variables
load_dotenv()

def query_llm(prompt: str, max_tokens: int = 1500, temperature: float = 0.3):
    """
    Sends prompt to Gemini API using strict JSON response mode.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise Exception("GEMINI_API_KEY not found.")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json"  # 🔥 FORCE STRICT JSON
            )
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        return response.text.strip()

    except Exception as e:
        print("Gemini API Error:", str(e))
        raise


# Local test
if __name__ == "__main__":
    test_prompt = """
    Return strictly this JSON:
    {
      "message": "hello world"
    }
    """
    print(query_llm(test_prompt))
