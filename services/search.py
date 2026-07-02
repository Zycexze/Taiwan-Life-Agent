from google import genai

from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)


def google_search(query: str) -> str:
    """
    使用 Gemini Google Search Grounding
    """

    try:

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=query,
            tools=[
                {
                    "type": "google_search"
                }
            ]
        )

        return interaction.output_text

    except Exception as e:
        return f"Google Search 發生錯誤：{e}"