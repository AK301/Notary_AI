from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import Draft, User
from utils.auth import get_current_user  # 🔐 JWT-based auth

router = APIRouter(prefix="/drafts", tags=["Draft History"])


@router.get("/")
def get_user_drafts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        drafts = (
            db.query(Draft)
            .filter(Draft.user_id == current_user.id)
            .order_by(Draft.id.desc())
            .all()
        )
        return [
            {"name": draft.name, "date": draft.date, "url": draft.url}
            for draft in drafts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load drafts: {str(e)}")
