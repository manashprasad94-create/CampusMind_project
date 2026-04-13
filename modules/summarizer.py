# modules/summarizer.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Initialize once
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def summarize_notes(markdown_text: str) -> str:
    """
    Takes markdown notes text
    Returns concise bullet point summary
    """
    try:
        print("📝 Summarizing notes...")

        prompt = f"""
You are a helpful study assistant.
Summarize the following notes into maximum 8 clear bullet points.
Rules:
- Only include the most important concepts
- Keep each bullet point concise (1 line)
- Use simple easy to understand language
- Preserve any important formulas or definitions
- Start each point with a relevant emoji

Notes:
{markdown_text}

Return ONLY the bullet points, nothing else.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        print("✅ Summary generated!")
        return response.text

    except Exception as e:
        return f"Error generating summary: {str(e)}"