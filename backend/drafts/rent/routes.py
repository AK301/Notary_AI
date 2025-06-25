from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import User, Draft
from backend.drafts.rent.schema import RentAgreementRequest
from backend.drafts.rent.generator import generate_rent_docx
from utils.email_sender import send_email_with_attachment
import datetime
import os

router = APIRouter(prefix="/rent", tags=["Rent Agreement Draft"])


@router.post("/generate")
async def generate_rent_agreement(
    data: RentAgreementRequest, db: Session = Depends(get_db)
):
    try:
        path = generate_rent_docx(data, filename_prefix=data.tenant_name)

        # Save in DB
        user = db.query(User).filter(User.email == data.user_token).first()
        if user:
            draft = Draft(
                name=f"Rent Agreement - {data.property_address}",
                date=str(datetime.date.today()),
                url=f"http://127.0.0.1:8000/download/{os.path.basename(path)}",
                owner=user,
            )
            db.add(draft)
            db.commit()

        # Send Email
        send_email_with_attachment(
            to_email=data.user_token,
            subject="Your Rent Agreement Document",
            body="Your rent agreement has been generated and is attached to this email.",
            attachment_path=path,
        )

        return FileResponse(
            path=path,
            filename=os.path.basename(path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Document generation failed: {str(e)}"
        )
