from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.drafts.partnership.generator import generate_partnership_docx
from backend.drafts.partnership.schema import PartnershipDeedRequest
from backend.models import Draft, User
from utils.email_sender import send_email_with_attachment
import datetime
import os

router = APIRouter(prefix="/partnership", tags=["Partnership Draft"])


@router.post("/generate")
async def generate_partnership_draft(
    data: PartnershipDeedRequest, db: Session = Depends(get_db)
):
    try:
        # ✅ Generate document
        filename_prefix = f"{data.firm_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        docx_path = generate_partnership_docx(data, filename_prefix=filename_prefix)

        # ✅ Save draft to DB if user exists
        user = db.query(User).filter(User.email == data.user_token).first()
        if user:
            draft = Draft(
                name=f"Partnership_Deed - {data.firm_name}",
                date=str(datetime.date.today()),
                url=f"http://127.0.0.1:8000/download/{os.path.basename(docx_path)}",
                owner=user,
            )
            db.add(draft)
            db.commit()

        # ✅ Send document via email
        send_email_with_attachment(
            to_email=data.user_token,
            subject="Your Partnership Deed Document",
            body="Dear user, your partnership deed is attached. Thank you for using NotaryAI.",
            attachment_path=docx_path,
        )

        return FileResponse(
            path=docx_path,
            filename=os.path.basename(docx_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except Exception as e:
        import traceback

        print("❌ Document generation failed:\n", traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Document generation failed: {str(e)}"
        )
