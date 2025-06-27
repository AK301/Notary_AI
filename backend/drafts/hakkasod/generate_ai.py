from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AIDraftRequest(BaseModel):
    scenario: str
    language: str = "marathi"


def generate_hakkasod_from_scenario(data: AIDraftRequest) -> str:
    try:
        print("✅ Received scenario:", data.scenario)

        prompt = f"""
        खालील माहितीच्या आधारे मराठीत हक्कसोड पत्र तयार करा:

        माहिती:
        {data.scenario}

        योग्य कायदेशीर शैली वापरा.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error during AI generation:", str(e))
        raise e
