# backend/main.py

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import openai
import datetime
from dotenv import load_dotenv
from passlib.hash import bcrypt
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from backend.deed_generator import generate_deed_text
from backend.pdf_generator import generate_pdf
from backend.docx_generator import generate_deed_docx
from backend.rent_agreement_docx_generator import generate_rent_agreement_docx

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./notaryai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    drafts = relationship("Draft", back_populates="owner")

class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(String)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="drafts")

Base.metadata.create_all(bind=engine)

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class DraftResponse(BaseModel):
    name: str
    date: str
    url: str

class ClauseRequest(BaseModel):
    field: str
    context: str

@app.get("/")
def read_root():
    return {"message": "NotaryAI backend is running"}

@app.post("/signup")
def signup(data: SignupRequest, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hash(data.password)
    new_user = User(email=data.email, name=data.name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful", "token": new_user.email}

@app.post("/login")
def login(data: LoginRequest, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": user.email}

@app.get("/drafts", response_model=List[DraftResponse])
def get_drafts(token: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return [DraftResponse(name=d.name, date=d.date, url=d.url) for d in user.drafts]

@app.post("/generate-docx/")
async def create_docx(data: dict, db: SessionLocal = Depends(get_db)):
    for key in ["execution_date", "jurisdiction", "business_address", "area_of_operation", "start_date"]:
        data.setdefault(key, str(datetime.date.today()) if "date" in key else f"[{key.replace('_', ' ').capitalize()} Not Provided]")
    for role in ["partner1", "partner2"]:
        data.setdefault(role, {})
        for k in ["full_name", "father_name", "age", "address"]:
            data[role].setdefault(k, f"[{k.replace('_', ' ').capitalize()}]")

    docx_path = generate_deed_docx(data, filename_prefix=data["firm_name"].replace(" ", "_"))
    token = data.get("user_token", "notary@example.com")
    user = db.query(User).filter(User.email == token).first()
    if user:
        draft = Draft(
            name=f"Partnership_Deed - {data.get('firm_name', 'Unnamed')}",
            date=str(datetime.date.today()),
            url=f"http://127.0.0.1:8000/download/{os.path.basename(docx_path)}",
            owner=user
        )
        db.add(draft)
        db.commit()
    return FileResponse(path=docx_path, filename=os.path.basename(docx_path), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.post("/generate-rent-agreement/")
async def create_rent_doc(data: dict, db: SessionLocal = Depends(get_db)):
    data.setdefault("agreement_date", str(datetime.date.today()))
    data.setdefault("landlord", {})
    data.setdefault("tenant", {})
    data.setdefault("property", {})
    data["property"].setdefault("number", "[Property Number Not Provided]")
    data["property"].setdefault("address", "[Property Address Not Provided]")

    for party in ["name", "father_name"]:
        data["landlord"].setdefault(party, f"[Landlord {party.replace('_', ' ').capitalize()}]")
        data["tenant"].setdefault(party, f"[Tenant {party.replace('_', ' ').capitalize()}]")

    path = generate_rent_agreement_docx(data, filename_prefix=data["tenant"]["company_name"].replace(" ", "_"))
    token = data.get("user_token", "notary@example.com")
    user = db.query(User).filter(User.email == token).first()
    if user:
        draft = Draft(
            name=f"Rent_Agreement - {data['tenant']['company_name']}",
            date=str(datetime.date.today()),
            url=f"http://127.0.0.1:8000/download/{os.path.basename(path)}",
            owner=user
        )
        db.add(draft)
        db.commit()
    return FileResponse(path=path, filename=os.path.basename(path), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = os.path.join("generated_pdfs", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@app.post("/suggest-clause/")
async def suggest_clause(body: ClauseRequest):
    prompt = {
        "duties": {
            "partnership": "Suggest professional duties and responsibilities for each partner in a partnership deed.",
            "rent": "Suggest standard tenant duties for a commercial rent agreement between landlord and company tenant."
        }
    }.get(body.field, {}).get(body.context, "Suggest a standard legal clause.")

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return {"suggestion": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"suggestion": None, "error": str(e)}
