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
        तुम्हाला हक्कसोड (Hakkasod Patra) तयार करायचा आहे. खाली दिलेल्या माहितीच्या आधारे, मराठी भाषेत एक कायदेशीर आणि योग्य हक्कसोड पत्र तयार करा. हक्कसोड पत्रात कोणती व्यक्ती कोणासाठी आणि कोणत्या कारणासाठी हक्क सोडत आहे हे स्पष्टपणे नमूद करा.:

        माहिती:
        {data.scenario}

        📌 कृपया योग्य कायदेशीर भाषा वापरा. व्यावसायिक स्वरूपाचा भाग Partnership Deed प्रमाणे नसावा.
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
