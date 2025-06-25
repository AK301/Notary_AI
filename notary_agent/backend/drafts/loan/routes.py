# backend/drafts/loan/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.drafts.loan.schema import LoanAgreementRequest
from backend.drafts.loan.generator import generate_loan_docx
from backend.models import User, Draft
import datetime
import os

router = APIRouter(prefix="/loan", tags=["Loan Agreement"])


@router.post("/generate")
async def generate_loan_draft(
    data: LoanAgreementRequest, db: Session = Depends(get_db)
):
    print(data)

    try:
        data_dict = data.model_dump()
        docx_path = generate_loan_docx(
            data_dict, filename_prefix=data_dict["landlord_name"].replace(" ", "_")
        )

        user = db.query(User).filter(User.email == data.user_token).first()
        if user:
            draft = Draft(
                name=f"Loan_Agreement_{data_dict['landlord_name']}.docx",
                path=docx_path,
                user_id=user.id,
                date=datetime.datetime.now(),
            )
            db.add(draft)
            db.commit()

        return {"message": "Document generated", "path": docx_path}

    except Exception as e:
        print(f"❌ Document generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate document")
