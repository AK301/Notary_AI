# drafts/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.drafts.schemas import DraftCreate, DraftResponse
from backend.drafts.utility import save_draft, get_user_drafts
from typing import List

router = APIRouter(prefix="/drafts", tags=["Drafts"])


@router.get("/", response_model=List[DraftResponse])
def list_drafts(token: str, db: Session = Depends(get_db)):
    return get_user_drafts(token, db)


@router.post("/", response_model=DraftResponse)
def create_draft(data: DraftCreate, db: Session = Depends(get_db)):
    return save_draft(data, db)
