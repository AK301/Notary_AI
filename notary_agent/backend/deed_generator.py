# backend/deed_generator.py

import openai
from dotenv import load_dotenv
import os
from backend.prompt_template import deed_prompt

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_deed_text(data: dict) -> str:
    prompt = deed_prompt(data)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal expert specializing in drafting legal agreements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error generating deed: {str(e)}"
