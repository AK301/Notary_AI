from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel
from backend.db import get_db
from backend.models import User

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hash(data.password)
    new_user = User(email=data.email, name=data.name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful", "token": new_user.email}


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "token": user.email}
