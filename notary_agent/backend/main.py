# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.deed_generator import generate_deed_text
from backend.pdf_generator import generate_pdf
from fastapi.responses import FileResponse
from fastapi import HTTPException
import os
from backend.docx_generator import generate_deed_docx
from backend.rent_agreement_docx_generator import generate_rent_agreement_docx
import openai
from dotenv import load_dotenv

from pydantic import BaseModel

class ClauseRequest(BaseModel):
    field: str
    context: str


app = FastAPI()

# Enable CORS for frontend (for now allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "NotaryAI backend is running"}

@app.post("/generate-deed/")
async def create_partnership_deed(data: dict):
    print("✅ Received POST data")
    deed_text = generate_deed_text(data)
    print("🧠 AI-generated deed text ready")
    
    pdf_path = generate_pdf(data, filename_prefix=data["firm_name"].replace(" ", "_"))
    print(f"📁 PDF path returned: {pdf_path}")
    
    return {"deed_text": deed_text, "pdf_path": pdf_path}
    
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    folder = "generated_pdfs"
    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@app.post("/generate-docx/")
async def create_docx(data: dict):
    docx_path = generate_deed_docx(data, filename_prefix=data["firm_name"].replace(" ", "_"))
    return FileResponse(path=docx_path, filename=os.path.basename(docx_path), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.post("/generate-rent-agreement/")
async def create_rent_doc(data: dict):
    path = generate_rent_agreement_docx(data, filename_prefix=data["tenant"]["company_name"].replace(" ", "_"))
    return FileResponse(path, filename=os.path.basename(path), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.post("/suggest-clause/")
async def suggest_clause(body: ClauseRequest):
    field = body.field
    context = body.context

    prompts = {
        "duties": {
            "partnership": "Suggest professional duties and responsibilities for each partner in a partnership deed.",
            "rent": "Suggest standard tenant duties for a commercial rent agreement between landlord and company tenant."
        }
    }

    prompt = prompts.get(field, {}).get(context, "Suggest a standard legal clause.")

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        suggestion = response.choices[0].message.content.strip()
        return { "suggestion": suggestion }
    except Exception as e:
        print("❌ GPT Error:", str(e))  # <-- log this
        return { "suggestion": None, "error": str(e) }
