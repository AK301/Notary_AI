# drafts/utils.py

from sqlalchemy.orm import Session
from backend.models import Draft, User
from backend.drafts.schemas import DraftCreate
from fastapi import HTTPException


def save_draft(data: DraftCreate, db: Session):
    user = db.query(User).filter(User.email == data.user_token).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid user token")

    draft = Draft(name=data.name, date=data.date, url=data.url, owner=user)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def get_user_drafts(user_token: str, db: Session):
    user = db.query(User).filter(User.email == user_token).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid user token")
    return user.drafts
