# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.deed_generator import generate_deed_text
from backend.pdf_generator import generate_pdf
from fastapi.responses import FileResponse
from fastapi import HTTPException
import os


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
    
    pdf_path = generate_pdf(deed_text, filename_prefix=data["firm_name"].replace(" ", "_"))
    print(f"📁 PDF path returned: {pdf_path}")
    
    return {"deed_text": deed_text, "pdf_path": pdf_path}
    
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    folder = "generated_pdfs"
    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)
